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
        try:
            dynamodb = boto3.client('dynamodb')
            auth = dynamodb.query(
                TableName=self.constants["TOKEN_TABLE"],
                KeyConditionExpression="TokenString = :v1",
                ExpressionAttributeValues={
                    ":v1": {
                        "S": self.event["token"]
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