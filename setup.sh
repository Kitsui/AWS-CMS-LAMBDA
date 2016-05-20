#!/bin/bash

ECHO "<------ RUNNING SETUP SCRIPT ------>"

# Run subsequent setup files for specific AWS modules
scripts/s3bucket/s3bucket.sh
scripts/lambda/lambda.sh
scripts/Dynamo/dynamo.sh
scripts/apigateway/apigateway.sh

ECHO "<------ SETUP SCRIPT COMPLETE ------>"