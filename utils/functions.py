'''
Support Functions
'''
from re import search
import pprint
#from random import random

def config_section_to_dict(config,section):
    '''
    Returns a dict of all items in section of the configuration object
    config.  Guess at their type (float or int or string).
    '''
    dict = {}
    for (option,val) in config.items(section):
        keys = option.split('_')
        d = dict
        lastKey = keys.pop(-1)
        for key in keys:
            if (not key in d):
                d[key] = {}
            d = d[key]
        if (search('\.',val)):
            try:
                valToStore = float(val)
            except ValueError:
                valToStore = val
        else:
            try:
                valToStore = int(val)
            except ValueError:
                valToStore = val            
        d[lastKey] = valToStore
    return dict

def nprint(o):
    '''pprint for o'''
    pp = pprint.PrettyPrinter()
    pp.pprint(o)
