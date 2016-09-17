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

from blog           import Blog
from error          import Error
from page           import Page
from security       import Security
from s3_upload      import S3Upload
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
    
    """ Authenticate the request unless it is login, as login requires no
        authentication
    """
    if request != "loginUser":
        # Check that a token is provided with the request
        if "token" in event:
            user_token = remove_prefix(event["token"])
        else:
            Error.send_error("noToken")
        
        # Check that the user has the necessary permissions to make the request
        authorized = Security.authenticate_and_authorize(
            user_token, request, resources["TOKEN_TABLE"], resources["USER_TABLE"]
        )
        
        # Check if authentication or authorization returned an error
        if authorized is not True and "error" in authorized:
            Error.send_error(authorized["error"], data=authorized["data"])
    
    # Process the request
    if "token" in event:
        response = process_request(request_body, resources, request,
                                   token=user_token)
    else:
        response = process_request(request_body, resources, request)
    
    # Check if response returned an error
    if "error" in response:
        Error.send_error(response["error"], data=response["data"])
    
    return response

def process_request(request_body, resources, request, token=None):
    if request == "getAllUsers":
        """ Request structure
            {
                request: getAllUsers
            }
        """
        return User.get_all_users(resources["USER_TABLE"])
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
        return User.get_user(email, resources["USER_TABLE"])
    elif request == "loginUser":
        """ Request structure
            {
                request: loginUser,
                email: <str: email>,
                password: <str: password>
            }
        """
        if not "email" in request_body:
            Error.send_error("noEmail", data={"request": request})
        if not "password" in request_body:
            Error.send_error("noPassword", data={"request": request})
        
        return User.login(request_body["email"], request_body["password"],
                          resources["USER_TABLE"], resources["TOKEN_TABLE"])
    elif request == "logoutUser":
        """ Request structure
            {
                request: logoutUser
            }
        """
        return User.logout(token, resources["TOKEN_TABLE"])
    elif request == "putUser":
        """ Request structure
            {
                request: putUser,
                email: <str: email>,
                username: <str: username>,
                password: <str: password>,
                userType: <str: user type>,
                parmissions: <list:
                    <str: permission1>,
                    <str: permission2>,
                    <str: etc...>
                >
            }
        """
        if not "email" in request_body:
            Error.send_error("noEmail", data={"request": request})
        if not "username" in request_body:
            Error.send_error("noUsername", data={"request": request})
        if not "password" in request_body:
            Error.send_error("noPassword", data={"request": request})
        if not "userType" in request_body:
            Error.send_error("noUserType", data={"request": request})
        if not "permissions" in request_body:
            Error.send_error("noPermissions", data={"request": request})
        
        email = request_body["email"]
        username = request_body["username"]
        password = request_body["password"]
        user_type = request_body["userType"]
        permissions = request_body["permissions"]
        return User.put_user(email, username, password, user_type, permissions,
                             resources["USER_TABLE"])
    elif request == "deleteUser":
        """ Request structure
            {
                request: deleteUser,
                email: <str: email>
            }
        """
        if not "email" in request_body:
            Error.send_error("noEmail", data={"request": request})
        
        email = request_body["email"]
        return User.delete_user(email, resources["USER_TABLE"])
    elif request == "getAllBlogs":
        """ Request structure
            {
                request: getAllBlogs
            }
        """
        return Blog.get_all_blogs(resources["BLOG_TABLE"])
    elif request == "getBlog":
        """ Request structure
            {
                request: getBlog,
                blogID: <str: blog id>
            }
        """
        if not "blogID" in request_body:
            Error.send_error("noBlogID", data={"request": request})
        
        blog_id = request_body["blogID"]
        return Blog.get_blog(blog_id, resources["BLOG_TABLE"])
    elif request == "putBlog":
        """ Request structure
            {
                request: putBlog,
                author: <str: author>,
                title: <str: title>,
                content: <str: content>,
                description: <str: description>,
                keywords: <list:
                    <str: keyword1>,
                    <str: keyword2>,
                    <str: etc...>
                >
            }
        """
        if not "author" in request_body:
            Error.send_error("noAuthor", data={"request": request})
        if not "title" in request_body:
            Error.send_error("noTitle", data={"request": request})
        if not "content" in request_body:
            Error.send_error("noContent", data={"request": request})
        if not "description" in request_body:
            Error.send_error("noDescription", data={"request": request})
        if not "keywords" in request_body:
            Error.send_error("noKeywords", data={"request": request})
        
        author = request_body["author"]
        title = request_body["title"]
        content = request_body["content"]
        description = request_body["description"]
        keywords = request_body["keywords"]
        return Blog.put_blog(author, title, content, description, keywords,
                             resources["BLOG_TABLE"], resources["BUCKET"])
    elif request == "deleteBlog":
        """ Request structure
            {
                request: deleteBlog,
                blogID: <str: blog id>
            }
        """
        if not "blogID" in request_body:
            Error.send_error("noBlogID", data={"request": request})
        
        blog_id = request_body["blogID"]
        return Blog.delete_blog(blog_id, resources["BLOG_TABLE"],
                                resources["BUCKET"])
    elif request == "getAllPages":
        """ Request structure
            {
                request: getAllPages
            }
        """
        return Page.get_all_pages(resources["PAGE_TABLE"])
    elif request == "getPage":
        """ Request structure
            {
                request: getBlog,
                pageName: <str: page name>
            }
        """
        if not "pageName" in request_body:
            Error.send_error("noPageName", data={"request": request})
        
        page_name = request_body["pageName"]
        return Page.get_page(page_name, resources["PAGE_TABLE"])
    elif request == "putPage":
        """ Request structure
            {
                request: putPage,
                pageName: <str: page name>,
                content: <str: content>,
                description: <str: description>,
                keywords: <list:
                    <str: keyword1>,
                    <str: keyword2>,
                    <str: etc...>
                >
            }
        """
        if not "pageName" in request_body:
            Error.send_error("noPageName", data={"request": request})
        if not "content" in request_body:
            Error.send_error("noContent", data={"request": request})
        if not "description" in request_body:
            Error.send_error("noDescription", data={"request": request})
        if not "keywords" in request_body:
            Error.send_error("noKeywords", data={"request": request})
        
        page_name = request_body["pageName"]
        content = request_body["content"]
        description = request_body["description"]
        keywords = request_body["keywords"]
        return Page.put_page(page_name, content, description, keywords,
                             resources["PAGE_TABLE"], resources["BUCKET"])
    elif request == "deletePage":
        """ Request structure
            {
                request: deletePage,
                pageName: <str: page name>
            }
        """
        if not "pageName" in request_body:
            Error.send_error("noPageName", data={"request": request})
        
        page_name = request_body["pageName"]
        return Page.delete_page(page_name, resources["PAGE_TABLE"],
                                resources["BUCKET"])
    elif request == "getPresignedPostImage":
        """ Request structure
            {
                request: getPresignedPostImage,
                filename: <str: filename>,
                acl: <str: acl>
            }
        """
        if not "filename" in request_body:
            Error.send_error("noFilename", data={"request": request})
        if not "acl" in request_body:
            Error.send_error("noAcl", data={"request": request})
        
        filename = request_body["filename"]
        acl = request_body["acl"]
        return S3Upload.get_presigned_post_image(filename, acl,
                                                 resources["BUCKET"])
    else:
        Error.send_error("unsupportedRequest", data={"request": request})

def supported_request(request):
    supported_gets = [
        "getUser", "getAllUsers", "getBlog", "getAllBlogs", "getPage",
        "getAllPages", "getPresignedPostImage"
    ]
    supported_puts = [
        "putUser", "putBlog", "putPage"
    ]
    supported_posts = [
        "loginUser", "logoutUser"
    ]
    supported_deletes = [
        "deleteUser", "deleteBlog", "deletePage"
    ]
    supported_requests = (supported_gets + supported_puts + supported_posts
        + supported_deletes)
    if request in supported_requests:
        return True
    else:
        return False

def remove_prefix(cookie):
    equals_index = cookie.find("=") + 1
    return cookie[equals_index:]