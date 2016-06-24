'''
Reward Calculator
'''

from base import RewardCalculatorBase
from utils.functions import config_section_to_dict

import pdb

class SimpleRewardCalculator(RewardCalculatorBase):
    '''Simple Reward Calculator'''
    def __init__(self):
        super(SimpleRewardCalculator, self).__init__()
        self.params = config_section_to_dict(self.config, self.MY_ID)
        
    def get_turn_reward(self, sys_da=None):
        '''The reward for given sys_da'''
        return self.params['turnReward']
    
    def get_final_goal_reward(self, user_goal, sys_prediction):
        '''The reward for correct or incorrect the user goal, so-called sucessful reward'''
        
        if not isinstance(sys_prediction, dict):#for specific case (this example) :(sad
            sys_prediction = {'decision': sys_prediction[1].type}
            
        if user_goal == sys_prediction:
            return self.params['goalCorrect']
        else:
            content = sys_prediction['decision']
            if content in self.params['goalWrong'].keys():
                return self.params['goalWrong'][content]
            
        return self.params['goalWrong']['all']
    
