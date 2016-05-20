// user.js
// Author: Adam Campbell
// Date: 20/May/2016

var user = function(){  

	var self = this;

	self.registerUser = function (AWS, event, context){

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
	};
};

module.exports = user;