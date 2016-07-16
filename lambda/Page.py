"""
# Page.py
# Created: 17/07/2016
# Author: Miguel Saavedra
"""

import boto3
import botocore
import uuid
import datetime
from Response import Response
from boto3.dynamodb.conditions import Key, Attr

class Page(object):

	def __init__(self, event, context):
		self.event = event
		self.context = context
		# Blog variables
		self.s3 = boto3.client('s3')
		self.Index_file= "PageIndex.html"
		self.bucket_name = "la-newslettter"

	def create_page(self):		
		# Get new blog params
		pageID = str(uuid.uuid4())
		author = self.event["page"]["pageAuthor"]
		title = self.event["page"]["pageTitle"]
		content = self.event["page"]["pageContent"]
		metaDescription = self.event["page"]["metaDescription"]
		metaKeywords = self.event["page"]["metaKeywords"]
		saveDate = str(datetime.datetime.now())

		page_params = {
			"PageID": {"S": pageID},
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
				TableName='Pages',
				Item=page_params,
				ReturnConsumedCapacity='TOTAL'
			)

		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			response = Response("Error", None)
			response.errorMessage = "Unable to save new page: %s" % e.response['Error']['Code']

			if e.response['Error']['Code'] == "NoSuchKey":
				self.update_index(blogID, title)
				self.save_new_blog()
			else:
				return response.to_JSON()

		self.put_page_object(pageID, author, title, content, saveDate, 
				metaDescription, metaKeywords)
		return Response("Success", None).to_JSON()

	def delete_page(self):
		pageID =self.event['page']['pageID']
	    	author = self.event['page']['pageAuthor']
	        
	    	try:
	 	   	dynamodb = boto3.resource('dynamodb')
	    		table = dynamodb.Table('Pages')
			table.delete_item(Key={'PageID': pageID, 'Author': author})
	    	except botocore.exceptions.ClientError as e:
	        	print e.response['Error']['Code']
	        	response = Response("Error", None)
			response.errorMessage = "Unable to delete page: %s" % e.response['Error']['Code']
			return response.to_JSON()

			self.update_index()
	    	return Response("Success", None).to_JSON()

	def update_index(self):
		indexContent = '<html><head><title>Page Index</title></head><body><h1>Index</h1>'
		blogData = {'items': [None]}
		blogTitle = ''
		dynamodb = boto3.client('dynamodb')

		data = dynamodb.scan(TableName="Pages", ConsistentRead=True)
		for item in data['Items']:
			indexContent = indexContent + '<br>' + '<a href="https://s3.amazonaws.com/' + self.bucket_name + '/page' + item['PageID']['S'] + '">'+ item['Title']['S'] +'</a>'
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

	def put_page_object(self, pageID, author, title, content, saveDate,
	 mDescription, mKeywords):
		page_key = 'page' + pageID
		
		self.update_index()

		put_blog_item_kwargs = {
	        'Bucket': self.bucket_name,
	        'ACL': 'public-read',
	        'Body': '<head> <title>' + title + '</title>' + 
	        ' <meta name="description" content="' + mDescription+ '">' 
	        + '<meta name="keywords" content="' + mKeywords + '">' +
	        '<meta http-equiv="content-type" content="text/html;charset=UTF-8">' +
	        '</head><p>' + author + '<br>' + title + '<br>' + 
	        content + '<br>' + saveDate + '</p>',
	        'Key': page_key
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

