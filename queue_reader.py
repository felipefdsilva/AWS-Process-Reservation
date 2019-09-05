#!/usr/bin/env python3
# Description: Reads and deletes messages from queue
# Author: Felipe Ferreira da Silva
# Date: 12/07/2019

import boto3 #for aws api

queue_url = 'https://sqs.us-east-1.amazonaws.com/518512136469/process-reservation-queue.fifo'

#instantiante sqs client
client = boto3.client('sqs', region_name='us-east-1')

#receives message from queue
print ("Reading message from queue")
response = client.receive_message(QueueUrl=queue_url)

#checks if there is any message
if (response['ResponseMetadata']['HTTPHeaders']['content-length'] == '240'):
    print("No message in queue")
    exit(1)

message = response['Messages'][0]

#saves message in input.json
print ("Creating input.json")
file = open('input.json', 'w+')
file.write(message['Body'])
file.close()

#deletes message from queue
print ("Deleting message from queue")
response = client.delete_message(
    QueueUrl=queue_url, 
    ReceiptHandle=message['ReceiptHandle']
)