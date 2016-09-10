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

    @staticmethod
    def login(email, password, user_table, token_table):
        try:
            dynamodb = boto3.client('dynamodb')
            result = dynamodb.query(
                TableName=user_table,
                KeyConditionExpression="Email = :v1",
                ExpressionAttributeValues={":v1": {"S": email}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Querying user table for login"
            return {"error": e.response["error"]["code"],
                    "data": {"exception": str(e), "action": action}}
        
        users_found = len(result["Items"])
        if users_found <= 0:
            action = "Attempting to log in"
            return {"error": "Invalid email",
                    "data": {"email": email, "action": action}}

        stored_password = result["Items"][0]["Password"]["S"]
        if(pbkdf2_sha256.verify(password, stored_password)):
            # Calculate an exiration date a day from now
            expiration = datetime.datetime.now() + datetime.timedelta(days=1)
            expiration = expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")
            
            # Generate a uuid for use as a token
            token = str(uuid.uuid4())
            
            # Add the token to the token table
            result = dynamodb.put_item(
                TableName=token_table,
                Item={'Token': {"S": token},
                      'UserEmail': {"S": result["Items"][0]["Email"]["S"]},
                      'Expiration': {"S": expiration}}
            )
            
            # Create the cookie that will be returned
            cookie = "token=%s; expires=%s" % (token, expiration)
            
            # Return the cookie
            return {"Set-Cookie": cookie}
        else:
            action = "Attempting to log in"
            return {"error": "invalidPassword",
                    "data": {"password": password, "action": action}}
    
    
#    def get_all_users(self):
#        """ function returns all user records frmo dynamo """
#        try:
#            dynamodb = boto3.client('dynamodb')
#            data = dynamodb.scan(TableName=self.constants["USER_TABLE"],
#                                 ConsistentRead=True)
#        except botocore.exceptions.ClientError as e:
#            print e.response['Error']['Code']
#            response = Response("Error", None)
#            response.errorMessage = "Unable to get user data: %s" % (
#                e.response['Error']['Code'])
#            return response.to_JSON()

#        response = Response("Success", data)
#        # format for table response to admin dash
#        # return response.format("All Users")
#        return data

#    """ function gets a user record from dynamo """
#    def get_user_data(self):
#        """ Gets user data from dynamoDB """
#        user_id = self.event["user"]["userID"]
#        try:
#            dynamodb = boto3.client("dynamodb")
#            user_data = dynamodb.query(
#                TableName=self.constants["USER_TABLE"],
#                KeyConditionExpression="ID = :v1",
#                ExpressionAttributeValues={
#                    ":v1": {
#                        "S": user_id
#                    }
#                }
#            )
#        except botocore.exceptions.ClientError as e:
#            print e.response["Error"]["Code"]
#            response = Response("Error", None)
#            response.errorMessage = "Unable to get user data: %s" % (
#                e.response["Error"]["Code"])
#            return response.to_JSON()

#        return user_data


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
