'''
Grammar for Automatic Speech Recognition
'''

class Grammar(object):
    '''
    Grammar for Automatic Speech Recognition and ASR Simulator
    Grammar is cached in advance in standard formated file
    This class only helps find out the file name and cardinality
    '''
    
    def __init__(self, name):
        #assert (name in available list)
        #Todo: Change in future, here only for decision with 3 values
        self.name = name
        self.fullname = name
        if self.name== 'decision':
            self.cardinality = 3#check again
        else:
            self.cardinality = 0

    def get_fullname(self):
        '''
        grammar file, can be different from name
        '''
        return self.fullname

    def __str__(self):
        return self.get_fullname()
