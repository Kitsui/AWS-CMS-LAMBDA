"""
# role.py
# Author: Adam Campbell & Miguel Saavedra
# Date: 05/08/2016
"""

import boto3
import botocore
import uuid
import json
from boto3.dynamodb.conditions import Attr, Key

from response import Response
from ui import UI

class Role(object):

    def __init__(self, event, context):
        self.event = event
        self.context = context
        with open("constants.json", "r") as constants_file:
            self.constants = json.loads(constants_file.read())

    """ function returns all the role records from dynamo """
    # Dictionary entry will not work with format code
    def get_all_roles(self):
        # Attempt to get all data from table
        try:
            dynamodb = boto3.client('dynamodb')
            data = dynamodb.scan(
                TableName=self.constants["ROLE_TABLE"],
                ConsistentRead=True)
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to get user data: %s" % e.response['Error']['Code']
            return response.to_JSON()

        # Loop through items and replace permissions with stringified permissions
        for item in data["Items"]:
            # get permissions dictionary
            permissions = item.get("Permissions")["M"]
            p_item = {}
            # loop though to remove N from dictionary values
            for p_key, p_value in permissions.iteritems():
                p_item[p_key] = p_value["N"]

            new_permissions = {}
            # Format as a json string type key pair
            new_permissions["S"] = p_item
            # Add new permissions to data
            item["Permissions"] = new_permissions
        response = Response("Success", data)
        return data

    """ function gets a role record from dynamo """
    def get_role_data(self):
        """ Gets role data from dynamoDB """
        role_id = self.event["role"]["roleID"]
        try:
            dynamodb = boto3.client("dynamodb")
            role_data = dynamodb.query(
                TableName=self.constants["ROLE_TABLE"],
                KeyConditionExpression="RoleID = :v1",
                ExpressionAttributeValues={
                    ":v1": {
                        "S": role_id
                    }
                }
            )
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            response = Response("Error", None)
            response.errorMessage = "Unable to get page data: %s" % (
                e.response["Error"]["Code"])
            return response.to_JSON()

        return role_data


    """ function adds a role to dynamo """
    def create_role(self):
        role_params = {
        "RoleName": {"S" : self.event["role"]["name"]},
        "RoleType": {"S" : self.event["role"]["type"]},
        "RoleID": {"S" : str(uuid.uuid4())},
        "Permissions": { "M" :{
            "Blog_CanCreate": {"N" : self.event["role"]["permissions"]["blog_canCreate"]},
            "Blog_CanDelete": {"N" : self.event["role"]["permissions"]["blog_canDelete"]},
            "Blog_CanRead": {"N" : self.event["role"]["permissions"]["blog_canRead"]},
            "Blog_CanUpdate": {"N" : self.event["role"]["permissions"]["blog_canUpdate"]},
            "User_CanCreate": {"N" : self.event["role"]["permissions"]["user_canCreate"]},
            "User_CanDelete": {"N" : self.event["role"]["permissions"]["user_canDelete"]},
            "User_CanRead": {"N" : self.event["role"]["permissions"]["user_canRead"]},
            "User_CanUpdate": {"N" : self.event["role"]["permissions"]["user_canUpdate"]},
            "Page_CanCreate": {"N" : self.event["role"]["permissions"]["page_canCreate"]},
            "Page_CanDelete": {"N" : self.event["role"]["permissions"]["page_canDelete"]},
            "Page_CanRead": {"N" : self.event["role"]["permissions"]["page_canRead"]},
            "Page_CanUpdate": {"N" : self.event["role"]["permissions"]["page_canUpdate"]},
            "Site_Settings_CanUpdate": {"N" : self.event["role"]["permissions"]["site_Settings_CanUpdate"]},
            "Menu_CanUpdate": {"N" : self.event["role"]["permissions"]["menu_canUpdate"]}
            }}
        }

        try:
            dynamodb = boto3.client('dynamodb')
            dynamodb.put_item(
                TableName=self.constants["ROLE_TABLE"],
                Item=role_params,
                ReturnConsumedCapacity='TOTAL'
            )
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to create role: %s" % e.response['Error']['Code']
            return response.to_JSON()

        return Response("Success", None).to_JSON()


    """ function edits a role record in dynamo """
    def edit_role(self):
        roleName = self.event["role"]["name"]
        roleID = self.event["role"]["roleID"]
        roleType = self.event["role"]["type"]
        permissions = {
            "Blog_CanCreate": {"N" : self.event["role"]["permissions"]["blog_canCreate"]},
            "Blog_CanDelete": {"N" : self.event["role"]["permissions"]["blog_canDelete"]},
            "Blog_CanRead": {"N" : self.event["role"]["permissions"]["blog_canRead"]},
            "Blog_CanUpdate": {"N" : self.event["role"]["permissions"]["blog_canUpdate"]},
            "User_CanCreate": {"N" : self.event["role"]["permissions"]["user_canCreate"]},
            "User_CanDelete": {"N" : self.event["role"]["permissions"]["user_canDelete"]},
            "User_CanRead": {"N" : self.event["role"]["permissions"]["user_canRead"]},
            "User_CanUpdate": {"N" : self.event["role"]["permissions"]["user_canUpdate"]},
            "Page_CanDelete": {"N" : self.event["role"]["permissions"]["page_canDelete"]},
            "Page_CanCreate": {"N" : self.event["role"]["permissions"]["page_canCreate"]},
            "Page_CanRead": {"N" : self.event["role"]["permissions"]["page_canRead"]},
            "Page_CanUpdate": {"N" : self.event["role"]["permissions"]["page_canUpdate"]},
            "Site_Settings_CanUpdate": {"N" : self.event["role"]["permissions"]["site_Settings_CanUpdate"]},
            "Menu_CanUpdate": {"N" : self.event["role"]["permissions"]["menu_canUpdate"]}
        }

        try:
            dynamodb = boto3.client('dynamodb')
            # Update item from dynamo
            dynamodb.update_item(
                TableName=self.constants["ROLE_TABLE"],
                Key={
                    'RoleID': {"S": roleID},
                    'RoleType': {"S": roleType}
                },
                UpdateExpression='SET RoleName = :r, #pm = :p',
                ExpressionAttributeNames={
                    "#pm": "Permissions"
                },
                ExpressionAttributeValues={
                    ':r': {"S": roleName},
                    ':p': {"M": permissions}
                }
            )
        except botocore.exceptions.ClientError as e:
            print e
            response = Response("Error", None)
            response.errorMessage = "Unable to edit role: %s" % (
                e.response['Error']['Code'])
            return response.to_JSON()

        return Response("Success", None).to_JSON()


    """ function deletes a role in dynamo """
    def delete_role(self):
        roleID = self.event["role"]["roleID"]
        roleType = self.event["role"]["type"]
        # delete item from dynamo
        try:
            dynamodb = boto3.client('dynamodb')
            dynamodb.delete_item(TableName=self.constants["ROLE_TABLE"],
                                 Key={
                                    'RoleID': {"S": roleID},
                                    'RoleType': {"S": roleType}
                                })
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to delete role: %s" % e.response['Error']['Code']
            return response.to_JSON()

        return Response("Success", None).to_JSON()
