#!/usr/bin/python2.7

"""
# replace_variables.py
# Author: Christopher Treadgold
# Date: N/D
"""

import warnings
warnings.filterwarnings("ignore")

def replace_variables(document, **args):
    replacements = []
    for i in range(len(document)):
        for key in args:
            variable_string = '$(' + key + ')'
            variable_length = len(variable_string)
            if document[i:i+variable_length] == variable_string and document[i-1] != '\\':
                replacements.append([i, key]) 
    
    finished_document = ''
    current_index = 0
    for replacement in replacements:
        finished_document += document[current_index:replacement[0]]
        finished_document += args[replacement[1]]
        current_index += (replacement[0] - current_index) + len(replacement[1]) + 3
    
    finished_document += document[current_index:]
    
    return finished_document
