#!/usr/bin/env python3
# Description: Automatically exchanges aws instance reservations
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import boto3 #for aws api
import json #for pretty print
import sys
import time

if (len(sys.argv) != 3):
    print ("Usage: python %s <reservation_id> <target instance type>")
    exit(1)

#argumentos de entrada do programa
reserved_instance_id = sys.argv[1]
target_instance_type = sys.argv[2]
instance_count_list = [1 1]

#instanciando cliente
session = boto3.Session(profile_name = 'painel')
client = session.client('ec2')

#Coletando dados da reserva
reservation_description = client.describe_reserved_instances(
    ReservedInstancesIds=[reserved_instance_id],
)['ReservedInstances'][0]

print ("Reservation Description")
print (json.dumps(reservation_description, indent = 4, sort_keys = True, default = str))
print ("---------- End of Description -------------")

target_config_list = []

for instance_count in instance_count_list:
    reservation_params = {
        'InstanceCount': instance_count,
        'InstanceType': target_instance_type,
        'Platform': 'EC2-VPC',
        'Scope': 'Region'
    }
    target_config_list.append(reservation_params)

#Modificaçao de reserva
modification_id = client.modify_reserved_instances(
    ReservedInstancesIds = [reserved_instance_id],
    TargetConfigurations=target_config_list
)['ReservedInstancesModificationId']

#Resultados da Modicação
modification_results = client.describe_reserved_instances_modifications(
    ReservedInstancesModificationIds=[modification_id]
)['ReservedInstancesModifications'][0]

#Loop que aguarda a modificação ser finalizada
for try_count in range(10):
    time.sleep(60)
    modification_results = client.describe_reserved_instances_modifications(
        ReservedInstancesModificationIds=[modification_id]
    )['ReservedInstancesModifications']
    print (modification_results['ModificationResults'])
    print("Status: " + modification_results['Status'])