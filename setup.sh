#!/bin/bash

ECHO "<------ RUNNING SETUP SCRIPT ------>"

# Run subsequent setup files for specific AWS modules
scripts/s3bucket/s3bucket.sh
scripts/groups/groups.sh
scripts/users/users.sh
scripts/roles/roles.sh
scripts/lambda/lambda.sh

ECHO "<------ SETUP SCRIPT COMPLETE ------>"