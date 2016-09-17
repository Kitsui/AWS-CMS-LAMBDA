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
# cms.create_cloudfront_distribution() TODO: Reactivate

# Create the dynamodb blog table
cms.create_blog_table()

# Create the dynamodb page table
cms.create_page_table()

# Create the dynamodb token table
cms.create_token_table()

# Create the dynamodb user table
cms.create_user_table()
# Add an admin to the user table
cms.create_admin_user_db_entry()

# Print the default login credentials and the login link
cms.print_login_link()

# Saves the cms installation information
cms.save_constants()
