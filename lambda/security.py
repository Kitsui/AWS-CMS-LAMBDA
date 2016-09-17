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
    def authenticate_and_authorize(token, request, token_table, user_table):
        """ Authenticates a token and checks that the associated user has the
        rights to be making a provided request.
        """
        # Get a dynamodb client object from boto3
        try:
            dynamodb = boto3.client('dynamodb')
        except botocore.exceptions.ClientError as e:
            action = "Getting dynamodb client"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Fetch token information from the token table
        try:
            token_info = dynamodb.get_item(TableName=token_table,
                                            Key={"Token": {"S": token}})
        except botocore.exceptions.ClientError as e:
            action = "Fetching token from the token table for authentication"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the token has an entry in the database associated with it
        if not "Item" in token_info:
            action = "Fetching token from the token table for authentication"
            return {"error": "invalidToken",
                    "data": {"token": token, "action": action}}
        
        # Checks if request is logoutUser as permission is not required
        if request == "logoutUser":
            return True
        
        # Check that the token has a user associated with it
        try:
            user_email = token_info["Item"]["UserEmail"]["S"]
        except KeyError:
            action = "Fetching token from the token table for authentication"
            return {"error": "tokenHasNoUser",
                    "data": {"token": token, "action": action}}
        
        # Query the user table for the user id extracted from the token table
        try:
            user_info = dynamodb.get_item(
                TableName=user_table,
                Key={"Email": {"S": user_email}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Querying the user table for authorization"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the user id has an enty in the database associated with it
        if not "Item" in user_info:
            action = "Fetching user from the user table for authorization"
            return {"error": "invalidUserEmail",
                    "data": {"user": user_email, "action": action}}
        
        # Check that the user has permissions attatched to it
        try:
            permissions = user_info["Item"]["Permissions"]["L"]
        except KeyError:
            action = "Fetching user from the user table for authorization"
            return {"error": "userHasNoPermissions",
                    "data": {"user": user_email, "action": action}}
        
        # Check that user has the appropriate permissions to make the request
        for permission in permissions:
            if permission["S"] == request or permission["S"] == "all":
                return True
            
        return {"error": "notAuthorizedForRequest",
                "data": {"user": user_email, "request": request}}