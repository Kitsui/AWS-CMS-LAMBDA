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
# from menu           import Menu
# from page           import Page
# from response       import Response
# from role           import Role
from security       import Security
# from ui             import UI
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
        Error.send_error("unsupportedRequest", data=request)
    
    # If the request is login, attempt to login, as a token is not required
    if request == "loginUser":
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
        token, request, resources["TOKEN_TABLE"], resources["USER_TABLE"],
        resources["ROLE_TABLE"]
    )
    
    # Check if authentication or authorization returned an error
    if "error" in authorized:
        Error.send_error(authorized["error"], data=authorized["data"])
    
    # Process the request
    response = process_request(request_body, resources, request)
    
    # Check if response returned an error
    if "error" in response:
        Error.send_error(response["error"], data=response["error"])
    
    return response

def process_request(request_body, resources, request):
    return {"data": "It worked!"}

def remove_prefix(cookie):
    equals_index = cookie.find("=") + 1
    return cookie[equals_index:]

def supported_request(request):
    supported_gets = [
        "getBlogData", "getBlogs", "editBlog", "getRoles", "getUsers",
        "getPages", "getSiteSettings", "getMenuItems", "getForm",
        "getImagePostUrl"
    ]
    supported_posts = [
        "loginUser", "logoutUser", "saveNewBlog", "registerUser", "editUser",
        "createRole", "editRole", "createPage", "editPage", "editSiteSettings",
        "setSiteSettings", "setMenuItems"
    ]
    supported_deletes = [
        "deleteSingleBlog", "deleteUser", "deleteRole", "deletePage"
    ]
    supported_requests = supported_gets + supported_posts + supported_deletes
    if request in supported_requests:
        return True
    else:
        return False
