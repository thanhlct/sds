'''
Base class fo extracting ASR hypothesis from cloud-based ASR
'''
from logging import getLogger
from utils.globalconfig import get_config

class TaskClassifier(object):
    MY_ID = 'TaskClassifier'
    '''Base class for delegation class defining stuffs for specific domain which is used in Q/GP-Sarsa dialogue policy'''
    def __init__(self):
        '''init something'''
        self.config = get_config()
        self.logger = getLogger(self.MY_ID)
    
    @classmethod
    def from_transcript(cls, transcript, last_task):
        pass
    
