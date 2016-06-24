'''
Extracting ASR hypotheses from cloud-based ASR Watson
'''
import math

from base import ASRResult
from common.dialogueact import *
from common.asr_hypothesis import ASRHypothesis

import pdb

class TranscriptASRResult(ASRResult):
    def __init__(self):
        '''init something'''
        super(TranscriptASRResult, self).__init__()
    
    @classmethod
    def GetASRHypotheses(cls, transcript, confidence, grammar):
        #TODO: to many thing to do, new methods is needed
        user_act_hyps = []
        probs = []
        candidates = ['accept', 'delay', 'reject']#get from grammar
        for c in candidates:
            user_act_hyps.append(DialogueAct(DialogueActItem('inform', {'decision':c})))
            probs.append(cls._calculate_prob_based_phoneme(transcript, c))

        total = float(sum(probs))
        if total !=0 :
            for i, p in enumerate(probs):
                probs[i] = confidence*probs[i]/total

        asr_hyps = ASRHypothesis(user_act_hyps, probs, grammar)
        return asr_hyps

    @classmethod
    def _calculate_prob_based_phoneme(cls, transcript, cand):
        transcript = transcript.lower()
        
        filter_words = ['want', 'to', 'would', 'like', 'the', 'appointment', 'not sure', 'let', 'love', 'he', 'she', 'him', 'her', 'be', 'never', 'how', 'about', 'that', 'is', 'it', 'i']
        replace_from = ['meet', 'later', 'hate']
        replace_to = ['accept', 'delay', 'reject']

        for w in filter_words:
            transcript = transcript.replace(w, '').strip()
        for i, w in enumerate(replace_from):
            transcript = transcript.replace(w, replace_to[i]).strip()

        print '----!!!filtered transcript', transcript
        count = 0
        for c in cand:
            if c in transcript:
                count +=1
        print 'part of %s: %f'%(cand, float(count)/len(cand))
        return float(count)/len(cand)
        
    
