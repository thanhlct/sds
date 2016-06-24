'''
Simple Dialogue Policy
'''
from dm.base import DialoguePolicy
from common.dialogueact import *
from common.grammar import Grammar

import pdb
#pdb.set_trace()

class SimpleRuleDialoguePolicy(DialoguePolicy):
    '''Simple DialoguePolicy Class'''
    
    def __init__(self):
        super(SimpleRuleDialoguePolicy, self).__init__()
        self._do_threshold = self.config.getfloat(self.MY_ID, 'doThreshold')

    def new_dialogue(self):
        '''Reset every value for new diagoue'''
        self.last_sys_act = None

    def get_da(self, user_act_queue, belief_tracker):
        grammar = Grammar('decision')
        sys_da = DialogueAct()

        belief_state = belief_tracker.get_belief_space()
        if belief_state is not None:
            max_assign, prob = belief_state.get_nbest_assignments(1)[0]
            if prob >= self._do_threshold:#do action and end dialog
                dai = DialogueActItem('end')
                sys_da = DialogueAct(dai)
                dai = DialogueActItem(str(max_assign), {'appointment':{'person': 'Mr. Bean', 'time': 'next Monday at 9.00 AM'}})
                sys_da.append(dai)
                return sys_da
        
        dai = DialogueActItem('request', {'decision':['accept','delay', 'reject'], 'appointment':{'person': 'Mr. Bean', 'time': 'next Monday at 9.00 AM'}}, grammar)
        sys_da = DialogueAct(dai)

        if self.last_sys_act==None:
            dai = DialogueActItem('hello', {})
            sys_da.append(dai)
        else:
            dai = DialogueActItem('sorry', {})
            sys_da.append(dai)

        user_act_queue = []
        
        self.last_sys_act = sys_da
        return self.last_sys_act
