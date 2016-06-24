'''
Extracting ASR hypotheses from cloud-based ASR Watson
'''
import random

from base import NaturalLanguageGenerator
from common.dialogueact import *

import pdb

class SimpleNLG(NaturalLanguageGenerator):
    
    def __init__(self):
        '''init something'''
        super(SimpleNLG, self).__init__()
        
    @classmethod
    def get_natural_text(cls, sys_da):
        cls._init_template()
        da_text = str(sys_da)
        if 'end' in da_text:
            act_type = 'reward'
        elif 'sorry' in da_text:
            act_type = 'sorry_repeats'
        else:
            act_type = 'request'
        
        if act_type == 'reward':
            text = cls.rewards[random.randint(0, len(cls.rewards)-1)]
            decision = sys_da[1].type
            text = text.replace('%decision', decision)
        elif act_type == 'sorry_repeats':
            text = cls.sorry_repeats[random.randint(0, len(cls.sorry_repeats)-1)]
        else:
            text = cls.requests[random.randint(0, len(cls.requests)-1)]
            person = sys_da[0].content['appointment']['person']
            time = sys_da[0].content['appointment']['time']
            reason = sys_da[0].content['appointment']['reason']
            text = text.replace('%person', person)
            text = text.replace('%time', time)
            text = text.replace('%reason', reason)
        
        return text

    @classmethod
    def _init_template(cls):
        cls.requests = ['Do you want to meet %person at %time for %reason?',
                    '%person want to visit you at %time about %reason?',
                    'You have got an appoinment from %person for %reason at %time, what do you think?']
        cls.rewards = ['Okay, %decision, is that correct?',
                   'You decided to %decision, did I get it correct?',
                   '%decision, I\'ve got it correct, isn\'t it?']
        cls.sorry_repeats = ['Sorry, did you say accept, delay or reject?',
                         'Can you repeat your decision? is that accept, delay or reject?',
                         'Sorry, could you please repeat your decision?']
        
