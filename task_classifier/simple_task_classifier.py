'''
Base class fo extracting ASR hypothesis from cloud-based ASR
'''
from logging import getLogger
from utils.globalconfig import get_config

class SimpleTaskClassifier(object):
    MY_ID = 'TaskClassifier'
    
    def __init__(self):
        '''init something'''
        super(SimpleTaskClassifier, self).__init__()
    
    @classmethod
    def from_transcript(cls, transcript, last_task):
        transcript = transcript.lower()
        if 'stop' in transcript or 'next one' in transcript:
            return 'user_end'
        
        if last_task == None:
            return 'get_list_appointment'
        elif last_task=='get_list_appointment':
            return 'appoinment_decision'
        elif last_task=='end_new_dialogue':
            return 'end_new_dialogue'

        return last_task
    
