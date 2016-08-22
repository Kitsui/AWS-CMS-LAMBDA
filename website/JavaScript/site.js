(function(){
	
var app = angular.module('Kitsui', []);
app.filter('unsafe', function($sce) { return $sce.trustAsHtml; });

app.controller('PageController', ['$http', '$location', function($http, $location){
	
	var controller = this;
	
	//var page.title = "Steven";
	$http.get("Content/Page/"+ $location.search()['page'] +".json").then(function(response) {
        controller.page = response.data;
		console.log(controller.page);
    });
	
} ]);

//Handles displaying post.
app.controller('PostController', ['$http', '$location', function($http, $location){
	
	var controller = this;
	
	//var page.title = "Steven";
	$http.get("Content/Post/"+ $location.search()['post'] +".json").then(function(response) {
        controller.post = response.data;
		console.log(controller.post);
    });
	
} ]);


})();