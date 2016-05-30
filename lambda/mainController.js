// mainController.js
// Author: Adam Campbell
// Date: 20/May/2016

"use strict";

var AWS = require('aws-sdk');
var User = require('user.js');

exports.handler = function(event, context) {

	GLOBAL.event = event;
	GLOBAL.context = context;
	
	
	var isAuth = true;
	var request = "login"


	if(isAuth) {

		switch(request) {
			case "register":
				var userInstance = new User();
				userInstance.registerUser(event, context);
				break;
			case "login":
				var user = new User();
				var email = "sempai@johncave.co.nz";
				var password = "SempaiIsGreat";
				user.loginUser(event.email, event.password);
				break;
			case "logout":
				var userInstance = new User();
				userInstance.logoutUser(event, context);
				break;
		}
	}
	else {
		console.log("You are not authorised");
	}
}