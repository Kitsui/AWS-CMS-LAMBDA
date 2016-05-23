#!/bin/bash
source params.sh

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