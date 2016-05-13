#!/bin/bash
source params.sh

ECHO "<------ RUNNING LAMBDA SCRIPT ------>"

sleep 5

# Create Lambda function
aws lambda create-function \
--function-name logEvent \
--runtime nodejs4.3 \
--role arn:aws:iam::$ACCOUNT_NUMBER:role/lambda_basic_execution \
--handler logEvent.handler \
--description "Prints out event JSON" \
--zip-file fileb://scripts/lambda/functions/logEvent.zip

ECHO "<------ LAMBDA SCRIPT COMPLETE ------>"