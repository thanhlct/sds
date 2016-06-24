'''
Gaussian Process and Sharsa Dialogue Policy
'''
import numpy as np
import random
import os.path

from dm.base import DialoguePolicy
from common.dialogueact import *
from utils.design_pattern import *
from utils.io_functions import *

#from common.grammar import Grammar
#from common.grid_approximation import GridApproximation
##from utils.kernel_functions import gaussian_kernel_fun, kronecker_delta_kernel_fun, polyminal_kernel_fun
##from utils.distance_measures import euclidean_distance

import pdb
#pdb.set_trace()

class QGPSarsaDialoguePolicy(DialoguePolicy):
    '''Gaussian Process Sharsa DialoguePolicy Class'''
    
    def __init__(self):
        super(QGPSarsaDialoguePolicy, self).__init__()
        #TODO: read from config, check redundant things from full GP-Sarsa
        self.reward_calculator = get_class(self.config.get(self.MY_ID, 'rewardCalculatorClassPath'))
        #self.gamma = 0.9#element in H matrix
        self.gamma = self.config.getfloat(self.MY_ID, 'gamma')
        #self.sigma = 5.916#square root of a half of the interval betwen max and min possible reward, using in update Q.
        self.sigma = self.config.getfloat(self.MY_ID, 'sigma')
        #self.epsilon = -1#0.1#the probability of take randomize action for exploration
        self.epsilon = self.config.getfloat(self.MY_ID, 'epsilon')
        #self.variance_scale=1#=1 no scale, =3 is optimize for CamInfo
        self.variance_scale = self.config.getfloat(self.MY_ID, 'varianceScale')
        #self.threshold_v = 0.015#threshold to push new data point to approximate dictionary D. Best CamInfo = 0.1
        self.threshold_v = self.config.getfloat(self.MY_ID, 'thresholdV')

        #for QGP-Sarsa
        self.off_policy = True#update in read parameters
        #self.threshold_variance = 4.6#threshold to change off-policy to on-policy
        self.threshold_variance = self.config.getfloat(self.MY_ID, 'thresholdTau')

        self.delegation_class = get_class(self.config.get(self.MY_ID, 'delegationClass'))
        #self.basis_fun = self._basis_fun#for future, when build general GP-Sharsa Dialogu poliy.
        self.basis_fun = self.delegation_class.basis_function
        #self.kernel = self._kernel#for future changing
        self.kernel = self.delegation_class.kernel_function
        #self.build_full_act = self._build_full_act
        self.build_full_act = self.delegation_class.build_full_act
        #self.get_action_set = self._get_action_set
        self.get_action_set = self.delegation_class.get_action_set
        self.acts = self.get_action_set()
        
        self._first_episode = True#update to false when end dialogue or read parameters from file
        self.means = None
        self.C= None
        self.c = None
        self.v1 = 0

        #For QGP-Sarsa
        #self.get_off_policy_act = self._get_off_policy_act
        self.get_off_policy_act = self.delegation_class.get_off_policy_act

        self.save_file = self.config.get(self.MY_ID, 'saveFile')
        self._read()#read current parameters
        
    def save(self):
        '''Save every thing to file for next re-run'''
        #Need to save: K, D, C, means
        if self.save_file != 'None':
            params = {'D': self.D, 'means': self.means, 'K1': self.K1, 'C': self.C, 'off_policy':self.off_policy}
            object_to_file(params, self.save_file)
    
    def _read(self):
        '''Read the every thing, parameter from file'''
        if os.path.isfile(self.save_file) and self.save_file != 'None':
            params = file_to_object(self.save_file)
            self.D = params['D']
            self.means = params['means']
            self.K1 = params['K1']
            self.C = params['C']
            self.off_policy = params['off_policy']
            self._first_episode = False

    def new_dialogue(self):
        '''Reset every value for new diagoue'''
        self.last_sys_act = None
        self.last_b = None
        self.last_a = None
        self.c_comma = None
        self.reward = None
        
        self._init_step = True
        #for QGP-Sarsa
        self.max_variance = 0
        self.delegation_class.new_dialogue()

    def end_dialogue(self, user_goal):
        print '------END DIALOUGE------, user goal=', user_goal
        #pdb.set_trace()
        #need to set reward, b' at the end dialogue don't used anywhere
        #a part of line 18
        #self.reward = self.reward_calculator.get_turn_reward(self.last_sys_act)
        self.reward = self.reward_calculator.get_final_goal_reward(user_goal, self.last_sys_act)
        #line 24
        self.g_comma = np.zeros((len(self.D), 1))
        self.delta = 0
        self.delta_k = self.kernel_all((self.last_b, self.last_a))
        self._calculate_from_second_turn(True)

        print 'max_variance=', self.max_variance
        if self.off_policy and self.max_variance<= self.threshold_variance:
            self.off_policy= False
            print '--------CHANGE THE POLICY-------'
        #pdb.set_trace()

    def _add_ba_to_D(self):
        #line 14, 28 in the algorithm
        #Problem/Change:in the paper, (b, a) add to the first element of D. But it is not suitalbe with means, C, and kerel(b, a) etc
        self.D.append((self.b, self.a))#do we need concat in the first position?
        #self.D.insert(0, (self.b, self.a))
        print 'add new representative point (%s, %s) to D' % (self.b, self.a)

    def _update_K1(self):
        #line 14, 28
        print '--update K^-1'
        print 'g_comma=\n', self.g_comma.T
        self.K1 = self.delta*self.K1
        self.K1 = self.K1 + np.dot(self.g_comma,self.g_comma.T)
        
        tmp_g = - self.g_comma.copy()
        self.K1 = np.hstack((self.K1, tmp_g))
        
        tmp_g = np.vstack((tmp_g, 1))
        self.K1 = np.vstack((self.K1, tmp_g.T))
        self.K1 = self.K1/float(self.delta)
    
    def _calculate_first_turn(self):
        print 'calculate first turn, line 11-> 16'
        #pdb.set_trace()
        self.c = np.zeros((len(self.D), 1))
        self.d = 0
        self.v1 = 0
        self.cov_ba = self.kernel_all((self.b, self.a))
        self.g = np.dot(self.K1, self.cov_ba)
        self.delta = self.kernel((self.b, self.a), (self.b, self.a))-np.dot(self.cov_ba.T, self.g)
        if self.delta > self.threshold_v:
            #print 'add new data point at first turn, check???'
            #pdb.set_trace()
            #Problem/Fix/Guess=NoGasic: update K^-1 similar to line 28 with g' buidt from old D (with out new data point)
            #G_COMMA represent the how new point covariance with existed others
            #self.g_comma = np.zeros((len(self.D), 1))#CHANGE: buiding g' updating K^-1 before push new point to D. LIke
            #self.g_comma[-1, -1] = 1#Problem/Guess=NotGasic: Since first turn so there is no corelation with any previous data point
            self.g_comma = self.g.copy()#since in update K1, the code used g' not g
            self._update_K1()
            
            self._add_ba_to_D()#line 14
            self.g = np.zeros((len(self.D), 1))#line 15
            self.g[-1, -1] = 1
            if self.means is None:
                self.means = np.array([[0.0]])
            else:
                self.means = np.vstack((self.means, 0))
            if self.C is None:
                self.C = np.array([[0.0]])
            else:
                self.C = self._add_one_column_zeros(self.C)
                self.C = self._add_one_row_zeros(self.C)
            if self.c is None:
                self.c = np.array([[0.0]])
            else:
                self.c = np.vstack((self.c, 0))
        #pdb.set_trace()
        self.update_q(False)

    def _add_one_column_zeros(self, m):
        p = np.zeros((m.shape[0],1))
        return np.hstack((m, p))
    def _add_one_row_zeros(self, m):
        p = np.zeros((1,m.shape[1]))
        return np.vstack((m, p))

    def _calculate_from_second_turn(self, end_dialogue = False):
        #From line 26 to line 42
        #CHECK: v = 0, check result d = NaN
        print 'Calculate from second turn, line 26->42'
        #pdb.set_trace()
        if self.v1==0: #line 26
            #Problem: since if the first episode choose the request action, the self.means still equa empty, then move to here into the matrix product
            #Solution: In fact, the element of means, C, c is always suitalbe with number of point in Diction nary. Need init immediately when push firs turn of first espisode to D.
            self.d = self.reward - np.dot(self.delta_k.T, self.means)
        else:
            self.d = (self.gamma*pow(self.sigma,2)/self.v1)*self.d + self.reward - np.dot(self.delta_k.T, self.means)
        #self.d = self.d[0,0]#take the number from matrix, don't really need it, but I like number is the number not a number is a matrix 1x1
        print 'delta at second turn', self.delta
        if self.delta>self.threshold_v and not end_dialogue:
            #Gasic'change: line 28 add new data point to D is move to almost end of this scope, since most calculation is based on old D.
            #self._add_ba_to_D()#line 28MOVI
            #Gasic's change: use g_comma in update K^-1, so move update g_comman before update K1
            #G_COMMA is from get_da represent the how new point covariance with existed others
            #self.g_comma = np.zeros((len(self.D), 1))#line 29, CHECK:the size of g' is not pointed out, but took as similar to first turn
            #self.g_comma[-1, -1] = 1#New point probably not covariance with nearest previous point#PROBLEM:askGasic:g_comma*g_comma.T alway zero in K^-1
            self._update_K1()
            
            self.h = np.vstack((self.g, -self.gamma))#is that g or g', so dangorous to code without deep understanding
            self.last_cov_ba = self.kernel_all((self.last_b, self.last_a))#TODO: Since use the old D so, it don't need to recalcuate
            self.cov_ba = self.kernel_all((self.b, self.a))
            #Problem/Fix/HAVE TO CHECK: since just add new point to D so, the size of self.g always less thant size of kernel((b,a)) 1 dimention
            #Solution: recalcuate self.g = self.K1*self.cov_ba or change g to g' (for current fix)
            #self.g = np.dot(self.K1,self.cov_ba)#why it is not K1xlast_cov_ba? similar to line 12?
            self.delta_ktt = np.dot(self.g.T,(self.last_cov_ba-2*self.gamma*self.cov_ba)) + pow(self.gamma, 2)*self.kernel((self.b, self.a),(self.b, self.a)) #line 30
            if self.v1 == 0:#line 31+32
                self.c_comma = self.h - np.vstack(((self.C.dot(self.delta_k)),0))#line 31
                self.v1 = (1 + pow(self.gamma,2))*pow(self.sigma, 2) + self.delta_ktt - np.dot(self.delta_k.T, self.C).dot(self.delta_k)
            else:#line 31+32
                self.c_comma = (self.gamma*pow(self.sigma,2)/self.v1)*np.vstack((self.c, 0)) + self.h - np.vstack(((self.C.dot(self.delta_k)),0))#line 31
                #Problem: self.c and self.delta_k is column vector, attend to the matrix product at the second term from the last
                #Solution: need to tranpose one of them
                self.v1 = (1 + pow(self.gamma,2))*pow(self.sigma, 2) + self.delta_ktt - np.dot(self.delta_k.T, self.C).dot(self.delta_k) + (2*self.gamma*pow(self.sigma,2)/self.v1)*np.dot(self.c.T, self.delta_k) - (pow(self.gamma, 2)*pow(self.sigma, 4))/float(self.v1)#line 32

            self._add_ba_to_D()#line 28 moved here since most calcuation used old D.
            #Problem/Guess=NotGasic/Solution: Also need to update g' to full size of new D to copy to g for next turn, If not, line 30, 35 is miss match:CORRECT
            self.g_comma = np.zeros((len(self.D), 1))#line not in presudo-code, CHECK:the size of g' is not pointed out, but took as similar to first turn
            self.g_comma[-1, -1] = 1
            self.means = np.vstack((self.means, 0))#line 33
            self.C = self._add_one_column_zeros(self.C)
            self.C = self._add_one_row_zeros(self.C)
            #Problem: self.c less is set from previous update D, so it less than one demension compared to self.means make error when update means
            #Solution: reset self.c fix with new D, Gasic checked using c'
            #self.c = np.vstack((self.c, 0))
        else:#not exceed to add to distionary or is the terminal/end dialogue
            #line 35
            print 'don''t add to D or last turn, line 35 -> 41'
            #pdb.set_trace()
            #line 35
            self.h = self.g - self.gamma*self.g_comma
            if self.v1==0:
                self.c_comma = self.h - np.dot(self.C, self.delta_k)
            else:
                self.c_comma = (self.gamma*pow(self.sigma,2)/self.v1)*self.c + self.h - np.dot(self.C, self.delta_k)
            #line 36
            if not end_dialogue:#can be wrote shorter, but it is not neassary
                if self.v1==0:#line 37
                    self.v1 = (1 + pow(self.gamma,2))*pow(self.sigma, 2) + np.dot(self.delta_k.T, self.c_comma)
                else:
                    self.v1 = (1 + pow(self.gamma,2))*pow(self.sigma, 2) + np.dot(self.delta_k.T, (self.c_comma + (self.gamma*pow(self.sigma, 2)/self.v1)*self.c)) - pow(self.gamma, 2)*pow(self.sigma, 4)/float(self.v1)
            else:#terminal turn
                print 'terminal turn, line 39'
                if self.v1==0:#line 39
                    self.v1 = pow(self.sigma, 2) + np.dot(self.delta_k.T, self.c_comma)
                else:
                    self.v1 = pow(self.sigma, 2) + np.dot(self.delta_k.T, (self.c_comma + (self.gamma*pow(self.sigma, 2)/self.v1)*self.c)) - pow(self.gamma, 2)*pow(self.sigma, 4)/self.v1
        #last line 42
        print 'Update means, C, c, g, CHECK'
        print '(before update) c.T=', self.c.T
        #pdb.set_trace()
        #Problem:CHANGE: CHECK self.c -> self.c_comma: CORRECT, Gasic checked
        self.means = self.means + (self.c_comma/float(self.v1))*self.d
        self.C = self.C + (1.0/self.v1)*np.dot(self.c_comma, self.c_comma.T)
        self.c = self.c_comma.copy()
        self.g = self.g_comma.copy()
        self.update_q(end_dialogue)

    def get_da(self, user_act_queue, belief_tracker):
        user_act = None#Currently not use user_act, tranfer to choose_act
        if len(user_act_queue)!= 0:
            user_act = user_act_queue.pop()

        self.belief_space = belief_tracker.get_belief_space()
        #self.b = self.basis_fun(belief_tracker.get_belief_space())
        self.b = self.basis_fun(self.belief_space)

        if self._first_episode:#First Episode
            print '--------first episode + first turn'
            self._first_episode = False
            self._init_step = False
            self.a = self.rand_act()
            self.D = [(self.b, self.a)]
            self.K1 = np.array([[1.0/self.kernel((self.b, self.a), (self.b, self.a))]])
            #Problem/Fix: this code to fix the element of means, C, c always agree with the D.
            self.means = np.array([[0.0]])
            self.C = np.array([[0.0]])
            self.c = np.array([[0.0]])#self.c will be init again in _calculate in first turn. Don't need
            #----------------
            self._calculate_first_turn()

            self.last_a = self.a
            self.last_b = self.b.copy()
            self.last_sys_act = self.build_full_act(user_act_queue, belief_tracker.get_belief_space(), self.a)
            return self.last_sys_act#take action a
        elif self._init_step:#it is the first turn of each dialogue
            print '---------init step/first turn'
            self._init_step = False
            self.a = self.choose_act()
            self._calculate_first_turn()

            self.last_a = self.a
            self.last_b = self.b.copy()
            self.last_sys_act = self.build_full_act(user_act_queue, belief_tracker.get_belief_space(), self.a)
            return self.last_sys_act#take action a

        #For every normal turn (except first turn)
        #variable b, a from here is representing for b', a' in the algorithm. the previous b, a is saved in self.last_a and self.last_b
        #self.cov_ba = kernel(b', a') and self.last_cov_ba = kernel(b, a)
        #Note: don't used the kernel(b, a) (cov_ba) again an again since it change frequently based on the Dictionary
        print '---------normal turn'
        #pdb.set_trace()
        self.reward = self.reward_calculator.get_turn_reward(self.last_sys_act)
        #self.R.append(self.reward)
        #line 20-22
        self.a = self.choose_act()#choose action a' for the current observed b'
        self.cov_ba = self.kernel_all((self.b, self.a))#kernel(b', a') - current observed b' and next act a'
        self.g_comma = np.dot(self.K1, self.cov_ba)
        self.delta = self.kernel((self.b, self.a), (self.b, self.a))-np.dot(self.cov_ba.T, self.g_comma)
        self.last_cov_ba = self.kernel_all((self.last_b, self.last_a))
        self.delta_k = self.last_cov_ba - self.gamma*self.cov_ba #the size of cov/kernel(b,a) can be diff
        #line 26-42
        self._calculate_from_second_turn()
        self.last_a = self.a#line 44
        self.last_b = self.b.copy()
        self.last_sys_act = self.build_full_act(user_act_queue, belief_tracker.get_belief_space(), self.a)
        #pdb.set_trace()
        return self.last_sys_act#take action a

    def kernel_all(self, (b, a)):
        '''return a list of kernel(X, (b,a)) where X is every current element in self.B'''
        ret = []
        for p in self.D:
            ret.append(self.kernel((b,a),p))
        ret = np.array([ret]).T#convert to column vector
        return ret

    def update_q(self, end_dialogue):
        print 'Info Summary:'
        if not end_dialogue:
            print '---B:', self.b
            print '---act:', self.a
        else:
            print '---B: END_DIALOG'
        print '---D:\n', np.array(self.D)
        print '---K-1:\n', self.K1
        print '---d:', self.d
        print '---C:\n', self.C
        print '---c.T:\n', self.c.T
        
        if 'c_comma' in self.__dict__.keys():
            print '---c_comma.T:\n', self.c_comma.T if self.c_comma is not None else ''
        if 'reward' in self.__dict__.keys():
            print '---reward:', self.reward
        print '---v1:', self.v1
        print '---means:\n', self.means        
        
        #pdb.set_trace()
        #for b, a in self.B:

    def calculate_q(self, b, a):
        #TODO: Gasic also user some parameter to multiple with variance, since current GP is not good to estiame the variance (current smaller)
        cov_ba = self.kernel_all((b, a))
        mean = np.dot(cov_ba.T, self.means)[0, 0]
        variance = self.kernel((b,a), (b,a))- np.dot(np.dot(cov_ba.T, self.C), cov_ba)#TODO: Choose the variance bigest to do in random action, to explore the most unstable part
        variance = variance[0,0]
        print '---action=', a, '-> Q(b, a) is sampling from N(%f, %f)'% (mean, variance)
        #pdb.set_trace()
        if variance <0:
            #TODO:Problem: remove, fix
            #variance = abs(variance)
            pdb.set_trace()
        #return np.random.normal(mean, self.variance_scale*pow(variance,0.5))
        return (mean, variance)
        #return mean

    def choose_act(self):
        if random.random()<=self.epsilon:#current set epsiolon=-1 meaning never e-greedy clearly. but e-greedy from Gaussian process based on uncertainty (active learning)
            return self.rand_act()
        else:
            print 'find the best act for belief', self.b
            #pdb.set_trace()
            q_values = []; q_variances = []
            for a in self.acts:
                mean , variance = self.calculate_q(self.b, a)
                q_values.append(np.random.normal(mean, self.variance_scale*pow(variance,0.5)))#sampling the values of Q(b, a)
                q_variances.append(variance)

            tmp = max(q_variances)
            if self.max_variance < tmp:
                self.max_variance = tmp
            
            print '---Got Q(b, a) =', q_values
            a = self.acts[np.array(q_values).argmax()]
            print '---Choose a = ', a
            
            #for QGP-Sarsa
            if self.off_policy:#Off policy learning
                a = self.get_off_policy_act(self.belief_space)
                
            print '---Finally, choose a = %s %s' % (a, '(off-policy)' if self.off_policy else '')
            return a

    def rand_act(self):
        #print 'random act'
        #return self.acts[random.randint(0, len(self.acts)-1)]
        return self.get_off_policy_act(self.belief_space)

