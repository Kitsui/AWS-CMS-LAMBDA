"""
# Blog.py
# Created: 23/06/2016
# Author: Adam Campbell
"""

import boto3
import botocore
import datetime
import uuid
from Response import Response

class Blog(object):

	def __init__(self, event, context):
		self.event = event
		self.context = context

	def get_blog_data(self):
		# Attempt to read blog data from dynamo
		try:
			dynamodb = boto3.client('dynamodb')
			blogData = dynamodb.get_item(
				TableName="Blog",
				Key={
					"BlogID": {"S": self.event["blog"]["blogID"]},
					"Author": {"S": self.event["blog"]["author"]}},
				ConsistentRead=True)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			response = Response("Error")
			response.errorMessage = "Unable to get blog data: %s" % e.response['Error']['Code']
			return response

		response = Response("Success")
		response.setData = blogData
		return response

	def get_all_blogs(self):
		# Attempt to get all data from table
		try:
			dynamodb = boto3.client('dynamodb')
			data = dynamodb.scan(
				TableName="Blog",
				ConsistentRead=True)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			response = Response("Error")
			response.errorMessage = "Unable to get blog data: %s" % e.response['Error']['Code']
			return response
		
		response = Response("Success")
		response.setData = data
		return response

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
			response = Response("Error")
			response.errorMessage = "Unable to save new blog: %s" % e.response['Error']['Code']
			return response
		
		return Response("Success")

	def edit_blog(self):
		blogID = self.event['blog']['blogID']
		author = self.event['blog']['author']
		content = self.event['blog']['content']
		title = self.event['blog']['title']

	    	try:
			dynamodb = boto3.resource('dynamodb')
			table = dynamodb.Table('Blog')
			table.update_item(Key={'BlogID': blogID, 'Author': author }, UpdateExpression="set Title = :t, Content=:c", ExpressionAttributeValues={ ':t': title, ':c': content})
	    	except botocore.exceptions.ClientError as e:
	        	print e.response['Error']['Code']
	        	response = Response("Error")
			response.errorMessage = "Unable to save edited blog: %s" % e.response['Error']['Code']
			return response

		return Response("Success")

	def delete_blog(self):
		blogID = self.event['blog']['blogID']
	    	author = self.event['blog']['author']
	        
	    	try:
	 	   	dynamodb = boto3.resource('dynamodb')
	    		table = dynamodb.Table('Blog')
			table.delete_item(Key={'BlogID': blogID, 'Author' : author})
	    	except botocore.exceptions.ClientError as e:
	        	print e.response['Error']['Code']
	        	response = Response("Error")
			response.errorMessage = "Unable to delete blog: %s" % e.response['Error']['Code']
			return response

	    	return Response("Success")