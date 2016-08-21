#!/usr/bin/python2.7

"""
# remove.py
# Author: Christopher Treadgold
# Date: N/D
# Edited: 07/08/2016 | Christopher Treadgold
"""

import json
import os
import sys

import boto3
from passlib.hash import pbkdf2_sha256

dynamodb = boto3.client('dynamodb')

# Get installed cms'
if os.path.isfile("./installed.json"):
    with open("installed.json", "r") as installed_file:
        installed = json.loads(installed_file.read())
else:
    print "No cms' are installed, exiting"
    sys.exit()

# Ask which cms to remove
print "Installed cms':"
for key in installed.keys():
    print "%s: %s" %(key, installed[key])
cms_selection = str(raw_input("Select a CMS by number: "))
if cms_selection not in installed.keys():
    print "Invalid selection, exiting."
    sys.exit()
else:
    constants_file_name = "%s-constants.json" % (installed[cms_selection])
    with open(constants_file_name, "r") as const:
        constants = json.loads(const.read())

# Ask which users password to reset
user_data = dynamodb.scan(
    TableName=constants["USER_TABLE"],
    ProjectionExpression="ID, Email, Username"
)
users = []
for item in user_data["Items"]:
    user = {
        "ID": item["ID"]["S"],
        "Email": item["Email"]["S"],
        "Username": item["Username"]["S"]
    }
    users.append(user)
    print "%s: %s, %s, %s" % (len(users), user["Username"], user["Email"], user["ID"])
user_selection = str(input("Select a user whose password you would like to reset: "))
if user_selection not in str(range(1, len(users) + 1)):
    print "Invalid selection, exiting."
    sys.exit()
user_selection = int(user_selection) - 1
selected_user = users[user_selection]

# Ask for the new password
new_password = str(raw_input("Enter new password: "))
if len(new_password) <= 0:
    print "No password entered, exiting."
    sys.exit()
new_password = pbkdf2_sha256.encrypt(new_password, rounds=20000)

# Update the user with the new password
dynamodb.update_item(
    TableName=constants["USER_TABLE"],
    Key={
        "ID": {"S": selected_user["ID"]},
        "Email": {"S": selected_user["Email"]}
    },
    UpdateExpression="set Password=:value1",
    ExpressionAttributeValues={
        ":value1": {"S": new_password}
    }
)
