'''
Extracting ASR hypotheses from cloud-based ASR Watson
'''
import math

from base import ASRResult
from common.dialogueact import *
from common.asr_hypothesis import ASRHypothesis
from utils.functions import config_section_to_dict
from watson_features import extract_features

class WatsonASRResult(ASRResult):
    '''Base class for delegation class defining stuffs for specific domain which is used in Q/GP-Sarsa dialogue policy'''
    def __init__(self):
        '''init something'''
        super(WatsonASRResult, self).__init__()
    
    @classmethod
    def GetASRHypotheses(cls, asr, grammar):
        self = cls()
        self.fields = ['decision']#TODO: get from DB and grammar
        user_act_hyps = []
        probs = []

        if 'nlu-sisr' in asr:
            for result in asr['nlu-sisr']:
                content = {}
                if 'interp' in result:
                    for field in self.fields:
                        if field in result['interp']:
                            content[field] = result['interp'][field]
                            
                if (len(content)>0):
                    user_act_hyps.append(DialogueAct(DialogueActItem('inform', content)))

        if len(user_act_hyps) == 0:#slient
            user_act_hyps = [DialogueAct(DialogueActItem('silent'))]
            probs = [1.0]
            asr_hyps = ASRHypothesis(user_act_hyps, probs, grammar)
            return asr_hyps

        
        section_name = '%s_%s' % (self.MY_ID,grammar.get_fullname())
        if not self.config.has_section(section_name):
            section_name = '%s_%s' % (self.MY_ID,'default')
        self.params = config_section_to_dict(self.config, section_name)

        turn = {'recoResults': asr}
        features = [1]
        asr_features = extract_features(turn)#TODO: check feature is None?
        features.extend(asr_features)

        partial = {}
        if (len(user_act_hyps) == 1):
            types = ['correct','offList']
        else:
            types = ['correct','onList','offList']
        for type in types:
            exponent = 0.0
            for (i,feature) in enumerate(features):
                exponent += feature * self.params['regression'][type][str(i)]
            partial[type] = math.exp(exponent)

        rawProbs = {}
        sum = 0.0
        for type in types:
            sum += partial[type]
        for type in types:
            rawProbs[type] = partial[type] / sum
        
        probs = [rawProbs['correct']]
        N = len(user_act_hyps)
        alpha = self.params['onListFraction']['alpha']
        beta = self.params['onListFraction']['beta']

        for n in range(1,len(user_act_hyps)):
            bucketLeftEdge = 1.0*(n-1)/N
            bucketRightEdge = 1.0*n/N
            betaRight = lbetai(alpha,beta,bucketRightEdge) / lbetai(alpha,beta,1.0)
            betaLeft = lbetai(alpha,beta,bucketLeftEdge) / lbetai(alpha,beta,1.0)
            betaPart = betaRight - betaLeft
            self.probs.append(1.0 * rawProbs['onList'] * betaPart )
        
        asr_hyps = ASRHypothesis(user_act_hyps, probs, grammar)
        return asr_hyps
        
    
