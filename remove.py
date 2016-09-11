#!/usr/bin/python2.7

"""
# remove.py
# Author: Christopher Treadgold
# Date: N/D
# Edited: 07/08/2016 | Christopher Treadgold
"""

import json
import os
import sys
import time

import boto3

# AWS clients used by the AWSCMS
apigateway = boto3.client('apigateway')
lmda = boto3.client('lambda')
iam = boto3.client('iam')
dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')

# Get installed cms'
if os.path.isfile("./installed.json"):
    with open("installed.json", "r") as installed_file:
        installed = json.loads(installed_file.read())
else:
    print "No cms' are installed, exiting"
    sys.exit()

# Ask the user which cms to remove
print "Installed cms':"
for key in installed.keys():
    print "%s: %s" %(key, installed[key])
user_selection = str(input("Enter the number of the cms you would like to uninstall: "))
if user_selection not in installed.keys():
    print "Invalid selection, exiting."
    sys.exit()
else:
    constants_file_name = "%s-constants.json" % (installed[user_selection])
    with open(constants_file_name, "r") as const:
        constants = json.loads(const.read())
    del installed[user_selection]

rest_api_names = [
    constants["REST_API"]
]
lmda_function_names = [
    constants["LAMBDA_FUNCTION"]
]
role_names = [
    constants["LAMBDA_ROLE"]
]
dynamodb_table_names = [
    constants["BLOG_TABLE"],
    constants["PAGE_TABLE"],
    constants["TOKEN_TABLE"],
    constants["USER_TABLE"]
]
s3_bucket_names = [
    constants["BUCKET"]
]

# Remove all AWSCMS api gateways
print 'Removing rest api'

rest_apis_deleted = 0
rest_apis = apigateway.get_rest_apis()['items']
for rest_api in rest_apis:
    if rest_api['name'] in rest_api_names:
        if rest_api != rest_apis[-1]:
            time.sleep(30.5)
        apigateway.delete_rest_api(restApiId=rest_api['id'])
        rest_apis_deleted += 1

if rest_apis_deleted > 0:
    print rest_apis_deleted, 'Rest api(s) removed'
else:
    print 'No apis to remove'

# Remove all AWSCMS lambda funtions
print 'Removing lambda functions'

functions_removed = 0
for lmda_function in lmda.list_functions()['Functions']:
    if lmda_function['FunctionName'] in lmda_function_names:
        lmda.delete_function(
            FunctionName=lmda_function['FunctionName'])
        functions_removed += 1

if functions_removed > 0:
    print functions_removed, 'lambda function(s) removed'
else:
    print 'No lambda functions to remove'

# Remove all AWSCMS iam roles
print 'Removing iam roles'

roles_removed = 0
for role in iam.list_roles()['Roles']:
    if role['RoleName'] in role_names:
        # Detach all role policies
        for policy in iam.list_attached_role_policies(RoleName=role['RoleName'])['AttachedPolicies']:
            iam.detach_role_policy(
                RoleName=role['RoleName'],
                PolicyArn=policy['PolicyArn'])
        for policy_name in iam.list_role_policies(RoleName=role['RoleName'])['PolicyNames']:
            iam.delete_role_policy(
                RoleName=role['RoleName'],
                PolicyName=policy_name)
        # Delete role
        iam.delete_role(
            RoleName=role['RoleName'])
        roles_removed += 1

if roles_removed > 0:
    print roles_removed, 'iam role(s) removed'
else:
    print 'No iam roles to remove'

# Remove all AWSCMS dynamodb tables
print 'Removing dynamodb tables'

tables_removed = 0
for table_name in dynamodb.list_tables()['TableNames']:
    if table_name in dynamodb_table_names:
        dynamodb.delete_table(
            TableName=table_name)
        tables_removed += 1

if tables_removed > 0:
    print tables_removed, 'dynamodb table(s) removed'
else:
    print 'No dynamodb tables to remove'

# Remove all AWSCMS s3 buckets
print 'Removing S3 buckets'

buckets_deleted = 0
objects_deleted = 0
for bucket in s3.list_buckets()['Buckets']:
    if bucket['Name'] in s3_bucket_names:
        print 'Deleting bucket:', bucket['Name']
        # Delete all bucket contents
        if 'Contents' in s3.list_objects_v2(Bucket=bucket['Name']).keys():
            for obj in s3.list_objects_v2(Bucket=bucket['Name'])['Contents']:
                print 'Deleting object:', obj['Key']
                s3.delete_object(
                    Bucket=bucket['Name'],
                    Key=obj['Key'])
                print 'Object deleted'
                objects_deleted += 1
        # Delete bucket
        s3.delete_bucket(
            Bucket=bucket['Name'])
        print 'Bucket deleted'
        buckets_deleted += 1

if buckets_deleted > 0:
    print buckets_deleted, 'S3 buckets removed'
    print objects_deleted, 'objects deleted'
else:
    print 'No S3 buckets to remove'


# Clean up files
if not installed:
    os.remove("installed.json")
else:
    with open("installed.json", "w") as inst:
        inst.write(json.dumps(installed, indent=4, sort_keys=True))

os.remove(constants_file_name)
