#!/usr/bin/env python3
# Description: Automatically modifies aws instance reservations (main function)
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import boto3 #for aws api
import json #for pretty print
import sys #for argv
from modify import modify_reservation
from exchange import exchange_reservation

if (len(sys.argv) != 6):
    print ("Usage: python %s <reservation id> <instance count for new reservation> <target instance type> <target platform> <max_price_difference>")
    exit(1)

reservation_id = sys.argv[1]
target_instance_type = sys.argv[3]
target_platform = sys.argv[4]
max_hourly_price_difference = float(sys.argv[5])
 
#Instanciando cliente
session = boto3.Session(profile_name = 'painel')
client = session.client('ec2')

#Coletando dados da reserva
reservation_description = client.describe_reserved_instances(
    ReservedInstancesIds = [reservation_id],
)['ReservedInstances'][0]

new_instance_count = int(sys.argv[2])
remaining_instance_count = int(reservation_description['InstanceCount'])-new_instance_count

if (target_platform != 'Linux/UNIX' &\ 
	target_platform != 'Linux/UNIX (Amazon VPC)' &\
	target_platform != 'Windows' &\
	target_platform != 'Windows (Amazon VPC)'):
	print ("Invalid target platform")
	exit(1)

if (remaining_instance_count < 0):
	print ("Cannot detach %i instances from a reservation with instance count equals to %s" %(new_instance_count, reservation_description['InstanceCount']))
	exit(1)

if (remaining_instance_count > 0):
	instance_count_list = [new_instance_count, remaining_instance_count]
	
	modification_response = modify_reservation(client, reservation_description, instance_count_list)
	print ("New reservations after the modification:")
	print ((json.dumps(modification_response['ModificationResults'], indent = 4, sort_keys = True, default = str)))

	for reservation in modification_response['ModificationResults']:
		if (reservation['TargetConfiguration']['InstanceCount'] == new_instance_count):
			reservation_description = client.describe_reserved_instances(
			    ReservedInstancesIds = [reservation['ReservedInstancesId']],
			)['ReservedInstances'][0]

if (target_instance_type != reservation_description['InstanceType']):
	print ("Exchanging reservation %s" %(reservation_description['ReservedInstancesId']))
	print (exchange_reservation(client, reservation_description, target_instance_type, target_platform, max_hourly_price_difference))