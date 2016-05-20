// mainController.js
// Author: Adam Campbell
// Date: 20/May/2016

"use strict";

var AWS = require('aws-sdk');
var User = require('user.js');

exports.handler = function(event, context) {

	var isAuth = true;
	var request = "register"

	if(isAuth) {

		switch(request) {
			case "register":
				var userInstance = new User();
				userInstance.registerUser(AWS, event, context);
				break;
		}
	}
	else {
		console.log("You are not authorised");
	}
}