'''
Test Reward Calculator
'''
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__),'../../'))

from utils.functions import config_section_to_dict
from utils.globalconfig import *

from simple_reward_calculator import SimpleRewardCalculator

def test1():
    init_config()
    config = get_config()
    config.read('../../config-all-simple.conf')
    reward = SimpleRewardCalculator()
    rs = [reward.get_final_goal_reward('accept', 'accept'),
          reward.get_final_goal_reward('accept', 'reject'),
          reward.get_final_goal_reward('accept', 'delay'),
          reward.get_final_goal_reward('reject', 'accept'),
          reward.get_final_goal_reward('reject', 'delay')]
    
    print rs      
    assert rs == [5, -20, -10, -20, -10], 'got ' + rs
    
if (__name__ == '__main__'):
    test1()
