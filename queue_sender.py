import boto3
import json

queue_url = 'https://sqs.us-east-1.amazonaws.com/518512136469/process-reservation-queue.fifo'
file = open("input.json", "r")
input = json.load(file)
file.close()

session = boto3.Session(profile_name='painel', region_name='us-east-1')
client = session.client('sqs')

print("Sending input.json to queue")

input = json.dumps(input)

response = client.send_message(
    QueueUrl=queue_url,
    MessageBody=input,
    MessageGroupId='parameters'
)
print ("Message sent")

client = session.client('lambda')

print ("Calling Lambda Function ipsense-ecs-start-task")

response_lambda_call = client.invoke(
    FunctionName='ipsense-ecs-start-task',
    InvocationType='Event',
    LogType='Tail',
    ClientContext='caller:SQS_sender'
)

print ("Response")
print (json.dumps(response_lambda_call, indent=4, sort_keys=True, default=str))
