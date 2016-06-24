'''
Sampling a value from given distribution
'''

from random import random
from numpy.random.mtrand import dirichlet

def sample_from_dict(dt):
    '''
    Given a dict, representing a multinomial distribution, 
    of the form:
    
      { 
        'key1' : prob1,
        'key2' : prob2,
        ...
      }

    sample a key according to the distribution of probs.
    '''
    r = random()
    s = 0.0
    for f in dt:
        s += dt[f]
        if (r < s):
            return f
    raise RuntimeError,'Didnt sample anything from this hash: %s (r=%f)' % (str(dt),r)

def sample_dirichlet_from_dict(dt):
    '''
    Sample one set or dirichlet distribution for given dictionary
    '''
    alphas = dt.values()
    raw_dist = dirichlet(alphas)
    return dict( zip((dt.keys()), (raw_dist)) )
