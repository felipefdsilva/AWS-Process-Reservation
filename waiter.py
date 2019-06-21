#!/usr/bin/env python3
# Description: describe aws instance reservations
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import boto3 #for aws api
import time #for sleep

def reservation_waiter (client, reservation_description):
    time_spent = 0

    #Waiting reservation to became active
    while (reservation_description['State'] != 'active'):
        time.sleep(60)
        time_spent = time_spent + 60

        reservation_description = client.describe_reserved_instances(
            ReservedInstancesIds = [reservation_description["ReservedInstancesId"]]
        )['ReservedInstances'][0]

        if (time_spent > 600):
            print ('Reservation took too long to become active')
            exit(1)