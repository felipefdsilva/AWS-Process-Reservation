#!/usr/bin/env python3
# Description: Automatically modifies aws instance reservations (main function)
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import boto3 #for aws api
import json #for pretty print
import time #for sleep
from sts import get_client
from modify import modify_reservation
from waiter import reservation_waiter, WaiterException
from exchange import batch_exchange_reservation, ExchangeException
from aws_platform import validate_platform, validate_waste, ParameterValidationException

#Publishes a message through a SNS topic
def publish (message):

	sns_topic = 'arn:aws:sns:us-east-1:518512136469:ipsense-automation-process-reservation'

	boto3.client('sns').publish(
		TopicArn=sns_topic,
		Message=str(message)
	)
	print (message)

	return

def get_input_parameters (filename):
	
	file = open(filename, "r")
	parameters = json.load(file)
	file.close()

	return parameters

def describe_reserved_instances (id):
	ec2 = get_client('ec2')
	
	try:
		reservation_list = ec2.describe_reserved_instances(
			ReservedInstancesIds=[id],
		)['ReservedInstances']

	except IndexError:
		raise ("Not a valid Reserved Instances ID")
	
	return reservation_list

def main ():

	input = get_input_parameters('input.json')

	if (not validate_platform(input['TargetRIsParams']['PlatformList'])):
		publish("Not a valid Product Description" + '\n' + input['TargetRIsParams']['PlatformList'])
		exit(1)

	try:
		print ("Collecting RI data")
		reservation_list = describe_reserved_instances (input['ReservationId'])
		
	except IndexError as e:
		publish(e)
		exit(1)

	#Waits RI to be available
	try:
		print ("Waiting RI to have 'available' status") 
		reservation_waiter(reservation_list[0])

	except WaiterException as error:
		publish (error)
		exit(1)

	#Calculates de ramaining instance count by subtracting waste
	try:
		remaining_instance_count = \
		validate_waste(input['WastedInstanceCount'], reservation_list[0]['InstanceCount'])

	except ParameterValidationException as error:
		publish (error)
		exit(1)

	#Modification to split used instances and wasted instances
	if (remaining_instance_count > 0):

		print ("Detaching waste from RI")
		waste = input['WastedInstanceCount']
		instance_count_list = [waste, remaining_instance_count]
		
		reservation_list = modify_reservation(reservation_list[0], instance_count_list)

		publish ('Detached waste from RI')
		
		print ("New reservations after waste detachment:")
		for reservation in reservation_list:
			print (json.dumps(reservation, indent=4, sort_keys=True, default=str))

		reservation_list = [reservation_list[0]]
		
		#Waiting waste instance to be available
		try:
			reservation_waiter(reservation_list[0])

		except WaiterException as error:
			publish(error)
			exit(1)

	#Exchange to trade RI
	trade_instance_type = input["TradeRIParams"]["InstanceTypeList"][0]

	if (reservation_list[0]['InstanceType'] != trade_instance_type):

		message =  "Exchanging RI {id} to {trade} RI".\
			format(id=reservation_list[0]['ReservedInstancesId'], trade=trade_instance_type)
		publish(message)

		try:	
			reservation_list = batch_exchange_reservation(reservation_list, input['TradeRIParams'])

		except ExchangeException as error:
			publish (error)
			exit(1)

		print ("Exchange Results:")
		print (json.dumps(reservation_list[0], indent=4, sort_keys=True, default=str))

		try:
			reservation_waiter(reservation_list[0])

		except WaiterException as error:
			publish(error)
			exit(1)

	#Spliting trade reservation for final exchanges
	instance_count_list = input['TradeRIParams']['SplitInstanceCountList']

	if (len(instance_count_list) > 1):
		print ("Spliting trade RI")

		reservation_list = modify_reservation (reservation_list[0], instance_count_list)

		print ("New reservations after trade RI split")
		for reservation in reservation_list:
			print (json.dumps(reservation, indent=4, sort_keys=True, default=str))

		publish('Trade RI splitted')

	#Final Exchange
	print ("Doing final exchanges")
	try:	
		final_reservations = batch_exchange_reservation (
			reservation_list,
			input['TargetRIsParams']
		)
	except ExchangeException as error:
		publish(error)
		exit(1)

	for reservation in final_reservations:
		message = json.dumps(reservation, indent=4, sort_keys=True, default=str)
		print (message)

	publish('Reservation Processing Done')
	return None

if __name__ == '__main__':
	main()