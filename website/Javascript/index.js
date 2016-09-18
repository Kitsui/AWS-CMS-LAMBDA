/*global angular*/

angular.module("index", ["ngRoute", "ui.tinymce"])
  .config(["$routeProvider", function($routeProvider) {
    $routeProvider
      .when("/page-form", {templateUrl: "page-form.html"})
      .when("/blog-form", {templateUrl: "blog-form.html"})
      .when("/user-form", {templateUrl: "user-registration-form.html"})
      .when("/role-form", {templateUrl: "user-role-form.html"})
      .when("/settings", {templateUrl: "site-settings.html"})
      .otherwise({templateUrl: "dashboard-sample.html"})
  }])
  .directive("cmsNav", [function () {
    "use strict";
    return {
      templateUrl: "navbar.html",
      replace: true
    };
  }])