#!/usr/bin/env python3
# Description: Automatically exchanges aws instance reservations
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import boto3 #for aws api
import json #for pretty print

reserved_instance_id = '018c6199-5a29-4b7c-8a47-a61455f5d35b'
reservation_duration = 94608000 #(31536000 | 94608000)
target_instance_type = 'i3.xlarge'
platform = 'Linux/UNIX (Amazon VPC)'
offering_type = 'No Upfront'
max_hourly_price_difference = 0.010

client = boto3.client('ec2')

reserved_instances_offerings = client.describe_reserved_instances_offerings(
    Filters=[
        {
            'Name' : 'scope',
            'Values': ['Region']
        },
    ],
    MinDuration = reservation_duration,
    MaxDuration = reservation_duration,
    InstanceType = target_instance_type,
    OfferingClass = 'convertible',
    ProductDescription = platform,
    InstanceTenancy = 'default',
    OfferingType = offering_type
)
number_of_offerings = len(reserved_instances_offerings['ReservedInstancesOfferings'])
print ("The search returned %i instance offering(s)" %(number_of_offerings))

if (number_of_offerings > 1):
    print ("The exchange can't be done automatically")
    answer = 'n'
    print ("Do you want to see the offerings? (y/n)")
    answer = input()
    if (answer == 'y'):
        print(json.dumps(reserved_instances_offerings, indent = 4, sort_keys = True))
    else:
        print ("Exiting")
        exit(1)

exchange_quote = client.get_reserved_instances_exchange_quote(
    ReservedInstanceIds = [
        reserved_instance_id,
    ],
    TargetConfigurations = [
        {
            'OfferingId': reserved_instances_offerings['ReservedInstancesOfferings'][0]['ReservedInstancesOfferingId']
        },
    ]
)
print(json.dumps(exchange_quote, indent = 4, sort_keys = True, default=str))

original_hourly_price = float(exchange_quote['ReservedInstanceValueSet'][0]['ReservationValue']['HourlyPrice'])
target_hourly_price = float(exchange_quote['TargetConfigurationValueSet'][0]['ReservationValue']['HourlyPrice'])
hourly_price_difference = target_hourly_price - original_hourly_price

if (hourly_price_difference < max_hourly_price_difference):
    print ("The exchange will be done")
else:
    print ("The exchange will not be done")
    print ("The hourly price difference is greater than $%f"%(max_hourly_price_difference))
    print ("Exiting")
    exit(1)
"""
accept_exchange = client.accept_reserved_instances_exchange_quote(
    ReservedInstanceIds=[
        reserved_instance_id,
    ],
    TargetConfigurations=[
        {
            'OfferingId': exchange_quote['TargetConfigurationValueSet'][0]['TargetConfiguration']['OfferingId']
        },
    ]
)
print (json.dumps(accept_exchange, indent = 4, sort_keys = True, default=str))
"""