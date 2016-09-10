"""
# error.py
# Author: Christopher Treadgold
# Date: 09/09/2016
"""

import json

class Error(object):

    @staticmethod
    def send_error(error, data=None):
#        error_function = error_function_map(error)
#        if error_function is not None:
#            return (error_function(data))
#        else:
        raise Exception(json.dumps({"status": 400, "error": error, "data": data}))
    
    @staticmethod
    def error_function_map(error):
        error_function_mapping = {
            "noRequest": Error.format_no_request,
            "unsupportedRequest": Error.format_unsuported_request,
            "noToken": Error.format_no_token,
            "invalidToken": Error.format_invalid_token,
            "tokenHasNoUser": Error.format_token_has_no_user,
            "invalidUserId": Error.format_invalid_user_id,
            "userHasNoRole": Error.format_user_has_no_role,
            "usernameOrPasswordMissing": Error.format_username_or_password_missing,
            "invalidRoleId": Error.format_invalid_role_id,
            "roleHasNoPermissions": Error.format_role_has_no_permissions,
            "unauthorizedRequest": Error.format_unauthorized_request
        }
        if error in error_function_mapping:
            return error_function_mapping[error]
        else:
            return None
    
    @staticmethod
    def format_no_request(data):
        return None
    
    @staticmethod
    def format_unsupported_request(data):
        return None
    
    @staticmethod
    def format_no_token(data):
        return None
    
    @staticmethod
    def format_invalid_token(data):
        return None
    
    @staticmethod
    def format_token_has_no_user(data):
        return None
    
    @staticmethod
    def format_invalid_user_id(data):
        return None
    
    @staticmethod
    def format_user_has_no_role(data):
        return None
    
    @staticmethod
    def format_username_or_password_missing(data):
        return None
    
    @staticmethod
    def format_invalid_role_id(data):
        return None
    
    @staticmethod
    def format_role_has_no_permissions(data):
        return None
    
    @staticmethod
    def format_unauthorized_request(data):
        return None
