"""
# user.py
# Author: Adam Campbell
# Date: 23/06/2016
# Edited: N/D        | Miguel Saavedra
#         02/08/2016 | Christopher Treadgold
#         05/08/2016 | Adam Campbell
#         07/08/2016 | Christopher Treadgold
#         21/08/2016 | Christopher Treadgold
#         10/09/2016 | Christopher Treadgold
"""

import Cookie
import datetime
import uuid

import boto3
import botocore
from passlib.hash import pbkdf2_sha256

class User(object):
    """ Provides functions for handling user related requests """
    HASH_ROUNDS = 10000 # The number of rounds to use for hashing passwords
    
    @staticmethod
    def login(email, password, user_table, token_table):
        """ Validates a user login request.
            Adds a token to the token table and provides it as a cookie in the
            response for use in future request validation.
        """
        # Use email to fetch user information from the user table
        try:
            dynamodb = boto3.client("dynamodb")
            user = dynamodb.get_item(TableName=user_table,
                                     Key={"Email": {"S": email}})
        except botocore.exceptions.ClientError as e:
            action = "Fetching user from the user table for login"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the email has a user associated with it
        if not "Item" in user:
            action = "Attempting to log in"
            return {"error": "InvalidEmail",
                    "data": {"email": email, "action": action}}
        
        # Check that the user has a password associated with it
        try:
            actual_password = user["Item"]["Password"]["S"]
        except KeyError:
            action = "Attempting to log in"
            return {"error": "userHasNoPassword",
                    "data": {"token": token, "action": action}}
        
        # Verify that the password provided is correct
        valid_password = pbkdf2_sha256.verify(password, actual_password)
        if not valid_password:
            action = "Attempting to log in"
            return {"error": "invalidPassword",
                    "data": {"password": password, "action": action}}
        
        # Calculate an exiration date a day from now
        expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        expiration = expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")
        # Generate a uuid for use as a token
        token = str(uuid.uuid4())
        
        # Add the generated token to the token table
        try:
            dynamodb.put_item(
                TableName=token_table,
                Item={"Token": {"S": token},
                      "UserEmail": {"S": email},
                      "Expiration": {"S": expiration}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting token in the token table for login"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Create the cookie that will be returned
        cookie = "token=%s; expires=%s" % (token, expiration)
        # Return the cookie
        return {"message": "Successfully logged in", "Set-Cookie": cookie}
    
    @staticmethod
    def logout(token, token_table):
        """ Logs out the user who made this request by removing their active
        token from the token table
        """
        try:
            dynamodb = boto3.client("dynamodb")
            delete_response = dynamodb.delete_item(
                TableName=token_table, Key={"Token": {"S": token}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Logging out user"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        return {"message": "Successfully logged out"}
    
    @staticmethod
    def get_all_users(user_table):
        """ Fetches all entries from the user table """
        try:
            dynamodb = boto3.client("dynamodb")
            users = dynamodb.scan(TableName=user_table, ConsistentRead=True)
        except botocore.exceptions.ClientError as e:
            action = "Getting all users"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the email has a user associated with it
        if not "Items" in users:
            action = "Fetching users from the user table"
            return {"error": "noUsers",
                    "data": {"action": action}}
        
        return {"message": "Successfully fetched users", "data": users["Items"]}
    
    @staticmethod
    def get_user(email, user_table):
        """ Fetches a user entry from the user table """
        try:
            dynamodb = boto3.client("dynamodb")
            user = dynamodb.get_item(TableName=user_table,
                                     Key={"Email": {"S": email}})
        except botocore.exceptions.ClientError as e:
            action = "Fetching user from the user table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the email has a user associated with it
        if not "Item" in user:
            action = "Fetching user from the user table"
            return {"error": "InvalidEmail",
                    "data": {"email": email, "action": action}}

        return {"message": "Successfully fetched user", "data": user["Item"]}

    @staticmethod
    def put_user(email, username, password, user_type, permissions, user_table):
        """ Puts a user in the user table """
        # Hash the password
        hashed_pass = pbkdf2_sha256.encrypt(password,
                                            rounds=User.HASH_ROUNDS)
        # Create the user entry
        user = {
            "Email": {"S": email},
            "Username": {"S": username},
            "Password": {"S": hashed_pass},
            "ID": {"S": str(uuid.uuid4())},
            "UserType": {"S": user_type},
            "Permissions": {"L": []}
        }
        for permission in permissions:
            user["Permissions"]["L"].append({"S": permission})
        
        # Put the user in the user table
        try:
            dynamodb = boto3.client("dynamodb")
            put_response = dynamodb.put_item(
                TableName=user_table, Item=user, ReturnConsumedCapacity="TOTAL"
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting user in the user table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        return {"message": "Successfully put user", "data": user}

    @staticmethod
    def delete_user(email, user_table):
        """ Deletes a user from the user table """
        try:
            dynamodb = boto3.client("dynamodb")
            delete_response = dynamodb.delete_item(
                TableName=user_table,
                Key={"Email": {"S": email}},
                ConditionExpression="attribute_exists(Email)"
            )
        except botocore.exceptions.ClientError as e:
            action = "Deleting user from the user table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        return {"message": "Successfully deleted user"}