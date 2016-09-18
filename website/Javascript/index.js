/*global angular*/

angular.module("index", ["forms"])
  .directive("cmsNav", [function () {
    "use strict";
    return {
      templateUrl: "navbar.html",
      replace: true
    };
  }])
  .directive("cmsExampleTable", [function () {
    "use strict";
    return {
      templateUrl: "table-sample.html",
      replace: true
    };
  }])
  .directive("cmsDashboardSample", [function () {
    "use strict";
    return {
      templateUrl: "dashboard-sample.html",
      replace: true
    };
  }]);