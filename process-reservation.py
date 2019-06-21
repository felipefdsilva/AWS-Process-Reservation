#!/usr/bin/env python3
# Description: Automatically modifies aws instance reservations (main function)
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import boto3 #for aws api
import json #for pretty print
import sys #for argv
import time #for sleep
from waiter import reservation_waiter
from modify import modify_reservation
from exchange import exchange_reservation, ExchangeException

if (len(sys.argv) != 2):
    print ("Usage: python %s <input-json-file>" %(sys.argv[0]))
    exit(1)

file = open(sys.argv[1], "r")
input = json.load(file)
file.close()

product_description_list = open('product_description_list.txt').read().splitlines()

#Validation of product_description input parameter
for target_product_description in input['TargetPlatformList']:
	valid_description = False

	for product_description in product_description_list:
		if (target_product_description == product_description):
			valid_description = True

	if (valid_description == False):
		print ("Not a valid product description - {}".format(target_product_description))
		exit(1)

#Instanciando cliente
session = boto3.Session(
	profile_name=input['AWSProfile'],
	region_name=input['Region']
)
client = session.client('ec2')

#Coletando dados da reserva
reservation_description = client.describe_reserved_instances(
    ReservedInstancesIds=[input['ReservationId']],
)['ReservedInstances'][0]

if (reservation_description['State'] is 'retired'):
    print("Reservation is retired")
    exit(1)
        
reservation_waiter(client, reservation_description)

#Validacao da contagem de instancias
remaining_instance_count = int(reservation_description['InstanceCount']) - input['WastedInstanceCount']

if (remaining_instance_count < 0):
	print ("Cannot detach {wasted} instances from a reservation with instance count equals to {instance_count}".
			format(wasted=input['WastedInstanceCount'], instance_count=reservation_description['InstanceCount']))
	exit(1)

#Modification to split used instances and wasted instances
if (remaining_instance_count > 0):
	instance_count_list = [input['WastedInstanceCount'], remaining_instance_count]
	
	modification_response = modify_reservation(client, reservation_description, instance_count_list)

	print ("New reservations after modification:")
	print ((json.dumps(modification_response['ModificationResults'], indent=4, sort_keys=True, default=str)))

	for reservation in modification_response['ModificationResults']:
		if (reservation['TargetConfiguration']['InstanceCount'] == input['WastedInstanceCount']):
			reservation_description = client.describe_reserved_instances(
			    ReservedInstancesIds=[reservation['ReservedInstancesId']],
			)['ReservedInstances'][0]

			reservation_waiter(client, reservation_description)

#Exchange to t3.nano
if (reservation_description['InstanceType'] != 't3.nano'):
	print ("Exchanging reservation {id}".format(id=reservation_description['ReservedInstancesId']))

	try:	
		reservation_description = exchange_reservation(
			client,
			reservation_description, 
			't3.nano',
			input['T3NanoExpectedInstanceCount'],
			'Linux/UNIX (Amazon VPC)', 
			input['MaxHourlyPriceDifference'],
		)
	except ExchangeException as error:
		print (error)
		exit(1)

	print ("Exchange Results:")
	print (json.dumps(reservation_description, indent=4, sort_keys=True, default=str))
	reservation_waiter(client, reservation_description)

#Spliting t3.nano reservation for final exchanges
if (len(input['T3NanoSplitInstanceCountList']) > 1):
	modification_response = modify_reservation (
		client, 
		reservation_description, 
		input['T3NanoSplitInstanceCountList']
	)
	print ("New reservations after the modification:")
	print (json.dumps(modification_response['ModificationResults'], indent=4, sort_keys=True, default=str))

#Flagging Reservations as a Exchange candidate
for reservation in modification_response['ModificationResults']:
	reservation['exchange_flag'] = True

#Final Exchange
for index in range (len(input['T3NanoSplitInstanceCountList'])):
	for reservation in modification_response['ModificationResults']:
		if (reservation['exchange_flag'] == True):
			if (reservation['TargetConfiguration']['InstanceCount'] == input['T3NanoSplitInstanceCountList'][index]):
				reservation['exchange_flag'] = False
	
				reservation_description = client.describe_reserved_instances(
					ReservedInstancesIds=[reservation['ReservedInstancesId']],
				)['ReservedInstances'][0]

				reservation_waiter(client, reservation_description)
				
				if (reservation_description['InstanceType'] != input['TargetInstanceTypeList'][index]) or \
					(reservation_description['ProductDescription'] != input['TargetPlatformList'][index]):
					try:	
						final_reservation = exchange_reservation (
							client,
							reservation_description,
							input['TargetInstanceTypeList'][index],
							input['TargetInstanceCountList'][index], 
							input['TargetPlatformList'][index],
							input['MaxHourlyPriceDifference']
						)
					except ExchangeException as error:
						print(error)

					print (json.dumps(final_reservation, indent=4, sort_keys=True, default=str))

				break