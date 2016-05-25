#!/bin/bash
source params.sh

# Delete bucket objects
aws s3 rm s3://$BUCKET_NAME --recursive
# Delete bucket
aws s3api delete-bucket --bucket $BUCKET_NAME
# Delete Dynamo
aws dynamodb delete-table --table-name User
aws dynamodb delete-table --table-name Token
# Delete Lambda
aws lambda delete-function --function-name mainController
