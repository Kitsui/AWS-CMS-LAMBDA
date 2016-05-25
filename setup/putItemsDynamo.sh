

# Create admin
 aws dynamodb put-item \
 --table-name User \
 --item file://dynamo/user.json \
 --return-consumed-capacity TOTAL



 # Create default token
aws dynamodb put-item \
 --table-name Token \
 --item file://dynamo/token.json \
 --return-consumed-capacity TOTAL