/*global angular, FileReader, post, FormData*/

angular.module("root", [])
    .config(function ($httpProvider) {
        "use strict";
        $httpProvider.defaults.withCredentials = true;
    })
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
                    "https://2eprazdmue.execute-api.us-east-1.amazonaws.com/prod",
                    presignedRequest
                ).then(function successCallback(response) {
                    $scope.status = "Uploading image to s3";
                    
                    var responseData, fields, postData, key, postConfig, field, uploadForm;
                    responseData = response.data;
                    fields = responseData.fields;
                    
                    postData = new FormData();
                    postData.append("key", "images/${filename}");
                    postData.append("AWSAccessKeyId", fields.AWSAccessKeyId);
                    postData.append("acl", fields.acl);
                    postData.append("policy", fields.policy);
                    postData.append("signature", fields.signature);
                    postData.append("x-amz-security-token", fields["x-amz-security-token"]);
                    postData.append("file", $scope.image);
                    postData.append("Content-Type", $scope.image.type);
                    
                    $http.post(responseData.url, postData, {
                        transformRequest: angular.identity,
                        headers: {"content-Type": undefined}
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