'''
Grid-based Approximation Test
'''
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__),'../../'))

from utils.distance_measures import euclidean_distance
from common.grid_approximation import GridApproximation
import numpy as np

def update_value_fun(old_value, new_value):
    for k, v in new_value.iteritems():
        old_value[k] = v
    return old_value

def test1():
    g = GridApproximation(euclidean_distance, update_value_fun, 0.2)#Todo: when finish gpsharsa, check threshold = 0.25, 0.3, 0.4
    print g.is_empty()
    g.add(tuple([0.2, 0.2, 0.2]), {'request': 1.5})
    print g.is_empty()
    g.add(tuple([0, 0, 0]), {'request': 1.5})
    g.add(tuple([0.2, 0.2, 0.4]), {'accept': 1.6})
    g.add(tuple([0.2, 0.33, 0.2]), {'reject': 1.5})
    g.add(tuple([1, 1, 1]), {'reject': 1.5})
    g.add(tuple([0, 0, 0.19]), {'request': 1005})
    g[(0.2, 0.2, 0.2)] = {'delay': 2.0}    
    g[[0, 0.1, 0.1]] = {'delay': 2.0}
    print g
    print 'Total point number', g.get_total_point_number()
    print g[0.2, 0.3, 0.2]
    print g[np.array([0.2, 0.3, 0.2])]
    print 'check distance:', euclidean_distance([0, 0, 0], [0.15, 0.15, 0.15])
        
if (__name__ == '__main__'):
    test1()
    

    

