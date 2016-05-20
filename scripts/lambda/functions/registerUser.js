"use strict";

var AWS = require('aws-sdk');

exports.handler = (event, context) => {

//console.log('Received event:', JSON.stringify(event, null, 2));

	var dynamodb = 	new AWS.DynamoDB();

	var minId = 0;
	var maxId = 999999999;
	var id = Math.floor(Math.random() * (maxId - minId + 1)) + minId;

	var params = {
		Item: {
		    "ID": {
		        N: id.toString()
		    },
			"Username": {
				S: event.user.username
			},
			"Email": {
				S: event.user.email
			},
			"Password": {
				S: event.user.password
			},
			"Roles": {
				S: "1"
			}
		},
		TableName: "User"
	}

	dynamodb.putItem(params, function(err, data) {
  		if (err) console.log(err, err.stack); // an error occurred
  		else     console.log(data);           // successful response
	});
}