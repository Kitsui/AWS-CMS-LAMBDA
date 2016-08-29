"""
# response.py
# Author: Adam Campbell
# Date: 27/06/2016
# Edited: N/D        | Miguel Saavedra
#         02/08/2016 | Christopher Treadgold
"""

import jsonpickle

class Response(object):

    def __init__(self, status, data):
        self.status = status;
        self.data = data
        if(self.data is not None):
            if(data["Items"][0] is not None):
                self.columns = data["Items"][0].keys()

    """ function formats replies querying dynamo"""
    def format(self, pTitle):
        # Get the type of table request and store it in a variable "User"
        record_type = pTitle[4:len(pTitle)-1]
        id_var = ""
        replyData = {}
        colm = []
        rows = []
        item = {}
        columns = self.data["Items"][0].keys()
        for i in self.data["Items"]:
            item = {}
            for it in i:
                if "ID" in it:
                    id_var = i[it]['S']
            for j in columns:
                if j == "Title":
                    item[j] =  ('<a href="#" method="'+'edit'+pTitle[4:len(pTitle)-1]+
                        '" '+record_type+':id="'+id_var+'">'+i[j]['S']+'</a>');
                else:
                    item[j] = (i[j]['S'])

            
            rows.append(item)
        replyData["rows"] = rows
        replyData["cols"] = columns
        replyData["page_title"] = pTitle
        #<a href="#" method="editBlog" id="69">Doop</a>
        return replyData

    def to_JSON(self):
        return jsonpickle.encode(self)
