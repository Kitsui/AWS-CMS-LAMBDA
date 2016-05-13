
// Test function for printing out the given event
exports.handler = function(event, context) {
	console.log('Received event:', JSON.stringify(event, null, 2));
}