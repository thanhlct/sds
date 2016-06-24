'''
Simple ASR Simulator
'''

from random import betavariate, sample, randint
from statlib.stats import lbetai

from simulation.base import ASRSimulator
from utils.functions import config_section_to_dict
from utils.sampledistribution import sample_from_dict, sample_dirichlet_from_dict
from common.dialogueact import *
from common.asr_hypothesis import ASRHypothesis

class SimpleASRSimulator(ASRSimulator):
    """Simulate ASR Hypothesis"""

    def __init__(self):
        super(SimpleASRSimulator, self).__init__()
        
        self.fields = self.config.get(self.MY_ID, 'fields')
        self.fields = self.fields.split(',')
        #Todo: in reall apps, add the special fields in future: all, confirm etc.
        
        self.params = {}
        self.params['default'] = config_section_to_dict(self.config, self.MY_ID + '_default')
        for field in self.fields:
            section_name = '%s_%s' % (self.MY_ID, field)
            if (self.config.has_section(section_name)):
                self.params[field] = config_section_to_dict(self.config,section_name)
            else:
                self.params[field] = self.params['default']
                
        self.logger.debug('Params = %s' % (self.params))

    def simulate_asr(self, grammar, user_da):
        """Simulate N-bets list ASR"""
        ret_type = self._sample_result_type(grammar, user_da) #The type of confusion: onlist, offlist, slient, correct
        
        #Todo: In more real apps, user can make request
        if (ret_type == 'silent'):
            user_act_hyps = [DialogueAct(DialogueActItem('silent'))]
            probs = [ 1.0 ]
            correct_pos = -1
        else:
            length = self.params[grammar.name]['maxLength']
            length = randint(1, length) #CHECK: always generate maxLength elements or [1, maxLength] elements
            if (length > grammar.cardinality):
                length = grammar.cardinality
            if (user_da.type == 'inform' and length == grammar.cardinality and ret_type == 'offlist'): # Inform with all possible hypothesis, so it must be onlist
                ret_type = 'onlist'
                
            if (ret_type == 'correct'):
                correct_pos = 0
            elif (ret_type == 'onlist' and length > 1):
                correct_pos = self._sample_onlist_position(grammar,length)
            else:#for offlist - don't appear in the list
                correct_pos = -1
            #print 'length_hyps\t=%d, ret_type= %s, correct_pos=%d' % (length, ret_type, correct_pos)
            user_act_hyps = self._sample_user_action_hyps(grammar,length,correct_pos,user_da)
            probs = self._sample_probs(grammar,'inform',ret_type,length)
            
        #print 'user_act_hyps\t=', user_act_hyps
        #print 'probs_hyps\t=', probs
        
        asr_hyps = ASRHypothesis(user_act_hyps, probs, grammar)
        self.logger.info('---ASR Hypothesis:\n%s'%(asr_hyps))
        return asr_hyps

    def _sample_result_type(self, grammar, user_da):
        """Sample the confusion way
        """
        return sample_from_dict(self.params[grammar.name]['confusionMatrix'][user_da.type])

    def _sample_onlist_position(self, grammar, length):
        '''
        Returns an index in the range [1,length-1]
        Length must be > 1
        '''
        assert (length > 1),'length must be > 1; length=%d' % (length)
        alpha = self.params[grammar.name]['onlistFraction']['alpha']
        beta = self.params[grammar.name]['onlistFraction']['beta']
        x = betavariate(alpha, beta) #Check: beta distribution
        position = int((length-1) * x) + 1
        if (position == length):
            position -= 1
        return position

    def _sample_user_action_hyps(self, grammar,length,correct_pos,user_da):
        '''
        Generating User DialogueAct Hypothesis
        '''
        #CHECK: the assert input values statement????
        if (user_da.type != 'inform' or correct_pos >= 0):
            assert (length <= grammar.cardinality), 'Length cannot be greater than ' \
          'grammar.cardinality (Length=%d, grammar.cardinality=%d, correctPosition=%d)' \
          % (length,grammar.cardinality,correct_pos)
        else:
            assert (length < grammar.cardinality), 'Length cannot be greater than ' \
              'OR EQUAL TO grammar.cardinality (Length=%d, grammar.cardinality=%d, correctPosition=%d)' % \
              (length,grammar.cardinality,correct_pos)
        
        user_da_hyps = []
        if grammar.name == 'all':
            #Todo: for open dialogue management, Generate more complex combination from database
            raise NotImplementedError, 'SimpleUserSimulator: grammar.name=all'
        else:   #get a random value for the field in grammar.name
            sample_length = length
            if correct_pos ==-1 and user_da.type =='inform':
                sample_length= length+1 #increase one in the case samle lucky true
            rowids = sample(xrange(grammar.cardinality), sample_length)

            for i in range(length):
                if i==correct_pos:
                    user_da_hyp = user_da
                else:
                    while True:
                        rowid = rowids.pop(0)
                        if grammar.name == 'confirm':
                            #Todo: In future for act_type: confirm
                            raise NotImplementedError, 'SimpleUserSimulator: grammar.name=all'
                        else:
                            content = self._get_fieldvalue_by_index(grammar.name, rowid)
                        user_da_hyp = DialogueAct(DialogueActItem('inform', {grammar.name:content}))
                        if user_da != user_da_hyp:
                            break
                user_da_hyps.append(user_da_hyp)
               
        return user_da_hyps
                            
    def _get_fieldvalue_by_index(sefl, grammar_name, rowid):
        '''
        Get value of field/slot at rowid
        '''
        #Todo: move to database class, and get from database
        values = ['accept', 'delay', 'reject']
        return values[rowid]

    def _sample_probs(self, grammar, user_action_type, ret_type, length):
        '''Sample the probability for every user_act_hyps
            The first hypothesis get the highest probability respective to [correct] element in config file
            The rest of N-Best list get the total probability respective to [onlist] element in config file
            Remaining offlist get the total probability w.r.t offlist
        '''
        #Check: dirichlet??
        ret_type_probs = sample_dirichlet_from_dict(self.params[grammar.name]['probGenerator'][user_action_type][ret_type])
        #print 'sample_type_probs \t=', ret_type_probs
        probs = []
        probs.append(ret_type_probs['correct'])
        if length==1:
            pass
        else:
            if length==2:
                onlist_fractions = [1.0]
            else:
                onlist_fractions = self._get_onlist_fractions(grammar.name, length)
            #print 'onlist_fractions\t=', onlist_fractions
            for i in range(1, length):
                probs.append(ret_type_probs['onlist']*onlist_fractions[i-1])
        #print 'sample probs\t=', probs
        return probs
                        
    def _get_onlist_fractions(self, grammar_name, length):
        '''Sample fractions of onlist distribution to hypothesis
            #CHECK
        '''
        frac = []; prev = 0.0
        step_size = 1.0/(length-1.0)
        alpha = self.params[grammar_name]['onlistFraction']['alpha']
        beta = self.params[grammar_name]['onlistFraction']['beta']
        for i in range(length-1):
            x = step_size*(i+1)
            #Check: lbetai distribution??
            b = lbetai(alpha, beta, x)
            frac.append(b-prev)
            prev = b
        return frac
        






