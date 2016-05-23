// user.js
// Author: Adam Campbell
// Date: 20/May/2016

"use strict";

// Module imports
var bcryptjs = require('bcryptjs');
var uuid = require('uuid');

// AWS services
var AWS = require('aws-sdk');
var dynamodb = 	new AWS.DynamoDB();

// Object
var user = function(){  

	var self = this;

	self.registerUser = function (event, context){

		var params = {
			Item: {
			    "ID": {
			        S: uuid.v1()
			    },
				"Username": {
					S: event.user.username
				},
				"Email": {
					S: event.user.email
				},
				"Password": {
					S: bcryptjs.hashSync(event.user.password, 8)
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
	};
};

module.exports = user;