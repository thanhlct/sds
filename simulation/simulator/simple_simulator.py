'''
Simulating dialgouge
'''

from simulation.base import Simulator
from utils.design_pattern import *
from common.dialogueact import *
from common.grammar import *

#import pdb

class SimpleSimulator(Simulator):
    def __init__(self):
        super(SimpleSimulator, self).__init__()
        self.user_simulator = get_class(self.config.get(self.MY_ID, 'userSimulatorClassPath'))
        self.asr_simulator = get_class(self.config.get(self.MY_ID, 'asrSimulatorClassPath'))
        self.dialogue_manager = get_class(self.config.get(self.MY_ID, 'dialogueManagerClassPath'))
        self.reward_calculator = get_class(self.config.get(self.MY_ID, 'rewardCalculatorClassPath'))
        
    def simulate_one_dialogue(self, dialogue_id):
        user_simulator = self.user_simulator
        asr_simulator = self.asr_simulator
        dialogue_manager = self.dialogue_manager
        reward_calculator = self.reward_calculator

        user_simulator.new_dialogue()
        dialogue_manager.new_dialogue()
        
        self.logger.info('\n\n-----------------------------------------------------------------------------')
        self.logger.info('Dialogue %d.\t\tUser Goal: %s' % (dialogue_id, user_simulator.goal))
        self.logger.info('-----------------------------------------------------------------------------')

        turns = []
        i = 1
        total_reward = 0
        while True:
            self.logger.info('\n------ Turn %d ------' % (i))
            total_reward += reward_calculator.get_turn_reward()
            
            sys_da = dialogue_manager.da_out()
            self.logger.info('System Action\t=%s' % (sys_da))
            if sys_da.type =='end':
                user_da = None
                break
            
            user_simulator.da_in(sys_da)
            user_da = user_simulator.da_out()
            self.logger.info('User Action\t= %s'% (user_da))
            if user_da.type =='end':
                #call dialgoue_manager.end_dialogue('parameter')
                #dialogue_manager.end_dialogue(None)#unknown user goal, user don't want to feedback
                #dialogue_manager.end_dialogue(user_simulator.goal)
                break
            
            asr_hyps = asr_simulator.simulate_asr(sys_da.grammar, user_da)
            self.logger.info('ASR Hypotheses\t=\n%s'% (asr_hyps))
            
            dialogue_manager.da_in(asr_hyps)
            self.logger.info('Belief State\t=\n%s' % (dialogue_manager.belief_tracker.get_belief_space()))

            turns.append({
                'sys_act': sys_da,
                'user_act': user_da,
                'asr_hyps': asr_hyps,
                'belief_state': dialogue_manager.belief_tracker,
                })
            i = i + 1

        #feedback from user
        dialogue_manager.end_dialogue(user_simulator.goal)#assume always know user's goal
        
        turns.append({
            'sys_act': sys_da,
            'user_act': user_da,
            'asr_hyps': None,
            'belief_state': None,
            })
            
        
        log  = {'user_goal': user_simulator.goal, 'turns': turns, 'sys_prediction': {'decision': turns[-1]['sys_act'][1].type}}
        total_reward += reward_calculator.get_final_goal_reward(log['user_goal'], log['sys_prediction'])
        #log['total_reward']= reward_calculator.calculate_total_reward(log)
        log['total_reward']= total_reward
        self.logger.info('TOTAL REWARD\t=%f'% (log['total_reward']))
        return log

    def end(self):
        self.dialogue_manager.save()
