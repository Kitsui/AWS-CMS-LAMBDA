"""
# user.py
# Author: Adam Campbell
# Date: 23/06/2016
# Edited: N/D        | Miguel Saavedra
#         02/08/2016 | Christopher Treadgold
#         05/08/2016 | Adam Campbell
#         07/08/2016 | Christopher Treadgold
#         21/08/2016 | Christopher Treadgold
"""

import Cookie
import datetime
import json
import uuid

import boto3
import botocore
from boto3.dynamodb.conditions import Attr, Key
from passlib.hash import pbkdf2_sha256

from response import Response

class User(object):

    def __init__(self, event, context):
        self.hash_rounds = 10000
        self.event = event
        self.context = context
        with open("constants.json", "r") as constants_file:
            self.constants = json.loads(constants_file.read())


    """ function returns all user records frmo dynamo """
    def get_all_users(self):
        # Attempt to get all data from table
        try:
            dynamodb = boto3.client('dynamodb')
            data = dynamodb.scan(TableName=self.constants["USER_TABLE"],
                                 ConsistentRead=True)
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to get user data: %s" % (
                e.response['Error']['Code'])
            return response.to_JSON()

        response = Response("Success", data)
        # format for table response to admin dash
        # return response.format("All Users")
        return data

    """ function gets a user record from dynamo """
    def get_user_data(self):
        """ Gets user data from dynamoDB """
        user_id = self.event["user"]["userID"]
        try:
            dynamodb = boto3.client("dynamodb")
            user_data = dynamodb.query(
                TableName=self.constants["USER_TABLE"],
                KeyConditionExpression="ID = :v1",
                ExpressionAttributeValues={
                    ":v1": {
                        "S": user_id
                    }
                }
            )
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            response = Response("Error", None)
            response.errorMessage = "Unable to get user data: %s" % (
                e.response["Error"]["Code"])
            return response.to_JSON()

        return user_data


    """ function adds a user record to dynamo """
    def register(self):
        # Get password for hashing
        password = self.event["user"]["password"]
        hashed = pbkdf2_sha256.encrypt(password, rounds=self.hash_rounds)
        # Get user register params
        register_params = {
            "ID": {"S": str(uuid.uuid4())},
            "Username": {"S": self.event["user"]["username"]},
            "Email": {"S": self.event["user"]["email"]},
            "Password": {"S": hashed},
            "Role": {"S": "c104ea59-7deb-4ae4-8418-225d8f4f42cd"}
        }

        # Attempt to add to dynamo
        try:
            dynamodb = boto3.client('dynamodb')
            dynamodb.put_item(
                TableName=self.constants["USER_TABLE"],
                Item=register_params,
                ReturnConsumedCapacity='TOTAL'
            )
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error")
            response.errorMessage = "Unable to register new user: %s" % (
                e.response['Error']['Code'])
            return response.to_JSON()

        return Response("Success", None).to_JSON()


    """ function deletes a user record from dynamo """
    def delete_user(self):
        userID = self.event["user"]["userID"]
        email = self.event["user"]["email"]
        try:
            dynamodb = boto3.client('dynamodb')
            dynamodb.delete_item(
                TableName=self.constants["USER_TABLE"],
                Key={
                    'ID': {"S": userID},
                    'Email': {"S": email}
                }
            )
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to delete role: %s" % e.response['Error']['Code']
            return response.to_JSON()

        return Response("Success", None).to_JSON()


    """ function edits a user record form dynamo """
    def edit_user(self):
        email = self.event["user"]["email"]
        userID = self.event["user"]["userID"]
        newUsername = self.event["user"]["newUsername"]
        newRoles = self.event["user"]["newRoles"]
        newPassword = self.event["user"]["newPassword"]

        try:
            dynamodb = boto3.client('dynamodb')
            dynamodb.update_item(
                TableName=self.constants["USER_TABLE"],
                Key={
                    'ID': {"S": userID},
                    'Email': {"S": email}
                },
                UpdateExpression='SET Username = :u, UserRoles = :r, Password = :p',
                ExpressionAttributeValues={
                    ':u': {"S": newUsername},
                    ':r': {"S": newRoles},
                    ':p': {"S": newPassword}
                }
            )
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to edit user: %s" % e.response['Error']['Code']
            return response.to_JSON()

        return Response("Success", None).to_JSON()


    """ function returns if a record exists with username
    and password matching the event input, then adds a token
    in dynamo which is returned back to the user """
    def login(self):
        try:
            dynamodb = boto3.client('dynamodb')
            result = dynamodb.query(
                TableName=self.constants["USER_TABLE"],
                IndexName='Email',
                KeyConditionExpression="Email = :v1",
                ExpressionAttributeValues={
                    ":v1": {
                        "S": self.event["User"]["Email"]
                    }
                }
            )

            password_guess = self.event["User"]["Password"]
            password = result["Items"][0]["Password"]["S"]
            if(pbkdf2_sha256.verify(password_guess, password)):
                expiration = datetime.datetime.now() + datetime.timedelta(days=14)
                token = str(uuid.uuid4())
                result = dynamodb.put_item(
                    TableName=self.constants["TOKEN_TABLE"],
                    Item={'TokenString': {"S": token},
                          'UserID': {"S": result["Items"][0]["ID"]["S"]},
                          'Expiration': {
                            "S": expiration.strftime(
                                "%a, %d-%b-%Y %H:%M:%S PST")
                          }
                    }
                )
                cookie = Cookie.SimpleCookie()
                cookie["token"] = token
                cookie["token"]["path"] = "/"
                cookie["token"]["expires"] = expiration.strftime(
                    "%a, %d-%b-%Y %H:%M:%S PST")

                return {"Cookie": cookie.output(header="").lstrip(),
                        "Response": Response("Success", None).to_JSON()}
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to log in: %s" % e.response['Error']['Code']
            return response.to_JSON()

        response = Response("Error", None)
        return response.to_JSON()


    """ function deletes a token record from dynamo"""
    def logout(self):
        # get user credentials
        token = self.event['tokenString']
        user = self.event['userID']

        try:
            # remove token from user
            dynamodb = boto3.client('dynamodb')
            response = table.delete_item(
                TableName=self.constants["TOKEN_TABLE"],
                Key={
                    'TokenString': {"S": token},
                    'UserID': {"S": user}
                }
            )
        except botocore.exceptions.ClientError as e:
            print e.response['Error']['Code']
            response = Response("Error", None)
            response.errorMessage = "Unable to log out: %s" % e.response['Error']['Code']
            return response.to_JSON()

        return Response("Success", None).to_JSON()
