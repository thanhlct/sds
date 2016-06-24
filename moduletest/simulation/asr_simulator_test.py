'''
__init__ methods for module
'''

from simulation. import SimpleUserSimulator
from common.dialogueact import *

def test1():
    user = SimpleUserSimulator()
    user.new_dialogue()
    dai = DialogueActItem('request', {'decision':['accept','delay', 'reject'], 'appointment':'Mr. Bean visits on next Monday at 9.00 AM'})
    sys_da = DialogueAct(dai)
    user.da_in(sys_da)
    user.da_in(sys_da)
    user_da = user.da_out()
    #user_da = None
    print 'system_action\t=', sys_da
    print 'user_action\t=', user_da
    #assert user_da is not None,'Fault - user doesn''t reply'
    return user_da is not None
