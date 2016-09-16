"""
# upload_image.py
# Author: Christopher Treadgold
# Edited: 16/09/2016 | Christopher Treadgold
"""

import boto3
import botocore

class S3Upload(object):
    """ Provides functions for generating presigned S3 post data """
    
    @staticmethod
    def get_presigned_post_image(filename, acl, bucket):
        """ Generates a presigned post for uploading images to S3 """
        try:
            s3 = boto3.client("s3")
            presigned_post = s3.generate_presigned_post(
                bucket, "Images/%s" % filename, Fields={"acl": acl},
                ExpiresIn=60, Conditions=[
                    {"acl": acl},
                    ["content-length-range", 0, 8920000],
                    ["starts-with", "$Content-Type", "image/"]
                ]
            )
        except botocore.exceptions.ClientError as e:
            action = "Getting presigned post for image upload"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
    
        return presigned_post