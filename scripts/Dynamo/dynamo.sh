#!/bin/bash
source params.sh

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
 --item file://scripts/Dynamo/user.json \
 --return-consumed-capacity TOTAL

