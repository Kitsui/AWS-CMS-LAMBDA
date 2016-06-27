"""
# User.py
# Created: 23/06/2016
# Author: Adam Campbell
"""

import boto3
import botocore
import uuid
from Response import Response
from passlib.apps import custom_app_context as pwd_context

class User(object):

	def __init__(self, event, context):
		self.event = event
		self.context = context

	def register(self):
		# Get password for hashing
		password = self.event["user"]["password"]
		hashed = pwd_context.encrypt(password)
		# Get user register params
		register_params = {
			"ID": {"S": str(uuid.uuid4())},
			"Username": {"S": self.event["user"]["username"]},
			"Email": {"S": self.event["user"]["email"]},
			"Password": {"S": hashed},
			"Roles": {"S": str(1)}
		}
		# Attempt to add to dynamo
		try:
			dynamodb = boto3.client('dynamodb')
			dynamodb.put_item(
				TableName='User',
				Item=register_params,
				ReturnConsumedCapacity='TOTAL'
			)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			response = Response("Error")
			response.errorMessage = "Unable to register new user: %s" % e.response['Error']['Code']
			return response.to_JSON()
		
		return Response("Success").to_JSON()

	def login(self):
		username = self.event["User"]["Username"]
		password =  self.event["User"]["Password"]
		# hash password for comparison
		hashed = pwd_context.encrypt(password)

		# Attempt to check dynamo
		try:			
			dynamodb = boto3.resource('dynamodb')
			from boto3.dynamodb.conditions import Key, Attr
	    		table = dynamodb.Table('User')    
			# response = table.scan()
			result = table.query(KeyConditionExpression=Key('Username').eq(username))

			for i in result['Items']:
				if(i['Password'] == hashed):
			    		return Response("Success")
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			response = Response("Error")
			response.errorMessage = "Unable to log in: %s" % e.response['Error']['Code']
			return response

		response = Response("Error")
		response.errorMessage = "Unable to login, username or password incorrect"
		return response

	def logout(self):
		# get user credentials
		token = self.event['tokenString']
    		user = self.event['userID']

		try:			
			# fetch dynamo table
			dynamodb = boto3.resource('dynamodb')
		    	table = dynamodb.Table('Token')

		    	# remove token from user
		    	response = table.delete_item(
		            Key={
		    	        'TokenString': token,
		                'UserID': user
	            		}
	        	)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			response = Response("Error")
			response.errorMessage = "Unable to log out: %s" % e.response['Error']['Code']
			return response
   
    		return Response("Success") 