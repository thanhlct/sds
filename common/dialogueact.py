'''
Dialoguge Acts
'''

#from exceptions import TypeError

class DialogueActItem(object):
    """
    Represents dialogue act item which is a component of a dialogue act.

    Each dialogue act item is composed of

        1) dialogue act type - e.g. inform, confirm, request, select, hello

        2) slot name and value pair - e.g. area, pricerange, food for name and
                                      centre, cheap, or Italian for value

    Attributes:
        type: dialogue act type (a string)
        content: dictionary slot name, value pairs
    """
    
    def __init__(self, type_=None, content={}, grammar=None):
        self.type = type_
        self.content = content
        self.grammar=grammar

    def __str__(self):
        return '{0}{1}'.format(self.type, self.content)

    def __eq__(self, da):
        if self.type != da.type or self.content != da.content:
            return False
        return True


class DialogueAct(list):
    """
    Represents a dialogue act (DA), i.e., a set of dialogue act items (DAIs).

     This class is not responsible for discarding a DAI which
    is repeated several times, so that you can obtain a DA that looks like
    this:

        request{address}&inform{food="chinese", area='central'}&request{address}
        e.g. Do you have address of a Chinese restaurant in central city?
    """
    TYPE_SUPPORT=DialogueActItem
    def __init__(self, *args):
        '''
        :param *args: Set of dialogue act item
        '''
        for item in args:
            self.append(item)
        
    def append(self, dialogue_action_item):
        '''
        Append knew dialogue action item
        '''
        if isinstance(dialogue_action_item,self.TYPE_SUPPORT):
            list.append(self, dialogue_action_item)
            #super(DialogueAct, self).append(dialogue_action_item)
        else:
            raise TypeError, 'Only sypport %s object' % (self.TYPE_SUPPORT)

    #should overide __setitem__, equal, etc.
    def __str__(self):
        ret = ''
        for item in self:
            ret = ret + '&' + str(item)
        return ret[1:]
    
    def _get_grammar(self):#can also overide __getattr__ and __setattr__
        #TODO: Dealing with multiple grammars from multiple Dialgoue ActiomItem
        self._grammar = self[0].grammar
        return self._grammar
    
    def _set_grammar(self, grammar):
        self._grammar = grammar

    grammar = property(_get_grammar, _set_grammar, None, None)

    def _get_type(self):#can also overide __getattr__ and __setattr__
        #TODO: Dealing with multiple grammars from multiple Dialgoue ActiomItem
        self._type = self[0].type
        return self._type
    
    def _set_type(self, type_):
        self._type = type_

    type = property(_get_type, _set_type, None, None)

    def _get_content(self):#can also overide __getattr__ and __setattr__
        #TODO: Dealing with multiple content from multiple Dialgoue ActiomItem
        return  self[0].content
    
    content = property(_get_content, None, None, None)
