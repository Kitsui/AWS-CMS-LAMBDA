(function(){
	
var app = angular.module('Kitsui', ['ngRoute'])
	.config(function($locationProvider, $routeProvider) {
        
		$routeProvider.when('/', {
           templateUrl: 'Templates/list.html', 
           controller: 'HomeController'
        });
		
		
        $routeProvider.when('/page/:pageid', {
            templateUrl: 'Templates/page.html', 
            controller: 'PageController',
			controllerAs: 'page'
        });
		
		$routeProvider.when('/post/:postid', {
            templateUrl: 'Templates/post.html', 
            controller: 'PostController',
			controllerAs: 'post'
        });
        //$routeProvider.otherwise({redirectTo: '/home', controller: HomeCtrl});
		$routeProvider.otherwise({templateUrl: 'Templates/404.html'});
     });



	 
app.filter('html', function($sce) { return $sce.trustAsHtml; });



app.controller('PageController', ['$http', '$routeParams', function($http, $routeParams){
	
	var controller = this;
	
	$http.get("Content/Page/"+ $routeParams.pageid +".json").then(function(response) {
        controller.page = response.data;
		controller.title = response.data.title;
		controller.content = response.data.content;
		console.log(controller);
    });
	
} ]);

app.controller('PostController', ['$http', '$routeParams', function($http, $routeParams){
	
	var post = this;
	
	$http.get("Content/Post/"+ $routeParams.postid +".json").then(function(response) {
        post.post = response.data;
		post.title = response.data.Title;
		post.content = response.data.Content;
		post.description = response.data.Description;
		post.date = response.data.SavedDate;
		post.author = response.data.Author;
		console.log(post);
    });
	
} ]);

//Handles displaying post.
app.controller('HomeController', ['$http', '$location', function($http, $location){
	
	var controller = this;
	
	$http.get("Content/post_list.json").then(function(response) {
        
		controller.posts = [];
		for(i = 0; i < response.data.items.length; ++i){ // Loop through the post IDs and fetch their data.
			$http.get("Content/Post/"+response.data.items[i]+".json").then(function(response) {
				controller.posts.push(response.data);
			});
			
			
		}
		
		console.log(controller);
    });
	
} ]);



/*
//Handles displaying post.
app.controller('PostController', ['$http', '$location', function($http, $location){
	
	var controller = this;
	
	//var page.title = "Steven";
	$http.get("Content/Post/"+ $location.search()['post'] +".json").then(function(response) {
        controller.post = response.data;
		console.log(controller);
    });
	
} ]);
*/
   



})();