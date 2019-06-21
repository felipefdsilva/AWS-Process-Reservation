#!/usr/bin/env python3
# Description: verifies if theres any reservation with 'payment-pending' status
# Author: Felipe Ferreira da Silva
# Date: 21/06/2019

def verify_payment_pending (client):

    reservation_list = client.describe_reserved_instances(
        Filters=[
            {
                'Name': 'state',
                'Values': ['payment-pending']
            },
        ],
    )['ReservedInstances']

    if (len(reservation_list)):
        return True

    return False