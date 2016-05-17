#User table
aws dynamodb create-table --table-name User \
 --attribute-definitions \
  AttributeName=UID,AttributeType=S \
  AttributeName=Username,AttributeType=S \
 --key-schema AttributeName=UID,KeyType=HASH AttributeName=Username,KeyType=RANGE \
 --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

#put new admin
source put-user.sh


#Role table


#id, username, password, email, roles

#role table-name
#UID  name C R U D

#create read update delete - action