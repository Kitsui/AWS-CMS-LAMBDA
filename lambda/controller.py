"""
# controller.py
# Author: Adam Campbell
# Date: 23/06/2016
# Edited: N/D        | Miguel Saavedra
#         02/08/2016 | Chistopher Treadgold
#         05/08/2016 | Adam Campbell
#         07/08/2016 | Christopher Treadgold
"""

import json

import boto3
import botocore
from boto3.dynamodb.conditions import Attr, Key

from blog import Blog
from page import Page
from response import Response
from user import User
from role import Role
from security import Security

def handler(event, context):
    # Custom object instances
    user = User(event["params"], context)
    blog = Blog(event["params"], context)
    page = Page(event["params"], context)
    role = Role(event["params"], context)
    security = Security(event["params"], context)

    # Map request type to function calls
    functionMapping = {
        "getBlogData": blog.get_blog_data,
        "getBlogs": blog.get_all_blogs,
        "editBlog": blog.edit_blog,
        "saveNewBlog": blog.save_new_blog,
        "deleteSingleBlog": blog.delete_blog,
        "getUsers": user.get_all_users,
        "registerUser": user.register,
        "loginUser": user.login,
        "logoutUser": user.logout,
        "editUser": user.edit_user,
        "deleteUser": user.delete_user,
        #"getRoles": role.get_all_roles,
        "createRole": role.create_role,
        "editRole": role.edit_role,
        "deleteRole": role.delete_role,
        "getPages": page.get_all_pages,
        "createPage": page.create_page,
        "deletePage": page.delete_page,
        "editPage": page.edit_page,
        "getSiteSettings": page.get_site_settings,
        "setSiteSettings": page.set_site_settings
    }

    # Get constants created by setup.py
    with open("constants.json", "r") as constants_file:
        constants = json.loads(constants_file.read())

    is_authenticated = False
    request = event["params"]["request"]
    
    # Check authentication token
    if request == "loginUser":
        is_authenticated = True
    else:
        is_authenticated = security.authenticate()





    if is_authenticated:
        return functionMapping[request]()
    else:
        response = Response("Authentication_Error", None)
        return response.to_JSON()

"""
    # Adams concept for request & requestUI handlers
    # Note: if request or requestUI relates to login, then simply allow
    
    # if request == "loginUser" or requestUI == "login":
        # do login work
    # elif is_authenticated:
        # if is_authorized:
            # if request != "undefined":
                # data =  functionMapping[request]()
            # if requestUI != "undefined":
                # data = ui.getForm(requestUI, data)

            # return data
        # response = Response("Authorization_Error", None)
        # return response.to_JSON()
    # else:
    #    response = Response("Authentication_Error", None)
    #    return response.to_JSON()
"""