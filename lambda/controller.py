"""
# controller.py
# Author: Adam Campbell
# Date: 23/06/2016
# Edited: N/D        | Miguel Saavedra
#         02/08/2016 | Chistopher Treadgold
#         05/08/2016 | Adam Campbell
"""

import boto3
import botocore
from boto3.dynamodb.conditions import Attr, Key

from blog import Blog
from page import Page
from response import Response
from user import User
from role import Role

def handler(event, context):

	isAuth = False
	request = event["params"]["request"]
	# Check authentication token
	if(request != "loginUser"):
		try:
			dynamodb = boto3.resource('dynamodb')
			table = dynamodb.Table('Token')
			auth = table.query(KeyConditionExpression=
				Key('TokenString').eq(event["params"]["token"]))
		except botocore.exceptions.ClientError as e:
			print e.response['Error']['Code']
			response = Response("Error", None)
			return response.to_JSON()
		if(len(auth['Items']) > 0):
			isAuth = True
	elif request == "loginUser":
		isAuth = True

	# Custom object instances
	user = User(event["params"], context)
	blog = Blog(event["params"], context)
	page = Page(event["params"], context)
	role = Role(event["params"], context)

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
		"deletePage": page.delete_page
	}

	if isAuth:
		return functionMapping[request]()
	else:
		response = Response("Authentication_Error", None)
		return response.to_JSON()
