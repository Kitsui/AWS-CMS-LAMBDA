#!/bin/bash
source params.sh

ECHO "<------ RUNNING GROUPS SCRIPT ------>"

# Create Admin group
aws iam create-group --group-name Admins
# Add custom policy to Admin group
aws iam put-group-policy \
--group-name Admins \
--policy-document file://scripts/policies/cms-admin.json \
--policy-name CMSAdmin

ECHO "<------ GROUPS SCRIPT COMPLETE ------>"