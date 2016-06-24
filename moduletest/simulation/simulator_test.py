'''
__init__ methods for module
'''

import numpy as np
import random

from simulation.simulator.simple_simulator import SimpleSimulator
from common.dialogueact import *
from utils.timecount import TimeStats
import pdb

def test2():
    num_eps = 100
    total_correct = 0
    total_turn = 0
    total_reward= 0

    time_sat = TimeStats()
    time_sat.start_clock('total')
    
    simulator = SimpleSimulator()
    for i in range(num_eps):
        key = 'dialog%d'%(i)
        time_sat.start_clock(key)
        log = simulator.simulate_one_dialogue(i+1)
        time_sat.end_clock(key)
        
        num_turn = len(log['turns'])
        ret = 'Dialogue %d......%d turns in %fs.' % (i+1, num_turn,time_sat.clocks[key])

        total_turn += num_turn
        if log['sys_prediction'] == log['user_goal']:
            total_correct += 1
            ret += ' CORRECT'
        else:
            ret += ' WRONG'
        reward = log['total_reward']
        total_reward += reward
        ret += '\t(final reward =%.2f)' % (reward)
        print ret
        
    time_sat.end_clock('total')

    num_eps = float(num_eps)
    items = ['Total %d success in %d dialgoues (%.2f%%)'%(total_correct, num_eps,total_correct*100/num_eps)]
    items.append('\tWith average turn number %.2f per dialogue'%(total_turn/num_eps))
    items.append('\tEach turn processed less than %fs.'%(time_sat.clocks['total']/float(total_turn)))
    items.append('\tAnd average total reward %fs.'%(total_reward/float(num_eps)))
    print '\n'.join(items)
    
    return True is not False


def testLog():#Log without multiple seeds
    num_eps = 1
    total_correct = 0
    total_turn = 0
    total_reward= 0
    #for process statictis
    num_eps_log = 1
    rewards = []
    turns = []
    num_correct = 0
    times = []

    time_sat = TimeStats()
    time_sat.start_clock('total')
    
    simulator = SimpleSimulator()
    for i in range(num_eps):        
        key = 'dialog%d'%(i)
        time_sat.start_clock(key)
        log = simulator.simulate_one_dialogue(i+1)
        time_sat.end_clock(key)
        
        num_turn = len(log['turns'])
        turns.append(num_turn)#for process statictis
        times.append(time_sat.clocks[key]/float(num_turn))#for process statictis
        ret = 'Dialogue %d......%d turns in %fs.' % (i+1, num_turn,time_sat.clocks[key])

        total_turn += num_turn
        if log['sys_prediction'] == log['user_goal']:
            total_correct += 1
            ret += ' CORRECT'
            num_correct+=1#for process statictis
        else:
            ret += ' WRONG'
        reward = log['total_reward']
        total_reward += reward
        ret += '\t(final reward =%.2f)' % (reward)
        rewards.append(reward)#for process statictis
        
        print ret
        #process statistical
        if i != 0 and (i+1)%num_eps_log==0:
            #calculate write log
            reward_mean = np.mean(rewards)
            reward_std = np.std(rewards)
            turn_mean = np.mean(turns)
            turn_std= np.std(turns)
            time_mean = np.mean(times)
            time_std = np.std(times)
            success_rate = float(num_correct)/num_eps_log
            with open('log.csv', 'a') as log_file:
                log_file.write('%d, %.2f, %.3f, %.3f, %.2f, %.2f, %.3f, %.3f\n'%(i+1, success_rate, reward_mean, reward_std, turn_mean, turn_std, time_mean, time_std))
            rewards = []
            turns = []
            num_correct = 0
        
    time_sat.end_clock('total')

    num_eps = float(num_eps)
    items = ['Total %d success in %d dialgoues (%.2f%%)'%(total_correct, num_eps,total_correct*100/num_eps)]
    items.append('\tWith average turn number %.2f per dialogue'%(total_turn/num_eps))
    items.append('\tEach turn processed less than %fs.'%(time_sat.clocks['total']/float(total_turn)))
    items.append('\tAnd average total reward %fs.'%(total_reward/float(num_eps)))
    print '\n'.join(items)
    
    return True is not False


