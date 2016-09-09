/*global angular, FileReader, post, FormData*/

angular.module("root", [])
  .directive("fileModel", [
    "$parse",
    function ($parse) {
      "use strict";
      return {
        restrict: "A",
        link: function (scope, element, attrs) {
          var model, modelSetter;
          model = $parse(attrs.fileModel);
          modelSetter = model.assign;
          element.bind("change", function () {
            scope.$apply(function () {
              if (attrs.multiple) {
                modelSetter(scope, element[0].files);
              } else {
                modelSetter(scope, element[0].files[0]);
              }
            });
          });
        }
      };
    }
  ])
  .directive("cmsUploadForm", ["$http", function ($http) {
    "use strict";
    return {
      http: $http,
      templateUrl: "cms_upload_form.html",
      replace: true,
      controller: "cmsUploadFormCtrl",
      controllerAs: "uploadCtrl"
    };
  }])
  .controller("cmsUploadFormCtrl", function ($http) {
    "use strict";
    var ctrlScope = this;
    ctrlScope.upload = function () {
      if (ctrlScope.image === undefined) {
        ctrlScope.status = "No image selected";
        return;
      }
      ctrlScope.contentType = ctrlScope.image.type;

      ctrlScope.status = "Fetching presigned URL";

      var presignedRequest = {
        "request": "uploadImage",
        "fileName": ctrlScope.image.name,
        "acl": "public-read"
      };

      $http.post(
        "$(API_URL)",
        presignedRequest,
        {
          withCredentials: true
        }
      ).then(function successCallback(response) {
        ctrlScope.status = "Uploading image to s3";

        var responseData, fields, postData, key, postConfig, field, uploadForm;
        responseData = response.data;
        fields = responseData.fields;

        postData = new FormData();
        postData.append("key", fields.key);
        postData.append("Content-Type", ctrlScope.image.type);
        postData.append("AWSAccessKeyId", fields.AWSAccessKeyId);
        postData.append("acl", fields.acl);
        postData.append("policy", fields.policy);
        postData.append("signature", fields.signature);
        postData.append("x-amz-security-token", fields["x-amz-security-token"]);
        postData.append("file", ctrlScope.image);

        $http({
          method: "POST",
          url: responseData.url,
          data: postData,
          headers: {"Content-Type": undefined,
                    "Cache-Control": "max-age=0",
                    "Upgrade-Insecure-Requests": "1"},
          transformRequest: angular.identity,
          withCredentials: false
        }).then(function successCallback(response) {
          ctrlScope.status = "Successfully uploaded " + ctrlScope.image.name;
        }, function errorCallback(response) {
          ctrlScope.status = response;
        });
      }, function errorCallback(response) {
        ctrlScope.status = "Unable to fetch presigned URL";
      });
    };
  });
