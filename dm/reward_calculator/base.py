'''
Reward Calculator
'''

from logging import getLogger

from utils.globalconfig import get_config
import pdb

class RewardCalculatorBase(object):
    MY_ID = 'RewardCalculator'
    def __init__(self):
        self.config = get_config()
        self.logger = getLogger(self.MY_ID)

    def get_turn_reward(self, sys_da):
        '''The reward for given sys_da'''
        pass
    
    def get_final_goal_reward(self, user_goal, sys_prediction):
        '''The reward for correct or incorrect the user goal, so-called sucessful reward'''
        pass

    def calculate_total_reward(self, full_dialogue_log):
        '''Calculate the total reward for a given full log of a dialogue'''
        r = 0
        for turn in full_dialogue_log['turns']:
            r += self.get_turn_reward(turn)
        r += self.get_final_goal_reward(full_dialogue_log['user_goal'], full_dialogue_log['sys_prediction'])
        return r
