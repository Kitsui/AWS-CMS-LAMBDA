/*global angular, FileReader, post, FormData*/

angular.module("root", [])
  .controller("index", ["$scope", "$http",
    function ($scope, $http) {
      "use strict";
      $scope.status = null;
      $scope.upload = function () {
        if ($scope.image === undefined) {
          $scope.status = "No image selected";
          return;
        }
        $scope.contentType = $scope.image.type;
        
        $scope.status = "Fetching presigned URL";
        
        var presignedRequest = {
          "request": "uploadImage",
          "fileName": $scope.image.name,
          "acl": "public-read"
        };
        
        $http.post(
          "https://i5q0xhg2lg.execute-api.us-east-1.amazonaws.com/prod",
          presignedRequest,
          {
            withCredentials: true
          }
        ).then(function successCallback(response) {
          $scope.status = "Uploading image to s3";
          
          var responseData, fields, postData, key, postConfig, field, uploadForm;
          responseData = response.data;
          fields = responseData.fields;
          
          postData = new FormData();
          postData.append("key", fields.key);
          postData.append("Content-Type", $scope.image.type);
          postData.append("AWSAccessKeyId", fields.AWSAccessKeyId);
          postData.append("acl", fields.acl);
          postData.append("policy", fields.policy);
          postData.append("signature", fields.signature);
          postData.append("x-amz-security-token", fields["x-amz-security-token"]);
          postData.append("file", $scope.image);
          
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
            $scope.status = "Successfully uploaded " + $scope.image.name;
          }, function errorCallback(response) {
            $scope.status = response;
          });
        }, function errorCallback(response) {
          $scope.status = "Unable to fetch presigned URL";
        });
      };
    }])
  .directive('fileModel', [
    '$parse',
    function ($parse) {
      "use strict";
      return {
        restrict: 'A',
        link: function (scope, element, attrs) {
          var model, modelSetter;
          model = $parse(attrs.fileModel);
          modelSetter = model.assign;
          element.bind('change', function () {
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
  ]);