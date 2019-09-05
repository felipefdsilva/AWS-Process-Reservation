#!/usr/bin/env python3
# Description: Automatically exchanges aws instance reservations
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import time #for sleep
from sts import get_client
from offering import get_exchange_offering, OfferingException
from quotation import check_exchange_quote, QuotationException
from waiter import reservation_waiter, wait_payment_pending, WaiterException

class ExchangeException (Exception):
    pass

def exchange_reservation (reservation, instance_type, intance_count, platform, max_price_difference):

    ec2 = get_client('ec2')

    try:
        reservation_waiter(reservation)

    except WaiterException as error:
        raise ExchangeException (error)

    reservation_id = reservation['ReservedInstancesId']

    #Listagem de ofertas
    try:
        offering_id = get_exchange_offering(reservation, instance_type, platform)

    except OfferingException as e:
        raise ExchangeException(e)

    #Orçamento das Mudanças
    try:
        check_exchange_quote(reservation_id, offering_id, intance_count, max_price_difference)

    except QuotationException as e:
        raise ExchangeException(e)
    
    #Realizacao da troca
    ec2.accept_reserved_instances_exchange_quote(
        ReservedInstanceIds=[reservation_id],
        TargetConfigurations=[{'OfferingId': offering_id}]
    )
    return

def batch_exchange_reservation (reservation_list, target_params):

    ec2 = get_client('ec2')

    #Waiting for no payment pending status
    wait_payment_pending(False)

    index = 0
    number_of_exchanges = 0

    for reservation in reservation_list:
        if (reservation['InstanceType'] != target_params['InstanceTypeList'][index]):
            try:
                exchange_reservation (
                    reservation,    
                    target_params["InstanceTypeList"][index], 
                    target_params['InstanceCountList'][index], 
                    target_params['PlatformList'][index],
                    target_params['MaxPriceDifference']
                )
                number_of_exchanges += 1

            except ExchangeException as e:
                raise ExchangeException (e)

        index += 1

    #Recuperando o ID da nova reserva
    wait_payment_pending(True)

    reservation_count = 0
    reservation_list = []

    while (reservation_count != number_of_exchanges):
        reservation_list = ec2.describe_reserved_instances(
            Filters=[
                {
                    'Name': 'state',
                    'Values': ['payment-pending']
                },
            ],
        )['ReservedInstances']

        reservation_count = len(reservation_list)

        time.sleep(3)

    return reservation_list