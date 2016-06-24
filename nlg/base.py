'''
Base class for generating natural text from system dialogue action
'''
from logging import getLogger
from utils.globalconfig import get_config

class NaturalLanguageGenerator(object):
    MY_ID = 'NaturalLanguageGenerator'
    
    def __init__(self):
        '''init something'''
        self.config = get_config()
        self.logger = getLogger(self.MY_ID)
    
    @classmethod
    def get_natural_text(cls, sys_da):
        pass
    
