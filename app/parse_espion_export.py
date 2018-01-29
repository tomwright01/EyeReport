# -*- coding: utf-8 -*-
"""
Code to parse an espion export file
"""
from app.exceptions import EspionExportError
from app.parse_vep_export import read_export_file
from app.parse_mferg_export import read_mferg_export_file
import logging

logger = logging.getLogger(__name__)

def find_type(fpath):
    """
    Reads an espion export file and determines if it is an mfERG or VEP/ERG
    export format.
    Returns a dict {'type': 'vep'|'mferg',
                    'sep': '\t'|','|' '|';'|':'}
    """
    separators = {'tab': '\t',
                  'comma': ',',
                  'semi': ';',
                  'colon': ':'}
    export_type, sep = None, None
    
    with open(fpath, 'r') as f:
        line = f.readline()
        for key in separators:
            if separators[key] in line:
                sep = separators[key]
                break
        if not sep:
            sep = ' '
        
        if line.split(sep)[0].strip() == 'Contents Table':
            export_type = 'vep'
        elif line.split(sep)[0].strip() == 'Parameter':
            export_type = 'mferg'
        else:
            raise EspionExportError('Unknown Type')
    return({'type': export_type,
            'sep': sep})
        
def load_file(fpath):
    """
    Parses an espion export file
    returns ['type': 'mferg'|'vep',
             'data': file contents]
    or raises an EspionExportError
    """
    info = find_type(fpath)

    try:
        if info['type'] == 'mferg':
            data = read_mferg_export_file(fpath, sep=info['sep'])
        else:
            data = read_export_file(fpath, sep=info['sep'])
    except:
        raise EspionExportError('Invalid file format:{}'.format(fpath))
    return([info, data])
    
