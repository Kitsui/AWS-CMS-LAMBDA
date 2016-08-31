(function(){
	
var app = angular.module('Kitsui', ['ngRoute'])
	.config(function($locationProvider, $routeProvider) {
        /*
		$routeProvider.when('/', {
           templateUrl: 'index.html', 
           controller: HomeController
        });
		*/
		
        $routeProvider.when('/page/:pageid', {
            templateUrl: 'Templates/page.html', 
            controller: 'PageController'
        });
		
		$routeProvider.when('/post/:postid', {
            templateUrl: 'Templates/post.html', 
            controller: 'PostController'
        });
        //$routeProvider.otherwise({redirectTo: '/home', controller: HomeCtrl});
     });



	 
app.filter('unsafe', function($sce) { return $sce.trustAsHtml; });





angular.module('Kitsui').controller('PageController', ['$http', '$routeParams', function($http, $routeParams){
	
	var controller = this;
	
	//var page.title = "Steven";
	$http.get("Content/Page/"+ $routeParams.pageid +".json").then(function(response) {
        controller.page = response.data;
		console.log(controller);
    });
	
} ]);




//Handles displaying post.
app.controller('PostController', ['$http', '$location', function($http, $location){
	
	var controller = this;
	
	//var page.title = "Steven";
	$http.get("Content/Post/"+ $location.search()['post'] +".json").then(function(response) {
        controller.post = response.data;
		console.log(controller);
    });
	
} ]);

//Handles displaying post.
app.controller('HomeController', ['$http', '$location', function($http, $location){
	
	var controller = this;
	
	//var page.title = "Steven";
	$http.get("Content/home.json").then(function(response) {
        controller.post = response.data;
		console.log(controller.post);
    });
	
} ]);
   



})();