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
    """ Provides a function for authentication and authorization of requests
    through a provided token.
    """

    @staticmethod
    def authenticate_and_authorize(token, request, token_table, user_table,
                                   role_table):
        """ Authenticates a token and checks that the associated user has the
        rights to be making a provided request.
        """
        # Get a dynamodb client object from boto3
        try:
            dynamodb = boto3.client('dynamodb')
        except botocore.exceptions.ClientError as e:
            action = "Getting dynamodb client instance in authenticate and authorize"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Fetch token information from the token table
        try:
            token_info = dynamodb.get_item(TableName=token_table,
                                            Key={"Token": {"S": token}})
        except botocore.exceptions.ClientError as e:
            action = "Fetching token from token table for authentication"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the token has an entry in the database associated with it
        if not "Item" in token_info:
            action = "Fetching token from token table for authentication"
            return {"error": "invalidToken",
                    "data": {"token": token, "action": action}}
        
        # Check that the token has a user associated with it
        try:
            user_email = token_info["Item"]["UserEmail"]["S"]
        except KeyError:
            action = "Fetching token from token table for authentication"
            return {"error": "tokenHasNoUser",
                    "data": {"token": token, "action": action}}
        
        # Query the user table for the user id extracted from the token table
        try:
            user_info = dynamodb.get_item(
                TableName=user_table,
                Key={"Email": {"S": user_email}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Querying user table for authorization"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the user id has an enty in the database associated with it
        if not "Item" in user_info:
            action = "Fetching user from user table for authorization"
            return {"error": "invalidUserEmail",
                    "data": {"user": user_email, "action": action}}
        
        # Check that the user has a role associated with it
        try:
            role_id = user_info["Item"]["Role"]["S"]
        except KeyError:
            action = "Fetching user from user table for authorization"
            return {"error": "userHasNoRole",
                    "data": {"user": user_email, "action": action}}
        
        # Query the role table for the role id extracted from the user table
        try:
            role_info = dynamodb.get_item(
                TableName=role_table,
                Key={"RoleID": {"S": role_id}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Fetching role from role table for authorization"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the role has an entry in the database associated with it
        if not "Item" in role_info:
            action = "Fetching role from role table for authorization"
            return {"error": "invalidRoleId",
                    "data": {"role": role_id, "action": action}}
        
        # Check that the role has permissions attatched to it
        try:
            permissions = role_info["Item"]["Permissions"]["L"]
        except KeyError:
            action = "Fetching role from role table for authorization"
            return {"error": "roleHasNoPermissions",
                    "data": {"user": user_email, "action": action}}
        
        # Check that user has the appropriate permissions to make the request
        for permission in permissions:
            if request == permission["S"]:
                return True
            
        return {"error": "unauthorizedRequest",
                "data": {"user": user_email, "request": request}}