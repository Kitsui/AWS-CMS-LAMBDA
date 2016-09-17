"""
# blog.py
# Author: Adam Campbell
# Date: 23/06/2016
# Edited: N/D        | Miguel Saavedra
#         29/07/2016 | Christopher Treadgold
#         07/08/2016 | Christopher Treadgold
#         12/09/2016 | Christopher Treadgold
"""

import datetime
import json
import uuid

import boto3
import botocore

class Blog(object):
    """ Provides functions for handling blog related requests """
    
    @staticmethod
    def get_all_blogs(blog_table):
        """ Fetches all entries from the blog table """
        try:
            dynamodb = boto3.client("dynamodb")
            blogs = dynamodb.scan(TableName=blog_table, ConsistentRead=True)
        except botocore.exceptions.ClientError as e:
            action = "Fetching blogs from the blog table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the blog id has a blog associated with it
        if not "Items" in blogs:
            action = "Fetching blogs from the blog table"
            return {"error": "noBlogs", "data": {"action": action}}
        
        return {"message": "Successfully fetched blogs", "data": blogs["Items"]}
    
    @staticmethod
    def get_blog(blog_id, blog_table):
        """ Fetches a blog entry from the blog table """
        try:
            dynamodb = boto3.client("dynamodb")
            blog = dynamodb.get_item(
                TableName=blog_table, Key={"ID": {"S": blog_id}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Fetching blog from the blog table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the blog id has a blog associated with it
        if not "Item" in blog:
            action = "Fetching blog from the blog table"
            return {"error": "InvalidBlogID",
                    "data": {"id": blog_id, "action": action}}

        return {"message": "Successfully fetched blog", "data": blog["Item"]}

    @staticmethod
    def put_blog(author, title, content, description, keywords, blog_table,
                 bucket):
        """ Puts a blog in the blog table """
        # Create the blog entry
        blog = {
            "ID": {"S": str(uuid.uuid4())},
            "SavedDate": {"S": str(datetime.datetime.now())},
            "Author": {"S": author},
            "Title": {"S": title},
            "Content": {"S": content},
            "Description": {"S": description},
            "Keywords": {"L": []}
        }
        for keyword in keywords:
            blog["Keywords"]["L"].append({"S": keyword})
        
        # Put the blog in the blog table
        try:
            dynamodb = boto3.client("dynamodb")
            put_response = dynamodb.put_item(
                TableName=blog_table, Item=blog, ReturnConsumedCapacity="TOTAL"
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting blog in the blog table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # TODO: Add paging table
        
        # Add blog as json to bucket
        try:
            s3 = boto3.client("s3")
            s3.put_object(
                Bucket=bucket, ACL="public-read", Body=json.dumps(blog),
                Key=("Content/Blogs/%s" % blog["ID"]),
                ContentType="application/json"
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting blog in the bucket"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        return {"message": "Successfully put blog", "data": blog}
        
    @staticmethod
    def delete_blog(blog_id, blog_table, bucket):
        """ Deletes a blog from the blog table """
        try:
            dynamodb = boto3.client("dynamodb")
            delete_response = dynamodb.delete_item(
                TableName=blog_table,
                Key={"ID": {"S": blog_id}},
                ConditionExpression="attribute_exists(ID)"
            )
        except botocore.exceptions.ClientError as e:
            action = "Deleting blog from the blog table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # TODO: Modify once pagination is implemented
        
        # Deletes the blog from the bucket
        try:
            s3 = boto3.client("s3")
            delete_response = s3.delete_object(
                Bucket=bucket,
                Key=("Content/Blogs/%s" % blog_id)
            )
        except botocore.exceptions.ClientError as e:
            action = "Deleting blog from the blog table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        return {"message": "Successfully deleted blog"}