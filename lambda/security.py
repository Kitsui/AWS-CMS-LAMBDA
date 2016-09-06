"""
# security.py
# Author: Miguel Saavedra
# Date: 05/08/2016
"""

import boto3
import botocore
import uuid
import json
from boto3.dynamodb.conditions import Attr, Key

class Security(object):

    def __init__(self, event, context):
        self.event = event
        self.context = context
        with open("constants.json", "r") as constants_file:
            self.constants = json.loads(constants_file.read())

    """ function authenticates user """
    def authenticate(self):

        # Get user token
        token = self.event["token"]
        
        try:
            dynamodb = boto3.client('dynamodb')
            auth = dynamodb.query(
                TableName=self.constants["TOKEN_TABLE"],
                KeyConditionExpression="TokenString = :v1",
                ExpressionAttributeValues={
                    ":v1": {
                        "S": token
                    }
                }
            )
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            return response.to_JSON()
        if(len(auth['Items']) > 0):
            return True

        return False

    """ Evaluates role permissions of a user """
    def authorize(self):

        # Get user token
        token = self.event["token"]

        try:
            dynamodb = boto3.client('dynamodb')
            # Query token table for user id
            token_results = dynamodb.query(
                TableName=self.constants["TOKEN_TABLE"],
                KeyConditionExpression="TokenString = :v1",
                ExpressionAttributeValues={
                    ":v1": {
                        "S": token
                    }
                }
            )

            # extract user id
            if token_results["Count"] > 0:
                user_id = token_results["Items"][0]["UserID"]["S"]
            else:
                return False;

            # Query user table for role id
            user_results = dynamodb.query(
                TableName=self.constants["USER_TABLE"],
                KeyConditionExpression="ID = :v1",
                ExpressionAttributeValues={
                    ":v1": {
                        "S": user_id
                    }
                }
            )

            # extract role id
            if user_results["Count"] > 0:
                role_id = user_results["Items"][0]["Role"]["S"]
            else:
                return False

            # Query role table for role permissions
            role_results = dynamodb.query(
                TableName=self.constants["ROLE_TABLE"],
                KeyConditionExpression="RoleID = :v1",
                ExpressionAttributeValues={
                    ":v1": {
                        "S": role_id
                    }
                }
            )

            # extract role permissions
            if role_results["Count"] > 0:
                permissions = role_results["Items"][0]["Permissions"]["M"]
            else:
                return False

        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            return response.to_JSON()

        # Request to Permission mapping
        # TODO: Move somewhere more appropriate
        request_access = {
            "getBlogData": "Blog_CanRead",
            "getBlogs": "Blog_CanRead",
            "editBlog": "Blog_CanUpdate",
            "saveNewBlog": "Blog_CanCreate",
            "deleteSingleBlog": "Blog_CanDelete",
            "getUsers": "User_CanRead",
            "registerUser": "User_CanCreate",
            "editUser": "User_CanUpdate",
            "deleteUser": "User_CanDelete",
            "getRoles": "Role_CanRead",
            "createRole": "Role_CanCreate",
            "editRole": "Role_CanUpdate",
            "deleteRole": "Role_CanDelete",
            "getPages": "Page_CanRead",
            "createPage": "Page_CanCreate",
            "deletePage": "Page_CanDelete",
            "editPage": "Page_CanUpdate",
            "getSiteSettings": "Site_Settings_CanUpdate",
            "editSiteSettings": "Site_Settings_CanUpdate",
            "setSiteSettings": "Site_Settings_CanUpdate",
            "getMenuItems": "Menu_CanUpdate",
            "setMenuItems": "Menu_CanUpdate",
			"uploadImage": "Image_CanUpload"
        }

        # Eval POST request for access
        request = self.event["request"]
        form_type = ""
        if "getForm" in request:
            if "blog" in self.event["type"]:
                request = "saveNewBlog"
            elif "user" in self.event["type"]:
                request = "registerUser"
            elif "siteSettings" in self.event["type"]:
                request = "getSiteSettings"
            else:
                f_letter = self.event["type"][:1]
                form_type = self.event["type"].replace(f_letter, "")
                f_letter = f_letter.upper()
                request = "create"+f_letter+form_type


        has_access = permissions[request_access[request]]

        # return success/fail bitflag
        return has_access['N']
