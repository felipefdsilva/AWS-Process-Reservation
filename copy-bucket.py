import boto3
import json #for debug

src_bucket = 'sulamerica.billing.us'
dst_bucket = 'ipsense.sulamerica.billing.us'

session_src = boto3.Session(profile_name = 'gov-sulamerica')
client_src = session_src.client('s3')

session_dst = boto3.Session(profile_name = 'temp-ipsense')
client_dst = session_dst.client('s3')

src_path = 'parquet/Billing_Parquet/Billing_Parquet/'

def copy_object(origin, destiny, object_key):
	s3_object = client_src.get_object(Bucket = origin, Key = object_key)
	client_dst.put_object (Bucket = destiny, Body = s3_object['Body'].read(), Key = object_key)

src_obj_list = client_src.list_objects_v2(Bucket = src_bucket, Prefix = src_path)
#print (json.dumps(src_obj_list, indent = 4, sort_keys = True, default=str))

for src_obj in src_obj_list['Contents']:
	try:
		dst_obj_metadata = client_dst.head_object(Bucket = dst_bucket, Key = src_obj['Key'])
	except:
		print ("There's no %s object in %s" %(src_obj['Key'], dst_bucket))
		print ("Copying object")

		copy_object(src_bucket, dst_bucket, src_obj['Key'])
		dst_obj_metadata = {}

	if (dst_obj_metadata != {}):
		if (dst_obj_metadata['LastModified'] < src_obj['LastModified']):
			print ("%s (origem): %s" %(src_obj['Key'], src_obj['LastModified']))
			print ("%s (destino): %s" %(src_obj['Key'], dst_obj_metadata['LastModified']))
			print ("Copying %s to %s" %(src_obj['Key'], dst_bucket))

			copy_object(src_bucket, dst_bucket, src_obj['Key'])
