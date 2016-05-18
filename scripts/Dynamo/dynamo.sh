#!/bin/bash
source params.sh

# Create User table
aws dynamodb create-table --table-name User \
 --attribute-definitions \
  AttributeName=UID,AttributeType=S \
  AttributeName=Username,AttributeType=S \
 --key-schema AttributeName=UID,KeyType=HASH AttributeName=Username,KeyType=RANGE \
 --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

# TODO: Miguel, need to figure out why the 
# --item file causes an error when running via setup.sh

# Insert admin into user table
# aws dynamodb put-item --table-name User \
# --item file://scripts/Dynamo/user.json \
# --return-consumed-capacity TOTAL