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
			if(data["Items"][0] is not None):
				self.columns = data["Items"][0].keys()


	def format(self):
		replyData = {}
		colm = []
		rows = []

		item = {}
		columns = self.data["Items"][0].keys()
		for i in self.data["Items"]:
			item["ID"] = (i['BlogID']['S'])
			item["Title"] = (i['Title']['S'])
			item["Author"] = (i['Author']['S'])
			item["Content"] = (i['Content']['S'])
			item["Meta_Description"] = (i['MetaDescription']['S'])
			item["Meta_Keywords"] = (i['MetaKeywords']['S'])
			item["Save_Date"] = (i['SavedDate']['S'])
			rows.append(item)
		replyData["rows"] = rows
		replyData["columns"] = columns
		return replyData

	def to_JSON(self):
		return jsonpickle.encode(self)