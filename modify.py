#!/usr/bin/env python3
# Description: Automatically modifies aws instance reservations
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import boto3 #for aws api
import time #for sleep

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

    modification_status = 'not fulfilled'

    #Loop que aguarda a modificação ser finalizada
    while ((modification_status != 'fulfilled')):
        modification_results = client.describe_reserved_instances_modifications(
            ReservedInstancesModificationIds = [modification_id]
        )['ReservedInstancesModifications'][0]

        modification_status = modification_results['Status']
        time.sleep(60)

    return modification_results