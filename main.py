'''
Main Program
'''
#import os, sys
#sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
#import autopath

import logging.config
import logging
import random, numpy as np

from utils.globalconfig import *
from moduletest.simulation import user_simulator_test, simulator_test


def main():
    random.seed(1)
    np.random.seed(1)
    
    init_config()
    config = get_config()
    config.read('config-all-simple.conf')
    logging.config.fileConfig('logging.conf')
    
    #assert user_simulator_test.test1(), 'Fault - usertest.test1'
    assert simulator_test.test1(), 'Fault - simulator.test1'
    
if (__name__ == '__main__'):
    main()
