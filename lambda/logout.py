import boto3

def my_handler(event, context) :
    token = event['tokenString']
    user = event['userID']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Token')
    response = table.delete_item(
            Key={
                'TokenString': token,
                'UserID': user
            }
        )
    # if message is 200 then successfully logged out    
    return {
        'message': response['ResponseMetadata']['HTTPStatusCode']    
    }
    