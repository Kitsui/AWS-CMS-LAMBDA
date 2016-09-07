/*global angular*/

angular.module("login", [])
  .config(function ($httpProvider) {
    "use strict";
    $httpProvider.defaults.withCredentials = true;
  })
  .controller("loginForm", ["$scope", "$http", "$window",
    function ($scope, $http, $window) {
      "use strict";
      $scope.buttonText = "Login";
      $scope.failedLogin = false;
      $scope.login = function () {
        $scope.uploading = true;
        $scope.failedLogin = false;
        $scope.buttonText = "Logging in...";
        $http.post(
          "$(API_URL)",
          {
            "request": "loginUser",
            "User": {
              "Email": $scope.email,
              "Password": $scope.password
            }
          }
        ).then(function successCallback(response) {
          $window.location.href = "admin.html";
        }, function errorCallback(response) {
          $scope.failedLogin = true;
          $scope.error = "Unable to log in";
          $scope.uploading = false;
          $scope.buttonText = "Login";
        });
      };
    }]);