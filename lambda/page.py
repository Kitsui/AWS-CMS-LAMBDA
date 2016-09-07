"""
# page.py
# Author: Miguel Saavedra
# Date: 17/07/2016
# Edited: 07/08/2016 | Christopher Treadgold
"""

import json
import uuid
import datetime

import boto3
import botocore
from boto3.dynamodb.conditions import Attr, Key

from response import Response

class Page(object):

    def __init__(self, event, context):
        self.event = event
        self.context = context
        # Blog variables
        self.s3 = boto3.client('s3')
        self.Index_file= "PageIndex.html"
        with open("constants.json", "r") as constants_file:
            self.constants = json.loads(constants_file.read())

    """ function gets a page record from dynamo """
    def get_page_data(self):
        """ Gets page data from dynamoDB """
        page_id = self.event["page"]["pageID"]
        try:
            dynamodb = boto3.client("dynamodb")
            page_data = dynamodb.query(
                TableName=self.constants["PAGE_TABLE"],
                KeyConditionExpression="PageID = :v1",
                ExpressionAttributeValues={
                    ":v1": {
                        "S": page_id
                    }
                }
            )
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            response = Response("Error", None)
            response.errorMessage = "Unable to get page data: %s" % (
                e.response["Error"]["Code"])
            return response.to_JSON()

        return page_data

    """ function returns site settings from dynamo db """
    def get_site_settings(self):
        # Attempt to get all data from table
        try:
            # Get site settings and read in the file body
            fileName= "Content/site-settings.json"
            get_kwargs = {
                'Bucket': self.constants["BUCKET"],
                'Key': fileName
            }
            result =  self.s3.get_object(**get_kwargs)
            site_settings_body = result['Body'].read()
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to get site setting data: %s" % e.response['Error']['Code']
            return response.to_JSON()
        # Return site settings json to be used
        return json.loads(site_settings_body)

    """ function sets up the site settings in dynamo and s3 """
    def set_site_settings(self):
        # Get new site settings params
        keys = self.event["site"].keys()
        site_atr_list = {}

        for key in keys:
            site_atr_list[key] = self.event["site"][key]

        site_atr_list["SavedDate"] = str(datetime.datetime.now())
        self.put_site_settings_object(self.event["site"])
        return Response("Success", None).to_JSON()

    """ function returns all pages in dynamo """
    def get_all_pages(self):
        # Attempt to get all data from table
        try:
            dynamodb = boto3.client('dynamodb')
            data = dynamodb.scan(TableName=self.constants["PAGE_TABLE"],
                                 ConsistentRead=True)
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to get page data: %s" % e.response['Error']['Code']
            return response.to_JSON()

        response = Response("Success", data)
        # format for table response to admin dash
        # return response.format("All Pages")
        return data


    """ functions creates a page in s3 and dynamo """
    def create_page(self):
        # Get new blog params
        page_id = str(uuid.uuid4())
        author = self.event["page"]["pageAuthor"]
        title = self.event["page"]["pageTitle"]
        content = self.event["page"]["pageContent"]
        meta_description = self.event["page"]["metaDescription"]
        meta_keywords = self.event["page"]["metaKeywords"]
        saved_date = str(datetime.datetime.now())

        # Item parameters
        page_params = {
            "PageID": {"S": page_id},
            "Author": {"S": author},
            "Title": {"S": title},
            "Content": {"S": content},
            "SavedDate": {"S": saved_date},
            "MetaDescription": {"S": meta_description},
            "MetaKeywords": {"S": meta_keywords},
        }

        # Put into dynamo
        try:
            dynamodb = boto3.client('dynamodb')
            dynamodb.put_item(
                TableName=self.constants["PAGE_TABLE"],
                Item=page_params,
                ReturnConsumedCapacity='TOTAL'
            )

        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to save new page: %s" % e.response['Error']['Code']

            if e.response['Error']['Code'] == "NoSuchKey":
                self.update_index(page_id, title)
                self.save_new_index()
            else:
                return response.to_JSON()

        self.put_page_object(page_id, author, title, content, saved_date,
                meta_description, meta_keywords)
        # Return back success
        return Response("Success", None).to_JSON()


    """ function which deletes a page record from dynamo and s3 """
    def delete_page(self):
        page_id =self.event['page']['pageID']
        author = self.event['page']['pageAuthor']

        # delete item from dynamo
        try:
            dynamodb = boto3.client('dynamodb')
            dynamodb.delete_item(
                TableName=self.constants["PAGE_TABLE"],
                Key={
                    'PageID': {"S": page_id},
                    'Author': {"S": author}
                }
            )
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to delete page: %s" % (
                e.response['Error']['Code'])
            return response.to_JSON()

        self.update_index()
        return Response("Success", None).to_JSON()


    """ function which updates a page index html object on s3 """
    def update_index(self):
        indexContent = '<html><head><title>Page Index</title></head><body><h1>Index</h1>'
        blogData = {'items': [None]}
        blogTitle = ''

        # put into dynamo
        try:
            dynamodb = boto3.client('dynamodb')
            data = dynamodb.scan(TableName=self.constants["PAGE_TABLE"],
                                 ConsistentRead=True)
            for item in data['Items']:
                indexContent = indexContent + '<br>' + '<a href="https://s3.amazonaws.com/' + self.constants["BUCKET"] + '/page' + item['PageID']['S'] + '">'+ item['Title']['S'] +'</a>'
            indexContent = indexContent + '<body></html>'
            print indexContent
            # Item parameters
            put_index_item_kwargs = {
                'Bucket': self.constants["BUCKET"],
                'ACL': 'public-read',
                'Body': indexContent,
                'Key': self.Index_file
            }
            print indexContent
            put_index_item_kwargs['ContentType'] = 'text/html'
            s3 = boto3.client("s3")
            # put into s3
            s3.put_object(**put_index_item_kwargs)
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to save site settings: %s" % (
                e.response['Error']['Code'])


    """ function which puts a page json object in s3 """
    def put_page_object(self, page_id, author, title, content, saved_date,
                        mDescription, mKeywords):
        page_key = page_id + '.json'

        self.update_index()
        # page body
        page_json =('{ "title": "'+title+'","content": "'+content+'","uuid": "'+page_id+
        '","meta-data" : { "description" : "'+mDescription+'","keywords" : "'+mKeywords+
        '"},"script-src" : "something"}')

        # Item parameters
        put_page_item_kwargs = {
            'Bucket': self.constants["BUCKET"],
            'ACL': 'public-read',
            'Body': page_json,
            'Key': 'Content/Page/'+page_key
        }

        put_page_item_kwargs['ContentType'] = 'application/json'
        try:
            s3 = boto3.client("s3")
            # put into s3
            s3.put_object(**put_page_item_kwargs)
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to save Page to s3: %s" % (
                e.response['Error']['Code'])


    # """ function which puts a site settings json object in s3 """
    # def put_site_settings_object(self, siteName, siteUrl, navItems, metaData,
    #                              header, footer):
    #     # file name
    #     site_settings_key = 'site-settings'

    #     # site settings body
    #     ss_json ='{ "site-name" : "'+siteName+'", "site-url:" : "'+siteUrl+'", "nav-items" : { '+navItems+'},"meta-data" : {'+metaData+'},"header" : {'+header+'}, "footer" : {'+footer+'}}'

    #     # Item parameters
    #     put_ss_item_kwargs = {
    #         'Bucket': self.constants["BUCKET"],
    #         'ACL': 'public-read',
    #         'Body': ss_json,
    #         'Key': site_settings_key
    #     }

    #     put_ss_item_kwargs['ContentType'] = 'application/json'
    #     # put into s3
    #     try:
    #         s3 = boto3.client("s3")
    #         s3.put_object(**put_ss_item_kwargs)
    #     except botocore.exceptions.ClientError as e:
    #         print e.response['Error']['Code']
    #         response = Response("Error", None)
    #         response.errorMessage = "Unable to save site settings: %s" % (
    #             e.response['Error']['Code'])

    """ function which puts a site settings json object in s3 """
    def put_site_settings_object(self, site_params):
        # file name
        site_settings_key = 'Content/site-settings.json'

        # site settings body
        ss_json = json.dumps(site_params)
        # Item parameters
        put_ss_item_kwargs = {
            'Bucket': self.constants["BUCKET"],
            'ACL': 'public-read',
            'Body': ss_json,
            'Key': site_settings_key
        }

        put_ss_item_kwargs['ContentType'] = 'application/json'
        # put into s3
        try:
            s3 = boto3.client("s3")
            s3.put_object(**put_ss_item_kwargs)
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to save site settings: %s" % (
                e.response['Error']['Code'])


    """ function which creates a new index if not found in s3 """
    def create_new_index(self):
        print "no index found ... creating Index"
        try:
            s3 = boto3.client("s3")
            # Item parameters
            put_index_item_kwargs = {
                'Bucket': self.constants["BUCKET"],
                'ACL': 'public-read',
                'Body':'<h1>Index</h1> <br>',
                'Key': self.Index_file
            }
            put_index_item_kwargs['ContentType'] = 'text/html'
            # put into s3
            s3.put_object(**put_index_item_kwargs)
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to save new blog: %s" % (
                e.response['Error']['Code'])
