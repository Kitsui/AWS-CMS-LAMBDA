"""
# security.py
# Author: Miguel Saavedra
# Date: 05/08/2016
# Edited: 10/09/2016 | Christopher Treadgold
"""

import uuid

import boto3
import botocore

class Security(object):

    @staticmethod
    def authenticate_and_authorize(token, request, token_table, user_table,
                                   role_table):
        """ Authenticates a token and checks that the associated user has the
        rights to be making a provided request
        """
        # Get a dynamodb client instance from boto3
        try:
            dynamodb = boto3.client('dynamodb')
        except botocore.exceptions.ClientError as e:
            action = "Getting dynamodb client instance in authenticate and authorize"
            return {"error": e.response["error"]["code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Query the token table for the provided token
        try:
            token_query = dynamodb.query(
                TableName=token_table,
                KeyConditionExpression="TokenString = :v1",
                ExpressionAttributeValues={":v1": {"S": token}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Querying token table for authentication"
            return {"error": e.response["error"]["code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the token has an entry in the database associated with it
        matching_tokens = len(token_query["Items"])
        if matching_tokens <= 0:
            action = "Querying token table for authentication"
            return {"error": "invalidToken",
                    "data": {"token": token, "action": action}}
        
        # Check that the token has a user associated with it
        try:
            user_email = token_query["Items"][0]["UserEmail"]["S"]
        except KeyError:
            action = "Querying token table for authentication"
            return {"error": "tokenHasNoUser",
                    "data": {"token": token, "action": action}}
        
        # Query the user table for the user id extracted from the token table
        try:
            user_query = dynamodb.query(
                TableName=user_table,
                KeyConditionExpression="ID = :v1",
                ExpressionAttributeValues={":v1": {"S": user_email}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Querying user table for authorization"
            return {"error": e.response["error"]["code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the user id has an enty in the database associated with it
        matching_users = len(user_query["Items"])
        if matching_users <= 0:
            action = "Querying user table for authorization"
            return {"error": "invalidUserEmail",
                    "data": {"user": user_email, "action": action}}
        
        # Check that the user has a role associated with it
        try:
            role_id = user_query["Items"][0]["Role"]["S"]
        except KeyError:
            action = "Querying user table for authorization"
            return {"error": "userHasNoRole",
                    "data": {"user": user_email, "action": action}}
        
        # Query the role table for the role id extracted from the user table
        try:
            role_query = dynamodb.query(
                TableName=role_table,
                KeyConditionExpression="RoleID = :v1",
                ExpressionAttributeValues={":v1": {"S": role_id}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Querying role table for authorization"
            return {"error": e.response["error"]["code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the role has an entry in the database associated with it
        matching_roles = len(role_query["Items"])
        if matching_roles <= 0:
            action = "Querying role table for authorization"
            return {"error": "invalidRoleId",
                    "data": {"role": role_id, "action": action}}
        
        # Check that the role has permissions attatched to it
        try:
            permissions = role_results["Items"][0]["Permissions"]["L"]
        except KeyError:
            action = "Querying role table for authorization"
            return {"error": "roleHasNoPermissions",
                    "data": {"user": user_email, "action": action}}
        
        # Check that user has the appropriate permissions to make the request
        for permission in permissions:
            if permission == request:
                return True
            
        return {"error": "unauthorizedRequest",
                "data": {"user": user_email, "request": request}}
