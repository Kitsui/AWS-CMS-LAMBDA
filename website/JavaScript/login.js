/*global angular*/

angular.module("login", ["api"])
  .config(function ($httpProvider) {
    "use strict";
    $httpProvider.defaults.withCredentials = true;
  })
  .directive("cmsLoginForm", ["$http", "$window", "apiUrl", function ($http, $window, apiUrl) {
    "use strict";
    return {
      http: $http,
      window: $window,
      apiUrl: apiUrl,
      templateUrl: "cms_login_form.html",
      replace: true,
      controller: "cmsLoginFormCtrl",
      controllerAs: "loginCtrl"
    };
  }])
  .controller("cmsLoginFormCtrl", function ($http, $window, apiUrl) {
    "use strict";
    var ctrlScope = this;
    ctrlScope.buttonText = "Login";
    ctrlScope.failedLogin = false;
    ctrlScope.login = function () {
      ctrlScope.uploading = true;
      ctrlScope.failedLogin = false;
      ctrlScope.buttonText = "Logging in...";
      $http.post(
        apiUrl,
        {
          "request": "loginUser",
          "email": ctrlScope.email,
          "password": ctrlScope.password
        }
      ).then(function successCallback(response) {
        $window.location.href = "index.html";
      }, function errorCallback(response) {
        ctrlScope.failedLogin = true;
        ctrlScope.error = "Unable to log in";
        ctrlScope.uploading = false;
        ctrlScope.buttonText = "Login";
      });
    };
  });
