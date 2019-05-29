import boto3

def get_object_from_source (source_bucket, object_key):
	client = boto3.client('s3')

	response = client.get_object(
        Bucket = bucket,
        Key = object_key
    )
    return response

def write_object_to_destination (destination_bucket, get_object_response, object_key):
	client = boto3.client('s3')

	response = client.put_object(
		Bucket = destination_bucket,
		Body = get_object_response['Body'],
		Key = object_key
	)
	return response

def retrieve_objects_list (bucket):
	client = boto3.client('s3')

	response = client.list_objects(
		Bucket = bucket
	)
	return response

source_object_list = retrieve_objects_list('teste-felipe-source')
destination_object_list = 

for s3_object in object_list:
