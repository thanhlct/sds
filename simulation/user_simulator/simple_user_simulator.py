'''
A simple user simulator
'''

import random

from simulation.base import UserSimulator
from common.dialogueact import (DialogueActItem, DialogueAct)
from utils.sampledistribution import sample_from_dict

#from utils.globalconfig import get_config
#from utils.designpattern import *



class SimpleUserSimulator(UserSimulator):
    user_goals = ['accept','delay', 'reject']
    
    def __init__(self):
        super(SimpleUserSimulator, self).__init__()
        param_fields = ['request_silenceProb',
                        'request_oogProb',
                        'request_directAnswerProb',
                        'patience_endProb',
                        'patience_continueProb']
        #Todo: ?Add request_cofusionProb for cofused answer inform('decision': 'accept')&inform('decision': 'delay')
        self.params = {'request':{}, 'patience':{}}
        for field in param_fields:
            assert self.config.has_option(self.MY_ID, field), 'UserSimulator section missing field %s' % (field)
            (force, param) = field.split('_')
            self.params[force][param] = self.config.getfloat(self.MY_ID, field)

        self._patient_level = self.config.getfloat(self.MY_ID, 'patience_level')
        self.logger.debug('Params = %s' % (self.params))
        
    def new_dialogue(self):
        '''
        Init status for a new dialogue. Sample a new user goal. Reset everything for simulating a new dialogue
        '''
        tmp = random.randint(0, 2)
        self.goal = {'decision': self.user_goals[tmp]}
        self._turn = 0
        
        self.logger.info('\n-----------------------------------------------------------------------------')
        self.logger.info('\t\tUser Goal: %s' % self.goal)
        self.logger.info('\n-----------------------------------------------------------------------------')
    
    def da_in(self, da):
        '''
        Recieving a system dialogue act, support reciving multiple da
        '''
        #Todo: Should be save in queue
        self.last_system_da = da
        self.logger.info('system_da\t=%s' % self.last_system_da)
    
    def da_out(self):
        '''
        Simulate a user dialogue act based on current state and other distribution
        '''
        #TODO: Take acount for only the first dialogue action item, how to deal with multiple dialogue action items when we have in specific apps
        self._turn += 1
        if self._turn > self._patient_level:
            user_end = sample_from_dict(self.params['patience'])
            if user_end == 'endProb':
                self.last_user_da = DialogueAct(DialogueActItem('end'))
                return self.last_user_da
        
        sys_dai = self.last_system_da
        assert sys_dai.type=='request', 'system.da.type == %s (must be "request")' % (sys_dai.type)
        
        user_action_type = sample_from_dict(self.params[sys_dai.type])
        if user_action_type=='silenceProb':
            ret_type = 'silent'
            ret_content = {}
        elif user_action_type=='oogProb':
            ret_type = 'oog'
            ret_content = {}
        elif user_action_type=='directAnswerProb':
            ret_type = 'inform'
            ret_content = self.goal
        else:
            raise RuntimeError,'Dont know userActionType=%s' % (user_action_type)

        self.last_user_da = DialogueAct(DialogueActItem(ret_type, ret_content))
        self.logger.info('user_da\t=%s' % self.last_user_da)
        return self.last_user_da












