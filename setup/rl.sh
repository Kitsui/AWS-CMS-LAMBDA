#!/bin/bash
source params.sh

# Delete Lambda
aws lambda delete-function --function-name mainController
