# -*- coding: utf-8 -*-
import re
from app import create_app, db

app=create_app()

#LATEX_SUBS = (
#    (re.compile(r'\\'), r'\\textbackslash'),
#    (re.compile(r'([{}_#%&$])'), r'\\\1'),
#    (re.compile(r'~'), r'\~{}'),
#    (re.compile(r'\^'), r'\^{}'),
#    (re.compile(r'"'), r"''"),
#    (re.compile(r'\.\.\.+'), r'\\ldots'),
#)
#
#def escape_tex(value):
#    newval = value
#    for pattern, replacement in LATEX_SUBS:
#        newval = pattern.sub(replacement, newval)
#    return newval
#
#
#texenv = app.create_jinja_environment()
#texenv.block_start_string = '((*'
#texenv.block_end_string = '*))'
#texenv.variable_start_string = '((('
#texenv.variable_end_string = ')))'
#texenv.comment_start_string = '((='
#texenv.comment_end_string = '=))'
#texenv.filters['escape_tex'] = escape_tex