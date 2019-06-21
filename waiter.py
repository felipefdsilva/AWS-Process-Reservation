#!/usr/bin/env python3
# Description: waits reservation to become active
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import boto3 #for aws api
import time #for sleep

class WaiterException (Exception):
    pass

def reservation_waiter (client, reservation_description):
    time_spent = 0

    if (reservation_description['State'] == 'retired'):
        raise WaiterException (
            "reservation {id} is retired".
            format(reservation_description['ReservedInstancesId'])
        )

    #Waiting reservation to became active
    while (reservation_description['State'] == 'payment-pending'):
        time.sleep(60)
        time_spent = time_spent + 60

        if (time_spent > 600):
            print ('Reservation took too long to become active')
            exit(1)

        reservation_description = client.describe_reserved_instances(
            ReservedInstancesIds = [reservation_description["ReservedInstancesId"]]
        )['ReservedInstances'][0]

        if (reservation_description['State'] == 'payment-failed'):
            raise WaiterException(
                "reservation {id} payment failed".
                format(reservation_description['ReservedInstancesId'])
            )
