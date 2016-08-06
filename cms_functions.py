#!/usr/bin/python2.7

import ast
import json
import mimetypes
import os
import sys
import time
import zipfile

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
        self.names = {}
        with open ("postfixes.json", "r") as postfixes_file:
            postfixes = json.loads(postfixes_file.read())
        for key in postfixes.keys():
            self.names[key] = unicode(cms_prefix, "utf-8") + postfixes[key]
    
    
    def store_names(self):
        """ Stores aws service names in a file """
        with open ("lambda/names.json", "w+") as names_file:
            names_file.write(json.dumps(self.names, indent=4, sort_keys=True))
    
    
    def upload_file(self, path, key):
        """ Uploads a file to s3 """
        bucket_name = self.names["BUCKET"]
        put_kwargs = {}
        mime = mimetypes.guess_type(path)
        if mime[0] != None:
            put_kwargs["ContentType"] = mime[0]
        if mime[1] != None:
            put_kwargs["ContentEncoding"] = mime[1]
        with open(path, "rb") as file_body:
            body = file_body.read()
        put_kwargs.update({
            "Bucket": bucket_name,
            "ACL": "public-read",
            "Body": body,
            "Key": key
        })
            
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
        bucket_name = self.names["BUCKET"]
        bucket_kwargs = {"ACL": "public-read", "Bucket": bucket_name}
        if self.region != "us-east-1":
            bucket_kwargs["CreateBucketConfiguration"] = {
                "LocationConstraint": self.region}
        
        try:
            s3 = boto3.client("s3")
            print "Creating bucket"
            bucket = s3.create_bucket(**bucket_kwargs)
            print "Bucket created"
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
                self.upload_file(path, key)
        print "Bucket populated"


    def create_role_table(self):
        """ Creates a role table. """
        with open("dynamo/role_table.json", "r") as thefile:
            role_table_json = json.loads(thefile.read())
        role_table_json["TableName"] = self.names["ROLE_TABLE"]
        
        try:
            print "Creating role table"
            dynamodb = boto3.client("dynamodb")
            role_table = dynamodb.create_table(**role_table_json)
            # Wait for the role table to be created
            self.wait_for_table(role_table)
            print "Role table created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()


    def create_user_table(self):
        """ Creates a user table. """
        with open("dynamo/user_table.json", "r") as thefile:
            user_table_json = json.loads(thefile.read())
        user_table_json["TableName"] = self.names["USER_TABLE"]
        
        try:
            print "Creating user table"
            dynamodb = boto3.client("dynamodb")
            user_table = dynamodb.create_table(**user_table_json)
            # Wait for the user table to be created
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
        token_table_json["TableName"] = self.names["TOKEN_TABLE"]
            
        try:
            print "Creating token table"
            dynamodb = boto3.client("dynamodb")
            token_table = dynamodb.create_table(**token_table_json)
            # Wait for the token table to be created
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
        blog_table_json["TableName"] = self.names["BLOG_TABLE"]
            
        try:
            print "Creating blog table"
            dynamodb = boto3.client("dynamodb")
            blog_table = dynamodb.create_table(**blog_table_json)
            # Wait for the blog table to be created
            self.wait_for_table(blog_table)
            print "Blog table created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()
        

    def create_page_table(self):
        """ Creates a page table. """
        with open("dynamo/page_table.json", "r") as thefile:
            page_table_json = json.loads(thefile.read())
        page_table_json["TableName"] = self.names["PAGE_TABLE"]
        
        try:
            print "Creating page table"
            dynamodb = boto3.client("dynamodb")
            page_table = dynamodb.create_table(**page_table_json)
            # Wait for the blog table to be created
            self.wait_for_table(page_table)
            print "Blog table created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()


    def wait_for_table(self, table):
        """ Waits for a table to finish being created. """
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


    def create_admin_role_db_entry(self):
        """ Creates an entry in the Role database that represents an adminrole"""
        with open("dynamo/role.json", "r") as thefile:
            admin_role_json = json.loads(thefile.read())
        admin_role_json["TableName"] = self.names["ROLE_TABLE"]
        
        try:
            print "Creating admin role db entry"
            dynamodb = boto3.client("dynamodb")
            dynamodb.put_item(**admin_role_json)
            print "Admin role db entry created"
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()

