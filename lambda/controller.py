"""
# controller.py
# Created: 23/06/2016
# Author: Adam Campbell
"""

from __future__ import print_function
import User

def handler(event, context):
	
	isAuth = True
	request = event["request"]

	# new User instance
	user = User.User(event, context)

	if isAuth:
		if request == "register":
			user.register()
		elif request == "login":
			user.login()
		elif request == "logout":
			user.logout()
	else:
		print("You are not authorized")