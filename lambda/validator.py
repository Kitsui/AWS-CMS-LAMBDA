"""
# validator.py
# Author: Miguel Saavedra
# Date: N/D
# Edited: 02/08/2016 | Christopher Treadgold
"""

class Validator(object):
    """ function checks if a string contains black listed strings """
    @staticmethod
    def validateBlog(dataString):
        caseStrings = ["<script>", "<button>", "<form>", "<input>"]
        for caseString in caseStrings:
            if caseString in dataString:
                return False
        return True
