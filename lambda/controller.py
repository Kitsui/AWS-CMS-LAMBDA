"""
# controller.py
# Created: 23/06/2016
# Author: Adam Campbell
# Edited By: Miguel Saavedra
"""

import User
import Blog
import Page
from Response import Response
import boto3
import botocore
from boto3.dynamodb.conditions import Key, Attr

def handler(event, context):

	isAuth = False
	request = event["params"]["request"]
	# Authentication check token
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
	user = User.User(event["params"], context)
	blog = Blog.Blog(event["params"], context)
	page = Page.Page(event["params"], context)

	# Map request type to function calls
	functionMapping = {
		
		"getBlogData": blog.get_blog_data,
		"getBlogs": blog.get_all_blogs,
		"editBlog": blog.edit_blog,
		"saveNewBlog": blog.save_new_blog,
		"deleteSingleBlog": blog.delete_blog,
		"registerUser": user.register,
		"loginUser": user.login,
		"logoutUser": user.logout,
		"editUser": user.edit_user,
		"deleteUser": user.delete_user,
		"createRole": user.create_role,
		"editRole": user.edit_role,
		"deleteRole": user.delete_role,
		"createPage": page.create_page,
		"deletePage": page.delete_page
	}

	if isAuth:
		return functionMapping[request]()
	else:
		response = Response("Authentication_Error", None)
		return response.to_JSON()
	
