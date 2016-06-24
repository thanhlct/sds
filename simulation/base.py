'''
Defining a general abstract UserSimulator
'''
from utils.globalconfig import get_config
from logging import getLogger

class UserSimulator(object):
    MY_ID = 'UserSimulator'
    
    def __init__(self):
        self.config = get_config()
        self.logger = getLogger(self.MY_ID)
        
    def new_dialogue(self):
        '''
        Sample a new user goal. Reset everything for simulating a new dialogue
        '''
        pass
    
    def da_in(self, da):
        '''
        Recieving a system dialogue act, support reciving multiple da
        '''
        pass
    
    def da_out(self):
        '''
        Simulate a user dialogue act based on current state and other distribution
        '''
        pass
    # end dialogue?

class ASRSimulator(object):
    MY_ID='ASRSimulator'
    
    def __init__(self):
        self.config = get_config()
        self.logger = getLogger(self.MY_ID)
        
    def simulate_asr(self, grammar, user_da):
        pass

class Simulator(object):
    MY_ID = 'Simulator'
    
    def __init__(self):
        self.config = get_config()
        self.logger = getLogger(self.MY_ID)
        
    def simulate_one_dialogue(self):
        '''Simulate one dialogue based on given user simulation, and so on'''
        pass
