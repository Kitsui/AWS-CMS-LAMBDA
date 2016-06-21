#!/usr/bin/python2.7

import boto3
import botocore
import os
import mimetypes
import time
import ast

# Creates a bucket for the CMS and populates it with the necessary files
def create_bucket(bucket_name=None, bucket_region=None):
	try:
		print 'Creating bucket'

		# Set the variables needed to create the bucket
		s3 = boto3.client('s3')
		bucket = None
		bucket_kwargs = {
			'ACL': 'public-read',
			'Bucket': bucket_name
		}
		if bucket_region != None and bucket_region != 'us-east-1':
			bucket_kwargs['CreateBucketConfiguration'] = {'LocationConstraint': bucket_region}

		# Create the bucket
		bucket = s3.create_bucket(**bucket_kwargs)

		print 'Bucket created'			
		print 'Populating bucket'

		# Populate the bucket
		for root, dirs, files in os.walk('website'):
			# Add all files from the website folder to the bucket
			for fl in files:
				# Set variables for adding the current file the bucket
				directory = root + '/' + fl
				key = directory[8:]
				mime = mimetypes.guess_type(directory)
				put_kwargs = {
					'ACL': 'public-read',
					'Body': directory,
					'Key': key
				}
				if mime[0] != None:
					put_kwargs['ContentType'] = mime[0]
				if mime[1] != None:
					put_kwargs['ContentEncoding'] = mime[1]
				
				print 'Uploading: %s' % key

				# Add file to the bucket
				bucket.put_object(**put_kwargs)

				print 'Complete'

		print 'Bucket populated'

	except botocore.exceptions.ClientError as e:
		print e.response['Error']['Code']
		return False

	return True

def create_user_table():
	try:
		dynamodb = boto3.client('dynamodb')
	
		print 'Creating user table'
	
		table = dynamodb.create_table(
			TableName='User',
			AttributeDefinitions=[
				{
					'AttributeName': 'ID',
					'AttributeType': 'S'
				},
				{
                	'AttributeName': 'Username',
                	'AttributeType': 'S'
            	}
			],
			KeySchema=[
				{
					'AttributeName': 'ID',
					'KeyType': 'HASH'
				},
				{
                	'AttributeName': 'Username',
                	'KeyType': 'RANGE'
            	}
			],
			ProvisionedThroughput={
				'ReadCapacityUnits': 5,
				'WriteCapacityUnits':5
			}
		)
	except botocore.exceptions.ClientError as e:
		print e.response['Error']['Code']
		return false

	created  = wait_for_table('User', dynamodb)
	return created

def create_token_table():
	try:
		dynamodb = boto3.client('dynamodb')

		print 'Creating token table'

		table = dynamodb.create_table(
			TableName='Token',
			AttributeDefinitions=[
				{
					'AttributeName': 'TokenString',
					'AttributeType': 'S'
				},
				{
					'AttributeName': 'UserID',
					'AttributeType': 'S'
				}
			],
			KeySchema=[
				{
					'AttributeName': 'TokenString',
					'KeyType': 'HASH'
				},
				{
					'AttributeName': 'UserID',
					'KeyType': 'RANGE'
				}
			],
			ProvisionedThroughput={
				'ReadCapacityUnits': 5,
				'WriteCapacityUnits':5
			}
		)
	except botocore.exceptions.ClientError as e:
		print e.response['Error']['Code']
		return false

	created = wait_for_table('Token', dynamodb)
	return created

def wait_for_table(table_name, dynamodb):
	response = {}
	table_creating = True
	retries = 10
	while table_creating and retries > 0:
		try:
			response = dynamodb.describe_table(TableName=table_name)
			table_creating = False
		except botocore.exceptions.ClientError as e:
			if e.response['error']['code'] == 'ResourceNotFoundException':
				retries -= 1
				time.sleep(0.5)
			else:
				print e.response['Error']['Code']
				return False

	while response['Table']['TableStatus'] == 'CREATING':
		time.sleep(0.1)
		response = dynamodb.describe_table(TableName=table_name)

	print table_name, 'table created'

	return True

def create_admin_db_entry():
	try:
		dynamodb = boto3.client('dynamodb')
		admin_json = ''
		with open('dynamo/user.json', 'r') as thefile:
			admin_json = ast.literal_eval(thefile.read())

		dynamodb.put_item(
			TableName='User',
			Item=admin_json,
			ReturnConsumedCapacity='TOTAL'
		)
	except botocore.exceptions.ClientError as e:
		print e.response['Error']['Code']
		return False

	return True

def create_token_db_entry():
	try:
		dynamodb = boto3.client('dynamodb')
		token_json = ''
		with open('dynamo/token.json', 'r') as thefile:
			token_json = ast.literal_eval(thefile.read())

		dynamodb.put_item(
			TableName='Token',
			Item=token_json,
			ReturnConsumedCapacity='TOTAL'
		)
	except botocore.exceptions.ClientError as e:
		print e.response['Error']['Code']
		return False

	return True

# Always returns 'MalformedPolicyDocument' error
def create_lambda_role():
	try:
		iam = boto3.client('iam')

		lambda_permissions_json = ''
		with open('lambda/lambda_permissions.json', 'r') as thefile:
			lambda_permissions_json = thefile.read()

		iam.create_role(
			RoleName='lambda_basic_execution',
			AssumeRolePolicyDocument={}
		)
	except botocore.exceptions.ClientError as e:
		print e.response['Error']['Code']
		return False

	return True

# Requires fix to 'create_lambda_role' to work
def create_lambda_function():
	try:
		a_lambda = boto3.client('lambda')
		iam = boto3.client('iam')
		lambda_basic_execution = iam.Role('lambda_basic_execution')		

		a_lambda.create_function(
			FunctionName='mainController',
			Runtime='python2.7',
			Role=lambda_basic_execution.arn
		)
	except botocore.exceptions.ClientError as e:
		print e.response['Error']['Code']
		return False

	return True

create_lambda_role()
