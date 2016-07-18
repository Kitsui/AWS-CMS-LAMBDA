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
from Validator import Validator
from boto3.dynamodb.conditions import Key, Attr

class Blog(object):

	def __init__(self, event, context):
		self.event = event
		self.context = context
		# Blog variables
		self.s3 = boto3.client('s3')
		self.Index_file= "BlogIndex.html"
		self.bucket_name = "la-newslettter"

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
		metaDescription = self.event["blog"]["metaDescription"]
		metaKeywords = self.event["blog"]["metaKeywords"]
		saveDate = str(datetime.datetime.now())

		if not Validator.validateBlog(content):
			response = Response("Error", None)
			response.errorMessage = "Invalid blog content"
			return response.to_JSON()

		blog_params = {
			"BlogID": {"S": blogID},
			"Author": {"S": author},
			"Title": {"S": title},
			"Content": {"S": content},
			"SavedDate": {"S": saveDate},
			"MetaDescription": {"S": metaDescription},
			"MetaKeywords": {"S": metaKeywords},
		}

		try:
			dynamodb = boto3.client('dynamodb')
			dynamodb.put_item(
				TableName='Blog',
				Item=blog_params,
				ReturnConsumedCapacity='TOTAL'
			)

		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			response = Response("Error", None)
			response.errorMessage = "Unable to save new blog: %s" % e.response['Error']['Code']

			if e.response['Error']['Code'] == "NoSuchKey":
				self.update_index(blogID, title)
				self.save_new_blog()
			else:
				return response.to_JSON()

		self.put_blog_object(blogID, author, title, content, saveDate, 
				metaDescription, metaKeywords)
		return Response("Success", None).to_JSON()

	def edit_blog(self):
		blogID = self.event['blog']['blogID']
		author = self.event['blog']['author']
		content = self.event['blog']['content']
		title = self.event['blog']['title']
		metaDescription = self.event["blog"]["metaDescription"]
		metaKeywords = self.event["blog"]["metaKeywords"]

		if not Validator.validateBlog(content):
			response = Response("Error", None)
			response.errorMessage = "Invalid blog content"
			return response.to_JSON()

	    	try:
	    		dynamodb = boto3.resource('dynamodb')
	    		table = dynamodb.Table('Blog')
	    		blogData = table.query(KeyConditionExpression=Key('BlogID').eq
	    			(self.event["blog"]["blogID"]))
	    		saveDate = blogData['Items'][0]['SavedDate']
	    		
	    		table.update_item(Key={'BlogID': blogID, 'Author': author }, 
	    			UpdateExpression="set Title = :t, Content=:c, SavedDate=:s, MetaDescription=:d, MetaKeywords=:k"
	    			, ExpressionAttributeValues={ ':t': title, ':c': content, ':s': saveDate,
	    			':d': metaDescription, ':k': metaKeywords})
	    	except botocore.exceptions.ClientError as e:
	        	print e.response['Error']['Code']
	        	if e.response['Error']['Code'] == "NoSuchKey":
	        		self.create_new_index()
	        		self.save_new_blog()
	        	else:
	        		response = Response("Error", None)
	        		response.errorMessage = "Unable to save edited blog: %s" % e.response['Error']['Code']
	        		return response.to_JSON()

		self.put_blog_object(blogID, author, title, content, 
	    			saveDate, metaDescription, metaKeywords)
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

	def update_index(self, blogID, title):
		indexContent = '<html><head><title>Blog Index</title></head><body><h1>Index</h1>'
		blogData = {'items': [None]}
		blogTitle = ''
		dynamodb = boto3.client('dynamodb')

		data = dynamodb.scan(TableName="Blog", ConsistentRead=True)
		for item in data['Items']:
			indexContent = indexContent + '<br>' + '<a href="https://s3.amazonaws.com/' + self.bucket_name + '/blog' + item['BlogID']['S'] + '">'+ item['Title']['S'] +'</a>'
		indexContent = indexContent + '<body></html>'
		print indexContent
		put_index_item_kwargs = {
			'Bucket': self.bucket_name,
			'ACL': 'public-read',
			'Body': indexContent,
			'Key': self.Index_file
		}
		print indexContent
		put_index_item_kwargs['ContentType'] = 'text/html'
		self.s3.put_object(**put_index_item_kwargs)


	def put_blog_object(self, blogID, author, title, content, saveDate,
	 mDescription, mKeywords):
		blog_key = 'blog' + blogID
		
		self.update_index(blogID, title)

		put_blog_item_kwargs = {
	        'Bucket': self.bucket_name,
	        'ACL': 'public-read',
	        'Body': '<head> <title>' + title + '</title>' + 
	        ' <meta name="description" content="' + mDescription+ '">' 
	        + '<meta name="keywords" content="' + mKeywords + '">' +
	        '<meta http-equiv="content-type" content="text/html;charset=UTF-8">' +
	        '</head><p>' + author + '<br>' + title + '<br>' + 
	        content + '<br>' + saveDate + '</p>',
	        'Key': blog_key
		}

		put_blog_item_kwargs['ContentType'] = 'text/html'
		self.s3.put_object(**put_blog_item_kwargs)


	def create_new_index(self):
		print "no index found ... creating Index"
		try:
			put_index_item_kwargs = {
	        'Bucket': self.bucket_name,
	        'ACL': 'public-read',
	        'Body':'<h1>Index</h1> <br>',
	        'Key': self.Index_file
			}
			put_index_item_kwargs['ContentType'] = 'text/html'
			self.s3.put_object(**put_index_item_kwargs)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			response = Response("Error", None)
			response.errorMessage = "Unable to save new blog: %s" % e.response['Error']['Code']