#Need to be difined to use the GP-Sharsa for a new dialogue system
##    def _get_off_policy_act(self, belief_space):
##        print '---Get off_policy_act:',
##        do_threshold = 0.6#read from config but outside of qgp-sarsa
##        max_assign, prob = belief_space.get_nbest_assignments(1)[0]
##        if prob >= do_threshold:#do action and end dialog
##            off_a = str(max_assign)
##        else:
##            off_a = 'request'
##        print off_a
##        return off_a
##    
##    def _kernel(self, (b1, a1), (b2, a2)):
##        self.state_kernel = gaussian_kernel_fun
##        #self.state_kernel = polyminal_kernel_fun
##        self.action_kernel = kronecker_delta_kernel_fun
##        return self.state_kernel(b1, b2, p=4, sigma=5)*self.action_kernel(a1, a2)
##        #TODO!!!TODO:CHECK the way of sigma related to both 
##
##    def _get_action_set(self):
##        acts = ['request', 'accept', 'delay', 'reject']
##        return acts
##
##    def _build_full_act(self, user_act_queue, belief_space, a):
##        grammar = Grammar('decision')
##        sys_da = DialogueAct()
##
##        if a=='accept' or a=='delay' or a=='reject':
##            dai = DialogueActItem('end')
##            sys_da = DialogueAct(dai)
##            dai = DialogueActItem(a, {'appointment':{'person': 'Mr. Bean', 'time': 'next Monday at 9.00 AM'}})
##            sys_da.append(dai)    
##        else:
##            dai = DialogueActItem('request', {'decision':['accept','delay', 'reject'], 'appointment':{'person': 'Mr. Bean', 'time': 'next Monday at 9.00 AM'}}, grammar)
##            sys_da.append(dai)
##
##        if self.last_sys_act==None:
##            dai = DialogueActItem('hello', {})
##            sys_da.append(dai)
##        elif a=='request':
##            dai = DialogueActItem('sorry', {})
##            sys_da.append(dai)
##            
##        return sys_da
##
##    def _basis_fun(self, belief_space):
##        return belief_space.probs
##
##    def _update_value_fun(self, old_value, new_value):
##        for k, v in new_value.iteritems():
##            old_value[k] = v
##        return old_value
##
##    def _create_q_store(self):
##        self.distant_threshold = 0.2
##        return GridApproximation(euclidean_distance, self._update_value_fun, self.distant_threshold) #Todo: when finish gpsharsa, check threshold = 0.25, 0.3, 0.4
