#!/usr/bin/python2.7

"""
# update_lambda.py
# Author: Christopher Treadgold
# Date: 09/08/2016
"""

import json
import os
import sys

import boto3


from cms_functions import AwsFunc

# Get installed cms'
if os.path.isfile("./installed.json"):
    with open("installed.json", "r") as installed_file:
        installed = json.loads(installed_file.read())
else:
    print "No cms' are installed, exiting"
    sys.exit()

# Ask the user which cms to update
print "Installed cms':"
for key in installed.keys():
    print "%s: %s" %(key, installed[key])
user_selection = str(input("Enter the number of the cms whose lambda "
                           "code you would like to update: "))
if user_selection not in installed.keys():
    print "Invalid selection, exiting."
    sys.exit()
else:
    constants_file_name = "%s-constants.json" % (installed[user_selection])
    with open(constants_file_name, "r") as const:
        constants = json.loads(const.read())

# Create the constants file in the lambda directory
with open("lambda/constants.json", "w") as constants_file:
    constants_file.write(json.dumps(constants, indent=4, sort_keys=True))

# Upload the function code to lambda
print "Uploading function code to lambda"
lambda_data = AwsFunc.zip_lambda()
try:
    lmda = boto3.client("lambda")
    lmda.update_function_code(
        FunctionName=constants["LAMBDA_FUNCTION"],
        ZipFile=lambda_data
    )
except botocore.exceptions.ClientError as e:
    print e.response["Error"]["Code"]
    print e.response["Error"]["Message"]
    sys.exit()
print "Done" 
print ("\a")

# Remove the constants file from the lambda directory
os.remove("lambda/constants.json")
