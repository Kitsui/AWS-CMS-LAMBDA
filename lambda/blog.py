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
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            response = Response("Error", None)
            response.errorMessage = "Unable to get blog data: %s" % (
                e.response["Error"]["Code"])
            return response.to_JSON()

        return blog_data


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
        # return response.format("All Blogs")
        return data


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
        # add id to event json
        self.event["blog"]["blogID"] = blog_id
        # add save date to event json
        self.event["blog"]["savedDate"] = saved_date
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
        # put blog into dynamo and s3
        try:
            dynamodb = boto3.client("dynamodb")
            dynamodb.put_item(TableName=self.constants["BLOG_TABLE"],
                              Item=blog_params, ReturnConsumedCapacity="TOTAL")
            self.put_blog_object(self.event["blog"])
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]

            response = Response("Error", None)
            response.errorMessage = "Unable to save new blog: %s" % e.response["Error"]["Code"]

            if e.response["Error"]["Code"] == "NoSuchKey":
                self.save_new_blog()
            else:
                return response.to_JSON()

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


    """ function which puts a blog json object in s3 """
    def put_blog_object(self, blog_json):
        blog_key = blog_json["blogID"] + ".json"

        ''' Call update index '''
        self.update_index(blog_json["blogID"])
        # blog body
        page_json = json.dumps(blog_json)

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
            # put into s3 with blog parameters
            s3.put_object(**put_blog_item_kwargs)
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to save Blog to s3: %s" % (
                e.response['Error']['Code'])


    """ function which updates a blog index in s3 """
    def update_index(self, uid):
        print "Index Updating..."

        # variables to be used
        s3 = boto3.client("s3")
        index_key = "Content/post_list.json"

        # create json item
        index_json_new_item = uid

        # Get old index and read in the file body
        fileName= index_key
        get_kwargs = {
            'Bucket': self.constants["BUCKET"],
            'Key': fileName
        }
        result =  s3.get_object(**get_kwargs)
        old_index_body = result['Body'].read()
        print old_index_body

        old_index_body_json = json.loads(old_index_body)
        new_json_body_string = ""

        # Add new item to index items
        old_index_body_json["items"].append(index_json_new_item)
        new_json_body_string = json.dumps(old_index_body_json)

        # update index
        put_index_item_kwargs = {
            "Bucket": self.constants["BUCKET"],
            "ACL": "public-read",
            "Body" : new_json_body_string,
            "Key": index_key
        }
        put_index_item_kwargs["ContentType"] = 'application/json'
        try:
            s3.put_object(**put_index_item_kwargs)
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            response = Response("Error", None)
            response.errorMessage = ("Unable to save new blog to index: %s" %
                e.response["Error"]["Code"])
