"""
# sitesettings.py
# Author: Adam Campbell
# Date: 17/07/2016
"""

import datetime
import json
import uuid

import boto3
import botocore

class Site_Settings(object):
    """ Provides functions for handling SiteSettings related requests """
    
    @staticmethod
    def get_all_settings():
        pass

    @staticmethod
    def put_settings():
        pass

    @staticmethod
    def get_nav_items(bucket):
        """ Reads the visitor navigation items from site settings JSON """
        # Get site setting JSON
        site_settings = read_site_settings(bucket)
        # Get nav item JSON
        nav_items = site_settings["nav"]
        # Return nav item data
        return nav_items

    @staticmethod
    def put_nav_items(nav_items, bucket):
        """ Puts updated visitor navigation items into site settings """
        # Get site setting JSON
        site_settings = json.loads(read_site_settings(bucket))
        # Set nav items
        site_settings["nav"] = nav_items
        # Save site setting JSON
        save_site_settings(site_settings, bucket)

    @staticmethod
    def read_site_settings(bucket):
        """ Reads the site settings JSON from an S3 Bucket """
        pass

    @staticmethod
    def save_site_settings(site_settings, bucket):
        """ Saves site settings to an S3 Bucket """
        # Save site settings to s3
        try:
            s3 = boto3.client("s3")
            s3.put_object(
                Bucket=bucket, ACL="public-read", Body=json.dumps(site_settings),
                Key=("Content/site_settings.json"),
                ContentType="application/json"
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting site settings in the bucket"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

