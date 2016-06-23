#!/usr/bin/python2.7

import AwsFunc

# Create bucket
AwsFunc.create_bucket("Adam-Miguel-Kitsui-Test", "us-east-1")
# Create dynamodb tables
AwsFunc.create_user_table()
AwsFunc.create_token_table()
# Create table entries
AwsFunc.create_admin_db_entry()
AwsFunc.create_token_db_entry()
# Create controller function
AwsFunc.create_lambda_function()