'''
Base class fo extracting ASR hypothesis from cloud-based ASR
'''
from logging import getLogger
from utils.globalconfig import get_config

class ASRResult (object):
    MY_ID = 'ASRResult'
    '''Base class for delegation class defining stuffs for specific domain which is used in Q/GP-Sarsa dialogue policy'''
    def __init__(self):
        '''init something'''
        self.config = get_config()
        self.logger = getLogger(self.MY_ID)
    
    @classmethod
    def get_asr_hypotheses(cls, asr):
        pass
    
