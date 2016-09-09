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
      templateUrl: 'cms_login_form.html',
      replace: true,
      controller: 'cmsLoginFormCtrl',
      controllerAs: 'loginCtrl'
    };
  }])
  .controller("cmsLoginFormCtrl",
    function ($http, $window) {
      "use strict";
      this.buttonText = "Login";
      this.failedLogin = false;
      this.login = function () {
        this.uploading = true;
        this.failedLogin = false;
        this.buttonText = "Logging in...";
        $http.post(
          "$(API_URL)",
          {
            "request": "loginUser",
            "User": {
              "Email": this.email,
              "Password": this.password
            }
          }
        ).then(function successCallback(response) {
          $window.location.href = "admin.html";
        }, function errorCallback(response) {
          this.failedLogin = true;
          this.error = "Unable to log in";
          this.uploading = false;
          this.buttonText = "Login";
        });
      };
    });