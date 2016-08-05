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
        self.index_file= "BlogIndex.html"
        self.bucket_name = $(bucket_name)
    
    
    def get_blog_data(self):
        """ Gets blog data from Blog table """
        blog_id = self.event["blog"]["blogID"]
        
        try:
            dynamodb = boto3.client("dynamodb")
            blog_data = dynamodb.query(
                TableName="Blog",
                KeyConditionExpression=Key("BlogID").eq(blog_id)
            )
            response = Response("Success", blog_data)
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
        blog_id = str(uuid.uuid4())
        author = self.event["blog"]["author"]
        title = self.event["blog"]["title"]
        content = self.event["blog"]["content"]
        meta_description = self.event["blog"]["metaDescription"]
        meta_keywords = self.event["blog"]["metaKeywords"]
        saved_date = str(datetime.datetime.now())
        
        # Validates the blog content
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
            "MetaKeywords": {"S": meta_keywords}
        }

        try:
            dynamodb = boto3.client("dynamodb")
            dynamodb.put_item(TableName="Blog", Item=blog_params,
                              ReturnConsumedCapacity="TOTAL")
            self.put_blog_object(blog_id, author, title, content, saved_date,
                         meta_description, meta_keywords)
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            
            if error_code == "NoSuchKey":
                self.update_index(blog_id, title)
                self.save_new_blog()
                self.put_blog_object(
                    blog_id, author, title, content, saved_date,
                    meta_description, meta_keywords
                )
            else:
                print error_code
                
                response = Response("Error", None)
                response.errorMessage = "Unable to save new blog: %s" % (
                    error_code)
                return response.to_JSON()

        return Response("Success", None).to_JSON()


    def edit_blog(self):
        """ Edits an existing blog in the Blog table """
        blog_id = self.event["blog"]["blogID"]
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
                KeyConditionExpression=Key("BlogID").eq(blog_id)
            )
            saved_date = blog_post["Items"][0]["SavedDate"]
            dynamodb.update_item(
                TableName="Blog",
                Key={"BlogID": blog_id, "Author": author},
                UpdateExpression=(
                    "set Title=:t Content=:c SavedDate=:s "
                    "MetaDescription=:d MetaKeywords=:k"
                ),
                ExpressionAttributeValues={
                    ":t": title, ":c": content, ":s": saved_date,
                    ":d": meta_description, ":k": meta_keywords
                }
            )
            self.put_blog_object(blog_id, author, title, content, saved_date,
                         meta_description, meta_keywords)
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            
            if error_code == "NoSuchKey":
                self.create_new_index()
                self.save_new_blog()
                self.put_blog_object(
                    blog_id, author, title, content, saved_date,
                    meta_description, meta_keywords
                )
            else:
                print error_code
                
                response = Response("Error", None)
                response.errorMessage = "Unable to save edited blog: %s" % (
                    e.response["Error"]["Code"])
                return response.to_JSON()
            
        return Response("Success", None).to_JSON()


    def delete_blog(self):
        """ Deletes a blog from the Blog table """
        blog_id = self.event["blog"]["blogID"]
        author = self.event["blog"]["author"]
        
        try:
            dynamodb = boto3.client("dynamodb")
            dynamodb.delete_item(
                TableName="Blog",
                Key={"BlogID": blog_id, "Author" : author}
            )
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            print error_code
            
            response = Response("Error", None)
            response.errorMessage = "Unable to delete blog: %s" % (
                error_code)
            return response.to_JSON()
        
        return Response("Success", None).to_JSON()


    def update_index(self, blog_id, title):
        """ Updates the index of blogs in the s3 bucket """
        try:
            dynamodb = boto3.client("dynamodb")
            s3 = boto3.client("s3")
            
            data = dynamodb.scan(TableName="Blog", ConsistentRead=True)
            blog_prefix = ("https://s3.amazonaws.com/" + self.bucket_name
                          + "/blog")
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
                    "<br><a href=\"" + blog_prefix + blog_id + "\">"
                    + blog_title + "</a>"
                )
            index_links = indexContent + ("</body></html>")
            
            put_index_item_kwargs = {
                "Bucket": self.bucket_name, "ACL": "public-read",
                "Body": indexContent, "Key": self.index_file,
                "ContentType": "text/html"
            }
            print indexContent
            
            s3.put_object(**put_index_item_kwargs)
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            print error_code
            
            response = Response("Error", None)
            response.errorMessage = "Unable to update index: %s" % (
                error_code)
            return response.to_JSON()
        
        return Response("Success", None).to_JSON()


    def put_blog_object(self, blog_id, author, title, content, saved_date,
                        meta_description, meta_keywords):
        """ Generates blog HTML and puts it in the s3 bucket """
        self.update_index(blog_id, title)
        
        blog_body = (
            "<head>"
                "<title>" + title + "</title>"
                "<meta name=description content=" + meta_description + ">"
                "<meta name=keywords content=" + meta_keywords + ">"
                "<meta http-equiv=content-type content=text/html;charset=UTF-8>"
            "</head>"
            "<p>"
                + author + "<br>"
                + title + "<br>"
                + content + "<br>"
                + saved_date
          + "</p>"
        )
        blog_key = "blog" + blog_id
        put_blog_item_kwargs = {
            "Bucket": self.bucket_name,
            "ACL": "public-read",
            "Body": blog_body,
            "Key": blog_key
        }

        put_blog_item_kwargs["ContentType"] = "text/html"
        self.s3.put_object(**put_blog_item_kwargs)


    def create_new_index(self):
        """ Creates a new blog index """
        print "no index found ... creating Index"
        
        try:
            put_index_item_kwargs = {
                "Bucket": self.bucket_name, "ACL": "public-read",
                "Body":"<h1>Index</h1> <br>", "Key": self.index_file
            }
            put_index_item_kwargs["ContentType"] = "text/html"
            self.s3.put_object(**put_index_item_kwargs)
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            print error_code
            
            response = Response("Error", None)
            response.errorMessage = "Unable to save new blog: %s" % (
                error_code)