#    def create_admin_db_entry(self):
#        """ Creates an entry in the User database that represents an admin """
#        try:
#            print "Creating admin db entry"
#            
#            admin_json = ""
#            with open("dynamo/user.json", "r") as thefile:
#                admin_json = ast.literal_eval(thefile.read())

#            self.dynamodb.put_item(**admin_json)
#        except botocore.exceptions.ClientError as e:
#            print e.response["Error"]["Code"]
#            print e.response["Error"]["Message"]
#            sys.exit()

#        print "Admin db entry created"


#    def create_token_db_entry(self):
#        """ Creates a token in the "Token" database """
#        try:
#            print "Creating token db entry"
#            
#            token_json = ""
#            with open("dynamo/token.json", "r") as thefile:
#                token_json = ast.literal_eval(thefile.read())

#            self.dynamodb.put_item(**token_json)
#        except botocore.exceptions.ClientError as e:
#            print e.response["Error"]["Code"]
#            print e.response["Error"]["Message"]
#            sys.exit()

#        print "Token db entry created"


#    def create_lambda_function(self):
#        """ Creates a lamda function and uploads AWS CMS to to it """
#        try:
#            print "Creating lambda function"
#            
#            lmda_role_json = ""
#            with open("lambda/role_policy.json", "r") as thefile:
#                lmda_role_json = thefile.read()
#            
#            code = b""
#            with open("lambda/controller.zip", "rb") as thefile:
#                code = thefile.read()
#            
#            # Create a role that can be attached to lambda functions
#            lmda_role = self.iam.create_role(
#                RoleName="lambda_basic_execution",
#                AssumeRolePolicyDocument=lmda_role_json
#            )
#            
#            # Attach permissions to the lambda role
#            self.iam.attach_role_policy(
#                RoleName=lmda_role["Role"]["RoleName"],
#                PolicyArn="arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
#            )
#            self.iam.attach_role_policy(
#                RoleName=lmda_role["Role"]["RoleName"],
#                PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
#            )
#            self.iam.attach_role_policy(
#                RoleName=lmda_role["Role"]["RoleName"],
#                PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess"
#            )
#            
#            time.sleep(10)
#            
#            # Create the lambda function
#            self.lmda.create_function(
#                FunctionName="controller",
#                Runtime="python2.7",
#                Role=lmda_role["Role"]["Arn"],
#                Handler="controller.handler",
#                Code={
#                    "ZipFile": code
#                },
#                Description="Central management function designed to handle any API Gateway request",
#                Timeout=10
#            )
#        except botocore.exceptions.ClientError as e:
#            print e.response["Error"]["Code"]
#            print e.response["Error"]["Message"]
#            sys.exit()
#        
#        print "Lambda function created"
    

    def zip_lambda():
        ignore_files = ["controller.zip", "role_policy.json"]
        
        print "Creating controller.zip"
        zipf = zipfile.ZipFile("lambda/controller.zip", "w")
        for root, dirs, files in os.walk("lambda"):
            for fl in files:
                if fl not in ignore_files:
                    path_to_file = os.path.join(root, fl)
                    file_key = path_to_file[7:]
                    zipf.write(os.path.join(root, fl), arcname=file_key)
        zipf.close()
        print "controller.zip created"

    
#    def create_api_gateway(self):
#        """ Creates the api gateway and links it to the lambda function """
#        try:
#            print "Creating the api gateway"
#            
#            # Create a rest api
#            self.rest_api_id = self.apigateway.create_rest_api(
#                name="AWS_CMS_Operations"
#            )["id"]
#            
#            # Get the rest api"s root id
#            root_resource = self.apigateway.get_resources(
#                restApiId=self.rest_api_id
#            )["items"][0]
#            
#            # Add a post method to the rest api
#            api_method = self.apigateway.put_method(
#                restApiId=self.rest_api_id,
#                resourceId=root_resource["id"],
#                httpMethod="POST",
#                authorizationType="NONE"
#            )

