#!/bin/bash

# Variables
STACK_NAME = "MyStack"
BUCKET_NAME = "adam-miguel-bash-bucket"

ECHO "--- SCRIPT START ---"

# Create CloudFormation Stack (s3 Bucket)
aws cloudformation create-stack --stack-name $STACK_NAME \
--template-body file://scripts/cloudformation/initFramework.json \
--parameters [{ParameterKey=BucketName, ParameterKey=$BUCKET_NAME}]

# Upload HTML to created bucket
aws s3api put-object --bucket $BUCKET_NAME --key index.html  --body resources/HTML/index.html 
aws s3api put-object --bucket $BUCKET_NAME --key error.html  --body resources/HTML/error.html

# Set access control list on HTML
aws s3api put-object-acl --bucket $BUCKET_NAME --key index.html --grant-read http://acs.amazonaws.com/groups/global/AllUsers
aws s3api put-object-acl --bucket $BUCKET_NAME --key error.html--grant-read http://acs.amazonaws.com/groups/global/AllUsers

ECHO "--- SCRIPT COMPLETE ---"