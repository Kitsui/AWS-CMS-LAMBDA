!/bin/bash
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
  AttributeName=ID,AttributeType=S \
  AttributeName=Username,AttributeType=S \
 --key-schema AttributeName=ID,KeyType=HASH AttributeName=Username,KeyType=RANGE \
 --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

# Create Token table
 aws dynamodb create-table --table-name Token \
 --attribute-definitions \
  AttributeName=TokenString,AttributeType=S \
  AttributeName=UserID,AttributeType=S \
 --key-schema AttributeName=TokenString,KeyType=HASH AttributeName=UserID,KeyType=RANGE \
 --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

sleep 30

# Create admin
 aws dynamodb put-item \
 --table-name User \
 --item file://dynamo/user.json \
 --return-consumed-capacity TOTAL

 # Create default token
aws dynamodb put-item \
 --table-name Token \
 --item file://dynamo/token.json \
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

ECHO "<------ Setting up API Gateway ------>"
## Create the API
API_ID=$(aws apigateway create-rest-api \
	--name AWS_CMS_Operations_DERP \
	--region "$REGION" \
	--output text \
	--query 'id')

ROOT_ID=$(aws apigateway get-resources \
	--rest-api-id "$API_ID" \
	--region "$REGION" \
	--output text \
	--query 'items[?path==`'/'`].[id]')

# Create a resource for API
RESOURCE_ID=$(aws apigateway create-resource \
--rest-api-id "$API_ID" \
--parent-id "$ROOT_ID" \
--path-part AWS_CMS_Manager \
--output text \
--query 'id')

# Create method (POST) on the above resource
aws apigateway put-method \
--rest-api-id $API_ID \
--resource-id $RESOURCE_ID \
--http-method POST \
--authorization-type NONE

# Set the Lambda function as the destination for the POST
aws apigateway put-integration \
--rest-api-id $API_ID \
--resource-id $RESOURCE_ID \
--http-method POST \
--type AWS \
--integration-http-method POST \
--uri arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$REGION:$ACCOUNT_NUMBER:function:mainController/invocations

# Set the API response to return JSON
aws apigateway put-method-response \
--rest-api-id $API_ID \
--resource-id $RESOURCE_ID \
--http-method POST \
--status-code 200 \
--response-models "{\"application/json\": \"Empty\"}"

# Set the Lambda response to return JSON
aws apigateway put-integration-response \
--rest-api-id $API_ID \
--resource-id $RESOURCE_ID \
--http-method POST \
--status-code 200 \
--response-templates "{\"application/json\": \"\"}"

# Deploy the API
aws apigateway create-deployment \
--rest-api-id $API_ID \
--stage-name prod

# Add grant permissions to gateway for invoking mainController function
aws lambda add-permission \
--function-name mainController \
--statement-id apigateway-production-aws-cms \
--action lambda:InvokeFunction \
--principal apigateway.amazonaws.com \
--source-arn "arn:aws:execute-api:$REGION:$ACCOUNT_NUMBER:$API_ID/prod/POST/AWS_CMS_Manager"
ECHO "<------ Setting up API Gateway COMPLETE ------>"



ECHO "<------ Setting up AWS CMS COMPLETE ------>"
