#!/usr/bin/env python3
# Description: Raises API clients
# Author: Felipe Ferreira da Silva
# Date: 27/07/2019

import boto3
import json

painel_account_number='518512136469'

#return a client object based on the paramentes on the input.json file
def get_client (service):

    #opening input file
    file = open('input.json', "r")
    input = json.load(file)
    file.close()

    if (input['AccountNumber'] == painel_account_number):
        return boto3.client(service, region_name=input['Region'])

    #Getting credentials to assume role
    account_credentials = boto3.client('sts').assume_role ( 
        RoleArn = 'arn:aws:iam::{accountNumber}:role/{role}'.
                    format(accountNumber=input['AccountNumber'], role=input['RoleName']),
        RoleSessionName = 'ipsense-process-reservation'
    )['Credentials']

    #Instantiating client
    external_client = boto3.client(service,
        aws_access_key_id = account_credentials['AccessKeyId'], 
        aws_secret_access_key = account_credentials['SecretAccessKey'], 
        aws_session_token = account_credentials['SessionToken'],
        region_name=input['Region']
    )
    return external_client