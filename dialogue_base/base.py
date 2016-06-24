'''
Denotation functions for VPA (scheduling appointments)
'''

class DelegationDialoguePolicy (object):
    '''Base class for delegation class defining stuffs for specific domain which is used in Q/GP-Sarsa dialogue policy'''
    def __init__(self):
        '''init something'''
        pass
    def new_dialogue(self):
        pass
    def end_dialogue(self):
        pass
    def basis_function(self, belief_space):
        '''Get representative datapoint from belief_space'''
        pass
    def kernel_function(self, (b1, a1), (b2, a2)):
        '''Compute the value of kernel function for given pair of data points'''
        pass
    def get_action_set(self):
        '''Get list of available actions in sort format (without detalied information)
            e.g. inform, offer, reject
        '''
        pass
    def build_full_act(self, user_act_queue, belief_space, a):
        '''Buiding action and full detailed information to transfer to NLG'''
        pass
    
