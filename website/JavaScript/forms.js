/*global angular*/

angular.module("forms", [])
  .config(function ($httpProvider) {
    "use strict";
    $httpProvider.defaults.withCredentials = true;
  })
  .controller("cmsPostListCtrl", ["$http", function ($http) {
    "use strict";
    var ctrlScope = this;
    ctrlScope.posts = [{title: "loading"}];
    $http.post(
      "https://ng50zamyr9.execute-api.us-east-1.amazonaws.com/prod",
      {
        "request": "getAllBlogs"
      }
    ).then(function successCallback(response) {
      var blogNum, responseMessage, responseData;
      responseMessage = response.message
      responseData = response.data.data
      
      ctrlScope.posts = [];
      for (blogNum in responseData) {
        ctrlScope.posts.push(
          {
            title: responseData[blogNum].Title.S,
            author: responseData[blogNum].Author.S,
            description: responseData[blogNum].Description.S,
            keywords: responseData[blogNum].Keywords.L,
            id: responseData[blogNum].ID.S,
            date: responseData[blogNum].SavedDate.S
          }
        )
      }
    }, function errorCallback(response) {
      ctrlScope.posts= [
        {
          title: response.error,
          author: response.error,
          description: response.error,
          keywords: response.error,
          id: response.error,
          date: response.error
        }
      ]
    });
  }]);
