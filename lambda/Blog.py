"""
# Blog.py
# Created: 23/06/2016
# Author: Adam Campbell
# Edited By: Miguel Saavedra
"""

import boto3
import botocore
import datetime
import uuid
from Response import Response
from Json_handler import Json_handler
from boto3.dynamodb.conditions import Key, Attr

class Blog(object):

	def __init__(self, event, context):
		self.event = event
		self.context = context

	def get_blog_data(self):
		# Attempt to read blog data from dynamo
		try:
			dynamodb = boto3.resource('dynamodb')
			table = dynamodb.Table('Blog')
			blogData = table.query(KeyConditionExpression=Key('BlogID').eq(self.event["blog"]["blogID"]))
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			response = Response("Error", None)
			response.errorMessage = "Unable to get blog data: %s" % e.response['Error']['Code']
			return response.to_JSON()

		response = Response("Success", blogData)
		# response.setData = blogData
		return response.to_JSON()

	def get_all_blogs(self):
		# Attempt to get all data from table
		try:
			dynamodb = boto3.client('dynamodb')
			data = dynamodb.scan(
				TableName="Blog",
				ConsistentRead=True)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			response = Response("Error", None)
			response.errorMessage = "Unable to get blog data: %s" % e.response['Error']['Code']
			return response.to_JSON()
		
		response = Response("Success", data)
		# response.setData = data
		response.format()
		return response.to_JSON()

	def save_new_blog(self):		
		# Get new blog params
		blogID = str(uuid.uuid4())
		author = self.event["blog"]["author"]
		title = self.event["blog"]["title"]
		content = self.event["blog"]["content"]
		saveDate = str(datetime.datetime.now())
		blog_params = {
			"BlogID": {"S": blogID},
			"Author": {"S": author},
			"Title": {"S": title},
			"Content": {"S": content},
			"SavedDate": {"S": saveDate}
		}
		# Attempt to add to dynamo
		try:
			dynamodb = boto3.client('dynamodb')
			dynamodb.put_item(
				TableName='Blog',
				Item=blog_params,
				ReturnConsumedCapacity='TOTAL'
			)
			s3 = boto3.client('s3')
			Index_file= "Index.html"
			bucket_name = "la-newslettter"
			blog_key = 'blog' + blog_params['BlogID']['S']

			put_blog_item_kwargs = {
		        'Bucket': bucket_name,
		        'ACL': 'public-read',
		        'Body': '<p>' + author + '<br>' + title + '<br>' + content + '<br>' + saveDate + '</p>',
		        'Key': blog_key
			}
			# create Blog post in s3
			put_blog_item_kwargs['ContentType'] = 'text/html'
			s3.put_object(**put_blog_item_kwargs)
			# get blog Index body to concatinate
			indexBody = s3.get_object(Bucket=bucket_name,
				Key=Index_file)['Body'].read()
			# add new link to index
			put_index_item_kwargs = {
		        'Bucket': bucket_name,
		        'ACL': 'public-read',
		        'Body': indexBody + '<br>' + '<a href="' + 
		        	'https://s3.amazonaws.com/' + bucket_name + 
		        	'/' + blog_key + '">'+ title +'</a>',
		        'Key': Index_file
			}
			put_index_item_kwargs['ContentType'] = 'text/html'
			s3.put_object(**put_index_item_kwargs)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			response = Response("Error", None)
			response.errorMessage = "Unable to save new blog: %s" % e.response['Error']['Code']
			return response.to_JSON()
		
		
		return Response("Success", None).to_JSON()

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
	        	response = Response("Error", None)
			response.errorMessage = "Unable to save edited blog: %s" % e.response['Error']['Code']
			return response.to_JSON()

		return Response("Success", None).to_JSON()

	def delete_blog(self):
		blogID = self.event['blog']['blogID']
	    	author = self.event['blog']['author']
	        
	    	try:
	 	   	dynamodb = boto3.resource('dynamodb')
	    		table = dynamodb.Table('Blog')
			table.delete_item(Key={'BlogID': blogID, 'Author' : author})
	    	except botocore.exceptions.ClientError as e:
	        	print e.response['Error']['Code']
	        	response = Response("Error", None)
			response.errorMessage = "Unable to delete blog: %s" % e.response['Error']['Code']
			return response.to_JSON()

	    	return Response("Success", None).to_JSON()