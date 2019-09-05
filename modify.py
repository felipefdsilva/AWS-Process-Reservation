#!/usr/bin/env python3
# Description: Automatically modifies aws instance reservations
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import time
from sts import get_client
from waiter import wait_payment_pending

#Modifies RI, spliting the instance count into new RIs 
def modify_reservation(reservation, instance_count_list):

    ec2 = get_client('ec2')

    platform = 'EC2-VPC'
    target_config_list = []

    for instance_count in instance_count_list:
        reservation_params = {
            'InstanceCount': instance_count,
            'InstanceType': reservation['InstanceType'],
            'Platform': platform,
            'Scope': reservation['Scope']
        }
        target_config_list.append(reservation_params)

    wait_payment_pending (False)

    modification_id = ec2.modify_reserved_instances(
        ReservedInstancesIds = [reservation['ReservedInstancesId']],
        TargetConfigurations = target_config_list
    )['ReservedInstancesModificationId']

    wait_payment_pending(True)

    modification_results = ec2.describe_reserved_instances_modifications(
        ReservedInstancesModificationIds = [modification_id]
    )['ReservedInstancesModifications'][0]

    #Listing new reservation IDs
    id_list = []
    for reservation in modification_results['ModificationResults']:
        id_list.append(reservation['ReservedInstancesId'])

    #Updating description list
    reservation_list = ec2.describe_reserved_instances(
        ReservedInstancesIds=id_list
    )['ReservedInstances']

    #reordering reservations
    for index in range(len(reservation_list)):
        for description_index in range (index, len(reservation_list)):

            if (instance_count_list[index] == reservation_list[description_index]['InstanceCount']):

                if (index != description_index):
                    reservation_aux = reservation_list[index]
                    reservation_list[index] = reservation_list[description_index]
                    reservation_list[description_index] = reservation_aux

    return reservation_list