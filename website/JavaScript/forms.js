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
      "$(API_URL)",
      {
        "request": "getAllBlogs"
      }
    ).then(function successCallback(response) {
      var blogNum, responseMessage, responseData, tempKeywords, keyword, keywords;
      responseMessage = response.message;
      responseData = response.data.data;
      
      ctrlScope.posts = [];
      for (blogNum in responseData) {
        keywords = responseData[blogNum].Keywords.L;
        tempKeywords = "";
        for (keyword in keywords) {
          tempKeywords = tempKeywords.concat(keywords[keyword].S);
          tempKeywords = tempKeywords.concat(", ");
        }
        tempKeywords = tempKeywords.substring(0, tempKeywords.length - 2);
        
        ctrlScope.posts.push(
          {
            title: responseData[blogNum].Title.S,
            author: responseData[blogNum].Author.S,
            description: responseData[blogNum].Description.S,
            keywords: tempKeywords,
            id: responseData[blogNum].ID.S,
            date: responseData[blogNum].SavedDate.S
          }
        );
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
      ];
    });
  }])
  .controller("cmsPageListCtrl", ["$http", function ($http) {
    "use strict";
    var ctrlScope = this;
    ctrlScope.pages = [{title: "loading"}];
    $http.post(
      "$(API_URL)",
      {
        "request": "getAllPages"
      }
    ).then(function successCallback(response) {
      var pageNum, responseMessage, responseData, tempKeywords, keyword, keywords;
      responseMessage = response.message;
      responseData = response.data.data;
      
      ctrlScope.pages = [];
      for (pageNum in responseData) {
        keywords = responseData[pageNum].Keywords.L;
        tempKeywords = "";
        for (keyword in keywords) {
          tempKeywords = tempKeywords.concat(keywords[keyword].S);
          tempKeywords = tempKeywords.concat(", ");
        }
        tempKeywords = tempKeywords.substring(0, tempKeywords.length - 2);
        
        ctrlScope.pages.push(
          {
            title: responseData[pageNum].Name.S,
            description: responseData[pageNum].Description.S,
            keywords: tempKeywords,
            date: responseData[pageNum].SavedDate.S
          }
        );
      }
    }, function errorCallback(response) {
      ctrlScope.pages= [
        {
          title: response.error,
          description: response.error,
          keywords: response.error,
          date: response.error
        }
      ];
    });
  }]);