# -*- coding: utf-8 -*-
"""
Utility functions
"""
def collapse_phone(value, seperators=[' ','-']):
    for s in seperators:
        value = value.replace(s,'')
    return value
    
def format_phone(value, seperator='-'):
    assert len(value) == 10, 'Invalid number'
    return('{}-{}-{}'.format(value[0:3],value[3:6],value[6:10]))