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


    def to_JSON(self):
        return jsonpickle.encode(self)
