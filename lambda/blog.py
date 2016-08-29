"""
# blog.py
# Author: Adam Campbell
# Date: 23/06/2016
# Edited: N/D        | Miguel Saavedra
#         29/07/2016 | Christopher Treadgold
#         07/08/2016 | Christopher Treadgold
"""

import datetime
import json
import uuid

import boto3
import botocore
from boto3.dynamodb.conditions import Attr, Key

from response import Response
from validator import Validator

class Blog(object):

    def __init__(self, event, context):
        self.event = event
        self.context = context
        self.index_file= "BlogIndex.html"
        with open("constants.json", "r") as constants_file:
            self.constants = json.loads(constants_file.read())
    
    """ function gets a blog record from dynamo """
    def get_blog_data(self):
        """ Gets blog data from dynamoDB """
        blog_id = self.event["blog"]["blogID"]
        try:
            dynamodb = boto3.client("dynamodb")
            blog_data = dynamodb.query(
                TableName=self.constants["BLOG_TABLE"],
                KeyConditionExpression="BlogID = :v1",
                ExpressionAttributeValues={
                    ":v1": {
                        "S": blog_id
                    }
                }
            )
            response = Response("Success", blog_data)
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            response = Response("Error", None)
            response.errorMessage = "Unable to get blog data: %s" % (
                e.response["Error"]["Code"])
            return response.to_JSON()

        response = Response("Success", blog_data)
        # response.setData = blog_data
        return response.to_JSON()


    """ function gets all blog records from dynamo """
    def get_all_blogs(self):
        # Attempt to get all data from table
        try:
            dynamodb = boto3.client("dynamodb")
            data = dynamodb.scan(TableName=self.constants["BLOG_TABLE"],
                                 ConsistentRead=True)
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            response = Response("Error", None)
            response.errorMessage = "Unable to get blog data: %s" % (
                e.response["Error"]["Code"])
            return response.to_JSON()
        
        response = Response("Success", data)
        # format for table response to admin dash
        return response.format("All Blogs")


    """ function saves a new blog record in dynamo """
    def save_new_blog(self):
        # Get new blog params
        blog_id = str(uuid.uuid4())
        author = self.event["blog"]["author"]
        title = self.event["blog"]["title"]
        content = self.event["blog"]["content"]
        meta_description = self.event["blog"]["metaDescription"]
        meta_keywords = self.event["blog"]["metaKeywords"]
        saved_date = str(datetime.datetime.now())

        if not Validator.validateBlog(content):
            response = Response("Error", None)
            response.errorMessage = "Invalid blog content"
            
            return response.to_JSON()

        blog_params = {
            "BlogID": {"S": blog_id},
            "Author": {"S": author},
            "Title": {"S": title},
            "Content": {"S": content},
            "SavedDate": {"S": saved_date},
            "MetaDescription": {"S": meta_description},
            "MetaKeywords": {"S": meta_keywords},
        }

        try:
            dynamodb = boto3.client("dynamodb")
            dynamodb.put_item(TableName=self.constants["BLOG_TABLE"],
                              Item=blog_params, ReturnConsumedCapacity="TOTAL")
            self.put_blog_object(blog_id, author, title, content, saved_date,
                         meta_description, meta_keywords)
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            
            response = Response("Error", None)
            response.errorMessage = "Unable to save new blog: %s" % e.response["Error"]["Code"]

            if e.response["Error"]["Code"] == "NoSuchKey":
                self.update_index(blog_id, title)
                self.save_new_blog()
            else:
                return response.to_JSON()

        self.put_blog_object(blog_id, author, title, content, saved_date,
                meta_description, meta_keywords)
        return Response("Success", None).to_JSON()


    """ function edits a blog record in dynamo """
    def edit_blog(self):
        blog_id = self.event["blog"]["blogID"]
        author = self.event["blog"]["author"]
        content = self.event["blog"]["content"]
        title = self.event["blog"]["title"]
        meta_description = self.event["blog"]["metaDescription"]
        meta_keywords = self.event["blog"]["metaKeywords"]

        if not Validator.validateBlog(content):
            response = Response("Error", None)
            response.errorMessage = "Invalid blog content"
            return response.to_JSON()

        try:
            dynamodb  = boto3.client("dynamodb")
            blog_post = dynamodb.query(
                TableName=self.constants["BLOG_TABLE"],
                KeyConditionExpression="BlogID = :v1",
                ExpressionAttributeValues={
                    ":v1": {
                        "S": blog_id
                    }
                }
            )
            saved_date = blog_post["Items"][0]["SavedDate"]["S"]
            
            # Update item from dynamo
            dynamodb.update_item(
                TableName=self.constants["BLOG_TABLE"],
                Key={
                    "BlogID": {"S": blog_id},
                    "Author": {"S": author}
                },
                UpdateExpression=(
                    "SET Title=:t, Content=:c, SavedDate=:s, "
                    "MetaDescription=:d, MetaKeywords=:k"
                ),
                ExpressionAttributeValues={
                    ":t": {"S": title}, ":c": {"S": content},
                    ":s": {"S": saved_date}, ":d": {"S": meta_description},
                    ":k": {"S": meta_keywords}
                }
            )
        except botocore.exceptions.ClientError as e:
            print e
            if e.response["Error"]["Code"] == "NoSuchKey":
                self.create_new_index()
                self.save_new_blog()
            else:
                response = Response("Error", None)
                response.errorMessage = "Unable to save edited blog: %s" % (
                    e.response["Error"]["Code"])
                return response.to_JSON()

        self.put_blog_object(blog_id, author, title, content, saved_date,
            meta_description, meta_keywords)

        return Response("Success", None).to_JSON()


    """ function deletes a blog record from dynamo """
    def delete_blog(self):
        blog_id = self.event["blog"]["blogID"]
        author = self.event["blog"]["author"]
        # delete item from dynamo
        try:
            dynamodb = boto3.client("dynamodb")
            dynamodb.delete_item(
                TableName=self.constants["BLOG_TABLE"],
                Key={
                    "BlogID": {"S": blog_id},
                    "Author" : {"S": author}
                }
            )
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            response = Response("Error", None)
            response.errorMessage = "Unable to delete blog: %s" % e.response["Error"]["Code"]
            return response.to_JSON()

        return Response("Success", None).to_JSON()


    """ function updates the index of blogs in the s3 bucket"""
    def update_index(self, blog_id, title):
        try:
            dynamodb = boto3.client("dynamodb")
            s3 = boto3.client("s3")
            
            data = dynamodb.scan(TableName=self.constants["BLOG_TABLE"],
                                 ConsistentRead=True)
            blog_prefix = "https://s3.amazonaws.com/%s/blog" % (
                self.constants["BUCKET"])
            index_links = (
                "<html>"
                    "<head><title>Blog Index</title></head>"
                        "<body>"
                            "<h1>Index</h1>"
            )
            for item in data["Items"]:
                blog_id = item["BlogID"]["S"]
                blog_title = item["Title"]["S"]
                index_links += (
                    "<br><a href=\"%s%s\">%s</a>" % (
                        blog_prefix, blog_id, blog_title)
                )
            index_links = "%s</body></html>" % (index_links)
            
            put_index_item_kwargs = {
                "Bucket": self.constants["BUCKET"], "ACL": "public-read",
                "Body": index_links, "Key": self.index_file,
                "ContentType": "text/html"
            }
            print index_links
            
            s3.put_object(**put_index_item_kwargs)
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            print error_code
            
            response = Response("Error", None)
            response.errorMessage = "Unable to update index: %s" % (
                error_code)
            return response.to_JSON()
        
        return Response("Success", None).to_JSON()

    """ function which puts a blog json object in s3 """
    def put_blog_object(self, blog_id, author, title, content, saved_date,
                        mDescription, mKeywords):
        blog_key = 'blog-json-' + blog_id
        
        ''' Call update index '''
        # self.update_index() 
        # page body
        page_json =('{ "title": "'+title+'","content": "'+content+'","uuid": "'+blog_id+
            '","meta-data" : { "description" : "'+mDescription+'","keywords" : "'+mKeywords+
            '"},"script-src" : "something"}')

        # Item parameters
        put_blog_item_kwargs = {
            'Bucket': self.constants["BUCKET"],
            'ACL': 'public-read',
            'Body': page_json,
            'Key': 'Content/Post/'+blog_key
        }

        put_blog_item_kwargs['ContentType'] = 'application/json'
        try:
            s3 = boto3.client("s3")
            # put into s3
            s3.put_object(**put_blog_item_kwargs)
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to save Blog to s3: %s" % (
                e.response['Error']['Code'])


    """ function which creates a new index if not found in s3 """
    def create_new_index(self):
        print "no index found ... creating Index"
        put_index_item_kwargs = {
            "Bucket": self.constants["BUCKET"], "ACL": "public-read",
            "Body":"<h1>Index</h1> <br>", "Key": self.index_file
        }
        put_index_item_kwargs["ContentType"] = "text/html"
        try:
            s3 = boto3.client("s3")
            s3.put_object(**put_index_item_kwargs)
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            response = Response("Error", None)
            response.errorMessage = "Unable to save new blog: %s" % e.response["Error"]["Code"]
