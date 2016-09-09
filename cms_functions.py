#!/usr/bin/python2.7

"""
# cms_functions.py
# Author: Christopher Treadgold
# Date: N/D
# Edited: 07/08/2016 | Christopher Treadgold
"""

import json
import mimetypes
import os
import sys
import time
import uuid
import zipfile
from io import BytesIO

import boto3
import botocore

from replace_variables import replace_variables

class AwsFunc:
    """ Contains functions for creating, modifying and deleting elements of the
    AWSCMS. Requires awscli configured or an aws configuration file.
    """
    
    def __init__(self, cms_prefix, region="us-east-1"):
        """ Gets low-level clients for services to be used and creates
        containers for AWS objects that will be filled by creation functions.
        """
        self.region = region
        self.constants = {}
        self.cms_prefix = cms_prefix
        with open ("postfixes.json", "r") as postfixes_file:
            postfixes = json.loads(postfixes_file.read())
        for key in postfixes.keys():
            self.constants[key] = unicode(cms_prefix, "utf-8") + postfixes[key]

        self.constants["DISQUS-ID"] = "arc-cms"
    
    
    def upload_file(self, path, key):
        """ Uploads a file to s3 """
        # Prepare argument variables
        bucket_name = self.constants["BUCKET"]
        put_kwargs = {}
        mime = mimetypes.guess_type(path)
        if mime[0] != None:
            put_kwargs["ContentType"] = mime[0]
        if mime[1] != None:
            put_kwargs["ContentEncoding"] = mime[1]
        
        # Store file data and make replacements to files with certain mimetypes
        with open(path, "rb") as file_body:
            body = file_body.read()
        if type(mime[0]) is str and not mime[0].startswith("image/"):
            body = replace_variables(body, **self.constants)
        put_kwargs.update({
            "Bucket": bucket_name,
            "ACL": "public-read",
            "Body": body,
            "Key": key
        })
        
        # Upload file to s3
        try:
            print "Uploading: %s" % key
            s3 = boto3.client("s3")
            s3.put_object(**put_kwargs)
            print "Complete"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()
        
        
    def create_bucket(self):
        """ Creates a bucket in region "bucket_region".
        
        If "bucket_region" is not given, bucket will default to US Standard
        region. Files for the AWS CMS are uploaded to the bucket.
        """
        bucket_name = self.constants["BUCKET"]
        bucket_kwargs = {"ACL": "public-read", "Bucket": bucket_name}
        if self.region != "us-east-1":
            bucket_kwargs["CreateBucketConfiguration"] = {
                "LocationConstraint": self.region}
        
        # Create bucket
        try:
            s3 = boto3.client("s3")
            print "Creating bucket: %s" % (bucket_name)
            bucket = s3.create_bucket(**bucket_kwargs)
            print "Bucket created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()
        
        # add bucket CORS
        try:
            s3 = boto3.client("s3")
            s3.put_bucket_cors(
                Bucket=bucket_name,
                CORSConfiguration={
                    "CORSRules": [{
                        "AllowedOrigins": ["*"],
                        "AllowedMethods": ["GET", "POST"],
                        "AllowedHeaders": ["Authorization", "Cache-Control",
                                           "Upgrade-Insecure-Requests"],
                        "MaxAgeSeconds": 3000
                    }]
                }
            )
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()
        
        # Populate the bucket, adding all files from the website folder
        print "Populating bucket"
        for root, dirs, files in os.walk("website"):
            for fl in files:
                path = os.path.join(root, fl)
                key = path[8:]
                # If the file has backslashes in it, replace them with forwardslashes
                key = key.replace("\\", "/")
                self.upload_file(path, key)
        print "Bucket populated"

    
    def create_cloudfront_distribution(self):
        """ Creates a coudfront distribution linked to the s3 bucket """
        try:
            print "Creating cloudfront distribution"
            origin_id = str(uuid.uuid4())
            cloudfront = boto3.client("cloudfront")
            cloudfront.create_distribution(
                DistributionConfig={
                    "CallerReference": str(uuid.uuid4()),
                    "DefaultRootObject": "index.html",
                    "Origins": {
                        "Quantity": 1,
                        "Items": [
                            {
                                "Id": origin_id,
                                "DomainName": "%s.s3.amazonaws.com" % (
                                    self.constants["BUCKET"]),
                                "S3OriginConfig": {
                                    "OriginAccessIdentity": ""
                                }
                            }
                        ]
                    },
                    "DefaultCacheBehavior": {
                        "TargetOriginId": origin_id,
                        "ForwardedValues": {
                            "QueryString": False,
                            "Cookies": {
                                "Forward": "none"
                            }
                        },
                        "TrustedSigners": {
                            "Enabled": False,
                            "Quantity": 0
                        },
                        "ViewerProtocolPolicy": "redirect-to-https",
                        "MinTTL": 0,
                        "MaxTTL": 2628000,
                        "DefaultTTL": 86400,
                        "AllowedMethods": {
                            "Quantity": 2,
                            "Items": ["GET", "HEAD"]
                        }
                    },
                    "Comment": "Distribution of %s.s3.amazonaws.com" % (
                        self.constants["BUCKET"]),
                    "Enabled": True
                }
            )
            print "Cloudfront distribution created"
        except botocore.exceptions.ClientError as e:
            print e
            sys.exit()
    

    def create_role_table(self):
        """ Creates a role table. """
        with open("dynamo/role_table.json", "r") as thefile:
            role_table_json = json.loads(thefile.read())
        role_table_json["TableName"] = self.constants["ROLE_TABLE"]
        
        try:
            print "Creating table: %s" % (self.constants["ROLE_TABLE"])
            dynamodb = boto3.client("dynamodb")
            role_table = dynamodb.create_table(**role_table_json)
            self.wait_for_table(role_table)
            print "Table created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()


    def create_user_table(self):
        """ Creates a user table. """
        with open("dynamo/user_table.json", "r") as thefile:
            user_table_json = json.loads(thefile.read())
        user_table_json["TableName"] = self.constants["USER_TABLE"]
        
        try:
            print "Creating table: %s" % (self.constants["USER_TABLE"])
            dynamodb = boto3.client("dynamodb")
            user_table = dynamodb.create_table(**user_table_json)
            self.wait_for_table(user_table)
            print "User table created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()


    def create_token_table(self):
        """ Creates a token table. """
        with open("dynamo/token_table.json", "r") as thefile:
            token_table_json = json.loads(thefile.read())
        token_table_json["TableName"] = self.constants["TOKEN_TABLE"]
            
        try:
            print "Creating table: %s" % (self.constants["TOKEN_TABLE"])
            dynamodb = boto3.client("dynamodb")
            token_table = dynamodb.create_table(**token_table_json)
            self.wait_for_table(token_table)
            print "Token table created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()
        
    
    def create_blog_table(self):
        """ Creates a blog table. """
        with open("dynamo/blog_table.json", "r") as thefile:
            blog_table_json = json.loads(thefile.read())
        blog_table_json["TableName"] = self.constants["BLOG_TABLE"]
            
        try:
            print "Creating table: %s" % (self.constants["BLOG_TABLE"])
            dynamodb = boto3.client("dynamodb")
            blog_table = dynamodb.create_table(**blog_table_json)
            self.wait_for_table(blog_table)
            print "Blog table created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()

    def create_menu_table(self):
        """ Creates a menu table. """
        with open("dynamo/menu_table_structure.json", "r") as thefile:
            menu_table_json = json.loads(thefile.read())
        menu_table_json["TableName"] = self.constants["MENU_TABLE"]
            
        try:
            print "Creating table: %s" % (self.constants["MENU_TABLE"])
            dynamodb = boto3.client("dynamodb")
            menu_table = dynamodb.create_table(**menu_table_json)
            self.wait_for_table(menu_table)
            print "Menu table created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()
        

    def create_page_table(self):
        """ Creates a page table. """
        with open("dynamo/page_table.json", "r") as thefile:
            page_table_json = json.loads(thefile.read())
        page_table_json["TableName"] = self.constants["PAGE_TABLE"]
        
        try:
            print "Creating table: %s" % (self.constants["PAGE_TABLE"])
            dynamodb = boto3.client("dynamodb")
            page_table = dynamodb.create_table(**page_table_json)
            self.wait_for_table(page_table)
            print "Page table created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()            
            
    def create_site_settings_table(self):
        """ Creates a site settings table. """
        with open("dynamo/site_settings_table.json", "r") as thefile:
            site_settings_table_json = json.loads(thefile.read())
        site_settings_table_json["TableName"] = self.constants["SETTINGS_TABLE"]
        
        try:
            print "Creating table: %s" % (self.constants["SETTINGS_TABLE"])
            dynamodb = boto3.client("dynamodb")
            site_settings_table = dynamodb.create_table(**site_settings_table_json)
            self.wait_for_table(site_settings_table)
            print "Settings table created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()


    def wait_for_table(self, table):
        """ Waits for a table to finish being created. """
        # Wait for dynamo to acknowledge a table is being created
        table_creating = True
        retries = 10
        while table_creating and retries > 0:
            try:
                dynamodb = boto3.client("dynamodb")
                response = dynamodb.describe_table(
                    TableName=table["TableDescription"]["TableName"])
                table_creating = False
            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    retries -= 1
                    time.sleep(0.5)
                else:
                    print e.response["Error"]["Code"]
                    print e.response["Error"]["Message"]
                    sys.exit()
                    
        # Wait while the table creates
        while response["Table"]["TableStatus"] == "CREATING":
            time.sleep(0.1)
            response = dynamodb.describe_table(
                TableName=table["TableDescription"]["TableName"])


    def create_site_settings_db_entry(self):
        """ Creates a default site settings in the site settings table """
        with open("dynamo/site_settings.json", "r") as thefile:
            ss_json = json.loads(thefile.read())
        for json_item in ss_json["Items"]:
            json_item["TableName"] = self.constants["SETTINGS_TABLE"]
            try:
                print "Creating Site settings db entry"
                dynamodb = boto3.client("dynamodb")
                dynamodb.put_item(**json_item)
                print "Site settings db entry created"
            except botocore.exceptions.ClientError as e:
                print e.response["Error"]["Code"]
                print e.response["Error"]["Message"]
                sys.exit()


    def create_blog_db_entry(self):
        """ Creates a default blog in the Blog table """
        with open("dynamo/blog.json", "r") as thefile:
            blog_json = json.loads(thefile.read())
        blog_json["TableName"] = self.constants["BLOG_TABLE"]
        
        try:
            print "Creating Blog entry"
            dynamodb = boto3.client("dynamodb")
            dynamodb.put_item(**blog_json)
            print "Blog created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()

    def create_menu_db_entries(self):
        """ Creates a default menu entries in the Menu table """
        with open("dynamo/menu_table_data.json", "r") as thefile:
            menu_json_temp = thefile.read()
            menu_json_temp = menu_json_temp.replace("MenuTable", self.constants["MENU_TABLE"])
            menu_json = json.loads(menu_json_temp)
        
        try:
            print "Creating Menu entries"
            dynamodb = boto3.client("dynamodb")
            dynamodb.batch_write_item(**menu_json)
            print "Menu entries created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()

    def create_page_db_entry(self):
        """ Creates a Page in the Page table """
        with open("dynamo/page.json", "r") as thefile:
            page_json = json.loads(thefile.read())
        page_json["TableName"] = self.constants["PAGE_TABLE"]
        
        try:
            print "Creating Page db entry"
            dynamodb = boto3.client("dynamodb")
            dynamodb.put_item(**page_json)
            print "Page db entry created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()


    def create_form_db_entry(self):
        """ Creates a Form in the Form table """
        with open("dynamo/form.json", "r") as thefile:
            form_json = json.loads(thefile.read())
        form_json["TableName"] = self.constants["FORM_TABLE"]
        
        try:
            print "Creating Form db entry"
            dynamodb = boto3.client("dynamodb")
            dynamodb.put_item(**form_json)
            print "Form db entry created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()


    def create_admin_role_db_entry(self):
        """ Creates an entry in the role database that represents an
        admin role
        """
        with open("dynamo/role.json", "r") as thefile:
            admin_role_json = json.loads(thefile.read())
        admin_role_json["TableName"] = self.constants["ROLE_TABLE"]
        
        try:
            print "Creating admin role db entry"
            dynamodb = boto3.client("dynamodb")
            dynamodb.put_item(**admin_role_json)
            print "Admin role db entry created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()


    def create_admin_user_db_entry(self):
        """ Creates an entry in the user database that represents an admin """
        with open("dynamo/user.json", "r") as thefile:
            admin_user_json = json.loads(thefile.read())
        admin_user_json["TableName"] = self.constants["USER_TABLE"]
        
        try:
            print "Creating admin db entry"
            dynamodb = boto3.client("dynamodb")
            dynamodb.put_item(**admin_user_json)
            print "Admin db entry created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()


    def create_token_db_entry(self):
        """ Creates a token in the token database """
        with open("dynamo/token.json", "r") as thefile:
            token_json = json.loads(thefile.read())
        token_json["TableName"] = self.constants["TOKEN_TABLE"]
        
        try:
            print "Creating token db entry"
            dynamodb = boto3.client("dynamodb")
            dynamodb.put_item(**token_json)
            print "Token db entry created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()

    def update_lambda(self):
        try:
            lmda = boto3.client("lambda")
            lmda.update_function_code(
                FunctionName=self.constants["LAMBDA_FUNCTION"],
                ZipFile=AwsFunc.zip_lambda(),
            )
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()

    def create_lambda_function(self):
        """ Creates a lamda function and uploads AWS CMS to to it """
        with open("lambda/role_policy.json", "r") as thefile:
            lmda_role_json = thefile.read()
        
        # Create the lambda iam role
        try:
            print "Creating iam role: %s" % (self.constants["LAMBDA_ROLE"])
            iam = boto3.client("iam")
            lambda_role_name = self.constants["LAMBDA_ROLE"]
            lambda_role = iam.create_role(
                RoleName=lambda_role_name,
                AssumeRolePolicyDocument=lmda_role_json
            )
            
            # Attach permissions to the lambda role
            iam.attach_role_policy(
                RoleName=lambda_role_name,
                PolicyArn="arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
            )
            iam.attach_role_policy(
                RoleName=lambda_role_name,
                PolicyArn=("arn:aws:iam::aws:"
                           "policy/service-role/AWSLambdaBasicExecutionRole")
            )
            iam.attach_role_policy(
                RoleName=lambda_role_name,
                PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess"
            )
            print "Role created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()
        
        # Necessary as it can take a few seconds for an iam role to be usable
        print "Waiting for role to be usable"
        time.sleep(10)
        
        # Store constants file in lambda directory
        self.store_lambda_constants()
        
        # Create the lambda function
        try:
            print "Creating lambda function"
            lmda = boto3.client("lambda")
            lambda_function = lmda.create_function(
                FunctionName=self.constants["LAMBDA_FUNCTION"],
                Runtime="python2.7",
                Role=lambda_role["Role"]["Arn"],
                Handler="controller.handler",
                Code={"ZipFile": AwsFunc.zip_lambda()},
                Description=("Aws cms central management function designed to "
                             "handle any API Gateway request"),
                Timeout=10
            )
            print "Function created"
            self.constants["LAMBDA_FUNCTION_ARN"] = (
                lambda_function["FunctionArn"])
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()
        
        self.create_api_invocation_uri()
        self.remove_lambda_constants()
    
    
    def create_rest_api(self):
        """ Creates the api gateway and links it to the lambda function """
        try:
            api_gateway = boto3.client("apigateway")
            
            print "Creating the rest api"
            rest_api = api_gateway.create_rest_api(
                name=self.constants["REST_API"]
            )
            print "Rest api created"
            
            self.constants["REST_API_ID"] = rest_api["id"]
            rest_api_resource = api_gateway.get_resources(
                restApiId=self.constants["REST_API_ID"]
            )
            self.constants["REST_API_ROOT_ID"] = (
                rest_api_resource["items"][0]["id"])
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()
            
        self.create_api_permissions_uri()
        self.create_api_url()
        
        
    def api_add_post_method(self):
        try:
            api_gateway = boto3.client("apigateway")
            rest_api_id = self.constants["REST_API_ID"]
            rest_api_root_id = self.constants["REST_API_ROOT_ID"]
            
            print "Adding POST method to rest api"
            # Add a POST method to the rest api
            api_gateway.put_method(
                restApiId=rest_api_id,
                resourceId=rest_api_root_id,
                httpMethod="POST",
                authorizationType="NONE",
                requestParameters={
                    "method.request.header.Cookie": False
                }
            )
            
            # Set the put integration of the POST method
            api_gateway.put_integration(
                restApiId=rest_api_id,
                resourceId=rest_api_root_id,
                httpMethod="POST",
                type="AWS",
                passthroughBehavior="NEVER",
                integrationHttpMethod="POST",
                uri=self.constants["API_INVOCATION_URI"],
                requestTemplates={
                    "application/json": (
                        "{\"params\": $input.body, "
                              "#if($input.params(\"Cookie\") && $input.params(\"Cookie\") != \"\") "
                                  "\"token\": \"$input.params(\"Cookie\")\" "
                              "#else "
                                  "\"token\": \"\" "
                              "#end"
                        "}"
                    )
                }
            )
            
            # Set the put method response of the POST method
            api_gateway.put_method_response(
                restApiId=rest_api_id,
                resourceId=rest_api_root_id,
                httpMethod="POST",
                statusCode="200",
                responseParameters={
                    "method.response.header.Set-Cookie": False,
                    "method.response.header.Access-Control-Allow-Credentials": False,
                    "method.response.header.Access-Control-Allow-Origin": False
                },
                responseModels={
                    "application/json": "Empty"
                }
            )
            
            # Set the put integration response of the POST method
            api_gateway.put_integration_response(
                restApiId=rest_api_id,
                resourceId=rest_api_root_id,
                httpMethod="POST",
                statusCode="200",
                responseParameters={
                    "method.response.header.Set-Cookie": (
                        "integration.response.body.Cookie"),
                    "method.response.header.Access-Control-Allow-Credentials": (
                        "\'true\'"),
                    "method.response.header.Access-Control-Allow-Origin": (
                        "\'https://s3.amazonaws.com\'")
                },
                responseTemplates={
                    "application/json": ""
                }
            )
            print "POST method added"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()
            
            
    def api_add_options_method(self):
        try:
            api_gateway = boto3.client("apigateway")
            rest_api_id = self.constants["REST_API_ID"]
            rest_api_root_id = self.constants["REST_API_ROOT_ID"]
            
            print "Adding OPTIONS method to rest api"
            # Add an options method to the rest api
            api_gateway.put_method(
                restApiId=rest_api_id,
                resourceId=rest_api_root_id,
                httpMethod="OPTIONS",
                authorizationType="NONE"
            )
            
            # Set the put integration of the OPTIONS method
            api_gateway.put_integration(
                restApiId=rest_api_id,
                resourceId=rest_api_root_id,
                httpMethod="OPTIONS",
                type="MOCK",
                requestTemplates={
                    "application/json": "{\"statusCode\": 200}"
                }
            )
            
            # Set the put method response of the OPTIONS method
            api_gateway.put_method_response(
                restApiId=rest_api_id,
                resourceId=rest_api_root_id,
                httpMethod="OPTIONS",
                statusCode="200",
                responseParameters={
                    "method.response.header.Access-Control-Allow-Headers": False,
                    "method.response.header.Access-Control-Allow-Origin": False,
                    "method.response.header.Access-Control-Allow-Credentials": False,
                    "method.response.header.Access-Control-Allow-Methods": False
                },
                responseModels={
                    "application/json": "Empty"
                }
            )

            # Set the put integration response of the OPTIONS method
            api_gateway.put_integration_response(
                restApiId=rest_api_id,
                resourceId=rest_api_root_id,
                httpMethod="OPTIONS",
                statusCode="200",
                responseParameters={
                    "method.response.header.Access-Control-Allow-Headers": (
                        "\'Content-Type,X-Amz-Date,Authorization,X-Api-Key,"
                        "X-Amz-Security-Token,Cookie,Accept,"
                        "Access-Control-Allow-Origin\'"
                    ),
                    "method.response.header.Access-Control-Allow-Origin": (
                        "\'https://s3.amazonaws.com\'"),
                    "method.response.header.Access-Control-Allow-Credentials": (
                        "\'true\'"),
                    "method.response.header.Access-Control-Allow-Methods": (
                        "\'POST,OPTIONS\'")
                },
                responseTemplates={
                    "application/json": ""
                }
            )
            print "OPTIONS method addded"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()
    
    
    def deploy_api(self):
        try:
            api_gateway = boto3.client("apigateway")
            rest_api_id = self.constants["REST_API_ID"]
            
            print "Deploying api"
            # Create a deployment of the rest api
            api_gateway.create_deployment(
                restApiId=rest_api_id,
                stageName="prod"
            )
            
            lmda = boto3.client("lambda")
            function_name = self.constants["LAMBDA_FUNCTION"]
            api_permissions_uri = self.constants["API_PERMISSIONS_URI"]
            
            # Give the api deployment permission to trigger the lambda function
            lmda.add_permission(
                FunctionName=function_name,
                StatementId="7rbvfF87f67",
                Action="lambda:InvokeFunction",
                Principal="apigateway.amazonaws.com",
                SourceArn=api_permissions_uri
            )
            print "Api deployed"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()
            
            
    def store_lambda_constants(self):
        """ Stores aws service constants in the lambda directory """
        with open ("lambda/constants.json", "w") as constants_file:
            constants_file.write(json.dumps(self.constants, indent=4,
                                 sort_keys=True))
    
    
    def save_constants(self):
        """ Stores aws service constants in a file """
        constants_file_name = "%s-constants.json" % (self.cms_prefix)
        with open (constants_file_name, "w") as constants_file:
            constants_file.write(json.dumps(self.constants, indent=4,
                                 sort_keys=True))
        
        if not os.path.isfile("./installed.json"):
            with open("installed.json", "w") as installed:
                installed.write(json.dumps({"1": self.cms_prefix}, indent=4,
                                           sort_keys=True))
        else:
            with open("installed.json", "r") as installed:
                installed_json = json.loads(installed.read())
            next_key = len(installed_json.keys()) + 1
            installed_json[next_key] = self.cms_prefix
            with open("installed.json", "w") as installed:
                installed.write(json.dumps(installed_json, indent=4,
                                           sort_keys=True))
    
    
    def remove_lambda_constants(self):
        """ Removes aws service constants from the lambda directory """
        os.remove("lambda/constants.json")


    def create_api_invocation_uri(self):
        """ Creates an api invocation uri """
        self.constants["API_INVOCATION_URI"] = (
            "arn:aws:apigateway:%s:lambda:"
            "path/2015-03-31/functions/%s/invocations"
        ) % (self.region, self.constants["LAMBDA_FUNCTION_ARN"])
        
        
    def create_api_permissions_uri(self):
        """ Creates the uri that is needed for giving the api deployment
        permission to trigger the lambda function
        """
        self.constants["API_PERMISSIONS_URI"] = (
            "arn:aws:execute-api:%s:%s:%s/*/POST/"
        ) % (self.region, AwsFunc.get_account_id(),
             self.constants["REST_API_ID"])
        
        
    def create_api_url(self):
        """ Creates the url needed to send requests to the api gateway """
        self.constants["API_URL"] = (
            "https://%s.execute-api.%s.amazonaws.com/prod" % (
                self.constants["REST_API_ID"], self.region))


    @staticmethod
    def get_account_id():
        sts = boto3.client("sts")
        return sts.get_caller_identity()["Account"]
        
    
    @staticmethod
    def zip_lambda():
        """ Zips all files needed to create the controller function and stores
        them in an object that will be uploaded to lambda.
        """
        # Don't zip these files
        ignore_files = ["controller.zip", "role_policy.json"] 
        
        # Zip the files and store them in a buffer
        zip_data = BytesIO()
        zipf = zipfile.ZipFile(zip_data, "w")
        for root, dirs, files in os.walk("lambda"):
            for fl in files:
                if fl not in ignore_files:
                    path_to_file = os.path.join(root, fl)
                    file_key = path_to_file[7:]
                    zipf.write(path_to_file, arcname=file_key)
        zipf.close()
        
        # Write the buffer to a variable and return it
        zip_data.seek(0)
        data = zip_data.read()
        zip_data.close()
        return data
