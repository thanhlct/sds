'''
Define abstract classes for Dialoguage Management:
    - DialoguageManager
    - BeliefState+Track
    - DialoguePolicy
'''

from logging import getLogger

from utils.globalconfig import get_config
from utils.design_pattern import *
from utils.io_functions import *


class BeliefState(object):
    '''Abstract BeliefState Class'''
    MY_ID = 'BeliefState'
    
    def __init__(self):
        self.config = get_config()
        self.logger = getLogger(self.MY_ID)

    def new_dialogue(self):
        '''Reset every value for new diagoue'''
        pass
    
    def update(self, user_da, last_sys_da):
        '''update belief date based on last_sys_da and given user_da'''
        pass

    def get_belief_space(self):
        '''can be summary space of full space'''
        pass
    #Todo: Add some more methods in future when need

class DialogueHistory(object):
    '''Abstract DialogueHistory Class
    Helps track the dialogue process
    '''
    MY_ID = 'DialogueHistory'
    
    def __init__(self):
        self.config = get_config()
        self.logger = getLogger(self.MY_ID)

    def new_dialogue(self):
        '''Reset every value for new diagoue
        '''
        pass
        
    def update(self, blief_state, user_da, last_sys_da):
        '''update dialogue history based on last_sys_da and given user_da
        '''
    #Todo: Add some more methods in future when need

class DialoguePolicy(object):
    '''Abstract DialoguePolicy class
    '''
    MY_ID = 'DialoguePolicy'
    
    def __init__(self):
        self.config = get_config()
        self.logger = getLogger(self.MY_ID)

    def new_dialogue(self):
        '''Reset every value for new diagoue
        '''
        pass

    def get_da(self, user_acts, belief_tracker):
        pass

    def end_dialogue(self, user_goal):
        pass

    def save(self, fout):
        '''Save current result parameters'''
        pass
    #Todo: Add some more methods in future when need

class DialogueManager(object):
    """General DialogueManager Class
    This is a base class for a dialogue manager. The purpose of a dialogue
    manager is to accept input in the form dialogue acts and respond again in
    the form of dialogue acts.

    The dialogue manager should be able to accept multiple inputs without
    producing any output and be able to produce multiple outputs without any
    input.

    """
    MY_ID='DialogueManager'
    
    def __init__(self):
        self.config = get_config()
        self.logger = getLogger(self.MY_ID)
        
        self.belief_tracker = get_class(self.config.get(self.MY_ID, 'belief_tracker_classPath'))
        self.dialogue_policy = get_class(self.config.get(self.MY_ID, 'dialogue_policy_classPath'))
        #dialgoue_history = get_class(self.config.get('DialogueManager', 'diaogue_history_classPath'))

    def new_dialogue(self):
        '''Initialises the dialogue manager and makes it ready for a new dialogue
        conversation.
        '''
        self.last_sys_da = None
        self.user_act_queue = []
        self.belief_tracker.new_dialogue()
        self.dialogue_policy.new_dialogue()

    def da_in(self, user_da):
        '''Receives an input user dialogue acts
        current user_da is the ASRHypothesis
        '''
        self.belief_tracker.update(user_da, self.last_sys_da)#CHECK: Which one control the DialogueHistory, normaly is BeliefState
        self.user_act_queue.append(user_da)#push user_da on the queue for waiting process
        #Problem:??? Push all ASRHypothesis into user_act not really comfortable, too many

    def da_out(self):
        '''Produces output dialogue act'''
        #self.user_act_queue is mutuable, so policy can change it accoording to which user_da have processed
        #Problem:?? How to deal with user_act(request(adress)) when don't push user_act into dilaogue policy to find suitable action
        self.last_sys_da = self.dialogue_policy.get_da(self.user_act_queue, self.belief_tracker)
        #some thing else encapsulated in history in belief_tracker
        
        return self.last_sys_da

    def end_dialogue(self, user_goal):
        """Ends the dialogue and post-process the data. user_goal or feedback"""
        self.dialogue_policy.end_dialogue(user_goal)

    def save(self):
        '''Save current result parameters, filenames is in cofig'''
        self.dialogue_policy.save()
        #object_to_file(self, 'dm.pck')
        
