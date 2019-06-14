#!/usr/bin/env python3
# Description: Automatically modifies aws instance reservations (main function)
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import boto3 #for aws api
import json #for pretty print
import sys #for argv
from modify import modify_reservation
from exchange import exchange_reservation

if (len(sys.argv) != 2):
    print ("Usage: python %s <input-json-file>" %(sys.argv[0]))
    exit(1)

file = open(sys.argv[1], "r")
input = json.load(file)

product_description_list = ['Linux/UNIX',
							'Linux/UNIX (Amazon VPC)',
							'SUSE Linux',
							'SUSE Linux (Amazon VPC)',
							'Red Hat Enterprise Linux',
							'Red Hat Enterprise Linux (Amazon VPC)',
							'Windows, Windows (Amazon VPC)',
							'Windows with SQL Server Standard',
							'Windows with SQL Server Standard (Amazon VPC)',
							'Windows with SQL Server Web',
							'Windows with SQL Server Web (Amazon VPC)',
							'Windows with SQL Server Enterprise',
							'Windows with SQL Server Enterprise (Amazon VPC)']

#Validation of product_description input parameter
for target_product_description in input['TargetPlatformList']:
	valid_description = False
	for product_description in product_description_list:
		if (target_product_description == product_description):
			valid_description = True
	if (valid_description == False):
		print ("Not a valid product description - %s" %(target_product_description))
		exit(1)

#Instanciando cliente
session = boto3.Session(profile_name = 'default')
client = session.client('ec2')

#Coletando dados da reserva
reservation_description = client.describe_reserved_instances(
    ReservedInstancesIds = [input['ReservationId']],
)['ReservedInstances'][0]

remaining_instance_count = int(reservation_description['InstanceCount']) - input['WastedInstanceCount']

#Instance Count validation
if (remaining_instance_count < 0):
	print ("Cannot detach %i instances from a reservation with instance count equals to %s"\
			%(new_instance_count, reservation_description['InstanceCount']))
	exit(1)

#Modification to split used instances and wasted instances
if (remaining_instance_count > 0):
	instance_count_list = [new_instance_count, remaining_instance_count]
	
	modification_response = modify_reservation(client, reservation_description, instance_count_list)
	print ("New reservations after the modification:")
	print ((json.dumps(modification_response['ModificationResults'], indent = 4, sort_keys = True, default = str)))

	for reservation in modification_response['ModificationResults']:
		if (reservation['TargetConfiguration']['InstanceCount'] == input['WastedInstanceCount']):
			reservation_description = client.describe_reserved_instances(
			    ReservedInstancesIds = [reservation['ReservedInstancesId']],
			)['ReservedInstances'][0]

#Exchange to t3.nano
if (reservation_description['ProductDescription'] != 't3.nano'):
	print ("Exchanging reservation %s" %(reservation_description['ReservedInstancesId']))
	t3_nano_reservation_str = exchange_reservation(
		client, 
		reservation_description, 
		't3.nano',
		input['T3NanoExpectedInstanceCount'],
		'Linux/UNIX', 
		input['MaxHourlyPriceDifference']
	)
	print (t3_nano_reservation_str)
	try:
		t3_nano_reservation = json.loads(t3_nano_reservation_str)
	except:
		exit(1)

modification_response = modify_reservation (client, t3_nano_reservation, input['T3NanoSplitInstanceCountList'])
print ("New reservations after the modification:")
print ((json.dumps(modification_response['ModificationResults'], indent = 4, sort_keys = True, default = str)))

#Flagging Reservations as a Exchange candidate
for reservation in modification_response['ModificationResults']:
	reservation['exchange_flag'] = True

#Final Exchange
for index in range (0, len(input['T3NanoSplitInstanceCountList'])):
	for reservation in modification_response['ModificationResults']:
		if (reservation['exchange_flag'] == True):
			if (reservation['TargetConfiguration']['InstanceCount'] == input['T3NanoSplitInstanceCountList'][index]):
				reservation['exchange_flag'] = False
			
				reservation_description = client.describe_reserved_instances(
					ReservedInstancesIds = [reservation['ReservedInstancesId']],
				)['ReservedInstances'][0]
				
				print ("New reservation: ")
				print(exchange_reservation(
					client, 
					reservation_description, 
					input['TargetPlatformList'][index],
					input['TargetInstanceCountList'][index],
					input['TargetInstanceTypeList'][index], 
					input['MaxHourlyPriceDifference']
				))
				break