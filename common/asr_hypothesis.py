'''
List of hypothesis from Automatic Speech Recognition
'''

class ASRHypothesisItem(object):
    '''An item of ASR result - the combination of User Dialogue Act and its probaility
    '''
    def __init__(self, dialogue_act, prob):
        self.dialogue_act = dialogue_act
        self.prob = prob

    def __str__(self):
        return '%s (%f)'%(self.dialogue_act, self.prob)


class ASRHypothesis(object):
    '''ASR hypothesis list
    '''
    MY_ID = 'ASRHypothesis'
    def __init__(self, dialogue_acts, probs, grammar=None):
        #self.logger = getLogger(self.MY_ID)
        #self.config = GetConfig()
        assert len(dialogue_acts)==len(probs), 'the size of diaogue_acts(%d) must be equal to the size of probs (%d)' % (len(dialogue_acts), len(probs))
        self.dialogue_acts = dialogue_acts
        self.probs = probs
        self.prob_total = sum(self.probs)

    def __getitem__(self, index):
        return ASRHypothesisItem(self.dialogue_acts[index], self.probs[index])

    def __iter__(self):
        i = 0
        while i<len(self.probs):
            yield self[i]
            i = i + 1

    def __len__(self):
        return len(self.probs)

    def get_description(self, max_show=-1):
        if max_show==-1:
            max_show = len(self.probs)
            
        items = []
        for i in range(min(max_show,len(self.probs))):
            items.append(str(self[i]))
            
        if max_show < len(self.probs):
            items[-1] += ' + %d more' % (len(self.probs) - max_show)
        items.append('[rest] (%f)' % (1.0 - self.prob_total))
        
        s = '\n'.join(items)
        return s
        
    def __str__(self):        
        return self.get_description(5)
