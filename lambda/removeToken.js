var AWS = require("aws-sdk");

exports.handler = function index(event, context, callback) {
var docClient = new AWS.DynamoDB.DocumentClient();

var tokenString = event.User.TokenString;
var userID = event.User.UserID;


var params = {
    TableName:"Token",
    Key:{
        "TokenString":tokenString,
        "UserID": userID
    }
};

console.log("Attempting a conditional delete...");

docClient.delete(params, function(err, data) {
    if (err) {
        console.error("Unable to delete item. Error JSON:", JSON.stringify(err, null, 2));
        context.fail("Error with Dynamo", JSON.stringify(err, null, 2));
    } else {
            console.log("Logout succeeded:", JSON.stringify(data, null, 2) , " Token has been Removed from token table");
            context.succeed("Logout Successful", JSON.stringify(data, null, 2), "Token removed from table");
    }
});
}