"""
# menu.py
# Author: Adam Campbell
# Date: 30/08/2016
"""

import boto3
import botocore
import uuid
from response import Response
import json
from boto3.dynamodb.conditions import Attr, Key

class Menu(object):

    def __init__(self, event, context):
        self.event = event
        self.context = context
        with open("constants.json", "r") as constants_file:
            self.constants = json.loads(constants_file.read())

    """ Reads menu item data from dynamo """
    def get_menu_items(self):
        # Get all menu item data from dynamo
        try:
            dynamodb = boto3.client("dynamodb")
            data = dynamodb.scan(TableName=self.constants["MENU_TABLE"],
                                 ConsistentRead=True)
        except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            response = Response("Error", None)
            response.errorMessage = "Unable to get menu item data: %s" % (
                e.response["Error"]["Code"])
            return response.to_JSON()
        
        response = Response("Success", data["Items"])
        return response.to_JSON()

    """ Updates menu item data in dynamo """
    def set_menu_items(self):
        
        # Get menuitem data from request
        menu_data = self.event["menuitems"]

        # Wipe menu table clean
