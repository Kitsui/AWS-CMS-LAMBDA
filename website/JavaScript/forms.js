/*global angular, FormData, FileReader, console, dim, startLoadingAnimation, stopLoadingAnimation, alert, removeElement*/

angular.module("forms", ["api", "ngRoute"])
  .config(function ($httpProvider) {
    "use strict";
    $httpProvider.defaults.withCredentials = true;
  })
  .controller("cmsPostListCtrl", ["$scope", "$http", "$routeParams", "apiUrl", function ($scope, $http, $routeParams, apiUrl) {
    "use strict";
    var ctrlScope = this;
    ctrlScope.posts = [{title: "loading"}];

    /** Function: Delete Blog 
    Passed an ID and submits a delete request to
    Lambda. Displays a Wait animation while waiting 
    for a response. On the event of a success/failure
    a success/failure message will be displayed 
    */
    $scope.deleteBlog = function (post) {
      // get identifier Variable
      var postID = post.id;
      console.log(postID);
      // Call Delete Request        
      dim(true);
      startLoadingAnimation();
      $http.post(
        apiUrl,
        {
          "request": "deleteBlog",
          "blogID": postID
        }
      ).then(function successCallback(response) {
        // Stop animation
        stopLoadingAnimation();
        dim(false);
        console.log("Deleted Successfully");
        // Remove element from view
        removeElement('#' + postID);
      }, function errorCallback(response) {
        // Stop animation
        stopLoadingAnimation();
        dim(false);
      });
    };

    $http.post(
      apiUrl,
      {
        "request": "getAllBlogs"
      }
    ).then(function successCallback(response) {
      var blogNum, responseMessage, responseData;
      responseMessage = response.data.message;
      responseData = response.data.data;
      ctrlScope.posts = [];

      for (blogNum in responseData) {
        ctrlScope.posts.push(
          {
            title: responseData[blogNum].Title,
            author: responseData[blogNum].Author,
            description: responseData[blogNum].Description,
            keywords: responseData[blogNum].Keywords.join(", "),
            date: responseData[blogNum].SavedDate,
            id: responseData[blogNum].ID
          }
        );
      }
    }, function errorCallback(response) {
      ctrlScope.posts = [
        {
          title: response.data.error,
          author: response.data.error,
          description: response.data.error,
          keywords: response.data.error,
          date: response.data.error,
          id: response.data.error,
          counter: response.data.error
        }
      ];
    });
  }])
  .controller("cmsPageListCtrl", ["$scope", "$http", "apiUrl", function ($scope, $http, apiUrl) {
    "use strict";
    var ctrlScope = this;
    ctrlScope.pages = [{name: "loading"}];
    
    /** Function: Delete Page 
    Passed an ID and submits a delete request to
    Lambda. Displays a Wait animation while waiting 
    for a response. On the event of a success/failure
    a success/failure message will be displayed 
    */
    $scope.deletePage = function (page) {
      // get identifier Variable
      var name = page.name;
      console.log(name);
      // Call Delete Request        
      dim(true);
      startLoadingAnimation();
      $http.post(
        apiUrl,
        {
          "request": "deletePage",
          "pageName": name
        }
      ).then(function successCallback(response) {
        // Stop animation
        stopLoadingAnimation();
        dim(false);
        console.log("Deleted Successfully");
        // Remove element from view
        removeElement('#' + name);
      }, function errorCallback(response) {
        // Stop animation
        stopLoadingAnimation();
        dim(false);
      });
    };
    
    $http.post(
      apiUrl,
      {
        "request": "getAllPages"
      }
    ).then(function successCallback(response) {
      var pageNum, responseMessage, responseData;
      responseMessage = response.data.message;
      responseData = response.data.data;
      
      ctrlScope.pages = [];
      for (pageNum in responseData) {
        ctrlScope.pages.push(
          {
            name: responseData[pageNum].PageName,
            description: responseData[pageNum].Description,
            keywords: responseData[pageNum].Keywords.join(", "),
            date: responseData[pageNum].SavedDate
          }
        );
      }
    }, function errorCallback(response) {
      ctrlScope.pages = [
        {
          name: response.data.error,
          description: response.data.error,
          keywords: response.data.error,
          date: response.data.error
        }
      ];
    });
  }])
  .controller("cmsUserListCtrl", ["$scope", "$http", "apiUrl", function ($scope, $http, apiUrl) {
    "use strict";
    var ctrlScope = this;

    /** Function: Delete User 
    Passed an ID and submits a delete request to
    Lambda. Displays a Wait animation while waiting 
    for a response. On the event of a success/failure
    a success/failure message will be displayed 
    */
    $scope.deleteUser = function (user) {
      // get identifier Variable
      var email = user.email;
      console.log(email);
           // Call Delete Request        
      dim(true);
      startLoadingAnimation();
      $http.post(
        apiUrl,
        {
          "request": "deleteUser",
          "email": email
        }
      ).then(function successCallback(response) {
        // Stop animation
        stopLoadingAnimation();
        dim(false);
        console.log("Deleted Successfully");
        // Remove element from view and remove # and @ from selector
        removeElement('#' + email.replace(/[#@]/g, ""));
      }, function errorCallback(response) {
        // Stop animation
        stopLoadingAnimation();
        dim(false);
      });
    };

    ctrlScope.users = [{email: "loading"}];
    $http.post(
      apiUrl,
      {
        "request": "getAllUsers"
      }
    ).then(function successCallback(response) {
      var userNum, responseMessage, responseData;
      responseMessage = response.data.message;
      responseData = response.data.data;
      
      ctrlScope.users = [];
      for (userNum in responseData) {
        ctrlScope.users.push(
          {
            id: responseData[userNum].ID,
            email: responseData[userNum].Email,
            username: responseData[userNum].Username,
            role: responseData[userNum].Role
          }
        );
      }
    }, function errorCallback(response) {
      ctrlScope.users = [
        {
          email: response.data.error,
          username: response.data.error,
          role: response.data.error
        }
      ];
    });
  }])
  .controller("cmsRoleListCtrl", ["$scope", "$http", "apiUrl", function ($scope, $http, apiUrl) {
    "use strict";
    var ctrlScope = this;
    
    /** Function: Delete Role 
    Passed an ID and submits a delete request to
    Lambda. Displays a Wait animation while waiting 
    for a response. On the event of a success/failure
    a success/failure message will be displayed 
    */
    $scope.deleteRole = function (role) {
      // get identifier Variable
      var roleName = role.Name;
      console.log(roleName);
           // Call Delete Request        
      dim(true);
      startLoadingAnimation();
      $http.post(
        apiUrl,
        {
          "request": "deleteRole",
          "roleName": roleName
        }
      ).then(function successCallback(response) {
        // Stop animation
        stopLoadingAnimation();
        dim(false);
        console.log("Deleted Successfully");
        // Remove element from view and remove # and @ from selector
        removeElement('#' + roleName);
      }, function errorCallback(response) {
        // Stop animation
        stopLoadingAnimation();
        dim(false);
      });
    };

    ctrlScope.roles = [{roleName: "loading"}];
    $http.post(
      apiUrl,
      {
        "request": "getAllRoles"
      }
    ).then(function successCallback(response) {
      var roleNum, responseMessage, responseData;
      responseMessage = response.data.message;
      responseData = response.data.data;
      
      ctrlScope.roles = [];
      for (roleNum in responseData) {
        ctrlScope.roles.push(
          {
            roleName: responseData[roleNum].RoleName,
            permissions: responseData[roleNum].Permissions.join(", ")
          }
        );
      }
    }, function errorCallback(response) {
      ctrlScope.roles = [
        {
          roleName: response.data.error,
          permissions: response.data.error
        }
      ];
    });
  }])
  .controller("cmsBlogFormCtrl", ["$http", "$routeParams", "apiUrl", function ($http, $routeParams, apiUrl) {
    "use strict";
    var ctrlScope = this;

    ctrlScope.submitBlog = function () {
      $http.post(
        apiUrl,
        {
          "request": "putBlog",
          "title": ctrlScope.blog.title,
          "content": ctrlScope.blog.content,
          "description": ctrlScope.blog.description,
          "keywords": ctrlScope.blog.keywords.match(/\S+/g)
        }
      ).then(function successCallback(response) {
        ctrlScope.status = ("Successfully published blog: " + ctrlScope.blog.title);
      }, function errorCallback(response) {
        ctrlScope.status = response.data.error;
      });
    };
  }])
  .controller("cmsVisitorNavFormCtrl", ["$http", "apiUrl", function ($http, apiUrl) {
    "use strict";
    var ctrlScope = this;
    
    ctrlScope.submitNav = function () {
      var str, isJson;
      
      str = ctrlScope.nav_json;
      isJson = function (str) {
        try {
          JSON.parse(str);
        } catch (e) {
          return false;
        }
        return true;
      };
      
      if (isJson(str)) {
        $http.post(
          apiUrl,
          {
            "request": "putNavItems",
            "nav_json": str.replace(/(\r\n|\n|\r)/gm, "")
          }
        ).then(function successCallback(response) {
          ctrlScope.status = ("Successfully published nav items");
          alert("Successfully published nav items");
        }, function errorCallback(response) {
          ctrlScope.status = response.data.error;
          alert("Unable to publish nav items");
        });
      } else {
        alert("Not valid JSON");
      }
    };

    $http.post(
      apiUrl,
      {
        "request": "getNavItems"
      }
    ).then(function successCallback(response) {

      var navJson = response.data.data;

      // Remove escaped double quotes
      navJson = navJson.replace(/\\"/g, '"');

      // Remove first and last double quotes
      if (navJson.charAt(0) === "\"" && navJson.charAt(navJson.length - 1 === "\"")) {
        navJson = navJson.substr(1, navJson.length - 2);
      }

      navJson = JSON.parse(navJson);

      ctrlScope.nav_json = JSON.stringify(navJson, null, 4);

    }, function errorCallback(response) {
      ctrlScope.nav = [
        {
          nav_json: response.data.error
        }
      ];
    });
  }])
  .controller("cmsPageFormCtrl", ["$http", "$routeParams", "apiUrl", function ($http, $routeParams, apiUrl) {
    "use strict";
    var ctrlScope = this;
    ctrlScope.retrieving = false;
    ctrlScope.header = "New Page";
    ctrlScope.namePlaceholder = "Page name";
    ctrlScope.descriptionPlaceholder = "Description";
    ctrlScope.keywordsPlaceholder = "Keywords";
    
    ctrlScope.submitPage = function () {
      $http.post(
        apiUrl,
        {
          "request": "putPage",
          "pageName": ctrlScope.page.name,
          "content": ctrlScope.page.content,
          "description": ctrlScope.page.description,
          "keywords": ctrlScope.page.keywords.match(/\S+/g)
        }
      ).then(function successCallback(response) {
        ctrlScope.status = ("Successfully published page: " + ctrlScope.page.name);
      }, function errorCallback(response) {
        ctrlScope.status = response.data.error;
      });
    };
    
    if ($routeParams.pageName !== undefined) {
      ctrlScope.editing = true;
      ctrlScope.retrieving = true;
      ctrlScope.header = "Edit Page";
      ctrlScope.namePlaceholder = "Retrieving...";
      ctrlScope.descriptionPlaceholder = "Retrieving...";
      ctrlScope.keywordsPlaceholder = "Retrieving...";
      $http.post(
        apiUrl,
        {
          "request": "getPage",
          "pageName": $routeParams.pageName
        }
      ).then(function successCallback(response) {
        ctrlScope.retrieving = false;
        ctrlScope.page = {
          name: response.data.PageName,
          description: response.data.Description,
          keywords: response.data.Keywords.join(" "),
          content: response.data.Content
        };
      });
    }
  }])
  .controller("cmsUserFormCtrl", ["$http", "$routeParams", "apiUrl", function ($http, $routeParams, apiUrl) {
    "use strict";
    var ctrlScope = this;
    
    ctrlScope.submitUser = function () {
      if (ctrlScope.user.password !== ctrlScope.user.passwordConfirm) {
        ctrlScope.status = "Password confirmation does not match password";
        return;
      }
      
      $http.post(
        apiUrl,
        {
          "request": "putUser",
          "email": ctrlScope.user.email,
          "username": ctrlScope.user.username,
          "password": ctrlScope.user.password,
          "roleName": ctrlScope.user.roleName
        }
      ).then(function successCallback(response) {
        ctrlScope.status = ("Successfully registered user: " + ctrlScope.user.username);
      }, function errorCallback(response) {
        ctrlScope.status = response.data.error;
      });
    };
  }])
  .controller("cmsRoleFormCtrl", ["$http", "$routeParams", "apiUrl", function ($http, $routeParams, apiUrl) {
    "use strict";
    var ctrlScope = this;
    ctrlScope.retrieving = false;
    ctrlScope.header = "New Role";
    ctrlScope.namePlaceholder = "Role name";
    ctrlScope.permissionsPlaceholder = "Permissions";
    
    ctrlScope.submitRole = function () {
      $http.post(
        apiUrl,
        {
          "request": "putRole",
          "roleName": ctrlScope.role.roleName,
          "permissions": ctrlScope.role.permissions.match(/\S+/g)
        }
      ).then(function successCallback(response) {
        ctrlScope.status = ("Successfully added role: " + ctrlScope.role.roleName);
      }, function errorCallback(response) {
        ctrlScope.status = response.data.error;
      });
    };
    
    if ($routeParams.roleName !== undefined) {
      ctrlScope.editing = true;
      ctrlScope.retrieving = true;
      ctrlScope.header = "Edit Role";
      ctrlScope.namePlaceholder = "Retrieving...";
      ctrlScope.permissionsPlaceholder = "Retrieving...";
      $http.post(
        apiUrl,
        {
          "request": "getRole",
          "roleName": $routeParams.roleName
        }
      ).then(function successCallback(response) {
        ctrlScope.retrieving = false;
        ctrlScope.role = {
          roleName: response.data.data.RoleName,
          permissions: response.data.data.Permissions.join(" ")
        };
      });
    }
  }])
  .controller("cmsSettingsFormCtrl", ["$http", "apiUrl", function ($http, apiUrl) {
    "use strict";
    var ctrlScope = this;
    ctrlScope.retrieving = true;
    ctrlScope.namePlaceholder = "Retrieving...";
    ctrlScope.descriptionPlaceholder = "Retrieving...";
    ctrlScope.facebookNamePlaceholder = "Retrieving...";
    ctrlScope.twitterHandlePlaceholder = "Retrieving...";
    ctrlScope.instagramNamePlaceholder = "Retrieving...";
    ctrlScope.googlePlusNamePlaceholder = "Retrieving...";
    ctrlScope.disqusIdPlaceholder = "Retrieving...";
    ctrlScope.googleIdPlaceholder = "Retrieving...";
    
    ctrlScope.submitSettings = function () {
      ctrlScope.retrieving = true;
      
      var siteName, siteDescription, facebook, twitter, instagram, googlePlus, footer, disqusId, googleId;
      
      if (ctrlScope.name !== undefined) { siteName = ctrlScope.name; } else { siteName = ""; }
      if (ctrlScope.description !== undefined) { siteDescription = ctrlScope.description; } else { siteDescription = ""; }
      if (ctrlScope.facebookName !== undefined) { facebook = ctrlScope.facebookName; } else { facebook = ""; }
      if (ctrlScope.twitterHandle !== undefined) { twitter = ctrlScope.twitterHandle; } else { twitter = ""; }
      if (ctrlScope.instagramName !== undefined) { instagram = ctrlScope.instagramName; } else { instagram = ""; }
      if (ctrlScope.googlePlusName !== undefined) { googlePlus = ctrlScope.googlePlusName; } else { googlePlus = ""; }
      if (ctrlScope.footer !== undefined) { footer = ctrlScope.footer; } else { footer = ""; }
      if (ctrlScope.disqusId !== undefined) { disqusId = ctrlScope.disqusId; } else { disqusId = ""; }
      if (ctrlScope.googleId !== undefined) { googleId = ctrlScope.googleId; } else { googleId = ""; }
      
      $http.post(
        apiUrl,
        {
          "request": "putSiteSettings",
          "siteName": siteName,
          "siteDescription": siteDescription,
          "facebook": facebook,
          "twitter": twitter,
          "instagram": instagram,
          "googlePlus": googlePlus,
          "footer": footer,
          "disqusId": disqusId,
          "googleId": googleId
        }
      ).then(function successCallback(response) {
        ctrlScope.retrieving = false;
      }).then(function errorCallback(response) {
        ctrlScope.retrieving = false;
      });
    };
    
    $http.post(
      apiUrl,
      {
        "request": "getSiteSettings"
      }
    ).then(function successCallback(response) {
      ctrlScope.retrieving = false;
      ctrlScope.namePlaceholder = "Name";
      ctrlScope.descriptionPlaceholder = "Description";
      ctrlScope.facebookNamePlaceholder = "Facebook name";
      ctrlScope.twitterHandlePlaceholder = "Twitter handle";
      ctrlScope.instagramNamePlaceholder = "Instagram name";
      ctrlScope.googlePlusNamePlaceholder = "Google plus name";
      ctrlScope.disqusIdPlaceholder = "Disqus id";
      ctrlScope.googleIdPlaceholder = "Google id";
      
      ctrlScope.name = response.data.site_name;
      ctrlScope.description = response.data.site_description;
      ctrlScope.footer = response.data.footer;
      ctrlScope.facebookName = response.data.facebook;
      ctrlScope.twitterHandle = response.data.twitter;
      ctrlScope.instagramName = response.data.instagram;
      ctrlScope.googlePlusName = response.data.google_plus;
      ctrlScope.disqusId = response.data.disqus_id;
      ctrlScope.googleId = response.data.google_id;
    });
  }])
  .controller("cmsVisitorNavFormCtrl", ["$http", "$routeParams", "apiUrl", function ($http, $routeParams, apiUrl) {
    "use strict";
    var ctrlScope = this;
    
    ctrlScope.submitNav = function () {
      $http.post(
        apiUrl,
        {
          "request": "putNavItems",
          "nav_items": [
            {
              "title": ctrlScope.nav_item.title,
              "url": ctrlScope.nav_item.url,
              "children": []
            }
          ]
        }
      ).then(function successCallback(response) {
        ctrlScope.status = ("Successfully published nav items");
      }, function errorCallback(response) {
        ctrlScope.status = response.data.error;
      });
    };
  }])
  .controller("cmsUploadImageCtrl", ["$http", "apiUrl", "$scope", function ($http, apiUrl, $scope) {
    "use strict";
    var ctrlScope = this;
    var reader = new FileReader();
    reader.onload = function (event) {
      ctrlScope.imageUrl = event.target.result;
      $scope.$apply();
    }
    
    ctrlScope.refreshPreview = function () {
      if (ctrlScope.image instanceof Blob) {
        reader.readAsDataURL(ctrlScope.image);
      }
    };
    
    ctrlScope.upload = function () {
      if (ctrlScope.image === undefined) {
        ctrlScope.status = "No image selected";
        return;
      }
      ctrlScope.contentType = ctrlScope.image.type;
      
      waitingDialog.show("Fetching presigned URL");

      var presignedRequest = {
        "request": "getPresignedPostImage",
        "filename": ctrlScope.image.name,
        "acl": "public-read"
      };

      $http.post(
        apiUrl,
        presignedRequest,
        {
          withCredentials: true
        }
      ).then(function successCallback(response) {
        waitingDialog.update("Uploading image to s3");

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
          waitingDialog.update("Successfully uploaded " + ctrlScope.image.name);
          setTimeout(waitingDialog.hide, 1000);
        }, function errorCallback(response) {
          var error = "Something went wrong";
          if (response.hasOwnProperty("data.error")) {
            error = respone.data.error;
          }
          waitingDialog.update(error);
          setTimeout(waitingDialog.hide, 1000);
        });
      }, function errorCallback(response) {
        var error = "";
        if (response.hasOwnProperty("data.error")) {
          error = respone.data.error;
        }
        waitingDialog.update("Unable to fetch presigned URL" + error);
        setTimeout(waitingDialog.hide, 1000);
      });
    };
  }])
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
  .filter("split", function () {
    return function(input) {
    return inputval = input.replace(/[#@]/g, "");
  }});

/**
 * Utility Functions
 */




/**
 * Dims the screen
 */
var dim = function (bool)
{
    if (typeof bool=='undefined') bool=true; // so you can shorten dim(true) to dim()
    document.getElementById('dimmer').style.display=(bool?'block':'none');
}    

  /**
 * Loading animation function which summons a loading
 * wheel in a DOM element selected by id
 */
var startLoadingAnimation =  function () {
    var opts = {
      lines: 13 // The number of lines to draw
      , length: 0 // The length of each line
      , width: 19 // The line thickness
      , radius: 42 // The radius of the inner circle
      , scale: 1 // Scales overall size of the spinner
      , corners: 0.6 // Corner roundness (0..1)
      , color: '#FFF' // #rgb or #rrggbb or array of colors
      , opacity: 0.05 // Opacity of the lines
      , rotate: 0 // The rotation offset
      , direction: 1 // 1: clockwise, -1: counterclockwise
      , speed: 1.7 // Rounds per second
      , trail: 61 // Afterglow percentage
      , fps: 20 // Frames per second when using setTimeout() as a fallback for CSS
      , zIndex: 2e9 // The z-index (defaults to 2000000000)
      , className: 'spinner' // The CSS class to assign to the spinner
      , top: '50%' // Top position relative to parent
      , left: '50%' // Left position relative to parent
      , shadow: false // Whether to render a shadow
      , hwaccel: false // Whether to use hardware acceleration
      , position: 'absolute' // Element positioning
    }
    var target = document.getElementById('page-wrapper')
    var spinner = new Spinner(opts).spin(target);
};

/**
 * Stops loading animation
 */
var stopLoadingAnimation = function () {
    $('.spinner').remove();
}

/**
 * Removes element by ID
 */
var removeElement = function (id) {
    $(id).remove();
}

/**
 * Adds an attribute to an element in the DOM
 */
var addAttribute = function (element, attribute, type) {
  var myEl = angular.element( document.querySelector( element ) );
  // Check type and apply attribute
  if (type == "class") {
    myEl.addClass(attribute);
  }
  else if (type == "id") {
    myEl.addIDToElement(attribute);
  }
}




/**
 * Module for displaying "Waiting for..." dialog using Bootstrap
 *
 * @author Eugene Maslovich <ehpc@em42.ru>
 */

var waitingDialog = waitingDialog || (function ($) {
    'use strict';

	// Creating modal dialog's DOM
	var $dialog = $(
		'<div class="modal fade" data-backdrop="static" data-keyboard="false" tabindex="-1" role="dialog" aria-hidden="true" style="padding-top:15%; overflow-y:visible;">' +
		'<div class="modal-dialog modal-m">' +
		'<div class="modal-content">' +
			'<div class="modal-header"><h3 style="margin:0;"></h3></div>' +
			'<div class="modal-body">' +
				'<div class="progress progress-striped active" style="margin-bottom:0;"><div class="progress-bar" style="width: 100%"></div></div>' +
			'</div>' +
		'</div></div></div>');

	return {
		/**
		 * Opens our dialog
		 * @param message Custom message
		 * @param options Custom options:
		 * 				  options.dialogSize - bootstrap postfix for dialog size, e.g. "sm", "m";
		 * 				  options.progressType - bootstrap postfix for progress bar type, e.g. "success", "warning".
		 */
		show: function (message, options) {
			// Assigning defaults
			if (typeof options === 'undefined') {
				options = {};
			}
			if (typeof message === 'undefined') {
				message = 'Loading';
			}
			var settings = $.extend({
				dialogSize: 'm',
				progressType: '',
				onHide: null // This callback runs after the dialog was hidden
			}, options);

			// Configuring dialog
			$dialog.find('.modal-dialog').attr('class', 'modal-dialog').addClass('modal-' + settings.dialogSize);
			$dialog.find('.progress-bar').attr('class', 'progress-bar');
			if (settings.progressType) {
				$dialog.find('.progress-bar').addClass('progress-bar-' + settings.progressType);
			}
			$dialog.find('h3').text(message);
			// Adding callbacks
			if (typeof settings.onHide === 'function') {
				$dialog.off('hidden.bs.modal').on('hidden.bs.modal', function (e) {
					settings.onHide.call($dialog);
				});
			}
			// Opening dialog
			$dialog.modal();
		},
		/**
		 * Closes dialog
		 */
		hide: function () {
			$dialog.modal('hide');
		},
        update: function (message) {
          $dialog.find('h3').text(message);
        }
	};

})(jQuery);
