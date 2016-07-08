"""
# Json_Handler.py
# Created: 5/07/2016
# Author: Miguel Saavedra
"""

import jsonpickle

class Json_handler(object):

	def __init__(self, data):
		self.data = data

	def to_JSON(self):
		return jsonpickle.encode(self)