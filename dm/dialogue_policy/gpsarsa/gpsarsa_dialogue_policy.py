'''
Gaussian Process and Sharsa Dialogue Policy
'''
import numpy as np

from dm.base import DialoguePolicy
from common.dialogueact import *
from utils.design_pattern import *

from common.grammar import Grammar
from common.grid_approximation import GridApproximation
from utils.kernel_functions import gaussian_kernel_fun, kronecker_delta_kernel_fun
from utils.distance_measures import euclidean_distance

import random
import pdb
#pdb.set_trace()

class GPSarsaDialoguePolicy(DialoguePolicy):
    '''Gaussian Process Sharsa DialoguePolicy Class'''
    
    def __init__(self):
        super(GPSarsaDialoguePolicy, self).__init__()
        #TODO: read from config
        self.reward_calculator = get_class(self.config.get(self.MY_ID, 'rewardCalculatorClassPath'))
        self.gamma = 0.9
        self.sigma = 5.916#square root of the interval betwen max and min possible reward
        
        self.basic_fun = self._basic_fun#for future, when build general GP-Sharsa Dialogu poliy.
        self.kernel = self._kernel#for future changing
        self.build_full_act = self._build_full_act
        self.choose_act = self._choose_act
        self.rand_act = self._rand_act
        self.create_q_store = self._create_q_store

        self._read('abc.pck')#read current parameters
        
        self._first_episode = True#update to false when end dialogue or read parameters from file

    def save(self, fout):
        '''Save every thing to file for next re-run'''
        pass
    
    def _read(self, fin):
        '''Read the every thing, parameter from file'''
        #read matrix/vector/tuple B, K, H, R, Q from file
        #Q save values of every pairs (b, a), since b contains continous values, we need to grid-based approximation
##        self.B = np.array()#can be list
##        self.H = np.ndarray()
##        self.K = np.ndarray()
        #self.R = []
        #TODO: Abstract the store of Q-approximation
        #self.Q = GridApproximation(euclidean_distance, self._update_value_fun, self.distant_threshold) #Todo: when finish gpsharsa, check threshold = 0.25, 0.3, 0.4
        #self.B = []
        self.Q = self.create_q_store()
        self.R= []
        #self._first_episode = False# set the suitalbe value from current

    def new_dialogue(self):
        '''Reset every value for new diagoue'''
        self.last_sys_act = None
        self._init_step = True

    def end_dialogue(self, user_goal):
        print 'END DIALOUGE', user_goal
        if self._first_episode:
            self._first_episode = False
        else:
            #self.B, self.K don't change
            plus = np.zeros((1,self.H.shape[1]))
            plus[0,-1] = 1
            self.H = np.vstack((self.H, plus))

            #TODO: Reward: in a general dialogue, we probably only have satisfied or unhappy as feedback or user
            #TODO: Reward:it the prediction of system also not inclued in last turn as in this example
            reward = self.reward_calculator.get_final_goal_reward(user_goal, self.last_sys_act)
            self.R.append(reward)
            self.update_q()
            
        #pdb.set_trace()
            

    def get_da(self, user_act_queue, belief_tracker):
        user_act = None#Currently not use user_act, tranfer to choose_act
        if len(user_act_queue)!= 0:
            user_act = user_act_queue.pop()

        b = self.basic_fun(belief_tracker.get_belief_space())

        if self._first_episode:#First Episode
            a = self.rand_act()
            self.B = [(b, a)]
            self.K = np.array([[self.kernel((b,a), (b, a))]])
            self.H = np.array([[1, -self.gamma]])
            self.R= []

            self.last_sys_act = self.build_full_act(a)
            return self.last_sys_act
        elif self._init_step:#it is the first turn of each dialogue
            print 'vao not first episode, init step'
            self._init_step = False
            a = self.choose_act(b, self.Q)
            self.last_sys_act = self.build_full_act(a)
            return self.last_sys_act

        #For every other normal turn (not for the first episode, first turn, termial. Do update H, B, K, R etc
        print 'normal turn'
        reward = self.reward_calculator.get_turn_reward(self.last_sys_act)
        self.R.append(reward)
        a = self.choose_act(b, self.Q)
        self.B.append((b, a))

        #add appropriate column, row for matrix H, not really effective when use np.v/hstack
        plus = np.zeros((self.H.shape[0],1))
        self.H = np.hstack((self.H, plus))
            
        plus = np.zeros((1,self.H.shape[1]))
        plus[0,-2], plus[0,-1] = 1, -self.gamma
        self.H = np.vstack((self.H, plus))

        #update matrix K
        plus = np.array([self.kernel_all((b,a))])
        self.K = np.hstack((self.K, plus[:,0:-1].T))
        self.K = np.vstack((self.K, plus))

        print '---B:\n', np.array(self.B)
        print '---H:\n', self.H
        print '---K:\n', self.K
        print '---R:\n', self.R
