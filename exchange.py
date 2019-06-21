#!/usr/bin/env python3
# Description: Automatically exchanges aws instance reservations
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import json #for pretty print
import time #for sleep
from verify_payment import verify_payment_pending

class ExchangeException (Exception):
    pass

def exchange_reservation (
    client, 
    reservation_description, 
    target_instance_type, 
    expected_intance_count, 
    target_platform, 
    max_hourly_price_difference
):
    #Listagem de ofertas
    reserved_instance_offerings = client.describe_reserved_instances_offerings(
        Filters = [
            {
                'Name' : 'scope',
                'Values': [reservation_description['Scope']]
            },
        ],
        MinDuration = reservation_description['Duration'],
        MaxDuration = reservation_description['Duration'],
        InstanceType = target_instance_type,
        OfferingClass = reservation_description['OfferingClass'],
        ProductDescription = target_platform,
        InstanceTenancy = reservation_description['InstanceTenancy'],
        OfferingType = reservation_description['OfferingType']
    )['ReservedInstancesOfferings']

    number_of_offerings = len(reserved_instance_offerings)

    if (number_of_offerings > 1):
        raise ExchangeException("The search returned " + \
                str(number_of_offerings) + \
                "instance offering(s)\n" + \
                "The exchange can't be done automatically\n" + \
                "Exiting\n")

    #Orçamento da mudança
    exchange_quote = client.get_reserved_instances_exchange_quote(
        ReservedInstanceIds = [reservation_description['ReservedInstancesId']],
        TargetConfigurations = [
            {
                'OfferingId': reserved_instance_offerings[0]['ReservedInstancesOfferingId']
            },
        ]
    )
    #Checagem de diferenca de preço
    original_hourly_price = float(
        exchange_quote['ReservedInstanceValueSet'][0]['ReservationValue']['HourlyPrice']
    )
    target_hourly_price = float(
        exchange_quote['TargetConfigurationValueSet'][0]['ReservationValue']['HourlyPrice']
    )
    hourly_price_difference = target_hourly_price - original_hourly_price

    if (hourly_price_difference > max_hourly_price_difference):
        raise ExchangeException("The exchange will not be done\n" + \
                "The target reservation hourly price is " + \
                str(target_hourly_price) + "\n" + \
                "The original reservation hourly price is " + \
                str(original_hourly_price) + "\n" + \
                "Exiting\n")

    #Checagem da contagem de instancias
    if (exchange_quote['TargetConfigurationValueSet'][0]['TargetConfiguration']['InstanceCount'] 
        != expected_intance_count):
        raise ExchangeException("The instance count did not match\n" + \
                "Instance Count by quotation: " + \
                str(exchange_quote['TargetConfigurationValueSet'][0]['TargetConfiguration']['InstanceCount']) + \
                "\n" + "Instance Count Expected: " + str (expected_intance_count) + "\n")

    payment_pending = True

    while (payment_pending):
        payment_pending = verify_payment_pending(client)

        if (payment_pending):
            time.sleep(10)
    
    #Realizacao da troca
    client.accept_reserved_instances_exchange_quote(
        ReservedInstanceIds=[reservation_description['ReservedInstancesId']],
        TargetConfigurations=[
            {
                'OfferingId': exchange_quote['TargetConfigurationValueSet'][0]['TargetConfiguration']['OfferingId']
            },
        ]
    )
    #Recuperando o ID da nova reserva
    time_spent = 0
    
    while (not payment_pending):
        payment_pending = verify_payment_pending(client)

        if(not payment_pending):
            time.sleep(10)

    new_reservation_description = client.describe_reserved_instances(
        Filters=[
            {
                'Name': 'state',
                'Values': ['payment-pending']
            },
        ],
    )['ReservedInstances']

    for reservation in new_reservation_description:
        if (reservation['InstanceCount']
            == exchange_quote['TargetConfigurationValueSet'][0]['TargetConfiguration']['InstanceCount']):
            return reservation
    
    raise ExchangeException("Could not retrieve new reservation ID")