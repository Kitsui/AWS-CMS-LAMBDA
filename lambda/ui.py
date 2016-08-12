"""
# ui.py
# Author: Adam Campbell
# Date: 12/08/2016
"""

class UI(object):

    def __init__(self, event, context):
        self.event = event
        self.context = context
        with open("constants.json", "r") as constants_file:
            self.constants = json.loads(constants_file.read())

    def getTable(self, page_name):
    	pass

    def getForm(self):
        pass


        