#!/usr/bin/python2.7

import cms_functions
import sys
import os

if len(sys.argv) != 2:
	command = ''
	for arg in sys.argv:
		command += arg + ' '
	print 'Invalid command: ' + command
	print 'Usage: %s <bucket-name>' % sys.argv[0]
	sys.exit()

cms = cms_functions.AwsFunc(sys.argv[1])	# Instantiate an AwsFunc class
cms.create_bucket()					# Create an s3 bucket
cms.create_user_table()				# Create a dynamodb user table
cms.create_admin_db_entry()			# Add an entry to the user table that represents an admin
cms.create_token_table()			# Create a dynamodb token table
cms.create_token_db_entry()			# Add an entry to the token table
cms.create_lambda_function()		# Create a lambda function
cms.create_api_gateway()			# Create an api gateway linked to the lambda function