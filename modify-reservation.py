#!/usr/bin/env python3
# Description: Automatically modifies aws instance reservations
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import boto3 #for aws api
import json #for pretty print
import sys #for argv
import time #for sleep

if (len(sys.argv) != 3):
    print ("Usage: python %s <reservation id list> <reservation instance count list>")
    exit(1)

#argumentos de entrada do programa
reserved_instance_id_list = sys.argv[1].split(',')
instance_count_list = [int(count) for count in sys.argv[2].split('-')]

#instanciando cliente
session = boto3.Session(profile_name = 'painel')
client = session.client('ec2')

#Coletando dados da reserva
reservation_description = client.describe_reserved_instances(
    ReservedInstancesIds = reserved_instance_id_list,
)['ReservedInstances'][0]

print ("Reservation Description")
print (json.dumps(reservation_description, indent = 4, sort_keys = True, default = str))
print ("---------- End of Description -------------")

target_config_list = []

for instance_count in instance_count_list:
    reservation_params = {
        'InstanceCount': instance_count,
        'InstanceType': reservation_description['InstanceType'],
        'Platform': 'EC2-VPC',
        'Scope': reservation_description['Scope']
    }
    target_config_list.append(reservation_params)

#Modificaçao de reserva
modification_id = client.modify_reserved_instances(
    ReservedInstancesIds = reserved_instance_id_list,
    TargetConfigurations = target_config_list
)['ReservedInstancesModificationId']

modification_status = 'not fulfilled'
wait = 0

#Loop que aguarda a modificação ser finalizada
while ((modification_status != 'fulfilled') and (wait < 900)):
    modification_results = client.describe_reserved_instances_modifications(
        ReservedInstancesModificationIds = [modification_id]
    )['ReservedInstancesModifications'][0]
    modification_status = modification_results['Status']
    wait = wait + 60
    time.sleep(60)

print (json.dumps(modification_results['ModificationResults'], indent = 4, sort_keys = True, default = str))