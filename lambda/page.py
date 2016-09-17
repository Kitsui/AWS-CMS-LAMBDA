"""
# page.py
# Author: Miguel Saavedra
# Date: 17/07/2016
# Edited: 07/08/2016 | Christopher Treadgold
#         17/09/2016 | Christopher Treadgold
"""

import datetime
import json
import uuid

import boto3
import botocore

class Page(object):
    """ Provides functions for handling page related requests """
    
    @staticmethod
    def get_all_pages(page_table):
        """ Fetches all entries from the page table """
        try:
            dynamodb = boto3.client('dynamodb')
            pages = dynamodb.scan(TableName=page_table,
                                 ConsistentRead=True)
        except botocore.exceptions.ClientError as e:
            action = "Getting all pages from the page table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        if not "Items" in pages:
            action = "Fetching pages from the page table"
            return {"error": "noPages", "data": {"action": action}}
        
        return pages["Items"]
    
    @staticmethod
    def get_page(page_name, page_table):
        """ Fetches a page entry from the page table """
        try:
            dynamodb = boto3.client("dynamodb")
            page = dynamodb.get_item(
                TableName=page_table, Key={"Name": {"S": page_name}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Getting page from the page table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        if not "Item" in page:
            action = "Fetching page from the page table"
            return {"error": "InvalidPageName",
                    "data": {"pageName": page_name, "action": action}}
            
        return page["Item"]

    @staticmethod
    def put_page(page_name, content, description, keywords, page_table, bucket):
        """ Puts a page in the page table """
        # Create the page entry
        page = {
            "Name": {"S": page_name},
            "SavedDate": {"S": str(datetime.datetime.now())},
            "Content": {"S": content},
            "Description": {"S": description},
            "Keywords": {"L": []}
        }
        for keyword in keywords:
            blog["Keywords"]["L"].append({"S": keyword})

        # Put the page in the page table
        try:
            dynamodb = boto3.client('dynamodb')
            dynamodb.put_item(
                TableName=page_table, Item=page, ReturnConsumedCapacity='TOTAL'
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting page in the page table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # TODO: Add paging table
        
        # Add blog as json to bucket
        try:
            s3 = boto3.client("s3")
            s3.put_object(
                Bucket=bucket, ACL="public-read", Body=json.dumps(page),
                Key=("Content/Pages/%s" % page["Name"]),
                ContentType="application/json"
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting page in the bucket"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        return {"message": "Successfully put page", "data": blog}

    @staticmethod
    def delete_page(page_name, page_table, bucket):
        """ Deletes a blog from the blog table """
        try:
            dynamodb = boto3.client("dynamodb")
            delete_response = dynamodb.delete_item(
                TableName=page_table,
                Key={"Name": {"S": page_name}},
                ConditionExpression="attribute_exists(Name)"
            )
        except botocore.exceptions.ClientError as e:
            action = "Deleting page from the page table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # TODO: Modify once pagination is implemented
        
        # Deletes the blog from the bucket
        try:
            s3 = boto3.client("s3")
            delete_response = s3.delete_object(
                Bucket=bucket,
                Key=("Content/Pages/%s" % page_name)
            )
        except botocore.exceptions.ClientError as e:
            action = "Deleting page from the page table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        return {"message": "Successfully deleted page"}