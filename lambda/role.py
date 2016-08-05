"""
# role.py
# Author: Adam Campbell
# Date: 05/08/2016
"""

import boto3
import botocore

class Role(object):

    def __init__(self, event, context):
        self.event = event
        self.context = context

	# def get_all_roles(self):
	# 	# Attempt to get all data from table
	# 	try:
	# 		dynamodb = boto3.client('dynamodb')
	# 		data = dynamodb.scan(
	# 			TableName="Role",
	# 			ConsistentRead=True)
	# 	except botocore.exceptions.ClientError as e:
	# 		print e.response['Error']['Code']
	# 		response = Response("Error", None)
	# 		response.errorMessage = "Unable to get user data: %s" % e.response['Error']['Code']
	# 		return response.to_JSON()
		
	# 	response = Response("Success", data)
	# 	# response.setData = data
	# 	return response.format()

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
            "Page_CanUpdate": {"N" : self.event["role"]["permissions"]["page_canUpdate"]}
            }}
        }
        try:
            dynamodb = boto3.client('dynamodb')
            dynamodb.put_item(
                TableName='Role',
                Item=role_params,
                ReturnConsumedCapacity='TOTAL'
            )
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to create role: %s" % e.response['Error']['Code']
            return response.to_JSON()

        return Response("Success", None).to_JSON()

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
            "Page_CanUpdate": {"N" : self.event["role"]["permissions"]["page_canUpdate"]}
        }
        try:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('Role')
            table.update_item(
                Key={
                    'RoleID': roleID, 
                    'RoleType': roleType
                }, 
                UpdateExpression='SET RoleName = :r, UserPermissions = :p', 
                ExpressionAttributeValues={ ':r': roleName,  ':p': permissions}
                )
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to edit role: %s" % e.response['Error']['Code']
            return response.to_JSON()

        return Response("Success", None).to_JSON()

    def delete_role(self):
        roleID = self.event["role"]["roleID"]
        try:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('Role')
            table.delete_item(
                Key={
                    'RoleID': roleID
                    }
                )
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to delete role: %s" % e.response['Error']['Code']
            return response.to_JSON()

        return Response("Success", None).to_JSON()