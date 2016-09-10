/*global angular*/

angular.module("login", [])
  .config(function ($httpProvider) {
    "use strict";
    $httpProvider.defaults.withCredentials = true;
  })
  .directive("cmsLoginForm", ["$http", "$window", function ($http, $window) {
    "use strict";
    return {
      http: $http,
      window: $window,
      templateUrl: "cms_login_form.html",
      replace: true,
      controller: "cmsLoginFormCtrl",
      controllerAs: "loginCtrl"
    };
  }])
  .controller("cmsLoginFormCtrl", function ($http, $window) {
    "use strict";
    var ctrlScope = this;
    ctrlScope.buttonText = "Login";
    ctrlScope.failedLogin = false;
    ctrlScope.login = function () {
      ctrlScope.uploading = true;
      ctrlScope.failedLogin = false;
      ctrlScope.buttonText = "Logging in...";
      $http.post(
        "$(API_URL)",
        {
          "request": "loginUser",
          "email": ctrlScope.email,
          "password": ctrlScope.password
        }
      ).then(function successCallback(response) {
        $window.location.href = "admin.html";
      }, function errorCallback(response) {
        ctrlScope.failedLogin = true;
        ctrlScope.error = "Unable to log in";
        ctrlScope.uploading = false;
        ctrlScope.buttonText = "Login";
      });
    };
  });