def test1():#Test for QGP-Sarsa paper, seeds, log files
    num_random_seed = 1#50 seeds
    num_eps = 3#2000 episodes
    num_eps_log = 1#500 logging at
    
    m_succ = np.ndarray((num_eps/num_eps_log, num_random_seed))
    m_reward = np.ndarray((num_eps/num_eps_log, num_random_seed))
    m_reward_std = np.ndarray((num_eps/num_eps_log, num_random_seed))
    m_turn = np.ndarray((num_eps/num_eps_log, num_random_seed))
    m_turn_std = np.ndarray((num_eps/num_eps_log, num_random_seed))
    for rand in range(num_random_seed):
        random.seed(rand)
        np.random.seed(rand)
        
        total_correct = 0
        total_turn = 0
        total_reward= 0
        #for process statictis
        rewards = []
        turns = []
        num_correct = 0
        times = []

        time_sat = TimeStats()
        time_sat.start_clock('total')
        
        simulator = SimpleSimulator()
        for i in range(int(num_eps)):        
            key = 'dialog%d'%(i)
            time_sat.start_clock(key)
            log = simulator.simulate_one_dialogue(i+1)
            time_sat.end_clock(key)
            
            num_turn = len(log['turns'])
            turns.append(num_turn)#for process statictis
            times.append(time_sat.clocks[key]/float(num_turn))#for process statictis
            ret = 'Dialogue %d......%d turns in %fs.' % (i+1, num_turn,time_sat.clocks[key])

            total_turn += num_turn
            if log['sys_prediction'] == log['user_goal']:
                total_correct += 1
                ret += ' CORRECT'
                num_correct+=1#for process statictis
            else:
                ret += ' WRONG'
            reward = log['total_reward']
            total_reward += reward
            ret += '\t(final reward =%.2f)' % (reward)
            rewards.append(reward)#for process statictis
            
            print ret
            #process statistical
            if i != 0 and (i+1)%num_eps_log==0:
                #calculate write log
                reward_mean = np.mean(rewards)
                reward_std = np.std(rewards)
                turn_mean = np.mean(turns)
                turn_std= np.std(turns)
                time_mean = np.mean(times)
                time_std = np.std(times)
                success_rate = float(num_correct)/num_eps_log
                with open('log.csv', 'a') as log_file:
                    log_file.write('%d, %.2f, %.3f, %.3f, %.2f, %.2f, %.3f, %.3f\n'%(i+1, success_rate, reward_mean, reward_std, turn_mean, turn_std, time_mean, time_std))
                    m_succ[i/num_eps_log, rand] = success_rate
                    m_reward[i/num_eps_log, rand] = reward_mean
                    m_reward_std[i/num_eps_log, rand] = reward_std
                    m_turn[i/num_eps_log, rand] = turn_mean
                    m_turn_std[i/num_eps_log, rand] = turn_std
                    
                                            
                rewards = []
                turns = []
                num_correct = 0
            
        time_sat.end_clock('total')

        num_eps = float(num_eps)
        items = ['Total %d success in %d dialgoues (%.2f%%)'%(total_correct, num_eps,total_correct*100/num_eps)]
        items.append('\tWith average turn number %.2f per dialogue'%(total_turn/num_eps))
        items.append('\tEach turn processed less than %fs.'%(time_sat.clocks['total']/float(total_turn)))
        items.append('\tAnd average total reward %fs.'%(total_reward/float(num_eps)))
        print '\n'.join(items)

        simulator.end()

    np.savetxt('sumsucc.csv', m_succ, fmt='%.4f', delimiter=',')
    np.savetxt('sumreward.csv', m_reward, fmt='%.4f', delimiter=',')
    np.savetxt('sumrewardstd.csv', m_reward_std, fmt='%.4f', delimiter=',')
    np.savetxt('sumturn.csv', m_turn, fmt='%.4f', delimiter=',')
    np.savetxt('sumturnstd.csv', m_turn_std, fmt='%.4f', delimiter=',')
    
    return True is not False

