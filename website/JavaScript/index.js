/*global angular*/

angular.module("index", ["ngRoute", "ui.tinymce", "forms"])
  .config(["$routeProvider", function($routeProvider) {
    $routeProvider
      .when("/pages", {
        templateUrl: "pages.html",
        
        replace: true
      })
      .when("/posts", {
        templateUrl: "posts.html",
        controller: "cmsPostListCtrl",
        controllerAs: "postCtrl",
        replace: true
      })
      .when("/page-form", {
        templateUrl: "page-form.html",
        replace: true
      })
      .when("/blog-form", {
        templateUrl: "blog-form.html",
        replace: true
      })
      .when("/user-form", {
        templateUrl: "user-registration-form.html",
        replace: true
      })
      .when("/role-form", {
        templateUrl: "user-role-form.html",
        replace: true
      })
      .when("/settings", {
        templateUrl: "site-settings.html",
        replace: true
      })
      .otherwise({
        templateUrl: "dashboard-sample.html",
        replace: true
      })
  }])
  .directive("cmsNav", [function () {
    "use strict";
    return {
      templateUrl: "navbar.html",
      replace: true
    };
  }]);
