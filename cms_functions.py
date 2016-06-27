#!/usr/bin/python2.7

import boto3
import botocore
import os
import mimetypes
import time
import ast
from replace_variables import replace_variables

class AwsFunc:
	""" Contains functions for creating, modifying and deleting elements of the AWSCMS.
	
	Requires awscli configured or an aws configuration file. 
	"""
	def __init__(self, bucket_name, account_id, region):
		""" Gets low-level clients for services to be used and creates containers for
		AWS objects that will be filled by creation functions.
		"""
		self.account_id = account_id
		self.region = region
		
		self.s3 = boto3.client('s3')
		self.bucket_name = bucket_name
		self.bucket = None

		self.dynamodb = boto3.client('dynamodb')
		self.user_table = None
		self.token_table = None

		self.lmda = boto3.client('lambda')
		self.lmda_function = None

		self.iam = boto3.client('iam')
		self.lmda_role = None
		
		self.apigateway = boto3.client('apigateway')
		self.rest_api = None
		self.api_key = None

	def create_bucket(self, bucket_region=None):
		""" Creates a bucket with the name 'bucket_name' in region 'bucket_region'. 
		
		If 'bucket_region' is not given, bucket will default to US Standard region.
		Files for the AWS CMS are uploaded to the bucket.
		"""
		try:
			print 'Creating bucket'

			# Set the variables needed to create the bucket
			bucket_kwargs = {
				'ACL': 'public-read',
				'Bucket': self.bucket_name
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
					with open(directory, 'rb') as file_body:
						body = file_body.read()
						body = replace_variables(body, endpoint_url=self.create_api_call_uri(), api_key=self.api_key)
						put_kwargs = {
							'Bucket': self.bucket['Location'][1:],
							'ACL': 'public-read',
							'Body': body,
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

	def create_role_table(self):
		""" Creates a role table. """
		try:
			print 'Creating role table'

			# Get the role table's json
			role_table_json = ''
			with open('dynamo/role_table.json', 'r') as thefile:
				role_table_json = ast.literal_eval(thefile.read())
	
			# Create the role table
			self.role_table = self.dynamodb.create_table(**role_table_json)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			print e.response['Error']['Message']
			return False

		# Wait for the role table to be created before continuing
		created = self.wait_for_table(self.role_table)

		print 'Role table created'
		return created

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

	def create_blog_table(self):
		""" Creates a blog table. """
		try:
			print 'Creating blog table'
			
			# Get the blog table's json
			blog_table_json = ''
			with open('dynamo/blog_table.json', 'r') as thefile:
				blog_table_json = ast.literal_eval(thefile.read())
			
			# Create the blog table
			self.blog_table = self.dynamodb.create_table(**blog_table_json)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			print e.response['Error']['Message']
			return False

		# Wait for the blog table to be created before continuing
		created = self.wait_for_table(self.blog_table)

		print 'Blog table created'

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

	def create_admin_role_db_entry(self):
		""" Creates an entry in the 'Role' database that represents an admin role"""
		try:
			print 'Creating admin role db entry'
			
			admin_role_json = ''
			with open('dynamo/role.json', 'r') as thefile:
				admin_role_json = ast.literal_eval(thefile.read())

			self.dynamodb.put_item(**admin_role_json)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			print e.response['Error']['Message']
			return False

		print 'Admin role db entry created'
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
			with open('lambda/controller.zip', 'rb') as thefile:
				code = thefile.read()
			
			# Create a role that can be attached to lambda functions
			self.lmda_role = self.iam.create_role(
				RoleName='lambda_basic_execution',
				AssumeRolePolicyDocument=lmda_role_json
			)
			
			# Attach permissions to the lambda role
			self.iam.attach_role_policy(
				RoleName=self.lmda_role['Role']['RoleName'],
				PolicyArn='arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess'
			)
			self.iam.attach_role_policy(
				RoleName=self.lmda_role['Role']['RoleName'],
				PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
			)
			
			time.sleep(10)
			
			# Create the lambda function
			self.lmda_function = self.lmda.create_function(
				FunctionName='controller',
				Runtime='python2.7',
				Role=self.lmda_role['Role']['Arn'],
				Handler='controller.handler',
				Code={
					'ZipFile': code
				},
				Description='Central management function designed to handle any API Gateway request',
				Timeout=10
			)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			print e.response['Error']['Message']
			return False
		
		print 'Lambda function created'

		return True
		
	def create_api_gateway(self):
		""" Creates the api gateway and links it to the lambda function """
		try:
			print 'Creating the api gateway'
			
			# Create a rest api
			self.rest_api = self.apigateway.create_rest_api(
				name='AWS_CMS_Operations'
			)
			
			# Get the rest api's root id
			root_resource = self.apigateway.get_resources(
				restApiId=self.rest_api['id']
			)['items'][0]
			
			# Add a post method to the rest api
			api_method = self.apigateway.put_method(
				restApiId=self.rest_api['id'],
				resourceId=root_resource['id'],
				httpMethod='POST',
				authorizationType='NONE'
			)
			
			# Set the put integration of the POST method
			self.apigateway.put_integration(
				restApiId=self.rest_api['id'],
				resourceId=root_resource['id'],
				httpMethod='POST',
				type='AWS',
				integrationHttpMethod='POST',
				uri=self.create_api_invocation_uri(),
				requestTemplates={
					'application/json': ''
				}
			)
			
			# Set the put method response of the POST method
			self.apigateway.put_method_response(
				restApiId=self.rest_api['id'],
				resourceId=root_resource['id'],
				httpMethod='POST',
				statusCode='200',
#				responseParameters={
#					'method.response.header.Access-Control-Allow-Origin': False
#				},
				responseModels={
					'application/json': 'Empty'
				}
			)
			
			# Set the put integration response of the POST method
			self.apigateway.put_integration_response(
				restApiId=self.rest_api['id'],
				resourceId=root_resource['id'],
				httpMethod='POST',
				statusCode='200',
#				responseParameters={
#					'method.response.header.Access-Control-Allow-Origin': '\'*\''
#				},
				responseTemplates={
					'application/json': ''
				}
			)
			
			"""
			# Add an options method to the rest api
			api_method = self.apigateway.put_method(
				restApiId=self.rest_api['id'],
				resourceId=root_resource['id'],
				httpMethod='OPTIONS',
				authorizationType='NONE'
			)
			
			# Set the put integration of the OPTIONS method
			self.apigateway.put_integration(
				restApiId=self.rest_api['id'],
				resourceId=root_resource['id'],
				httpMethod='OPTIONS',
				type='MOCK',
				requestTemplates={
					'application/json': ''
				}
			)
			
			# Set the put method response of the OPTIONS method
			self.apigateway.put_method_response(
				restApiId=self.rest_api['id'],
				resourceId=root_resource['id'],
				httpMethod='OPTIONS',
				statusCode='200',
				responseParameters={
					'method.response.header.Access-Control-Allow-Headers': False,
					'method.response.header.Access-Control-Allow-Origin': False,
					'method.response.header.Access-Control-Allow-Methods': False
				},
				responseModels={
					'application/json': 'Empty'
				}
			)

			# Set the put integration response of the OPTIONS method
			self.apigateway.put_integration_response(
				restApiId=self.rest_api['id'],
				resourceId=root_resource['id'],
				httpMethod='OPTIONS',
				statusCode='200',
				responseParameters={
					'method.response.header.Access-Control-Allow-Headers': '\'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token\'',
					'method.response.header.Access-Control-Allow-Methods': '\'POST,OPTIONS\'',
					'method.response.header.Access-Control-Allow-Origin': '\'*\''
					
				},
				responseTemplates={
					'application/json': ''
				}
			)
			"""
			
			# Create a deployment of the rest api
			self.apigateway.create_deployment(
				restApiId=self.rest_api['id'],
				stageName='prod'
			)
			
			# Create an api key linked to the rest api
			self.api_key = self.apigateway.create_api_key(
				name='AWS_CMS_Api_Key',
				description='Allows sending of requests to the AWS CMS',
				enabled=True,
				stageKeys=[
					{
						'restApiId': self.rest_api['id'],
						'stageName': 'prod'
					},
				]
			)['id']
			
			# Give the api deployment permission to trigger the lambda function
			self.lmda.add_permission(
				FunctionName=self.lmda_function['FunctionName'],
				StatementId='c67ytfvu65ytd5tsrdghk',
				Action='lambda:InvokeFunction',
				Principal='apigateway.amazonaws.com',
				SourceArn=self.create_api_permission_uri()
			)
			
			print 'Api gateway created'
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			print e.response['Error']['Message']
			return False
			
		return True

	def create_api_invocation_uri(self):
		""" Creates the uri that is needed for an integration method """
		uri = 'arn:aws:apigateway:'
		uri += self.region
		uri += ':lambda:path/2015-03-31/functions/'
		uri += self.lmda_function['FunctionArn']
		uri += '/invocations'
		return uri
		
	def create_api_permission_uri(self):
		""" Creates the uri that is needed for giving the api deployment permission to trigger the lambda function """
		uri = 'arn:aws:execute-api:'
		uri += self.region
		uri += ':'
		uri += self.account_id
		uri += ':'
		uri += self.rest_api['id']
		uri += '/*/POST/'
		return uri
		
	def create_api_call_uri(self):
		uri = 'https://'
		uri += self.apigateway.get_rest_api(
			restApiId=self.rest_api['id']
		)['id']
		uri += '.execute-api.us-east-1.amazonaws.com/prod'
		return uri
