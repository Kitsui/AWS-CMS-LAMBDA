"""
# menu.py
# Author: Adam Campbell
# Date: 30/08/2016
"""

import boto3
import botocore
import uuid
from boto3.dynamodb.conditions import Attr, Key

class Menu(object):

    def __init__(self, event):
        self.event = event
        with open("constants.json", "r") as constants_file:
            self.constants = json.loads(constants_file.read())

    """ Reads menu item data from dynamo """
    def get_menu_items(self):
        pass

    """ Updates menu item data in dynamo """
    def set_menu_items(self):
        pass
