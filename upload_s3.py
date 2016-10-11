#!/usr/bin/python2.7


"""
# upload.py
# Author: Miguel Saavedra
# Date: 10/10/2016
"""
# upload selected file

import json
import os
import sys
import mimetypes

import boto3


from cms_functions import AwsFunc

def print_help():
    print """ 
Help :
[Upload-File] : python upload_s3.py [location-in-s3] [location-of-local-file-to-upload]

[Upload-Website-File] python upload_s3.py [location-of-local-file-to-upload]
"""

if (str(sys.argv[1]) == "--help"):
    print_help()
    sys.exit()

# Get file local location and destination
if (str(sys.argv[1]) == "1"): # Default website deployment
    path = "website/"+str(sys.argv[2])
    fileKey = str(sys.argv[2])
else: # Manual path selection
    path = str(sys.argv[1])
    fileKey = str(sys.argv[2])

print "Uploading ::" + path + " to Location in s3 ::" + fileKey

# Get installed cms'
if os.path.isfile("./installed.json"):
    with open("installed.json", "r") as installed_file:
        installed = json.loads(installed_file.read())
else:
    print "No cms' are installed, exiting"
    print_help()
    sys.exit()

# Ask the user which cms to update
print "Installed cms':"
for key in installed.keys():
    print "%s: %s" %(key, installed[key])
user_selection = str(input("Enter the number of the cms whose lambda "
                           "code you would like to update: "))
if user_selection not in installed.keys():
    print "Invalid selection, exiting."
    print_help()
    sys.exit()
else:
    # Get Constants value according to the CMS
    constants_file_name = "%s-constants.json" % (installed[user_selection])
    with open(constants_file_name, "r") as const:
        constants = json.loads(const.read())


""" Uploads a file to s3 """
# Prepare argument variables
bucket_name = constants["BUCKET"]
put_kwargs = {}
mime = mimetypes.guess_type(path)
if mime[0] != None:
    put_kwargs["ContentType"] = mime[0]
if mime[1] != None:
    put_kwargs["ContentEncoding"] = mime[1]

# Store file data and make replacements to files with certain mimetypes
with open(path, "rb") as file_body:
    body = file_body.read()
put_kwargs.update({
    "Bucket": bucket_name,
    "ACL": "public-read",
    "Body": body,
    "Key": fileKey
})

# Upload file to s3
try:
    print "Uploading: " + fileKey
    s3 = boto3.client("s3")
    s3.put_object(**put_kwargs)
    print "Completed upload"
except botocore.exceptions.ClientError as e:
    print e.response["Error"]["Code"]
    print e.response["Error"]["Message"]
    print_help()
    sys.exit()


# run this python update.py [location-in-s3] [location of file to upload]


print "Done" 
# alert user finished
print ("\a")

