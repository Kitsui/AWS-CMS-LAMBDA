"""
# upload_image.py
# Author: Christopher Treadgold
# Date: 22/08/2016
"""

import json

import boto3

class UploadImage(object):
    
    def __init__(self, event, context):
        self.event = event
        self.context = context
        with open("constants.json", "r") as constants_file:
            self.constants = json.loads(constants_file.read())
    
    def get_url(self):
        try:
            s3 = boto3.client("s3")
            return s3.generate_presigned_post(
                self.constants["BUCKET"],
                "Images/%s" % self.event["fileName"],
                Fields={
                    "acl": self.event["acl"]
                },
                Conditions=[
                    {"acl": self.event["acl"]},
                    ["content-length-range", 0, 8920000],
                    ["starts-with", "$Content-Type", "image/"]
                ],
                ExpiresIn=60
            )
        except botocore.exceptions.ClientError as e:
            print e
            response = Response("Error", None)
            response.errorMessage = e
            return response.to_JSON()
