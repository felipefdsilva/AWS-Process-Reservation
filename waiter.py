#!/usr/bin/env python3
# Description: waits reservation to become active
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import boto3 #for aws api
import time #for sleep
from sts import get_client

class WaiterException (Exception):
    pass
    
#Waits reservation to have 'active' status
def reservation_waiter (reservation):

    ec2 = get_client('ec2')

    reservation_id = reservation['ReservedInstancesId']
    reservation_state = reservation['State']

    if (reservation_state == 'retired'):
        raise WaiterException ("reservation {id} is retired".format(id=reservation_id))

    time_spent = 0
    
    while (reservation_state == 'payment-pending'):
        time.sleep(10)
        time_spent = time_spent + 10

        if (time_spent > 1200):
            raise WaiterException('Reservation took too long to become active')

        if (reservation_state == 'payment-failed'):
            raise WaiterException("reservation {id} payment failed".format(reservation_id))

        reservation_state = ec2.describe_reserved_instances(
            ReservedInstancesIds = [reservation["ReservedInstancesId"]]
        )['ReservedInstances'][0]['State']

    return

# Waits the describe method to return no reservation with payment pending if value is False
# or to return any reservation with payment pending if value is True
def wait_payment_pending (value):

    ec2 = get_client('ec2')

    payment_pending = not value
    
    while payment_pending is not value:

        time.sleep(10)
        reservation_list = ec2.describe_reserved_instances(
            Filters=[
                {
                    'Name': 'state',
                    'Values': ['payment-pending']
                },
            ],
        )['ReservedInstances']

        if (len(reservation_list)):
            payment_pending = True
        else:
            payment_pending = False

    return