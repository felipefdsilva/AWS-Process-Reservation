#!/usr/bin/env python3
# Description: Automatically modifies aws instance reservations
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import time

def modify_reservation(client, reservation_description, instance_count_list):
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
        ReservedInstancesIds = [reservation_description['ReservedInstancesId']],
        TargetConfigurations = target_config_list
    )['ReservedInstancesModificationId']

    time_spent = 0
    while (time_spent < 60):
        modification_results = client.describe_reserved_instances_modifications(
            ReservedInstancesModificationIds = [modification_id]
        )['ReservedInstancesModifications'][0]

        if (modification_results['ModificationResults'][0]['ReservedInstancesId']):
            break
        time.sleep(10)
        time_spent +=10

    return modification_results