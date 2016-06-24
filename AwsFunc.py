#!/usr/bin/python2.7

import boto3
import botocore
import os
import mimetypes
import time
import ast

class AwsFunc(object):
	""" Contains functions for creating, modifying and deleting elements of the AWSCMS. """
	def __init__(self):
		""" Gets low-level clients for services to be used and creates containers for
		AWS objects that will be filled by creation functions.
		"""
		self.s3 = boto3.client('s3')
		self.bucket = None

		self.dynamodb = boto3.client('dynamodb')
		self.user_table = None
		self.token_table = None

		self.lmda = boto3.client('lambda')
		self.lmda_function = None
		self.lmda_role = None

		self.iam = boto3.client('iam')

	def create_bucket(self, bucket_name=None, bucket_region=None):
		""" Creates a bucket with the name 'bucket_name' in region 'bucket_region'. If 
		'bucket_region' is not given, bucket will default to US Standard region.
		The bucket is then populated with files.
		"""
		try:
			print 'Creating bucket'

			# Set the variables needed to create the bucket
			bucket_kwargs = {
				'ACL': 'public-read',
				'Bucket': bucket_name
			}
			if bucket_region != None and bucket_region != 'us-east-1':
				bucket_kwargs['CreateBucketConfiguration'] = {'LocationConstraint': bucket_region}

			# Create the bucket
			self.bucket = self.s3.create_bucket(**bucket_kwargs)

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
						'Bucket': self.bucket['Location'][1:],
						'ACL': 'public-read',
						'Body': directory,
						'Key': key
					}
					if mime[0] != None:
						put_kwargs['ContentType'] = mime[0]
					if mime[1] != None:
						put_kwargs['ContentEncoding'] = mime[1]
				
					print 'Uploading: %s' % key

					# Add the current file to the bucket
					self.s3.put_object(**put_kwargs)

					print 'Complete'

			print 'Bucket populated'

		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			print e.response['Error']['Message']
			return False

		return True

	def create_user_table(self):
		""" Creates a user table. """
		try:
			print 'Creating user table'

			# Get the user table's json
			user_table_json = ''
			with open('dynamo/user_table.json', 'r') as thefile:
				user_table_json = ast.literal_eval(thefile.read())
	
			# Create the user table
			self.user_table = self.dynamodb.create_table(**user_table_json)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			print e.response['Error']['Message']
			return False

		# Wait for the user table to be created before continuing
		created = self.wait_for_table(self.user_table)

		print 'User table created'

		return created

	def create_token_table(self):
		""" Creates a token table. """
		try:
			print 'Creating token table'
			
			# Get the token table's json
			token_table_json = ''
			with open('dynamo/token_table.json', 'r') as thefile:
				token_table_json = ast.literal_eval(thefile.read())
			
			# Create the token table
			self.token_table = self.dynamodb.create_table(**token_table_json)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			print e.response['Error']['Message']
			return False

		# Wait for the token table to be created before continuing
		created = self.wait_for_table(self.token_table)

		print 'Token table created'

		return created

	def wait_for_table(self, table):
		""" Waits for a table to finish being created. """
		response = {}
		table_creating = True
		retries = 10
		# Attempt to query the table till its first response
		while table_creating and retries > 0:
			try:
				response = self.dynamodb.describe_table(TableName=table['TableDescription']['TableName'])
				table_creating = False
			except botocore.exceptions.ClientError as e:
				if e.response['Error']['Code'] == 'ResourceNotFoundException':
					retries -= 1
					time.sleep(0.5)
				else:
					print e.response['Error']['Code']
					print e.response['Error']['Message']
					return False

		# Wait while the table creates
		while response['Table']['TableStatus'] == 'CREATING':
			time.sleep(0.1)
			response = self.dynamodb.describe_table(TableName=table['TableDescription']['TableName'])

		return True

	def create_admin_db_entry(self):
		""" Creates an entry in the 'User' database that represents an admin """
		try:
			print 'Creating admin db entry'
			
			admin_json = ''
			with open('dynamo/user.json', 'r') as thefile:
				admin_json = ast.literal_eval(thefile.read())

			self.dynamodb.put_item(**admin_json)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			print e.response['Error']['Message']
			return False

		print 'Admin db entry created'

		return True

	def create_token_db_entry(self):
		""" Creates a token in the 'Token' database """
		try:
			print 'Creating token db entry'
			
			token_json = ''
			with open('dynamo/token.json', 'r') as thefile:
				token_json = ast.literal_eval(thefile.read())

			self.dynamodb.put_item(**token_json)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			print e.response['Error']['Message']
			return False

		print 'Token db entry created'

		return True

	def create_lambda_function(self):
		""" Creates a lamda function and uploads AWS CMS to to it """
		try:
			print 'Creating lambda function'
			
			lmda_role_json = ''
			with open('lambda/role_policy.json', 'r') as thefile:
				lmda_role_json = thefile.read()
			
			code = b''
			with open('lambda/mainController.zip', 'rb') as thefile:
				code = thefile.read()

			self.lmda_role = self.iam.create_role(
				RoleName='lambda_basic_execution',
				AssumeRolePolicyDocument=lmda_role_json
			)

			self.iam.attach_role_policy(
				RoleName=self.lmda_role['Role']['RoleName'],
				PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
			)
			
			time.sleep(1)	# This prevents an error from being thrown about the lambda role
			
			self.lmda_function = self.lmda.create_function(
				FunctionName='mainController',
				Runtime='python2.7',
				Role=self.lmda_role['Role']['Arn'],
				Handler='mainController.handler',
				Code={
					'ZipFile': code
				},
				Description='Central management function designed to handle any API Gateway request'
			)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			print e.response['Error']['Message']
			return False
		
		print 'Lambda function created'

		return True
		
test = AwsFunc()
