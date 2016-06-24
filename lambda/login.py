# Test case
# {
#     "User" : {
#         "Username" : "Admin",
#         "Password" : "password123"
#     }

# }

import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    from boto3.dynamodb.conditions import Key, Attr
    table = dynamodb.Table('User')
    
    username = event["User"]["Username"]
    password =  event["User"]["Password"]
    
    # response = table.scan()
    response = table.query(KeyConditionExpression=Key('Username').eq(username))
    
    
    for i in response['Items']:
        if(i['Password'] == password):
            return "successfully logged in"

return "failed to login"