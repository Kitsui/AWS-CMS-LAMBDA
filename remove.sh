#!/bin/bash
source params.sh

#
# Author: Adam Campbell
# Date: 18/05/2016
# Description: Script used to rollback all
# 			   resources pushed onto AWS via setup.sh

# Delete bucket objects
aws s3 rm s3://$BUCKET_NAME --recursive
# Delete bucket
aws s3api delete-bucket --bucket $BUCKET_NAME
# Delete Dynamo
aws dynamodb delete-table --table-name User
# Delete Lambda
aws lambda delete-function --function-name logEvent