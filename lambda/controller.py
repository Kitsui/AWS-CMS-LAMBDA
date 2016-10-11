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
from site_settings  import Site_Settings

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
    
    if "token" in event:
        user_token = remove_prefix(event["token"])
    else:
        user_token = None
    
    """ Authenticate the request unless it is login, as login requires no
        authentication
    """
    if request != "loginUser":
        # Check that a token is provided with the request
        if user_token == None:
            Error.send_error("noToken")
        
        # Check that the user has the necessary permissions to make the request
        user_info = Security.authenticate_and_authorize(
            user_token, request, resources["TOKEN_TABLE"],
            resources["USER_TABLE"], resources["ROLE_TABLE"]
        )

        print user_info
        
        # Strip dynamo type identifiers from user info
        user_info = strip_dynamo_types(user_info)
        
        # Check if authentication or authorization returned an error
        if "error" in user_info:
            Error.send_error(authorized["error"], data=authorized["data"])
    else:
        user_info = None
    
    # Process the request
    if not user_info == None:
        response = process_request(request_body, resources, request,
                                   user_info=user_info, token=user_token)
    else:
        response = process_request(request_body, resources, request)
    
    # Check if response returned an error
    if "error" in response:
        Error.send_error(response["error"], data=response["data"])
    
    return strip_dynamo_types(response)

