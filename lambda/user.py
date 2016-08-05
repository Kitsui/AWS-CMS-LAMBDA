"""
# user.py
# Author: Adam Campbell
# Date: 23/06/2016
# Edited: N/D        | Miguel Saavedra
#         02/08/2016 | Christopher Treadgold
#		  05/08/2016 | Adam Campbell
"""

import Cookie
import datetime
import uuid

import boto3
import botocore
from boto3.dynamodb.conditions import Attr, Key
from passlib.apps import custom_app_context as pwd_context

from response import Response

class User(object):

	def __init__(self, event, context):
		self.event = event
		self.context = context

	def get_all_users(self):
		# Attempt to get all data from table
		try:
			dynamodb = boto3.client('dynamodb')
			data = dynamodb.scan(
				TableName="User",
				ConsistentRead=True)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			response = Response("Error", None)
			response.errorMessage = "Unable to get user data: %s" % e.response['Error']['Code']
			return response.to_JSON()
		
		response = Response("Success", data)
		# response.setData = data
		return response.format()

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
			"Role": {"S": "c104ea59-7deb-4ae4-8418-225d8f4f42cd"}
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
		
		return Response("Success", None).to_JSON()

	def delete_user(self):
		userID = self.event["user"]["userID"]
		email = self.event["user"]["email"]
		try:
			dynamodb = boto3.resource('dynamodb')
			table = dynamodb.Table('User')
			table.delete_item(
				Key={
					'ID': userID,
					'Email': email
					}
				)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			response = Response("Error", None)
			response.errorMessage = "Unable to delete user: %s" % e.response['Error']['Code']
			return response.to_JSON()
   
		return Response("Success", None).to_JSON()

	def edit_user(self):
		email = self.event["user"]["email"]
		userID = self.event["user"]["userID"]
		newUsername = self.event["user"]["newUsername"]
		newRole = self.event["user"]["newRole"]
		newPassword = self.event["user"]["newPassword"]
		try:
			dynamodb = boto3.resource('dynamodb')
			table = dynamodb.Table('User')
			table.update_item(
				Key={
				'ID': userID, 
				'Email': email
				}, 
				UpdateExpression='SET Username = :u, newRole = :r, Password = :p', 
				ExpressionAttributeValues={':u': newUsername,':r': newRole, ':p': newPassword }
			)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			response = Response("Error", None)
			response.errorMessage = "Unable to edit user: %s" % e.response['Error']['Code']
			return response.to_JSON()
   
		return Response("Success", None).to_JSON()

	def login(self):
		# Attempt to check dynamo
		try:
			dynamodb = boto3.resource('dynamodb')
			table = dynamodb.Table('User')
			password =  self.event["User"]["Password"]
			result = table.query(IndexName='Email', KeyConditionExpression=Key('Email').eq(self.event["User"]["Email"]))

			for i in result['Items']:
				if(pwd_context.verify(password, i['Password'])):
					expiration = datetime.datetime.now() + datetime.timedelta(days=14)
					token = str(uuid.uuid4())
					table2 = dynamodb.Table('Token')
					result = table2.put_item(
						Item={
				            'TokenString': token,
				            'UserID': i['ID'],
				            'Expiration': \
				            	expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")
				        }
				    )
					cookie = Cookie.SimpleCookie()
					cookie["token"] = token
					cookie["token"]["path"] = "/"
					cookie["token"]["expires"] = \
					  expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")

					return {"Cookie": cookie.output(header="").lstrip(), "Response": Response("Success", None).to_JSON()}
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			response = Response("Error", None)
			response.errorMessage = "Unable to log in: %s" % e.response['Error']['Code']
			return response.to_JSON()

		response = Response("Error", None)
		return response.to_JSON()

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
			response = Response("Error", None)
			response.errorMessage = "Unable to log out: %s" % e.response['Error']['Code']
			return response.to_JSON()
   
    		return Response("Success", None).to_JSON()

	def assign_role(self):
		pass