/*global angular*/

angular.module("apiAccess", [])
  .config(function ($httpProvider) {
    "use strict";
    $httpProvider.defaults.withCredentials = true;
  })
  .controller("login", ["$scope", "$http",
    function ($scope, $http) {
      "use strict";
      
    }]);