#        pdb.set_trace()
        #self.update_q()
        
        self.last_sys_act = self.build_full_act(a)
        return self.last_sys_act

    def kernel_all(self, (b, a)):
        '''return a list of kernel(X, (b,a)) where X is every current element in self.B'''
        ret = []
        for p in self.B:
            ret.append(self.kernel(p, (b,a)))
        return ret

    def update_q(self):
        print 'UPDATE Q'
        print '---B:\n', np.array(self.B)
        print '---H:\n', self.H
        print '---K:\n', self.K
        print '---R:\n', self.R
        sigma= self.sigma
        h = self.H
        ht = h.T
        k = self.K
        r = self.R
        pdb.set_trace()
        #gram= ht*(h*k*ht+pow(sigma,2)*h*ht)*r
        
        for b, a in self.B:
            kbat = np.array([self.kernel_all((b, a))]).T#check again tranpose or not.            
            #tmp = kbat
            

#Need to be difined to use the GP-Sharsa for a new dialogue system    
    def _kernel(self, (b1, a1), (b2, a2)):
        self.state_kernel = gaussian_kernel_fun
        self.action_kernel = kronecker_delta_kernel_fun
        return self.state_kernel(b1, b2)*self.action_kernel(a1, a2)

    def _choose_act(self, b, Q):
        acts = ['request', 'accept', 'delay', 'reject']
        epsilon = 0.2
        apoint = Q.get_approximated_point(b)
        if random.random()<=epsilon or apoint is None:
            return self._rand_act()
        else:
            print 'find the best act'
            pdb.set_trace()

    def _rand_act(self):
        acts = ['request', 'accept', 'delay', 'reject']
        return acts[random.randint(0, len(acts)-1)]

    def _build_full_act(self, a):
        grammar = Grammar('decision')
        sys_da = DialogueAct()

        if a=='accept' or a=='delay' or a=='reject':
            dai = DialogueActItem('end')
            sys_da = DialogueAct(dai)
            dai = DialogueActItem(a, {'appointment':{'person': 'Mr. Bean', 'time': 'next Monday at 9.00 AM'}})
            sys_da.append(dai)    
        else:
            dai = DialogueActItem('request', {'decision':['accept','delay', 'reject'], 'appointment':{'person': 'Mr. Bean', 'time': 'next Monday at 9.00 AM'}}, grammar)
            sys_da.append(dai)

        if self.last_sys_act==None:
            dai = DialogueActItem('hello', {})
            sys_da.append(dai)
        elif a=='request':
            dai = DialogueActItem('sorry', {})
            sys_da.append(dai)
            
        return sys_da

    def _basic_fun(self, belief_space):
        return belief_space.probs

    def _update_value_fun(self, old_value, new_value):
        for k, v in new_value.iteritems():
            old_value[k] = v
        return old_value

    def _create_q_store(self):
        self.distant_threshold = 0.2
        return GridApproximation(euclidean_distance, self._update_value_fun, self.distant_threshold) #Todo: when finish gpsharsa, check threshold = 0.25, 0.3, 0.4
