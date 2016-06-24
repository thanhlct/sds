'''
DialogueManager with GPSarsa
'''

from dm.base import DialogueManager
from utils.designpattern import *

class SimpleRuleDM(DialogueManager):
    
    def __init__(self):
        super(SimpleBeliefStateTracker, self).__init__()
        #DialogManager.__init__(self)
        
        belief_tracker = get_class(self.config.get('DialogueManager', 'belief_tracker_classPath'))
        dialgoue_policy = get_class(self.config.get('DialogueManager', 'diaogue_policy_classPath'))

    def new_dialogue(self):
        '''Initialises the dialogue manager and makes it ready for a new dialogue
        conversation.
        '''
        self.belief_tracker.new_dialgoue()
        self.last_sys_da = None

    def da_in(self, da):
        '''Receives an input user dialogue acts 
        '''
        #self.dialogue_state.update(da, self.last_system_dialogue_act)
        pass

    def da_out(self):
        '''Produces output dialogue act
        '''
##        if self.last_sys_da is None:
##            self.last_sys_da = 'hello'
##            return self.last_sys_da
        
        #self.last_system_da = self.policy.get_da(self.dialogue_state)
        #return self.last_system_da
        pass

    def end_dialogue(self):
        """Ends the dialogue and post-process the data."""
        pass
