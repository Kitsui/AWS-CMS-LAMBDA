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

        # set form type according type of request
        if data is not None:
            form_type = self.event["request"][4:]
        else:
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
                form_type = "SiteSettings"

        
        #for key, value in d.iteritems():
        # Get form json from json file
        form_data["input"] = self.forms[form_type]
        form_data["type"] = "form"
        form_data["status"] = "success"
        form_data["page_title"] = "New Blog"

        # Populate json fields if data exists
        form_input = ""
        if data is not None:
            for item_f in form_data["input"]:
                for key in data["Items"]:
                    # Edit name values in form json to match table columns
                    f_letter = item_f["name"][:1]
                    form_char_list = list(item_f["name"])
                    form_char_list[0] = f_letter.upper()
                    form_input = "".join(form_char_list)
                    # Check if form input exists in form
                    if key[form_input] is not None:
                        # Replace value in form json
                        item_f["value"] = key[form_input]["S"]

                        
        # Will return json
        return form_data

        


        