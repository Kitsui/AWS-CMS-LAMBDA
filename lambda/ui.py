"""
# ui.py
# Author: Adam Campbell & Miguel Saavedra
# Date: 12/08/2016
"""


import json

class UI(object):

    def __init__(self, event, context):
        self.event = event
        self.context = context
        with open("constants.json", "r") as constants_file:
            self.constants = json.loads(constants_file.read())
        with open("forms.json", "r") as forms_file:
            self.forms = json.loads(forms_file.read())


    
    def getForm(self, data):
        form_data = {}
        form_type = ""
        # Find type of form requested
        if "user" in self.event["type"]:
            form_type = "User"
        elif "blog" in self.event["type"]:
            form_type = "Blog"
        elif "page" in self.event["type"]:
            form_type = "Page"
        elif "role" in self.event["type"]:
            form_type = "Role"
        elif "siteSetting" in self.event["type"]:
            form_type = "SiteSetting"

        # Populate json fields
        # Get form json from json file
        form_data["input"] = self.forms[form_type]
        form_data["type"] = "form"
        form_data["status"] = "success"
        form_data["page_title"] = "New Blog"
        
        # Will return json
        return form_data

        


        