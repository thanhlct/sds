'''
Support Functions similar to Matlab
'''
import numpy as np

def ismember(a, b):
    return np.array([1 if v in b else 0 for v in a])

def diff(a, b):
    return np.array([1 if v not in b else 0 for v in a])
    
def find(condition):
    #Require element in condtion is np.array :(
    return np.where(condition)[0]

def find_indexes(a, b):
    '''find index in b for elements in a where a is subset of b'''
    a = list(a)
    b = list(b)
    ids = []
    for val in a:
        ids.append(b.index(val))
    return ids
            
