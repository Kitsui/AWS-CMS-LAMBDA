/*global angular*/

angular.module("apiAccess", [])
  .config(function ($httpProvider) {
    "use strict";
    $httpProvider.defaults.withCredentials = true;
  })
  .controller("getBlogs", ["$scope", "$http",
    function ($scope, $http) {
      "use strict";
      $http.post(
        "$(API_URL)",
        {
          "request": "getBlogs"
        }
      ).then(function successCallback(response) {
        $scope.blogData = response.data.rows;
      }, function errorCallback(response) {
        $scope.test = response;
      });
    }])
  .controller("uploadBlog", ["$scope", "$http",
    function ($scope, $http) {
      "use strict";
      $scope.sendBlog = function () {
        $http.post(
          "$(API_URL)",
          {
            "request": "saveNewBlog",
            "blog": {
              "author": $scope.blog.author,
              "title": $scope.blog.author,
              "content": $scope.blog.content,
              "metaDescription": $scope.blog.description,
              "metaKeywords": $scope.blog.keywords
            }
          }
        ).then(function successCallback() {
          
        }, function errorCallback() {
          
        });
      };
    }]);