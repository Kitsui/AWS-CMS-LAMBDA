#!/bin/bash
source params.sh

ECHO "<------ RUNNING USERS SCRIPT ------>"

# Create Admin user
aws iam create-user --user-name $ADMIN_NAME
# Update Admin password
#aws iam update-login-profile --user-name $ADMIN_NAME --password pa$$w0rd
# Add to Admin group
aws iam add-user-to-group --user-name $ADMIN_NAME --group-name Admins

ECHO "<------ ROLES USERS COMPLETE ------>"