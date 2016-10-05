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

class SiteSettings(object):
    """ Provides functions for handling SiteSettings related requests """
    
    @staticmethod
    def get_all_settings(page_table):
        pass

    @staticmethod
    def put_settings(page_name, content, description, keywords, page_table, bucket):
        pass

    @staticmethod
    def get_nav_items(page_name, page_table, bucket):
        pass

    @staticmethod
    def put_nav_items(nav_items):
        # TODO: ADAM - Call set_site_settings func at end
        pass

    @staticmethod
    def read_site_settings():
        pass

    @staticmethod
    def save_site_settings(settings):
        pass