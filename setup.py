#!/usr/bin/python2.7

import cms_functions
import sys
import os

if len(sys.argv) != 4:
	command = ''
	for arg in sys.argv:
		command += arg + ' '
	print 'Invalid command: ' + command
	print 'Usage: %s <bucket-name> <account-id> <region>' % sys.argv[0]
	sys.exit()

cms = cms_functions.AwsFunc(sys.argv[1], sys.argv[2], sys.argv[3])	# Instantiate an AwsFunc class
cms.create_lambda_function()		# Create a lambda function
cms.create_api_gateway()			# Create an api gateway linked to the lambda function
cms.create_bucket()					# Create an s3 bucket
cms.create_user_table()				# Create a dynamodb user table
cms.create_admin_db_entry()			# Add an entry to the user table that represents an admin
cms.create_token_table()			# Create a dynamodb token table
cms.create_token_db_entry()			# Add an entry to the token table
cms.create_blog_table()				# Create a dynamodb blog table
