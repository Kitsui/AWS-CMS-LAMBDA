"""
# Response.py
# Created: 27/06/2016
# Author: Adam Campbell
# Edited By: Miguel Saavedra
"""

import jsonpickle

class Response(object):

	def __init__(self, status, data):
		self.status = status;
		self.data = data
		if(self.data is not None):
			self.columns = data["Items"][0].keys()

	def format(self):
		dct = {}
		i = 0
		items = []
		columns = self.data["Items"][0].keys()
		for item in self.data["Items"]:
		    i += 1
		    for col in columns:
		        items.append({col : item[col]['S']})
		        dct[i] = items
	        self.data = dct


	def to_JSON(self):
		return jsonpickle.encode(self)