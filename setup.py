#!/usr/bin/python2.7

"""
# setup.py
# Author: Christopher Treadgold
# Date: N/D
# Edited: 07/08/2016 | Christopher Treadgold
"""

import cms_functions
import sys
import os

if len(sys.argv) not in range(2, 4):
    command = ''
    for arg in sys.argv:
        command += arg + ' '
    print 'Invalid command: ' + command
    print 'Usage: %s <cms_prefix> <region (optional)>' % sys.argv[0]
    sys.exit()

# Instantiate an AwsFunc class
if len(sys.argv) == 3:
    cms = cms_functions.AwsFunc(sys.argv[1], region=sys.argv[2])
else:
    cms = cms_functions.AwsFunc(sys.argv[1])

# Create tje rest api
cms.create_rest_api()

# Create the lambda function
cms.create_lambda_function()

# Setup the rest api
cms.api_add_post_method()
cms.api_add_options_method()
cms.deploy_api()

# Create the s3 bucket
cms.create_bucket()
# Create the cloudfront distribution
cms.create_cloudfront_distribution()

# Create the dynamodb blog table
cms.create_blog_table()
# Add a blog to the blog table
cms.create_blog_db_entry()

# Create the dynamodb page table
cms.create_page_table()
# Add a page to the page table
cms.create_page_db_entry()

# Create the dynamodb role table
cms.create_role_table()
# Add an admin role to the role table
cms.create_admin_role_db_entry()

# Create the dynamodb token table
cms.create_token_table()
# Add a token to the token table
cms.create_token_db_entry()

# Create the dynamodb user table
cms.create_user_table()
# Add an admin to the user table
cms.create_admin_user_db_entry()

# Create the dynamodb site settings table
cms.create_site_settings_table()
# Add default site settings to the site settings table
cms.create_site_settings_db_entry()

# Create the dynamo form table
cms.create_form_table()
# Add a form to form table
cms.create_form_db_entry()

# Create the dynamo table table
cms.create_table_table()

# Saves the cms installation information
cms.save_constants()
