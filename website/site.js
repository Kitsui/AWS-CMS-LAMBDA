(function(){
	
var app = angular.module('Kitsui', ['ngRoute'])
	.config(function($locationProvider, $routeProvider) {
        
		$routeProvider.when('/', {
           templateUrl: 'Templates/list.html', 
           controller: 'HomeController',
		   controllerAs: 'home'
        });
		
		$routeProvider.when('/home/:page', {
           templateUrl: 'Templates/list.html', 
           controller: 'HomeController',
		   controllerAs: 'home'
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


app.filter('base64', function() { 
	return function(x){
		y = btoa(x).replace(/\W/g, '');
		return y;
	};
});

app.controller('SettingsController', [ '$http', '$rootScope', function($http, $rootScope){
	var controller = this;
	
	$http.get("Content/site_settings.json").then(function(response){
		for (var key in response.data){
			controller[key] = response.data[key];
		}
		controller.nav = JSON.parse(response.data.nav);
		$rootScope.primary_colour = response.data.primary_colour;
		$rootScope.highlight_colour = response.data.highlight_colour;
	});
	
}]);


app.controller('PageController', ['$http', '$routeParams', '$rootScope', function($http, $routeParams, $rootScope){
	
	var controller = this;
	
	$http.get("Content/Pages/"+ $routeParams.pageid +".json").then(function(response) {
        controller.page = response.data;
		controller.title = response.data.PageName;
		controller.content = response.data.Content;
		$rootScope.page_name = response.data.PageName;
    });
	
} ]);

app.controller('PostController', ['$http', '$routeParams', '$rootScope', function($http, $routeParams, $rootScope){
	
	var post = this;
	
	$http.get("Content/Post/"+ $routeParams.postid +".json").then(function(response) {
        post.post = response.data;
		post.title = response.data.Title;
		post.content = response.data.Content;
		post.description = response.data.Description;
		post.date = response.data.SavedDate;
		post.author = response.data.Author;
		$rootScope.page_name = response.data.Title;
    });
	
} ]);

//Handles displaying post.
app.controller('HomeController', ['$http', '$routeParams', '$location', '$rootScope', function($http, $routeParams, $location, $rootScope){
	
	// What page we are on of the home feed, if applicable.
	var current_page = $routeParams.page;
	if (!current_page){
		current_page = 1;
	}
	
	var controller = this;
	
	$http.get("Content/post_list.json", {cache:false}).then(function(response) {
        
		controller.posts = [];
		
		if(response.data[''+current_page]){ // In case there are no posts yet.
			// Get each post's JSON file.
			for(i = 0; i < response.data[''+current_page].length; ++i){ // Loop through the post IDs and fetch their data.
				$http.get("Content/Post/"+response.data[''+current_page][i]+".json").then(function(response) {
					controller.posts.push(response.data);
				});
				
			}
		} else { // fall back to something, todo.
			
		}
		
		//Figure out if there's a next page
		controller.next_page = parseInt(current_page) + 1;
		// Check that there is a next page in the data
		if(!response.data[controller.next_page]){
			controller.next_page = null;
		}
		
		//Figure out if there's a previous page
		controller.previous_page = parseInt(current_page) - 1;
		// Check that there is a previous page in the data
		if(!response.data[controller.previous_page]){
			controller.previous_page = null;
		}
		
		
    });
	
	$rootScope.page_name = "Latest";
	
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