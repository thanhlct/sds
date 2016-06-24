'''
Simple Blief Tracker
'''

from dm.base import BeliefState
from common.factor import DiscreteFactor
import numpy as np

#import pdb
#pdb.set_trace()

class SimpleBeliefTracker(BeliefState):
    '''Simple BeliefState Class for only the specific task, Appointment with 3 states - represent as 3-D vectors
    '''
    #TODO: Make it more general for every apps and apply another better belief mornitering methods
    #TODO: Load the parameter from config, build the factor initilized from Dictionary

    def __init__(self):
        super(SimpleBeliefTracker, self).__init__()
        self.slots = {'decision':['accept', 'delay', 'reject'],}
        self._pi = DiscreteFactor(['PI'], [len(self.slots['decision'])], self.slots['decision'], [0.33, 0.33, 0.33])#pi parmeter for z1
        self._phi = DiscreteFactor(['DecisionState', 'Observation'], [3,3], self.slots['decision']*2, [0.5, 0.2, 0.3, 0.25, 0.5, 0.25, 0.3, 0.2, 0.5])#essmision parameter for P(x|z)
        self._trans = DiscreteFactor(['Z', 'Z\''], [3,3], self.slots['decision']*2, [1, 0, 0, 0, 1, 0, 0, 0 , 1])
        self.logger.info(self._pi)
        self.logger.info(self._phi)
        #print '%s\n%s\n%s\n'%(self._pi, self._phi, self._trans)
        
        self._last_z = None #equivalent to alpha(z_n-1)
        self._z = None #equivalent to alpha(z_n)

    def new_dialogue(self):
        '''Reset every value for new diagoue'''
        self._first_turn = True
        self._last_z = None
        self._z = None
        #self._prior_z = self._phi
        
        self._last_z = self._pi.copy()
        self._last_z.variables[0] = 'Z'

    def _compute_px_zn(self, user_da):
        maginal_phi = self._phi.maginalize('Observation')
        px_zn = DiscreteFactor(['Z\''], [3], self.slots['decision'])
        px_zn.set_all_probs_zero()
        for row in px_zn:
            k = row[0]#calculate the P(x|Zn=k)
            for asr_hyp in user_da:#for every asr_hypothesis#tinh p(x|Zn)
                if len(asr_hyp.dialogue_act.content)==0:#for oog, slient
                    break
                x= asr_hyp.dialogue_act.content['decision']#the value of observation
                po= asr_hyp.prob#the probability of observation - asr
                phi = self._phi[k,x]#the prob of observation x given z=k
                #px_zn[k] += (po*phi)/maginal_phi[k]#??How to include po??How to includ multiple hyps
                px_zn[k] += (po*phi)#without dividing P(z_n)
        px_zn.normalize()
        return px_zn
    
    def update(self, user_da, last_sys_da):
        '''update belief date based on last_sys_da and given user_da'''
        if user_da[0].dialogue_act.type == 'silent' or user_da[0].dialogue_act.type == 'oog':
            return
        
        if self._first_turn:#The first user turn - z1
            #equation 13.73, calculate z1 #TODO: Please check again using PHI and multip hypothesis
            #TODO: Vectorlization implementation??possible, matrix multiplication? use factor product, magnilize
            self._first_turn = False
            self._z = DiscreteFactor(['Z'], [3], self.slots['decision'])
            maginal_phi = self._phi.maginalize('Observation')
            for row in self._z:#for every value/state of z
                k = row[0]#evaluate the state k of z
                pik = self._pi[k]#the value pi_k
                px_phi = 0#P(X|Phi_k)
                for asr_hyp in user_da:#for every asr_hypothesis#tinh p(x|PHI_k)
                    if len(asr_hyp.dialogue_act.content)==0:#for oog, slient
                        continue
                    x= asr_hyp.dialogue_act.content['decision']#the value of observation
                    po= asr_hyp.prob#the probability of observation - asr
                    phi = self._phi[k,x]#the prob of observation x given z=k
                    #px_phi += (po*phi)/maginal_phi[k]#??How to include po??How to includ multiple hyps
                    px_phi += (po*phi)#without dividing P(z_n)
                self._z[k] = pik*px_phi
        else:#Calculate Zn from Zn-1
            #Equation 13.36
            px_zn = self._compute_px_zn(user_da)
            self._z = px_zn*(self._last_z*self._trans).maginalize('Z')
            #pdb.set_trace()
        
        self._z.normalize()
        self._last_z = self._z.copy()
        self._last_z.variables[0] = 'Z'

    def get_belief_space(self):
        '''Return the full belief space'''
        return self._last_z

    def __str__(self):
        return str(self.get_belief_space)
