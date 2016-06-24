'''
Discrete Factor
'''
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))

import numpy as np
import utils.matlab_functions as matlab
#from ..utils import matlab_functions as matlab
import copy
import pdb
#pdb.set_trace()

class DiscreteFactor(object):
    '''Represent factor of one or many discerete variable
    '''
    #TODO: Initial from Dictionary, Text ....
    #TODO: Optimize every steps with vectorlized implementation
    #TODO: Implement maginalization, product etc...
    #TODO:important: assert the input data
    #TODO: Set more conventions to speed up, e.g. all values maps to 0, 1, 2, 3, speed up significantly
    #TODO: Test is it correct impelmented for bigger factor
    def __init__(self, variables, cardinalities, values, probs=None):
        '''All parameter are list of things with suitable (conventioned) order???more??
        '''
        #TODO: Do some assert about the size
        self.variables = np.array(variables)
        self.cards = np.array(cardinalities, dtype=int)
        self.values = values
        #self.probs = np.ndarray(probs)
        self.probs = np.array(probs)#dtype=np.float#np.float64
        if probs is None:
            self.set_all_probs_zero()
        
        #primarily index calculation
        self.repeat_prob = [1]#the number repeated times for a variable in prob table
        for i in range(len(self.cards)-1,0,-1):
            self.repeat_prob.append(self.repeat_prob[-1]*self.cards[i])
        self.repeat_prob.reverse()
        
        self.align_val = [0]#the alignment of values
        for card in self.cards[0:-1]:
            self.align_val.append(self.align_val[-1]+ card)

        #self.to_dict()
        self._build_dict_index()

    def to_dict(self):
        self.dict = {}
        for row in self:
            d = self.dict
            last_val = ''
            for val in row:
                if isinstance(val, basestring):
                    if last_val != '':
                        if last_val in d:
                            d = d[last_val]
                        else:
                            d[last_val] = {}
                            d = d[last_val]
                    last_val = val
                else:
                    d[last_val] = val
        return self.dict

    def from_dict(self):
        pass

    def _build_dict_index(self):
        self._iddict = {}
        idx = 0
        for row in self:
            d = self._iddict
            last_val = ''
            for val in row:
                if isinstance(val, basestring):
                    if last_val != '':
                        if last_val in d:
                            d = d[last_val]
                        else:
                            d[last_val] = {}
                            d = d[last_val]
                    last_val = val
                else:
                    d[last_val] = idx
                    idx += 1
        return self._iddict

