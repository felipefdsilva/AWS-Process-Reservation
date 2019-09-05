# Description: Starts ECS Task and send process-reservation input to SQS
# Author: Felipe Ferreira da Silva
# Date: 21/08/2019

import json
import boto3

def send_to_queue (queue_url, message):
    sqs = boto3.client('sqs')

    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message,
        MessageGroupId='parameters'
    )

def start_task ():
    ecs = boto3.client('ecs', region_name='us-east-1')

    run_task = ecs.run_task(
        cluster='process-reservation-cluster',
        taskDefinition='exec_process_reservation:2',
        count=1,
        startedBy='ipsense-ecs-start-task',
        group='process-reservation',
        launchType='FARGATE',
        platformVersion='LATEST',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': [
                    'subnet-0f8ba00b21e3c08fd',
                ],
                'securityGroups': [
                    'sg-02bfc62c8842f5f58',
                ],
                'assignPublicIp': 'ENABLED'
            }
        }
    )
    return run_task


def lambda_handler(event, context):

    queue_url = 'https://sqs.us-east-1.amazonaws.com/518512136469/process-reservation-queue.fifo'
    message = json.dumps(event)

    print("Sending input.json to queue")
    send_to_queue (queue_url, message)
    print ("Message sent")
    
    print ("Starting ECS task: exec_process_reservation")
    response = start_task()
    print(response)
    
    return {'statusCode': 200}
