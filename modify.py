#!/usr/bin/env python3
# Description: Automatically modifies aws instance reservations
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import time
from verify_payment import verify_payment_pending

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

    payment_pending = True

    while (payment_pending):
        payment_pending = verify_payment_pending(client)

        time.sleep(10)

    #Modificaçao de reserva
    modification_id = client.modify_reserved_instances(
        ReservedInstancesIds = [reservation_description['ReservedInstancesId']],
        TargetConfigurations = target_config_list
    )['ReservedInstancesModificationId']

    while (not payment_pending):
        payment_pending = verify_payment_pending(client)

        time.sleep(10)

    modification_results = client.describe_reserved_instances_modifications(
        ReservedInstancesModificationIds = [modification_id]
    )['ReservedInstancesModifications'][0]

    return modification_results