##    def _get_value_ids_from_assigns(self, assigns):
##        '''Get the value order (index) given the variable and the assigns'''
##        ret_ids = []
##        for assign in assigns:
##            idx = []
##            for col in len(assign):
##                idx.append(self.values.index(assign, self.align_val(col))-self.align_val(col))
##            ret_ids.append(tuple(ids))
##        return ret_ids

    def _get_dict_value_from_keys(self, d, keys):
        '''Get the herihicarl value for given set key in a tuple keys'''
        tmp = d
        if isinstance(keys, tuple):
            for key in keys:
                tmp = tmp[key]
        else:#str
            tmp = tmp[keys]
        return tmp

    def _assignments_to_indexes(self, assigns):
        '''Get the indexes for given assigns'''
        ids = []
        if isinstance(assigns, tuple) or isinstance(assigns, str):
            ids.append(self._get_dict_value_from_keys(self._iddict, assigns))
        else:#type is a list
            for assign in assigns:
                ids.append(self._get_dict_value_from_keys(self._iddict, assign))
        return ids
    
    def _indexes_to_assignments(self, indexes):
        if isinstance(indexes, int):
            indexes = [indexes]
        assigns = []
        for r in indexes:
            line = []
            for c in range(len(self.variables)):
                line.append(self._get_value(c,r))
            assigns.append(tuple(line))
        return assigns
    
    def __getitem__(self, assigns):
        '''Get the prob for the given assigns'''
        return self.probs[self._assignments_to_indexes(assigns)]

    def __setitem__(self, assigns, probs):
        '''Set the prob for the given assigns'''
        self.probs[self._assignments_to_indexes(assigns)] = probs
        
    def set_all_probs_zero(self):
        self.probs = np.zeros((1, self.total_assignments))[0]
    
    def set_all_probs_one(self):
        self.probs = np.ones((1,self.total_assignments))[0]

    def normalize(self):
        #self.probs = np.linalg.norm(self.probs)#?What is the linear algbera norm?
        total = float(np.sum(self.probs))
        if total != 0:
            self.probs = self.probs/total
        
    def _get_total_assignments(self):
        return np.prod(self.cards)
    total_assignments = property(_get_total_assignments)
    
    def _get_value_id(self, var_col, order):
        '''Get the index of value of a variable given the order in the full table'''
        vid = (order/self.repeat_prob[var_col])%self.cards[var_col]
        return vid + self.align_val[var_col]

    def _get_value(self, variable, order):
        '''Get the value of variable of given variable and the order in the full table'''
        if isinstance(variable, str):
            variable = list(self.variables).index(variable)
        return self.values[self._get_value_id(variable, order)]

    def __iter__(self):
        '''iterating row by row in the full table'''
        assigns = self._indexes_to_assignments(range(self.total_assignments))
        for assign, prob in zip(assigns, self.probs):
            assign = list(assign)
            assign.extend([prob])
            yield tuple(assign)

    def _get_variables_values(self, var_ids):
        vals = []
        for col in var_ids:
            vals.extend(self.values[self.align_val[col]:self.align_val[col]+self.cards[col]])
        return vals

    def _observe_indexes(self, variables, values):
        id_map = matlab.find(matlab.ismember(self.variables, variables)==1)
        assigns = self._get_all_assignments()

        obs_ids = []
        for r, assign in enumerate(assigns):
            vals = np.array(assign)[id_map]
            if np.array_equal(vals, values):
                obs_ids.append(r)
        return obs_ids
        
    def observe(self, variables, values):
        id_vars = matlab.find(matlab.diff(self.variables, variables)==1)        
        f = DiscreteFactor(self.variables[id_vars], self.cards[id_vars], self._get_variables_values(id_vars))
        obs_ids = self._observe_indexes(variables, values)
        f.probs= self.probs[obs_ids]
        f.normalize()
        return f

    def _get_all_assignments(self):
        return self._indexes_to_assignments(range(self.total_assignments))
    
    def _maginal_sum_indexs(self, factor):
        id_map = matlab.find(matlab.ismember(self.variables, factor.variables)==1)
        assigns = self._get_all_assignments()
        mag_assigns = factor._get_all_assignments()
        mag_ids = []
        for assign in assigns:
            vals = tuple(np.array(assign)[id_map])
            mag_ids.append(mag_assigns.index(vals))
        return mag_ids
    
    def maginalize(self, *variables):
        '''Maginalize the given vars, return the maginalized vector, no change the self'''
        ids = matlab.find(matlab.diff(self.variables, variables)==1)
        f = DiscreteFactor(self.variables[ids], self.cards[ids], self._get_variables_values(ids))
        
        mag_ids = np.array(self._maginal_sum_indexs(f))#required to user matlab.find                
        for r, assign in enumerate(f._get_all_assignments()):
            ids = matlab.find(mag_ids==r)
            f[assign] = sum(self.probs[ids])
        return f
    
    def product(self, factor):
        #TODO: Vector optimize later
        variables = np.union1d(self.variables, factor.variables)        
        map1 = matlab.find_indexes(self.variables, variables)
        map2 = matlab.find_indexes(factor.variables, variables)
        cards = np.zeros((1,len(variables)))[0]
        cards[map1] = self.cards
        cards[map2] = factor.cards
        
        values = []
        for var in variables:
            if var in list(self.variables):
                col = matlab.find(self.variables==var)
                values.extend(self._get_variables_values(col))
            else:
                col = matlab.find(factor.variables==var)
                values.extend(factor._get_variables_values(col))
                
        f = DiscreteFactor(variables, cards, values)
        for r, assign in enumerate(f._get_all_assignments()):
            assign = np.array(assign)
            a1 = tuple(assign[map1])
            a2 = tuple(assign[map2])
            f.probs[r] = self[a1][0]*factor[a2][0]
        return f
    
    def get_nbest_assignments(self, number):      
        assigns = []
        probs = self.probs.copy()
        for i in range(number):
            max_id = probs.argmax()
            ass = list(self._indexes_to_assignments(max_id)[0])
            ass.append(probs[max_id])
            assigns.append(tuple(ass))
            probs[max_id] = -1
        return assigns
    
    def get_description(self, format_type=0):
        '''print type0-three lines, type1-full table'''
        if format_type==0:
            items = []
            items.append('Variables: ' + str(self.variables))
            items.append('Cardinalities: ' + str(self.cards))
            items.append('Variables_values: ' + str(self.values))
            items.append('Probabilities: ' + str(self.probs))
        else:
            #TODO: Check the code below when have real factor, probaly cached the result :D
            items = ['\t'.join(self.variables)]
            items[0] = 'rowID\t' + items[0] + '\tProbability'
            items.append('------------------------ ')
            
            for (rid, row) in enumerate(self):
                line = [str(rid)]
                line.extend(row[:-1])
                line.append(str(row[-1]))
                items.append('\t'.join(line))
                
        return '\n'.join(items)
        
    def __str__(self):
        return self.get_description(1)

    def copy(self):
        return copy.deepcopy(self)

    def __mul__(self, factor):
        return self.product(factor)

def test1():
    p = DiscreteFactor(['Var1', 'Var2', 'Var3'], [2,3,4], ['1', '2', '1', '2', '3', '1', '2', '3', '4'], range(24))#essmision parameter for P(x|z)
    p2 = DiscreteFactor(['Var1', 'Var2', 'Var3', 'Var4'], [2,2,3,4], ['1', '2', '1', '2', '1', '2', '3', '1', '2', '3', '4'], range(48))#essmision parameter for P(x|z)
    assigns = [('1', '2', '3'),('2', '3', '1')]
##    print p
##    print p[assigns]
##    p['2', '2', '1'] = 222
##    p[assigns] = [111, 111]
##    print p
##    p.normalize()
#    print p
    #p.maginalize('Var2', 'Var1')
    #f = p.maginalize('Var2')
    #f = p.maginalize('Var3', 'Var1')
    #print p
    #print f
    #f = p.observe(['Var2'], ['2'])
    #print f
    p2 = p.copy()
    p2.variables[1] = 'Var4'
    #p2.variables[2] = 'Var4'
    #p2 = p2.maginalize('Var3', 'Var1')
    print p
    print p2
    print p.product(p2)
    
if (__name__ == '__main__'):
    test1()