#            # Add headers to the method of the POST method
#            self.apigateway.update_method(
#                restApiId=self.rest_api_id,
#                resourceId=root_resource["id"],
#                httpMethod="POST",
#                patchOperations=[
#                    {
#                        "op": "add",
#                        "path": "/requestParameters/method.request.header.Cookie",
#                        "value": "False"
#                    }
#                ]
#            )
#            
#            # Set the put integration of the POST method
#            self.apigateway.put_integration(
#                restApiId=self.rest_api_id,
#                resourceId=root_resource["id"],
#                httpMethod="POST",
#                type="AWS",
#                passthroughBehavior="NEVER",
#                integrationHttpMethod="POST",
#                uri=self.create_api_invocation_uri(),
#                requestTemplates={
#                    "application/json":"{"params": $input.body, \
#                        #if($input.params(\"Cookie\") && $input.params(\"Cookie\") != "") \
#                        "Cookie": "$input.params(\"Cookie\")" \
#                        #else \
#                        "Cookie": "" \
#                        #end \
#                    }"
#                }
#            )
#            
#            # Set the put method response of the POST method
#            self.apigateway.put_method_response(
#                restApiId=self.rest_api_id,
#                resourceId=root_resource["id"],
#                httpMethod="POST",
#                statusCode="200",
#                responseModels={
#                    "application/json": "Empty"
#                }
#            )
#            
#            # Set the put integration response of the POST method
#            self.apigateway.put_integration_response(
#                restApiId=self.rest_api_id,
#                resourceId=root_resource["id"],
#                httpMethod="POST",
#                statusCode="200",
#                responseTemplates={
#                    "application/json": ""
#                }
#            )
#            
#            # Add headers to the method response of the POST method
#            self.apigateway.update_method_response(
#                restApiId=self.rest_api_id,
#                resourceId=root_resource["id"],
#                httpMethod="POST",
#                statusCode="200",
#                patchOperations=[
#                    {
#                        "op": "add",
#                        "path": "/responseParameters/method.response.header.Set-Cookie",
#                        "value": "False"
#                    },
#                    {
#                        "op": "add",
#                        "path": "/responseParameters/method.response.header.Access-Control-Allow-Credentials",
#                        "value": "False"
#                    },
#                    {
#                        "op": "add",
#                        "path": "/responseParameters/method.response.header.Access-Control-Allow-Origin",
#                        "value": "False"
#                    }
#                ]
#            )
#            
#            # Add headers to the integration response of the POST method
#            self.apigateway.update_integration_response(
#                restApiId=self.rest_api_id,
#                resourceId=root_resource["id"],
#                httpMethod="POST",
#                statusCode="200",
#                patchOperations=[
#                    {
#                        "op": "add",
#                        "path": "/responseParameters/method.response.header.Set-Cookie",
#                        "value": "integration.response.body.Cookie"
#                    },
#                    {
#                        "op": "add",
#                        "path": "/responseParameters/method.response.header.Access-Control-Allow-Credentials",
#                        "value": "\"true\""
#                    },
#                    {
#                        "op": "add",
#                        "path": "/responseParameters/method.response.header.Access-Control-Allow-Origin",
#                        "value": "\"https://s3.amazonaws.com\""
#                    }
#                ]
#            )
#            
#            # Add an options method to the rest api
#            self.apigateway.put_method(
#                restApiId=self.rest_api_id,
#                resourceId=root_resource["id"],
#                httpMethod="OPTIONS",
#                authorizationType="NONE"
#            )
#            
#            # Set the put method response of the OPTIONS method
#            self.apigateway.put_method_response(
#                restApiId=self.rest_api_id,
#                resourceId=root_resource["id"],
#                httpMethod="OPTIONS",
#                statusCode="200",
#                responseModels={
#                    "application/json": "Empty"
#                }
#            )

#            # Set the put integration of the OPTIONS method
#            self.apigateway.put_integration(
#                restApiId=self.rest_api_id,
#                resourceId=root_resource["id"],
#                httpMethod="OPTIONS",
#                type="MOCK",
#                requestTemplates={
#                    "application/json": "{"statusCode": 200}"
#                }
#            )

