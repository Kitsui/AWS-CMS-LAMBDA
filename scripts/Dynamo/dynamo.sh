#!/bin/bash
source params.sh

# Create User table
aws dynamodb create-table --table-name User \
 --attribute-definitions \
  AttributeName=UID,AttributeType=S \
  AttributeName=Username,AttributeType=S \
 --key-schema AttributeName=UID,KeyType=HASH AttributeName=Username,KeyType=RANGE \
 --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

source scripts/Dynamo/register-admin.sh

