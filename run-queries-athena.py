#!/usr/bin/env python3
import boto3 #for aws api
import datetime #for object path creation in bucket
import time #for waiters
import re #for regex

def get_database (accountNumber, environment, s3_output, date):
    client = boto3.client('athena') #client athena instantiation
    database_list = [] #list declaration
    response = run_query("SHOW DATABASES;", "default", s3_output, date) #running query that returns all databases
    query_results = client.get_query_results(QueryExecutionId = response['QueryExecutionId'])['ResultSet']['Rows'] #saving query results

    for row in query_results:
        database_list.append(row['Data'][0]['VarCharValue']) #saving database names i\n a list

    #searching for the mathing database name in database list
    for database in database_list:
        if re.search(accountNumber, database):
            if re.search(environment+'$', database):
                return database #the database name has the account number and ends with de desired environment ('dev', 'homolog' or 'prod')

#Function that runs an sql query
def run_query(query, database, s3_output, date):
    
    client = boto3.client('athena')

    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': database
            },
        ResultConfiguration={
            'OutputLocation': s3_output + "/" + query + "/" + str(date.year) + "/" + str(date.month) + "/" + str(date.day) + "/" #s3 bucket where the results will be stored
            }
        )
    print('Execution ID: ' + response['QueryExecutionId']) #prints query's Execution ID
    
    status = check_query_status(response['QueryExecutionId']) #checks query's status
    
    if (status == 'failed'):
        query_results = boto3.client('athena').get_query_results(
            QueryExecutionId = response['QueryExecutionId']
        )['ResultSet']['Rows']
        boto3.client('sns').publish(
            TopicArn = 'arn:aws:sns:us-east-1:518512136469:run_queries_status',
            Message = 'Query \"' + query + '\" failed!\n\n' + str(query_results)
        )
    print ("Query execution status: " + status)
    return response

def check_query_status (query_execution_id):

    client = boto3.client('athena')

    status = client.get_query_execution(
        QueryExecutionId = query_execution_id
    )['QueryExecution']['Status']['State']

    while (status == 'QUEUED'):
        time.sleep(5) 
        status = client.get_query_execution(QueryExecutionId = query_execution_id)
        
    while (status == 'RUNNING'):
        time.sleep(3)  
        status = client.get_query_execution(QueryExecutionId = query_execution_id)
        
    if (status == 'FAILED'):
        return "failed"
        
    if (status == 'CANCELLED'):
        return "cancelled"
        
    return "success"

#Retrieves a queries list from a bucket stored file
def get_queries_from_bucket (bucket, object_key):
    client = boto3.client('s3') 

    response = client.get_object(
        Bucket=bucket,
        Key=object_key
    )
    queries = response['Body'].read().decode('utf-8') #retrieving object body (file content)
    return queries.split('\n')

def lambda_handler(event, context):
    date = datetime.datetime.now()
    bucket = 'aws-athena-query-results-518512136469-us-east-1'
    s3_output = 's3://' + bucket
    queries_filename = event['queries_filename']
    account_number = event['account_number']
    environment = event['environment']

    queries = get_queries_from_bucket(bucket, queries_filename)
    database = get_database (account_number, environment, s3_output, date)

    for query in queries:
        print("Executing query: %s" % (query))
        response = run_query(query, database, s3_output, date)
