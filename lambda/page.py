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
            blog_data = dynamodb.query(
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

        return blog_data

    """ function returns site settings from dynamo db """
    def get_site_settings(self):
        # Attempt to get all data from table
        try:
            dynamodb = boto3.client('dynamodb')
            data = dynamodb.scan(TableName=self.constants["SETTINGS_TABLE"],
                                 ConsistentRead=True)
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to get site setting data: %s" % e.response['Error']['Code']
            return response.to_JSON()
        
        response = Response("Success", data)
        # format for table response to admin dash
        return response.format("Site Settings")

    """ function sets up the site settings in dynamo and s3 """
    def set_site_settings(self):
        # Get new blog params
        site_name = self.event["site"]["siteName"]
        site_url = self.event["site"]["siteURL"]
        nav_items = self.event["site"]["navItems"]
        meta_data = self.event["site"]["metaData"]
        header = self.event["site"]["header"]
        footer = self.event["site"]["footer"]
        saved_date = str(datetime.datetime.now())

        # init strings
        nav_items_string = ''
        meta_data_string = ''
        header_string = ''
        footer_string = ''

        # put dict var into string format
        for key, value in nav_items.iteritems():
            nav_items_string+= '"'+str(key)+'": "' +str(value)+ '",'

        items_list = list(nav_items_string)
        items_list[-1] = ''
        nav_items_string = ''.join(items_list)


        for key, value in meta_data.iteritems():
            meta_data_string+= '"'+str(key)+'": "' +str(value)+ '",'

        items_list = list(meta_data_string)
        items_list[-1] = ''
        meta_data_string = ''.join(items_list)
        
        for key, value in header.iteritems():
            header_string+= '"'+str(key)+'": "' +str(value)+ '",'

        items_list = list(header_string)
        items_list[-1] = ''
        header_string = ''.join(items_list)


        for key, value in footer.iteritems():
            footer_string+= '"'+str(key)+'": "' +str(value)+ '",'

        items_list = list(footer_string)
        items_list[-1] = ''
        footer_string = ''.join(items_list)

        # site settings item parameters
        site_params = {
            "SiteName": {"S": site_name},
            "SiteUrl": {"S": site_url},
            "NavItems": {"S": nav_items_string},
            "MetaData": {"S": meta_data_string},
            "Header": {"S": header_string},
            "Footer": {"S": footer_string},
            "LastSaved" : {"S": saved_date}
        }
        # put into dynamo
        try:
            dynamodb = boto3.client('dynamodb')
            dynamodb.put_item(
                TableName=self.constants["SETTINGS_TABLE"],
                Item=site_params,
                ReturnConsumedCapacity='TOTAL'
            )

        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to set new site settings: %s" % e.response['Error']['Code']

        # put site settings object into s3
        self.put_site_settings_object(site_name, site_url, nav_items_string, 
            meta_data_string, header_string, footer_string)
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
        return response.format("All Pages")


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


    ''' DEPRECATED - edit create page to take ID to replace existing records'''
    # """ function edits a page record in dynamo and s3 """
    # def edit_page(self):
    #     page_id = self.event["page"]["pageID"]
    #     author = self.event["page"]["pageAuthor"]
    #     title = self.event["page"]["pageTitle"]
    #     content = self.event["page"]["pageContent"]
    #     meta_description = self.event["page"]["metaDescription"]
    #     meta_keywords = self.event["page"]["metaKeywords"]
        
    #     try:
    #         dynamodb = boto3.client('dynamodb')
    #         # Get item instance from dynamo
    #         page = dynamodb.query(
    #             TableName=self.constants["PAGE_TABLE"],
    #             KeyConditionExpression="PageID = :v1",
    #             ExpressionAttributeValues={
    #                 ":v1": {
    #                     "S": page_id
    #                 }
    #             }
    #         )

    #         saved_date = page["Items"][0]["SavedDate"]["S"]
            
    #         # Update item from dynamo
    #         dynamodb.update_item(
    #             TableName=self.constants["PAGE_TABLE"],
    #             Key={
    #                 "PageID": {"S": page_id},
    #                 "Author": {"S": author}
    #             },
    #             UpdateExpression=(
    #                 "set Title=:t, Content=:c, SavedDate=:s, "
    #                 "MetaDescription=:d, MetaKeywords=:k"
    #             ),
    #             ExpressionAttributeValues={
    #                 ":t": {"S": title}, ":c": {"S": content}, 
    #                 ":s": {"S": saved_date}, ":d": {"S": meta_description},
    #                 ":k": {"S": meta_keywords}
    #             }
    #         )
    #     except botocore.exceptions.ClientError as e:
    #         print e
    #         response = Response("Error", None)
    #         response.errorMessage = "Unable to edit page: %s" % (
    #             e.response['Error']['Code'])

    #         if e.response['Error']['Code'] == "NoSuchKey":
    #             self.update_index(blogID, title)
    #             self.save_new_blog()
    #         else:
    #             return response.to_JSON()

    #     self.put_page_object(page_id, author, title, content, saved_date,
    #             meta_description, meta_keywords)
    #     return Response("Success", None).to_JSON()



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
        page_key = 'page-json-' + page_id
        
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


    """ function which puts a site settings json object in s3 """
    def put_site_settings_object(self, siteName, siteUrl, navItems, metaData,
                                 header, footer):
        # file name
        site_settings_key = 'site-settings'

        # site settings body
        ss_json ='{ "site-name" : "'+siteName+'", "site-url:" : "'+siteUrl+'", "nav-items" : { '+navItems+'},"meta-data" : {'+metaData+'},"header" : {'+header+'}, "footer" : {'+footer+'}}'

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
