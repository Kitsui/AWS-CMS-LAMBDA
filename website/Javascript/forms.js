/*global angular*/

angular.module("forms", ["ui.tinymce"])
  .directive("cmsBlogForm", [function () {
    "use strict";
    return {
      templateUrl: "blog-form.html",
      replace: true
    };
  }])
  .directive("cmsPageForm", [function () {
    "use strict";
    return {
      templateUrl: "page-form.html",
      replace: true
    };
  }])
  .directive("cmsSiteSettingsForm", [function () {
    "use strict";
    return {
      templateUrl: "site-settings-form.html",
      replace: true
    };
  }])
  .directive("cmsUserRegistrationForm", [function () {
    "use strict";
    return {
      templateUrl: "user-registration-form.html",
      replace: true
    };
  }])
  .directive("cmsUserRolesForm", [function () {
    "use strict";
    return {
      templateUrl: "user-roles-form.html",
      replace: true
    };
  }]);