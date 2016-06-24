# Test case
# {
#     "User": {
#         "Username" : "mrPoopyPants",
#         "Password" : "mrPoopyPants123",
#         "Email" : "mrPoopyPants@poopymail.com"
#     }
# }


import boto3
import logging
#import bcrypt
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('User')
    
    username = event['User']["Username"]
    password = event['User']["Password"]
    email = event['User']["Email"]
    userID = "1" # need to use randomizer
    roles = "1" # Currently admin by default
    
    # Hash and salt here
    # comment back in when can import bcrypt
    # salt = bcrypt.gensalt()
    # hash = bcrypt.hashpw(password, salt)
    
    # Need to add check if user exists
    
    response = table.put_item(
       Item={
            'ID': userID,
            'Username': username,
            'Email': email,
            'Password': password,
            'Roles': roles
            }
    )
    
    responseCode = response['ResponseMetadata']['HTTPStatusCode']
    
    if(responseCode == 200) :
        return 'successfully registered ' + username + ' to the UserTable'    
    
    return 'Register unsuccessful'