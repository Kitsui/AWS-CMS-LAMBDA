#!/bin/bash
source params.sh

ECHO "<------ RUNNING ROLES SCRIPT ------>"

# Create Administrator role
aws iam create-role \
--role-name lambda_basic_execution \
--assume-role-policy-document file://scripts/policies/lambda-basic-exec.json

ECHO "<------ ROLES SCRIPT COMPLETE ------>"