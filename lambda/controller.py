"""
# controller.py
# Created: 23/06/2016
# Author: Adam Campbell
"""

import User
import Blog

def handler(event, context):
	
	isAuth = True
	request = event["request"]

	# Custom object instances
	user = User.User(event, context)
	blog = Blog.Blog(event, context)

	# Map request type to function calls
	functionMapping = {
		"getBlogs": blog.get_all_blogs,
		"saveNewBlog": blog.save_new_blog,
		"registerUser": user.register,
		"loginUser": user.login,
		"logoutUser": user.logout
	}

	if isAuth:
		functionMapping[request]()
	else:
		print "You are not authorized"