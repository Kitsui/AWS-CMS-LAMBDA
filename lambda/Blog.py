"""
# Blog.py
# Created: 23/06/2016
# Author: Adam Campbell
"""

import boto3
import botocore
import datetime
import uuid

class Blog(object):

	def __init__(self, event, context):
		self.event = event
		self.context = context

	def get_single_blog(self):
		pass

	def get_all_blogs(self):
		# Attempt to get all data from table
		try:
			dynamodb = boto3.client('dynamodb')
			data = dynamodb.scan(
				TableName="Blog",
				ConsistentRead=True)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			return False
		
		print data
		return True

	def save_new_blog(self):		
		# Get new blog params
		blog_params = {
			"BlogID": {"S": str(uuid.uuid4())},
			"Author": {"S": self.event["blog"]["author"]},
			"Title": {"S": self.event["blog"]["title"]},
			"Content": {"S": self.event["blog"]["content"]},
			"SavedDate": {"S": str(datetime.datetime.now())}
		}
		# Attempt to add to dynamo
		try:
			dynamodb = boto3.client('dynamodb')
			dynamodb.put_item(
				TableName='Blog',
				Item=blog_params,
				ReturnConsumedCapacity='TOTAL'
			)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			return False
		
		return True

	def edit_blog(self):
		dynamodb = boto3.resource('dynamodb')
		table = dynamodb.Table('Blog')

		blogID = self.event['blog']['BlogID']
		author = self.event['blog']['Author']
		content = self.event['blog']['Content']
		title = self.event['blog']['Title']

		response = table.update_item(Key={'BlogID': blogID, 'Author': author }, UpdateExpression="set Title = :t, Content=:c", ExpressionAttributeValues={ ':t': title, ':c': content})
		responseCode =  {'message': response['ResponseMetadata']['HTTPStatusCode']}
		return responseCode

	def delete_blog(self):
		blogID = self.event['blog']['BlogID']
	    	author = self.event['blog']['Author']
	        
	    	dynamodb = boto3.resource('dynamodb')
	    	table = dynamodb.Table('Blog')
	    	try:
			response = table.delete_item(Key={'BlogID': blogID, 'Author' : author})
	    	except botocore.exceptions.ClientError as e:
	        	print e.response['Error']['Code']
	        	return False
	    	responseStatusCode = {'message': response['ResponseMetadata']['HTTPStatusCode']}
	    	return responseStatusCode