"""
# User.py
# Created: 23/06/2016
# Author: Adam Campbell
"""

import boto3
import botocore
import uuid

class User(object):

	def __init__(self, event, context):
		self.event = event
		self.context = context

	def register(self):
		# Get user register params
		register_params = {
			"ID": {"S": str(uuid.uuid4())},
			"Username": {"S": self.event["user"]["username"]},
			"Email": {"S": self.event["user"]["email"]},
			"Password": {"S": self.event["user"]["password"]},
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
			return False
		
		return True

	def login(self):
	        dynamodb = boto3.resource('dynamodb')
		    from boto3.dynamodb.conditions import Key, Attr
		    table = dynamodb.Table('User')
		    
		    username = event["User"]["Username"]
		    password =  event["User"]["Password"]
		    
		    # response = table.scan()
		    response = table.query(KeyConditionExpression=Key('Username').eq(username))
		    
		    for i in response['Items']:
		        if(i['Password'] == password):
		            return "successfully logged in"

		return "failed to login"
		pass

	def logout(self):
		# get user credentials
		token = self.event['tokenString']
    		user = self.event['userID']

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
		# if message is 200 then successfully logged out    
	    	return {'message': response['ResponseMetadata']['HTTPStatusCode']} 