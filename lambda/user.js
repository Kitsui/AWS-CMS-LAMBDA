// user.js
// Author: Adam Campbell
// Date: 20/May/2016

"use strict";

// Module imports
var bcryptjs = require('bcryptjs');
var uuid = require('uuid');
var crypto = require('crypto');

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
	self.loginUser = function(email, password){
		
		var docClient = new AWS.DynamoDB.DocumentClient();

  //some code


var params = {
    TableName: "User",
    ProjectionExpression: "ID, Username, Email, Password"
};

console.log("Scanning User table.");
docClient.scan(params, onScan);

function onScan(err, data) {
    if (err) {
        console.error("Unable to scan the table. Error JSON:", JSON.stringify(err, null, 2));
    } else {
        // print all the users
        console.log("Scan succeeded.");
        data.Items.forEach(function(user) {
           console.log(
                user.Username,
                user.ID,
                user.Email);
				if(user.Email == email && bcryptjs.compareSync(password, user.Password)){

					/** Sync */
					function randomStringAsBase64Url(size) {
						return crypto.randomBytes(size).toString('base64');
					}
					var token = randomStringAsBase64Url(30);
					var params = {
						Item:{
							"TokenString": {
								S: token
							},
							"UserID": {
								S: user.ID
							}
						},
						TableName: "Token"
					}
					dynamodb.putItem(params, function(err, data) {
						if (err) console.log(err, err.stack); // an error occurred
						else     console.log(data);           // successful response
					});
					context.succeed("Logged in user "+user.Username+". Please set token "+token);
				}
        });
		//context.succeed(data.Items);

        // continue scanning if we have more movies
        if (typeof data.LastEvaluatedKey != "undefined") {
            console.log("Scanning for more...");
            params.ExclusiveStartKey = data.LastEvaluatedKey;
            docClient.scan(params, onScan);
        }
    }
}

		
		/*
		var docClient = new AWS.DynamoDB.DocumentClient();
		
		var params = {
			TableName: "User",
			ProjectionExpression: "Email",
			FilterExpression: "Email equals "+email,
		};
		
		var results = docClient.scan(params);
		context.succeed(results);
		
		
		if(email == "me@here.com" & bcryptjs.compareSync(password, "$2a$08$ICaYC34Tz1VTv6TRJjNJ/.SkactuwKti7eOYR97yUmHch34nNCSvy")){
			console.log("Logged in user "+email);
			context.succeed({success: true, message: "You are now logged in."});
		} else{
			console.log("Incorrect login attempted from IP 8.8.4.44");
			context.fail({success: false, message: "Email or password was incorrect."});
		} */
	};
};

module.exports = user;