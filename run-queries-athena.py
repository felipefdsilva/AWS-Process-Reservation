#!/usr/bin/env python3
import boto3 #for aws api
import datetime #for object path creation in bucket
import time #for waiters
import re #for regex

def get_database (accountNumber, environment, s3_output, date):
    #client athena instantiation
    client = boto3.client('athena') #client athena instantiation
    database_list = [] #list declaration
    response = run_query("SHOW DATABASES;", "default", s3_output, date) #running query that returns all databases
    query_results = client.get_query_results(QueryExecutionId = response['QueryExecutionId'])['ResultSet']['Rows'] #saving query results

    for row in query_results:
        database_list.append(row['Data'][0]['VarCharValue']) #saving database names in a list

    #searching for the mathing database name in database list
    for database in database_list:
        if re.search(accountNumber, database):
            if re.search(environment+'$', database):
                return database #the database name has the account number and ends with de desired environment ('dev', 'homolog' or 'prod')

#Function that runs an sql query
def run_query(query, database, s3_output, date):
    #client athena instantiation
    client = boto3.client('athena')
    #running query
    response = client.start_query_execution(
        QueryString=query,#sql query string
        QueryExecutionContext={
            'Database': database #the athena database name string
            },
        ResultConfiguration={
            'OutputLocation': s3_output + "/" + query + "/" + str(date.year) + "/" + str(date.month) + "/" + str(date.day) + "/" #s3 bucket where the results will be stored
            }
        )
    print('Execution ID: ' + response['QueryExecutionId']) #prints query's Execution ID
    status = check_query_status(response['QueryExecutionId']) #checks query's status
    print ("Query execution status: " + status) #prints query's status
    return response

def check_query_status (query_execution_id):
    #client athena instantiation
    client = boto3.client('athena')
    #getting query execution status
    status = client.get_query_execution(QueryExecutionId = query_execution_id)
    #Dealing with queries execution outcomes
    while (status['QueryExecution']['Status'] == 'QUEUED'):
        time.sleep(5) #waits 5 seconds
        status = client.get_query_execution(QueryExecutionId = query_execution_id) #re-checks
    while (status['QueryExecution']['Status'] == 'RUNNING'):
        time.sleep(3)  #waits 3 seconds
        status = client.get_query_execution(QueryExecutionId = query_execution_id) #re-checks
    if (status['QueryExecution']['Status'] == 'FAILED'):
        return "failed"
    if (status['QueryExecution']['Status'] == 'CANCELLED'):
        return "cancelled"
    return "success"

#Retrieves a queries list from a bucket stored file
def get_queries_from_bucket (bucket, object_key):
    client = boto3.client('s3') #instantiates s3 client

    response = client.get_object( #retrieving file object
        Bucket=bucket,
        Key=object_key
    )
    queries = response['Body'].read().decode('utf-8') #retrieving object body (file content)

    return queries.split('\n')

def handler (event, context):

    date = datetime.datetime.now()
    s3_output = 's3://aws-athena-query-results-518512136469-us-east-1'
    bucket = 'aws-athena-query-results-518512136469-us-east-1'
    queries_filename = event['queries_filename']
    account_number = event['account_number']
    environment = event['environment']

    queries = get_queries_from_bucket(bucket, queries_filename)
    database = get_database (account_number, environment, s3_output, date)

    for query in queries:
        print("Executing query: " + query)
        response = run_query(query, database, s3_output, date)
