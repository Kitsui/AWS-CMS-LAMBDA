"""
# blog.py
# Author: Adam Campbell
# Date: 23/06/2016
# Edited: N/D        | Miguel Saavedra
#         29/07/2016 | Christopher Treadgold
"""

import datetime
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
        self.Index_file= "BlogIndex.html"
        self.bucket_name = $(bucket_name)


    def get_blog_data(self):
        """ Gets blog data from Blog table """
        blog_id = self.event["blog"]["blogID"]
        
        try:
            dynamodb = boto3.client("dynamodb")
            blogData = table.query(
                TableName="Blog",
                KeyConditionExpression=Key("BlogID").eq(blog_id)
            )
            response = Response("Success", blogData)
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            print error_code
            
            response = Response("Error", None)
            response.errorMessage = "Unable to get blog data: %s" % (
                error_code)
                
        return response.to_JSON()


    def get_all_blogs(self):
        """ Gets blog data for all blogs from Blog table """
        try:
            dynamodb = boto3.client("dynamodb")
            data = dynamodb.scan(TableName="Blog", ConsistentRead=True)
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            print error_code
            
            response = Response("Error", None)
            response.errorMessage = "Unable to get blog data: %s" % (
                error_code)
            return response.to_JSON()
        
        response = Response("Success", data)
        return response.format("All Blogs")


    def save_new_blog(self):
        """ Creates a new blog and enters it into the Blog table """
        blogID = str(uuid.uuid4())
        author = self.event["blog"]["author"]
        title = self.event["blog"]["title"]
        content = self.event["blog"]["content"]
        metaDescription = self.event["blog"]["metaDescription"]
        metaKeywords = self.event["blog"]["metaKeywords"]
        saveDate = str(datetime.datetime.now())
        
        # Validates the blog content
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
            "MetaKeywords": {"S": metaKeywords}
        }

        try:
            dynamodb = boto3.client("dynamodb")
            dynamodb.put_item(TableName="Blog", Item=blog_params,
                              ReturnConsumedCapacity="TOTAL")
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            
            if error_code == "NoSuchKey":
                self.update_index(blogID, title)
                self.save_new_blog()
            else:
                print error_code
                
                response = Response("Error", None)
                response.errorMessage = "Unable to save new blog: %s" % (
                    error_code)
                return response.to_JSON()

        self.put_blog_object(blogID, author, title, content, saveDate,
                             metaDescription, metaKeywords)
        
        return Response("Success", None).to_JSON()


    def edit_blog(self):
        """ Edits an existing blog in the Blog table """
        blogID = self.event["blog"]["blogID"]
        author = self.event["blog"]["author"]
        content = self.event["blog"]["content"]
        title = self.event["blog"]["title"]
        meta_description = self.event["blog"]["metaDescription"]
        meta_keywords = self.event["blog"]["metaKeywords"]
        
        # Validates the blog content
        if not Validator.validateBlog(content):
            response = Response("Error", None)
            response.errorMessage = "Invalid blog content"
            return response.to_JSON()

        try:
            dynamodb  = boto3.client("dynamodb")
            blog_post = dynamodb.query(
                TableName="Blog",
                KeyConditionExpression=Key("BlogID").eq(blogID)
            )
            saved_date = blog_post["Items"][0]["SavedDate"]
            
            dynamodb.update_item(
                TableName="Blog",
                Key={"BlogID": blogID, "Author": author},
                UpdateExpression=(
                    "set Title=:t Content=:c SavedDate=:s "
                    "MetaDescription=:d MetaKeywords=:k"
                ),
                ExpressionAttributeValues={
                    ":t": title, ":c": content, ":s": saved_date,
                    ":d": meta_description, ":k": meta_keywords
                }
            )
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            
            if error_code == "NoSuchKey":
                self.create_new_index()
                self.save_new_blog()
            else:
                print error_code
                
                response = Response("Error", None)
                response.errorMessage = "Unable to save edited blog: %s" % (
                    e.response["Error"]["Code"])
                return response.to_JSON()

    self.put_blog_object(blogID, author, title, content, saved_date,
                         meta_description, meta_keywords)
                         
    return Response("Success", None).to_JSON()


    def delete_blog(self):
        """ Deletes a blog from the Blog table """
        blogID = self.event["blog"]["blogID"]
        author = self.event["blog"]["author"]
        
        try:
            dynamodb = boto3.client("dynamodb")
            table.delete_item(
                TableName="Blog",
                Key={"BlogID": blogID, "Author" : author}
            )
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            print error_code
            
            response = Response("Error", None)
            response.errorMessage = "Unable to delete blog: %s" % (
                error_code)
            return response.to_JSON()

        return Response("Success", None).to_JSON()


    def update_index(self, blogID, title):
        try:
            dynamodb = boto3.client("dynamodb")
            s3 = boto3.client("s3")
            
            indexContent = (
                "<html>"
                    "<head><title>Blog Index</title></head>"
                        "<body>"
                            "<h1>Index</h1>"
            )
            blog_prefix = "https://s3.amazonaws.com/" + self.bucket_name + "/blog/"
            data = dynamodb.scan(TableName="Blog", ConsistentRead=True)
            for item in data["Items"]:
                index_links += (
                    "<br><a href=\"" + blog_prefix + item["BlogID"]["S"] + "\">"
                    + item["Title"]["S"] + "</a>"
                )
            indexContent = indexContent + (
                    "<body>"
                "</html>"
            )
            print indexContent
            put_index_item_kwargs = {
                "Bucket": self.bucket_name, "ACL": "public-read",
                "Body": indexContent, "Key": self.Index_file
            }
            print indexContent
            put_index_item_kwargs["ContentType"] = "text/html"
            s3.put_object(**put_index_item_kwargs)


    def put_blog_object(self, blogID, author, title, content, saveDate,
     mDescription, mKeywords):
        blog_key = "blog" + blogID
        
        self.update_index(blogID, title)

        put_blog_item_kwargs = {
            "Bucket": self.bucket_name,
            "ACL": "public-read",
            "Body": "<head> <title>" + title + "</title>" +
            " <meta name="description" content="" + mDescription+ "">"
            + "<meta name="keywords" content="" + mKeywords + "">" +
            "<meta http-equiv="content-type" content="text/html;charset=UTF-8">" +
            "</head><p>" + author + "<br>" + title + "<br>" +
            content + "<br>" + saveDate + "</p>",
            "Key": blog_key
        }

        put_blog_item_kwargs["ContentType"] = "text/html"
        self.s3.put_object(**put_blog_item_kwargs)


    def create_new_index(self):
        print "no index found ... creating Index"
        try:
            put_index_item_kwargs = {
            "Bucket": self.bucket_name,
            "ACL": "public-read",
            "Body":"<h1>Index</h1> <br>",
            "Key": self.Index_file
            }
            put_index_item_kwargs["ContentType"] = "text/html"
            self.s3.put_object(**put_index_item_kwargs)
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            response = Response("Error", None)
            response.errorMessage = "Unable to save new blog: %s" % e.response["Error"]["Code"]
