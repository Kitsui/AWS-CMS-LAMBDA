#!/bin/bash
source params.sh

ECHO "<------ RUNNING CLOUD FORMATION SCRIPT ------>"

# Create CloudFormation Stack 
aws cloudformation create-stack --stack-name $STACK_NAME \
--template-body file://scripts/cloudformation/template.json \
--parameters ParameterKey=BucketName,ParameterValue=$BUCKET_NAME

ECHO "<------ CLOUD FORMATION SCRIPT COMPLETE ------>"