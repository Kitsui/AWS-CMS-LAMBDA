"""
# error.py
# Author: Christopher Treadgold
# Date: 09/09/2016
"""

import json

class Error(object):

    @staticmethod
    def send_error(error, data=None):
        status = Error.error_status_map(error)
        if status is not None:
            raise Exception(json.dumps({"status": status, "error": error, "data": data}))
        else:
            raise Exception(json.dumps({"status": 400, "error": error, "data": data}))
    
    @staticmethod
    def error_status_map(error):
        error_status_mapping = {
            
        }
        if error in error_status_mapping:
            return error_status_mapping[error]
        else:
            return None