#!/bin/bash

# Variables
STACK_NAME="MyStack"

ECHO "--- SCRIPT START ---"

# Create CloudFormation Stack (s3 Bucket)
aws cloudformation create-stack --stack-name $STACK_NAME \
--template-body file://scripts/cloudformation/initFramework.json \
--parameters file://scripts/cloudformation/templateParams.json

ECHO "--- SCRIPT COMPLETE ---"