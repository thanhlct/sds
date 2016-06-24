'''
Extracting ASR hypotheses from cloud-based ASR Watson
'''
import math

from base import ASRResult
from common.dialogueact import *
from common.asr_hypothesis import ASRHypothesis

class TranscriptASRResult(ASRResult):
    def __init__(self):
        '''init something'''
        super(TranscriptASRResult, self).__init__()
    
    @classmethod
    def get_asr_hypotheses(cls, asr_hyps, grammar):
        #TODO: to many thing to do, new methods is needed
        accept_threshold = 0.15
        candidates = ['accept', 'delay', 'reject']#get from grammar
        user_act_hyps = []
        probs = []

        counts = []
        for c in candidates:
            count = cls._calculate_prob_based_phoneme(asr_hyps, c)
            counts.append(count)

        confidence = asr_hyps["0"]["confidence"]
        print 'counts:', counts
        total = float(sum(counts))
        if total>0:
            for i, c in enumerate(candidates):
                prob = confidence*counts[i]/total
                print '--c, p:', c, prob
                if prob >= accept_threshold:
                    user_act_hyps.append(DialogueAct(DialogueActItem('inform', {'decision':c})))
                    probs.append(prob)

        print 'probs:', probs
        if len(probs)==0 or total==0:
            user_act_hyps = [DialogueAct(DialogueActItem('oog'))]
            probs = [1.0]
            
        asr_hyps = ASRHypothesis(user_act_hyps, probs, grammar)
        return asr_hyps

    @classmethod
    def _calculate_prob_based_phoneme(cls, asr_hyps, cand):
        count = 0
        for i in range(asr_hyps['length']):
            hyp = asr_hyps[str(i)]
            transcript = hyp['transcript']
            confidence = hyp['confidence']
            if confidence == 0 and i!=0:
                confidence = asr_hyps["0"]["confidence"]/(i*1.5)
            if confidence!=0:
                count += confidence*cls.count_phoneme(transcript, cand)
            
        return count

    @classmethod
    def count_phoneme(cls, text, cand):
        text = text.lower()
        text = cls._standard_asr_transcript(text)
        filter_words = ['want', 'to', 'would', 'like', 'the', 'appointment', 'department', 'not sure', 'let', 'love', 'he', 'she', 'him', 'her', 'be', 'never', 'how', 'about', 'that', 'is', 'it', 'i', 'hello', 'hi', 'are', 'you']
        count = 0
        words = text.split()
        for i in range(len(cand)):
            changed = False
            for j in range(len(cand)-i):
                part = cand[j: j+i+1]
                for w in words:
                    if w not in filter_words and part in w:
                        count += i+1#can change to give more weight for bigger part
                        changed = True
            if not changed:
                break
        return count

    @classmethod
    def _standard_asr_transcript(cls, text):
        replace_from = ['\'', 'dont want to meet', 'want to meet', 'later', 'hate', 'yes', 'no', 'okay', 'ok', 'cancel', 'love', 'busy']
        replace_to = ['', 'reject', 'accept', 'delay', 'reject', 'accept', 'reject', 'accept', 'accept', 'reject', 'accept', 'reject']
        
        for i, w in enumerate(replace_from):
            text = text.replace(w, replace_to[i]).strip()
            
        return text

    @classmethod
    def get_user_goal(cls, asr_hyps, last_sys_da):
        goal = {'decision': last_sys_da[1].type}#correct
        
        transcript = asr_hyps['0']['transcript'].lower()
        nos = ['no', 'not', 'didn\'t', 'don\'t', 'wrong', 'incorrect']
        for no in nos:
            if no in transcript:
                goal = {'decision': 'incorrect'}
                break

        return goal
            

    
    
