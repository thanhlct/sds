'''
Design Pattern Support Tools
'''

def reflection(pathClass):
    '''
    Import a module/library/class from string
    '''
    paths = pathClass.split('.')
    m = __import__('.'.join(paths[:-1]))
    for p in paths[1:]:
        m = getattr(m, p)
    return m

def factory(aClass, args):
    '''
    Create a class with argumetns
    '''
    return apply(aClass, args) #Can be done with aClass(args)

def get_class(pathClass, *args):
    '''
    Get an instance of a class figured out in path string and construction args as args
    '''
    c = reflection(pathClass)
    return factory(c, args)

def get_function(pathFuns):
    '''
    Get an instance of a class figured out in path string and construction args as args
    '''
    fun = reflection(pathFuns)
    return fun
