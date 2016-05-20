#!/bin/bash
source params.sh

ECHO "<------ Setting up AWS CMS ------>"

ECHO "<------ Setting up S3 Bucket ------>"
# Create s3 Bucket
aws s3api create-bucket \
--bucket $BUCKET_NAME \
--region $REGION \
--acl public-read

# Upload HTML to created bucket
aws s3api put-object --bucket $BUCKET_NAME --key index.html  \
--body ../s3/HTML/index.html --content-type text/html

aws s3api put-object --bucket $BUCKET_NAME --key error.html  \
--body ../s3/HTML/error.html --content-type text/html

aws s3api put-object --bucket $BUCKET_NAME --key register.html  \
--body ../s3/HTML/register.html --content-type text/html

# Set access control list on HTML
aws s3api put-object-acl --bucket $BUCKET_NAME --key index.html \
--grant-read uri=http://acs.amazonaws.com/groups/global/AllUsers

aws s3api put-object-acl --bucket $BUCKET_NAME --key error.html \
--grant-read uri=http://acs.amazonaws.com/groups/global/AllUsers

aws s3api put-object-acl --bucket $BUCKET_NAME --key register.html \
--grant-read uri=http://acs.amazonaws.com/groups/global/AllUsers
ECHO "<------ Setting up S3 Bucket ------>"

ECHO "<------ Setting up DynamoDB ------>"
# Create User table
aws dynamodb create-table --table-name User \
 --attribute-definitions \
  AttributeName=ID,AttributeType=N \
  AttributeName=Username,AttributeType=S \
 --key-schema AttributeName=ID,KeyType=HASH AttributeName=Username,KeyType=RANGE \
 --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

sleep 5

# Create admin
 aws dynamodb put-item \
 --table-name User \
 --item file://dynamo/user.json \
 --return-consumed-capacity TOTAL
ECHO "<------ Setting up DynamoDB COMPLETE------>"

ECHO "<------ Setting up Lambda ------>"
# Create Lambda function
aws lambda create-function \
--function-name mainController \
--runtime nodejs4.3 \
--role arn:aws:iam::$ACCOUNT_NUMBER:role/lambda_basic_execution \
--handler mainController.handler \
--description "Central management function designed to handle any API Gateway request" \
--zip-file fileb://../lambda/mainController.zip
ECHO "<------ Setting up Lambda COMPLETE ------>"

ECHO "<------ Setting up AWS CMS COMPLETE ------>"