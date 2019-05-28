#!/usr/bin/env python3
# Description: Automatically exchanges aws instance reservations
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import boto3 #for aws api
import json #for pretty print

reservation_duration = 94608000 #(31536000 | 94608000)
instance_type = 't2.medium'
platform = 'Linux/UNIX (Amazon VPC)'

client = boto3.client('ec2')

response = client.describe_reserved_instances_offerings(
    Filters=[
        {
            'Name': 'duration',
            'Values': ['94608000']
        },
    ],
    InstanceType=instance_type,
    OfferingClass='convertible',
    ProductDescription=platform,
    InstanceTenancy='default',
    OfferingType='No Upfront'
)

print(json.dumps(response, indent=4, sort_keys=True))
"""
response = client.get_reserved_instances_exchange_quote(
    DryRun = True,
    ReservedInstanceIds=[
        reserved_instance_id,
    ],
    TargetConfigurations=[
        {
            'InstanceCount': 123,
            'OfferingId': offering_id
        },
    ]
)
"""