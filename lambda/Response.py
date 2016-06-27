"""
# Response.py
# Created: 27/06/2016
# Author: Adam Campbell
"""

import jsonpickle

class Response(object):

	def __init__(self, status):
		self.status = status;

	def to_JSON(self):
		return jsonpickle.encode(self)