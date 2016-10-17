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
            pages = dynamodb.scan(
                TableName=page_table, ConsistentRead=True,
                ProjectionExpression="#N, SavedDate, Description, Keywords",
                ExpressionAttributeNames={
                    "#N": "PageName"
                }
            )
        except botocore.exceptions.ClientError as e:
            action = "Getting all pages from the page table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        if not "Items" in pages:
            action = "Fetching pages from the page table"
            return {"error": "noPages", "data": {"action": action}}
        
        return {"message": "Successfully fetched pages", "data": pages["Items"]}
    
    @staticmethod
    def get_page(page_name, page_table):
        """ Fetches a page entry from the page table """
        try:
            dynamodb = boto3.client("dynamodb")
            page = dynamodb.get_item(
                TableName=page_table, Key={"PageName": {"S": page_name}}
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
        saved_date = datetime.datetime.utcnow()
        saved_date = saved_date.strftime("%d-%b-%Y %H:%M UTC")
        page = {
            "PageName": {"S": page_name},
            "SavedDate": {"S": saved_date},
            "Content": {"S": content},
            "Description": {"S": description},
            "Keywords": {"L": []}
        }
        page_for_s3 = {
            "PageName": page_name,
            "SavedDate": saved_date,
            "Content": content,
            "Description": description,
            "Keywords": keywords
        }
        for keyword in keywords:
            page["Keywords"]["L"].append({"S": keyword})

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
        
        # Add page as json to bucket
        try:
            s3 = boto3.client("s3")
            s3.put_object(
                Bucket=bucket, ACL="public-read", Body=json.dumps(page_for_s3),
                Key=("Content/Pages/%s.json" % page_for_s3["PageName"]),
                ContentType="application/json"
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting page in the bucket"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        return {"message": "Successfully put page", "data": page}

    @staticmethod
    def delete_page(page_name, page_table, bucket):
        """ Deletes a page from the page table """
        try:
            dynamodb = boto3.client("dynamodb")
            delete_response = dynamodb.delete_item(
                TableName=page_table,
                Key={"PageName": {"S": page_name}},
                ConditionExpression="attribute_exists(PageName)"
            )
        except botocore.exceptions.ClientError as e:
            action = "Deleting page from the page table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # TODO: Modify once pagination is implemented
        
        # Deletes the page from the bucket
        try:
            s3 = boto3.client("s3")
            delete_response = s3.delete_object(
                Bucket=bucket,
                Key=("Content/Pages/%s.json" % page_name)
            )
        except botocore.exceptions.ClientError as e:
            action = "Deleting page from the page table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        return {"message": "Successfully deleted page"}