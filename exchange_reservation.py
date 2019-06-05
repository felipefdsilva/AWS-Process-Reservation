#!/usr/bin/env python3
# Description: Automatically exchanges aws instance reservations
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import boto3 #for aws api
import json #for pretty print
import sys #for argv
import time #for sleep

if (len(sys.argv) != 4):
    print ("Usage: python %s <reservation_id> <target_instance_type> <max_hourly_price_difference>")
    exit(1)

#argumentos de entrada
reservation_id = sys.argv[1]
target_instance_type = sys.argv[2]
max_hourly_price_difference = float(sys.argv[3])

#instanciando cliente
session = boto3.Session(profile_name = 'painel')
client = session.client('ec2')

#Coletando dados da reserva
reservation_description = client.describe_reserved_instances(
    ReservedInstancesIds = [reservation_id],
)['ReservedInstances'][0]

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
    ProductDescription = reservation_description['ProductDescription'],
    InstanceTenancy = reservation_description['InstanceTenancy'],
    OfferingType = reservation_description['OfferingType']
)['ReservedInstancesOfferings']

number_of_offerings = len(reserved_instance_offerings)
print ("The search returned %i instance offering(s)" %(number_of_offerings))

if (number_of_offerings > 1):
    print ("The exchange can't be done automatically") 
    print ("Exiting")
    exit(1)

#Orçamento da mudança
exchange_quote = client.get_reserved_instances_exchange_quote(
    ReservedInstanceIds = [reservation_id],
    TargetConfigurations = [
        {
            'OfferingId': reserved_instance_offerings[0]['ReservedInstancesOfferingId']
        },
    ]
)
print(json.dumps(exchange_quote, indent = 4, sort_keys = True, default = str))

original_hourly_price = float(exchange_quote['ReservedInstanceValueSet'][0]['ReservationValue']['HourlyPrice'])
target_hourly_price = float(exchange_quote['TargetConfigurationValueSet'][0]['ReservationValue']['HourlyPrice'])

hourly_price_difference = target_hourly_price - original_hourly_price

if (hourly_price_difference > max_hourly_price_difference):
    print ("The exchange will not be done")
    print ("The hourly price difference is greater than $%f" %(max_hourly_price_difference))
    print ("Exiting")
    exit(1)

#Realização da troca
accept_exchange = client.accept_reserved_instances_exchange_quote(
    ReservedInstanceIds=[reservation_id],
    TargetConfigurations=[
        {
            'OfferingId': exchange_quote['TargetConfigurationValueSet'][0]['TargetConfiguration']['OfferingId']
        },
    ]
)
time.sleep(10)

#retrieving the new reservation id
new_reservation_description = client.describe_reserved_instances(
    Filters=[
        {
            'Name': 'scope',
            'Values': [reservation_description['Scope']],
        },
        {
            'Name': 'duration',
            'Values': [str(reservation_description['Duration'])],
        },
        {
            'Name': 'instance-type',
            'Values': [target_instance_type],
        },
        {
            'Name': 'product-description',
            'Values': [reservation_description['ProductDescription']],
        },
    ],
    OfferingClass = reservation_description['OfferingClass'],
    OfferingType = reservation_description['OfferingType']
)['ReservedInstances']

for reservation in new_reservation_description:
    if (reservation['InstanceCount'] == exchange_quote['TargetConfigurationValueSet'][0]['TargetConfiguration']['InstanceCount']):
        if (reservation['State'] == 'payment-pending'):
            print(json.dumps(reservation, indent = 4, sort_keys = True, default=str))