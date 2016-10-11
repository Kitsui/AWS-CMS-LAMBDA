/*global angular*/

angular.module("index", ["ngRoute", "ui.tinymce", "forms", "api"])
  .config(["$routeProvider", function ($routeProvider) {
    "use strict";
    $routeProvider
      .when("/pages", {
        templateUrl: "pages.html",
        controller: "cmsPageListCtrl",
        controllerAs: "pageCtrl",
        replace: true
      })
      .when("/posts", {
        templateUrl: "posts.html",
        controller: "cmsPostListCtrl",
        controllerAs: "postCtrl",
        replace: true
      })
      .when("/users", {
        templateUrl: "users.html",
        controller: "cmsUserListCtrl",
        controllerAs: "userCtrl",
        replace: true
      })
      .when("/roles", {
        templateUrl: "roles.html",
        controller: "cmsRoleListCtrl",
        controllerAs: "roleCtrl",
        replace: true
      })
      .when("/page-form/:pageName?", {
        templateUrl: "page-form.html",
        controller: "cmsPageFormCtrl",
        controllerAs: "pageFormCtrl",
        replace: true
      })
      .when("/blog-form/:blogId?", {
        templateUrl: "blog-form.html",
        controller: "cmsBlogFormCtrl",
        controllerAs: "blogFormCtrl",
        replace: true
      })
      .when("/user-form/:userId?", {
        templateUrl: "user-registration-form.html",
        controller: "cmsUserFormCtrl",
        controllerAs: "userFormCtrl",
        replace: true
      })
      .when("/role-form/:roleName?", {
        templateUrl: "role-form.html",
        controller: "cmsRoleFormCtrl",
        controllerAs: "roleFormCtrl",
        replace: true
      })
      .when("/upload-image", {
        templateUrl: "upload-image.html",
        controller: "cmsUploadImageCtrl",
        controllerAs: "imageCtrl",
        replace: true
      })
      .when("/settings", {
        templateUrl: "site-settings.html",
        controller: "cmsSettingsFormCtrl",
        controllerAs: "settingsFormCtrl",
        replace: true
      })
      .when("/visitor-nav", {
        templateUrl: "visitor-navigation.html",
        controller: "cmsVisitorNavFormCtrl",
        controllerAs: "visitorNavFormCtrl",
        replace: true
      })
      .otherwise({
        templateUrl: "dashboard-sample.html",
        replace: true
      });
  }])
  .directive("cmsNav", [function () {
    "use strict";
    return {
      templateUrl: "navbar.html",
      replace: true
    };
  }]);
