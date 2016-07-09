(function(){
	
var app = angular.module('dashboard', []);

app.controller('DashboardController', ['$http', function($http){
	
	var controller = this;
	
	$http.get("https://johncave.co.nz/test.php").then(function(response) {
        controller.response = response.data;
		console.log(controller.response);
    });
	
} ]);


})();
