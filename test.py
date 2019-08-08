# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 12:30:51 2019

@author: twright
"""

import argparse
import os

if __name__== '__main__':
    parser = argparse.ArgumentParser(description='Test')
    parser.add_argument('-f', '--file', required=True, action='append' )
    parser.add_argument('-b', '--base', help="base path for input files, value is prefixed to paths specified by -f", default='.')
    parser.add_argument('-s', '--step', action='append', help='enter steps to print')
    parser.add_argument('--noprompt', help="Dont prompt for options. Use default settings or command line options", action='store_true')
    args = parser.parse_args()
    
    filenames = [os.path.join(args.base, f) for f in args.file]
    if args.noprompt:
        print('flub')