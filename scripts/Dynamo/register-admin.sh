# Insert admin into user table
 aws dynamodb put-item --table-name User --item file://scripts/Dynamo/user.json --return-consumed-capacity TOTAL