def process_request(request_body, resources, request, user_info=None, token=None):
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
        
        email = request_body["email"]
        password = request_body["password"]
        return User.login(email, password, token, resources["USER_TABLE"],
                          resources["TOKEN_TABLE"])
    elif request == "logoutUser":
        """ Request structure
            {
                request: logoutUser
            }
        """
        return User.logout(token, resources["TOKEN_TABLE"])
    elif request == "getPermissions":
        """ Request structure
            {
                request: logoutUser
            }
        """
        return Security.get_permissions(token, request, resources["TOKEN_TABLE"],
            resources["USER_TABLE"], resources["ROLE_TABLE"])
    elif request == "putUser":
        """ Request structure
            {
                request: putUser,
                email: <str: email>,
                username: <str: username>,
                password: <str: password>,
                roleName: <str: role name>
            }
        """
        if not "email" in request_body:
            Error.send_error("noEmail", data={"request": request})
        if not "username" in request_body:
            Error.send_error("noUsername", data={"request": request})
        if not "password" in request_body:
            Error.send_error("noPassword", data={"request": request})
        if not "roleName" in request_body:
            Error.send_error("noRoleName", data={"request": request})
        
        email = request_body["email"]
        username = request_body["username"]
        password = request_body["password"]
        role_name = request_body["roleName"]
        return User.put_user(email, username, password, role_name,
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
    elif request == "getAllRoles":
        """ Request structure
            {
                request: getAllRoles
            }
        """
        return User.get_all_roles(resources["ROLE_TABLE"])
    elif request == "getRole":
        """ Request structure
            {
                request: getRole,
                roleName: <str: role name>
            }
        """
        if not "roleName" in request_body:
            Error.send_error("noRoleName", data={"request": request})
        
        role_name = request_body["roleName"]
        return User.get_role(role_name, resources["ROLE_TABLE"])
    elif request == "putRole":
        """ Request structure
            {
                request: putRole,
                roleName: <str: role name>,
                permissions: <list:
                    <str: permission1>,
                    <str: permission2>,
                    <str: etc...>
                >
            }
        """
        if not "roleName" in request_body:
            Error.send_error("noRoleName", data={"request": request})
        if not "permissions" in request_body:
            Error.send_error("noPermissions", data={"request": request})
        
        role_name = request_body["roleName"]
        permissions = request_body["permissions"]
        return User.put_role(role_name, permissions, resources["ROLE_TABLE"])
    elif request == "deleteRole":
        """ Request structure
            {
                request: deleteRole,
                roleName: <str: role name>
            }
        """
        if not "roleName" in request_body:
            Error.send_error("noRoleName", data={"request": request})
        
        role_name = request_body["roleName"]
        return User.delete_role(role_name, resources["ROLE_TABLE"])
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
        if not "title" in request_body:
            Error.send_error("noTitle", data={"request": request})
        if not "content" in request_body:
            Error.send_error("noContent", data={"request": request})
        if not "description" in request_body:
            Error.send_error("noDescription", data={"request": request})
        if not "keywords" in request_body:
            Error.send_error("noKeywords", data={"request": request})
        
        author = user_info["Username"]
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
    elif request == "getSiteSettings":
        """ Request structure
            {
                request: getSiteSettings
            }
        """
        return Site_Settings.get_site_settings(resources["BUCKET"])
    elif request == "putSiteSettings":
        """ Request structure
            {
                request: putSiteSettings,
                siteName: <str: site name>,
                siteDescription: <str: site description>,
                facebook: <str: facebook name>,
                twitter: <str: twitter handle>,
                instagram: <str: instagram name>,
                googlePlus: <str: google plus name>,
                footer: <str: site footer>,
                disqusId: <str: disqus id>,
                googleId: <str: google id>
            }
        """
        if not "siteName" in request_body:
            Error.send_error("noSiteName", data={"request": request})
        if not "siteDescription" in request_body:
            Error.send_error("noSiteDescription", data={"request": request})
        if not "facebook" in request_body:
            Error.send_error("noFacebookName", data={"request": request})
        if not "twitter" in request_body:
            Error.send_error("noTwitterHandle", data={"request": request})
        if not "instagram" in request_body:
            Error.send_error("noInstagramName", data={"request": request})
        if not "googlePlus" in request_body:
            Error.send_error("noGooglePlusName", data={"request": request})
        if not "footer" in request_body:
            Error.send_error("noSiteFooter", data={"request": request})
        if not "disqusId" in request_body:
            Error.send_error("noDisqusId", data={"request": request})
        if not "googleId" in request_body:
            Error.send_error("noGoogleId", data={"request": request})
        
        site_name = request_body["siteName"]
        site_description = request_body["siteDescription"]
        facebook = request_body["facebook"]
        twitter = request_body["twitter"]
        instagram = request_body["instagram"]
        google_plus = request_body["googlePlus"]
        footer = request_body["footer"]
        disqus_id = request_body["disqusId"]
        google_id = request_body["googleId"]
        return Site_Settings.put_site_settings(
            site_name, site_description, facebook, twitter, instagram,
            google_plus, footer, disqus_id, google_id, resources["BUCKET"]
        )
    elif request == "getNavItems":
        """ Request structure
            {
                request: getNavItems
            }
        """
        return Site_Settings.get_nav_items(resources["BUCKET"])
    elif request == "putNavItems":
        """ Request structure
            {
                request: putNavItems,
                nav_json: <str: json>
            }
        """
        if not "nav_json" in request_body:
            Error.send_error("noNavJson", data={"request": request})
            
        nav_json = request_body["nav_json"]
        return Site_Settings.put_nav_items(nav_json, resources["BUCKET"])
    else:
        Error.send_error("unsupportedRequest", data={"request": request})


def supported_request(request):
    """Function which Returns back a boolean indicating if the request type is valid or not
    New request types need to be added to the corresponding arrays """

    supported_gets = [
        "getUser", "getAllUsers", "getAllRoles", "getRole", "getBlog",
        "getAllBlogs", "getPage", "getAllPages", "getPresignedPostImage",
        "getSiteSettings", "getNavItems"
    ]
    supported_puts = [
        "putUser", "putRole", "putBlog", "putPage", "putNavItems",
        "putSiteSettings"
    ]
    supported_posts = [
        "loginUser", "logoutUser"
    ]
    supported_deletes = [
        "deleteUser", "deleteRole", "deleteBlog", "deletePage"
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

def strip_dynamo_types(response):
    type_identifiers = [
        "S", "N", "B", "SS", "NS", "BS", "M", "L", "NULL", "BOOL"
    ]

    if type(response).__name__ == "dict":
        if len(response) == 1:
            for key in response:
                if key in type_identifiers:
                    response = strip_dynamo_types(response[key])
                else:
                    response[key] = strip_dynamo_types(response[key])
        else:
            for key in response:
                response[key] = strip_dynamo_types(response[key])
    elif type(response).__name__ == "list":
        for index in range(len(response)):
            response[index] = strip_dynamo_types(response[index])
        
    return response
