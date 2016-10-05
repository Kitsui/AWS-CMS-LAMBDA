"""
# sitesettings.py
# Author: Adam Campbell
# Date: 17/07/2016
"""

import datetime
import json
import uuid

import boto3
import botocore

class SiteSettings(object):
    """ Provides functions for handling SiteSettings related requests """
    
    @staticmethod
    def get_all_settings(page_table):
        """ Fetches all entries from the page table """
        try:
            dynamodb = boto3.client('dynamodb')
            pages = dynamodb.scan(
                TableName=page_table, ConsistentRead=True,
                ProjectionExpression="#N, SavedDate, Description, Keywords",
                ExpressionAttributeNames={
                    "#N": "Name"
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
    def put_settings(page_name, content, description, keywords, page_table, bucket):
        """ Puts a page in the page table """
        # Create the page entry
        saved_date = datetime.datetime.utcnow()
        saved_date = saved_date.strftime("%d-%b-%Y %H:%M UTC")
        page = {
            "Name": {"S": page_name},
            "SavedDate": {"S": saved_date},
            "Content": {"S": content},
            "Description": {"S": description},
            "Keywords": {"L": []}
        }
        page_for_s3 = {
            "Name": page_name,
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
                Key=("Content/Pages/%s.json" % page_for_s3["Name"]),
                ContentType="application/json"
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting page in the bucket"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        return {"message": "Successfully put page", "data": page}

    @staticmethod
    def get_nav_items(page_name, page_table, bucket):
        """ Deletes a page from the page table """
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

    @staticmethod
    def put_nav_items(nav_items):
        """ Puts a page in the page table """
        # Create the page entry
        saved_date = datetime.datetime.utcnow()
        saved_date = saved_date.strftime("%d-%b-%Y %H:%M UTC")
        page = {
            "Name": {"S": page_name},
            "SavedDate": {"S": saved_date},
            "Content": {"S": content},
            "Description": {"S": description},
            "Keywords": {"L": []}
        }
        page_for_s3 = {
            "Name": page_name,
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
        
        # Add page as json to bucket
        try:
            s3 = boto3.client("s3")
            s3.put_object(
                Bucket=bucket, ACL="public-read", Body=json.dumps(page_for_s3),
                Key=("Content/Pages/%s.json" % page_for_s3["Name"]),
                ContentType="application/json"
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting page in the bucket"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        # TODO: ADAM - Call set_site_settings func at end

        return {"message": "Successfully put page", "data": page}

    @staticmethod
    def read_site_settings():
        pass

    @staticmethod
    def save_site_settings(settings):
        pass