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
    
#Function that checks query status (works like a waiter)
def check_query_status (query_execution_id):

    client = boto3.client('athena') #client athena instantiation

    status = client.get_query_execution(QueryExecutionId = query_execution_id) #getting query execution status
    #Dealing with queries execution outcomes
    while (status['QueryExecution']['Status'] == 'QUEUED'): #if query was not executed yet
        time.sleep(5) #waits 5 seconds
        status = client.get_query_execution(QueryExecutionId = query_execution_id) #re-checks query status
    while (status['QueryExecution']['Status'] == 'RUNNING'): #if query is running
        time.sleep(3)  #waits 3 seconds
        status = client.get_query_execution(QueryExecutionId = query_execution_id) #re-checks query status
    if (status['QueryExecution']['Status'] == 'FAILED'): #if query execution failed
        return "failed" #return status
    if (status['QueryExecution']['Status'] == 'CANCELLED'): #if query was cancelled
        return "cancelled" #return status
    return "success" #if query did not failed of was cacelled, than it was a success

#Retrieves a queries list from a bucket stored file
def get_queries_from_bucket (bucket, object_key):
    client = boto3.client('s3') #instantiates s3 client

    response = client.get_object( #retrieving object from bucket
        Bucket=bucket,
        Key=object_key
    )
    queries = response['Body'].read().decode('utf-8') #retrieving object body (file content)

    return queries.split('\n') #return all queries in a list

#Handler function for AWS Lambda
def handler (event, context): #arguments are passed as a json payload in 'event'

    date = datetime.datetime.now() #saving courrent date for s3_output
    s3_output = 's3://aws-athena-query-results-518512136469-us-east-1' #de default bucket for athena query results
    bucket = 'aws-athena-query-results-518512136469-us-east-1' #the bucket where queries are stored
    queries_filename = event['queries_filename'] #the object-key
    account_number = event['account_number'] #the AWS account number to identify the database
    environment = event['environment'] #it must be 'dev', 'homolog' or 'prod'

    queries = get_queries_from_bucket(bucket, queries_filename) #retrieving queries list
    database = get_database (account_number, environment, s3_output, date) #getting database name

    for query in queries: #loop to run all queries
        print("Executing query: " + query) #print query name for log purposes
        response = run_query(query, database, s3_output, date) #runs query