#            # Set the put integration response of the OPTIONS method
#            self.apigateway.put_integration_response(
#                restApiId=self.rest_api_id,
#                resourceId=root_resource["id"],
#                httpMethod="OPTIONS",
#                statusCode="200",
#                responseTemplates={
#                    "application/json": ""
#                }
#            )
#            
#            # Add headers to the method response of the OPTIONS method
#            self.apigateway.update_method_response(
#                restApiId=self.rest_api_id,
#                resourceId=root_resource["id"],
#                httpMethod="OPTIONS",
#                statusCode="200",
#                patchOperations=[
#                    {
#                        "op": "add",
#                        "path": "/responseParameters/method.response.header.Access-Control-Allow-Headers",
#                        "value": "False"
#                    },
#                    {
#                        "op": "add",
#                        "path": "/responseParameters/method.response.header.Access-Control-Allow-Origin",
#                        "value": "False"
#                    },
#                    {
#                        "op": "add",
#                        "path": "/responseParameters/method.response.header.Access-Control-Allow-Credentials",
#                        "value": "False"
#                    },
#                    {
#                        "op": "add",
#                        "path": "/responseParameters/method.response.header.Access-Control-Allow-Methods",
#                        "value": "False"
#                    }
#                ]
#            )
#            
#            # Add headers to the integration response of the OPTIONS method
#            self.apigateway.update_integration_response(
#                restApiId=self.rest_api_id,
#                resourceId=root_resource["id"],
#                httpMethod="OPTIONS",
#                statusCode="200",
#                patchOperations=[
#                    {
#                        "op": "add",
#                        "path": "/responseParameters/method.response.header.Access-Control-Allow-Headers",
#                        "value": "\"Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,Cookie,Accept,Access-Control-Allow-Origin\""
#                    },
#                    {
#                        "op": "add",
#                        "path": "/responseParameters/method.response.header.Access-Control-Allow-Origin",
#                        "value": "\"https://s3.amazonaws.com\""
#                    },
#                    {
#                        "op": "add",
#                        "path": "/responseParameters/method.response.header.Access-Control-Allow-Credentials",
#                        "value": "\"true\""
#                    },
#                    {
#                        "op": "add",
#                        "path": "/responseParameters/method.response.header.Access-Control-Allow-Methods",
#                        "value": "\"POST,OPTIONS\""
#                    }
#                ]
#            )
#            
#            # Create a deployment of the rest api
#            self.apigateway.create_deployment(
#                restApiId=self.rest_api_id,
#                stageName="prod"
#            )
#            
#            # Give the api deployment permission to trigger the lambda function
#            self.lmda.add_permission(
#                FunctionName=,
#                StatementId="c67ytfvu65ytd5tsrdghk",
#                Action="lambda:InvokeFunction",
#                Principal="apigateway.amazonaws.com",
#                SourceArn=self.create_api_permission_uri()
#            )
#            
#            print "Api gateway created"
#        except botocore.exceptions.ClientError as e:
#            print e.response["Error"]["Code"]
#            print e.response["Error"]["Message"]
#            sys.exit()


#    def get_account_id(self):
#        sts = boto3.client("sts")
#        return sts.get_caller_identity()["Account"]


#    def create_api_invocation_uri(self):
#        """ Creates the uri that is needed for an integration method """
#        uri = "arn:aws:apigateway:"
#        uri += self.region
#        uri += ":lambda:path/2015-03-31/functions/"
#        uri += 
#        uri += "/invocations"
#        return uri
#        
#        
#    def create_api_permission_uri(self):
#        """ Creates the uri that is needed for giving the api deployment permission to trigger the lambda function """
#        uri = "arn:aws:execute-api:"
#        uri += self.region
#        uri += ":"
#        uri += self.get_account_id()
#        uri += ":"
#        uri += self.rest_api_id
#        uri += "/*/POST/"
#        return uri
#        
#        
#    def create_api_call_uri(self):
#        uri = "https://"
#        uri += self.apigateway.get_rest_api(
#            restApiId=self.rest_api_id
#        )["id"]
#        uri += ".execute-api.us-east-1.amazonaws.com/prod"
#        return uri
