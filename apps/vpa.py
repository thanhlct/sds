'''
Denotation dialogue prolicy for VPA (scheduling appointments)
'''
import random

from dialogue_base.base import DelegationDialoguePolicy
from common.grammar import Grammar
from common.dialogueact import *
from utils.kernel_functions import gaussian_kernel_fun, kronecker_delta_kernel_fun, polyminal_kernel_fun

class VPA(DelegationDialoguePolicy):
    '''Defined specific stuff for VPA dialogue policy'''
    
    def __init__(self):
        '''init something'''
        self.last_sys_act = None
        self.persons = ['Mr. Bean', 'Dr. Peter', 'Ms. Marry', 'Harry Potter', 'Taylor Swift', 'The President']
        self.times = ['next Monday at 9.00 AM', 'tonight', 'tomorrow', 'after the conference', 'new year']
        self.reasons = ['building the new OS', 'recording a new album', 'your advices', 'showing your holiday at England', 'eating', 'playing tennis', 'watching the new movie', 'a new idea', 'the new devices']

    def new_dialogue(self):
        self.last_sys_act = None
        person = self.persons[random.randint(0, len(self.persons)-1)]
        time = self.times[random.randint(0, len(self.times)-1)]
        reason = self.reasons[random.randint(0, len(self.reasons)-1)]
        self.appointment = {'person': person, 'time': time, 'reason': reason}
        
    def end_dialogue(self):
        pass
        
    def basis_function(self, belief_space):
        '''Get representative datapoint from belief_space'''
        return belief_space.probs
        
    def kernel_function(self, (b1, a1), (b2, a2)):
        '''Compute the value of kernel function for given pair of data points'''
        self.state_kernel = gaussian_kernel_fun
        #self.state_kernel = polyminal_kernel_fun
        self.action_kernel = kronecker_delta_kernel_fun
        return self.state_kernel(b1, b2, p=4, sigma=5)*self.action_kernel(a1, a2)
        #TODO!!!TODO:CHECK the way of sigma related to both
    
    def get_action_set(self):
        '''Get list of available actions in sort format (without detalied information)
            e.g. inform, offer, reject
        '''
        acts = ['request', 'accept', 'delay', 'reject']
        return acts
    
    def build_full_act(self, user_act_queue, belief_space, a):
        '''Buiding action and full detailed information to transfer to NLG e.g. request(price=[cheap, moderate, expersive])'''
        #TODO: need to track dialogue history to build suitable action
        #appointment = {'person': 'Mr. Bean', 'time': 'next Monday at 9.00 AM', 'reason': 'the new OS'}
        grammar = Grammar('decision')
        sys_da = DialogueAct()

        if a=='accept' or a=='delay' or a=='reject':
            dai = DialogueActItem('end')
            sys_da = DialogueAct(dai)
            dai = DialogueActItem(a, {'appointment': self.appointment})
            sys_da.append(dai)    
        else:
            dai = DialogueActItem('request', {'decision':['accept','delay', 'reject'], 'appointment': self.appointment}, grammar)
            sys_da.append(dai)

        if self.last_sys_act==None:
            dai = DialogueActItem('hello', {})
            sys_da.append(dai)
        elif a=='request':
            dai = DialogueActItem('sorry', {})
            sys_da.append(dai)

        self.last_sys_act = sys_da
        return sys_da

    def get_off_policy_act(self, belief_space):
        print '---Get off_policy_act:',
        do_threshold = 0.45#read from config but outside of qgp-sarsa
        max_assign, prob = belief_space.get_nbest_assignments(1)[0]
        if prob >= do_threshold:#do action and end dialog
            off_a = str(max_assign)
        else:
            off_a = 'request'
        print off_a
        return off_a
