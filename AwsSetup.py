#!/usr/bin/python2.7

import boto3
import botocore
import os
import mimetypes

class AwsSetup(object): 
	def create_bucket(self, bucket_name=None, bucket_region=None):
		try:
			# Set the variables needed to create the bucket
			s3 = boto3.resource('s3')
			bucket = None
			bucket_kwargs = {
				'ACL': 'public-read',
				'Bucket': bucket_name
			}
			if bucket_region != None and bucket_region != 'us-east-1':
				bucket_kwargs['CreateBucketConfiguration'] = {'LocationConstraint': bucket_region}

			# Create the bucket
			bucket = s3.create_bucket(**bucket_kwargs)
			
			# Populate the bucket
			for root, dirs, files in os.walk('website'):
				# Add all files from the website folder to the bucket
				for fl in files:
					# Set variables for adding the current file the bucket
					directory = root + '/' + fl
					mime = mimetypes.guess_type(directory)
					put_kwargs = {
						'ACL': 'public-read',
						'Body': directory,
						'Key': directory
					}
					if mime[0] != None:
						put_kwargs['ContentType'] = mime[0]
					if mime[1] != None:
						put_kwargs['ContentEncoding'] = mime[1]
					
					# Add file to the bucket
					bucket.put_object(**put_kwargs)
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			return False

		return True

test = AwsSetup()
print test.create_bucket(bucket_name='banana-hammock-3')	
