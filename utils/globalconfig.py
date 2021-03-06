'''
A module for globally sharing ConfigParser objects.
'''

from ConfigParser import ConfigParser

_GLOBAL_CONFIG = None

def init_config():
    global _GLOBAL_CONFIG
    assert (_GLOBAL_CONFIG == None),'init_config has already been called.'
    _GLOBAL_CONFIG = ConfigParser()
    _GLOBAL_CONFIG.optionxform = str

def get_config():
    global _GLOBAL_CONFIG
    return _GLOBAL_CONFIG

def set_config_none():
    global _GLOBAL_CONFIG
    _GLOBAL_CONFIG = None

   
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
