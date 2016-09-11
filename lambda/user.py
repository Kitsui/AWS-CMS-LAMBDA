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
import json
import uuid

import boto3
import botocore
from passlib.hash import pbkdf2_sha256

class User(object):
    """ Provides functions for handling user based requests """

    @staticmethod
    def login(email, password, user_table, token_table):
        """ Validates user login request. Adds a token to the token table 
            and provides it in the response for future requests.
        """
        # Use email to fetch user information from the user table
        try:
            dynamodb = boto3.client('dynamodb')
            user = dynamodb.get_item(TableName=user_table,
                                     Key={"Email": {"S": email}})
        except botocore.exceptions.ClientError as e:
            action = "Fetching user from user table for login"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the email has a user in the database associated with it
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
                Item={'Token': {"S": token},
                      'UserEmail': {"S": email},
                      'Expiration': {"S": expiration}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting token in token table for login"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Create the cookie that will be returned
        cookie = "token=%s; expires=%s" % (token, expiration)
        
        # Return the cookie
        return {"Set-Cookie": cookie}
    
    @staticmethod
    def get_all_users(user_table):
        """ Fetches all entries from user table """
        try:
            dynamodb = boto3.client('dynamodb')
            users = dynamodb.scan(TableName=user_table, ConsistentRead=True)
        except botocore.exceptions.ClientError as e:
            action = "Getting all users"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        return users
    
    @staticmethod
    def get_user(email, user_table):
        """ Fetches user entry associated with the provided email """
        try:
            dynamodb = boto3.client("dynamodb")
            user = dynamodb.get_item(TableName=user_table,
                                     Key={"Email": {"S": email}})
        except botocore.exceptions.ClientError as e:
            action = "Fetching user from user table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the email has a user in the database associated with it
        if not "Item" in user:
            action = "Fetching user from user table"
            return {"error": "InvalidEmail",
                    "data": {"email": email, "action": action}}

        return user


#    """ function adds a user record to dynamo """
#    def register(self):
#        # Get password for hashing
#        password = self.event["user"]["password"]
#        hashed = pbkdf2_sha256.encrypt(password, rounds=self.hash_rounds)
#        # Get user register params
#        register_params = {
#            "ID": {"S": str(uuid.uuid4())},
#            "Username": {"S": self.event["user"]["username"]},
#            "Email": {"S": self.event["user"]["email"]},
#            "Password": {"S": hashed},
#            "Role": {"S": "c104ea59-7deb-4ae4-8418-225d8f4f42cd"}
#        }

#        # Attempt to add to dynamo
#        try:
#            dynamodb = boto3.client('dynamodb')
#            dynamodb.put_item(
#                TableName=self.constants["USER_TABLE"],
#                Item=register_params,
#                ReturnConsumedCapacity='TOTAL'
#            )
#        except botocore.exceptions.ClientError as e:
#            print e.response['Error']['Code']
#            response = Response("Error")
#            response.errorMessage = "Unable to register new user: %s" % (
#                e.response['Error']['Code'])
#            return response.to_JSON()

#        return Response("Success", None).to_JSON()


#    """ function deletes a user record from dynamo """
#    def delete_user(self):
#        userID = self.event["user"]["userID"]
#        email = self.event["user"]["email"]
#        try:
#            dynamodb = boto3.client('dynamodb')
#            dynamodb.delete_item(
#                TableName=self.constants["USER_TABLE"],
#                Key={
#                    'ID': {"S": userID},
#                    'Email': {"S": email}
#                }
#            )
#        except botocore.exceptions.ClientError as e:
#            print e.response['Error']['Code']
#            response = Response("Error", None)
#            response.errorMessage = "Unable to delete role: %s" % e.response['Error']['Code']
#            return response.to_JSON()

#        return Response("Success", None).to_JSON()


#    """ function edits a user record form dynamo """
#    def edit_user(self):
#        email = self.event["user"]["email"]
#        userID = self.event["user"]["userID"]
#        newUsername = self.event["user"]["newUsername"]
#        newRoles = self.event["user"]["newRoles"]
#        newPassword = self.event["user"]["newPassword"]

#        try:
#            dynamodb = boto3.client('dynamodb')
#            dynamodb.update_item(
#                TableName=self.constants["USER_TABLE"],
#                Key={
#                    'ID': {"S": userID},
#                    'Email': {"S": email}
#                },
#                UpdateExpression='SET Username = :u, UserRoles = :r, Password = :p',
#                ExpressionAttributeValues={
#                    ':u': {"S": newUsername},
#                    ':r': {"S": newRoles},
#                    ':p': {"S": newPassword}
#                }
#            )
#        except botocore.exceptions.ClientError as e:
#            print e.response['Error']['Code']
#            response = Response("Error", None)
#            response.errorMessage = "Unable to edit user: %s" % e.response['Error']['Code']
#            return response.to_JSON()

#        return Response("Success", None).to_JSON()


#    """ function deletes a token record from dynamo"""
#    def logout(self):
#        # get user credentials
#        token = self.event['tokenString']
#        user = self.event['userID']

#        try:
#            # remove token from user
#            dynamodb = boto3.client('dynamodb')
#            response = table.delete_item(
#                TableName=self.constants["TOKEN_TABLE"],
#                Key={
#                    'TokenString': {"S": token},
#                    'UserID': {"S": user}
#                }
#            )
#        except botocore.exceptions.ClientError as e:
#            print e.response['Error']['Code']
#            response = Response("Error", None)
#            response.errorMessage = "Unable to log out: %s" % e.response['Error']['Code']
#            return response.to_JSON()

#        return Response("Success", None).to_JSON()
