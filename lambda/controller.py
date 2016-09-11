"""
# controller.py
# Author: Adam Campbell
# Date: 23/06/2016
# Edited: N/D        | Miguel Saavedra
#         02/08/2016 | Chistopher Treadgold
#         05/08/2016 | Adam Campbell
#         07/08/2016 | Christopher Treadgold
#         09/09/2016 | Christopher Treadgold
"""

import json

import boto3
import botocore

# from blog           import Blog
from error          import Error
# from page           import Page
from security       import Security
# from upload_image   import UploadImage
from user           import User

def handler(event, context):
    # Get info on the cms' resources from the constants file
    with open("constants.json", "r") as resources_file:
        resources = json.loads(resources_file.read())
    
    # Extract the request body
    request_body = event["body"]
    
    # Check that a request is included
    if "request" in request_body:
        request = request_body["request"]
    else:
        Error.send_error("noRequest")
    
    # Check that the request is supported
    if not supported_request(request):
        Error.send_error("unsupportedRequest", data={"request": request})
    
    # If the request is login, attempt to login, as a token is not required
    if request == "loginUser":
        """ Request structure
            {
                request: loginUser,
                email: <str: email>,
                password: <str: password>
            }
        """
        if "email" in request_body and "password" in request_body:
            response = User.login(request_body["email"], request_body["password"],
                                  resources["USER_TABLE"], resources["TOKEN_TABLE"])
        else:
            Error.send_error("emailOrPasswordMissing")
        
        # Check if the login function returned an error
        if "error" in response:
            Error.send_error(response["error"], data=response["data"])
        
        return response
    
    # Check that a token is provided with the request
    if "token" in event:
        token = remove_prefix(event["token"])
    else:
        Error.send_error("noToken")
    
    # Check that the user has the necessary permissions to make the request
    authorized = Security.authenticate_and_authorize(
        token, request, resources["TOKEN_TABLE"], resources["USER_TABLE"]
    )
    
    # Check if authentication or authorization returned an error
    if authorized is not True and "error" in authorized:
        Error.send_error(authorized["error"], data=authorized["data"])
    
    # Process the request
    response = process_request(request_body, resources, token, request)
    
    # Check if response returned an error
    if "error" in response:
        Error.send_error(response["error"], data=response["data"])
    
    return response

def process_request(request_body, resources, token, request):
    if request == "getAllUsers":
        """ Request structure
            {
                request: getAllUsers
            }
        """
        response = User.get_all_users(resources["USER_TABLE"])
    elif request == "getUser":
        """ Request structure
            {
                request: getUser,
                email: <str: email>
            }
        """
        if not "email" in request_body:
            Error.send_error("noEmail", data={"request": request})
        
        email = request_body["email"]
        response = User.get_user(email, resources["USER_TABLE"])
    elif request == "addUser":
        """ Request structure
            {
                request: addUser,
                email: <str: email>,
                password: <str: password>,
                parmissions: <list:
                    <str: permission1>,
                    <str: permission2>,
                    <str: etc...>
                >
            }
        """
        if not "email" in request_body:
            Error.send_error("noEmail", data={"request": request})
        if not "password" in request_body:
            Error.send_error("noPassword", data={"request": request})
        if not "permissions" in request_body:
            Error.send_error("noPermissions", data={"request": request})
        
        email = request_body["email"]
        password = request_body["password"]
        permissions = request_body["permissions"]
        response = User.add_user(email, password, permissions,
                                 resources["USER_TABLE"])
    elif request == "removeUser":
        """ Request structure
            {
                request: removeUser,
                email: <str: email>
            }
        """
        if not "email" in request_body:
            Error.send_error("noEmail", data={"request": request})
        
        email = request_body["email"]
        response = User.remove_user(email, resources["USER_TABLE"])
    elif request == "logoutUser":
        """ Request structure
            {
                request: logoutUser
            }
        """
        response = User.logout(token, resources["TOKEN_TABLE"])
    else:
        Error.send_error("unsupportedRequest", data={"request": request})
    
    return response

def supported_request(request):
    supported_gets = [
        "getAllUsers", "getUser"
        # "getBlogData", "getBlogs", "editBlog", "getRoles",
        # "getPages", "getSiteSettings", "getMenuItems", "getForm",
        # "getImagePresignedPost"
    ]
    supported_posts = [
        "loginUser", "addUser"
        # "saveNewBlog", "editUser",
        # "createRole", "editRole", "createPage", "editPage", "editSiteSettings",
        # "setSiteSettings", "setMenuItems"
    ]
    supported_deletes = [
        "logoutUser", "removeUser"
        # "deleteSingleBlog", "deleteRole", "deletePage"
    ]
    supported_requests = supported_gets + supported_posts + supported_deletes
    if request in supported_requests:
        return True
    else:
        return False

def remove_prefix(cookie):
    equals_index = cookie.find("=") + 1
    return cookie[equals_index:]