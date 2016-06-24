'''
A HTTP Server for the simple VPA
'''

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))

from BaseHTTPServer import HTTPServer
from CGIHTTPServer import CGIHTTPRequestHandler
import jsonlib
from logging import getLogger

from utils.globalconfig import *
from utils.design_pattern import *
from asr.watson_asr_result import WatsonASRResult
from asr.transcript_asr_result import TranscriptASRResult
from task_classifier.simple_task_classifier import SimpleTaskClassifier
from nlg.simple_nlg import SimpleNLG


import pdb

global dms, config, logger, last_sys_da, last_task, dialogue_num
class StatefulHandler(CGIHTTPRequestHandler):
    MY_ID = 'HTTPServer'

##    def __init__(self, request, client_address, server):#visit every single request
##        #super.__init__(self, p1, p2, p3)
##        #super(StatefulHandler, self).__init__(p1, p2, p3)
##        CGIHTTPRequestHandler.__init__(self,request,client_address,server)
##        self.config = get_config()
##        self.logger = getLogger(self.MY_ID)
##        global dms
##        dms = {}
    
    def do_POST(self):
        print '---Have a request'
        
        output_text = self.do_POST_inner()
        #add http header
        output_text = 'HTTP/1.0 200 OK\nContent-Type: application/json\n\n' + output_text + '\n'

        #serve result
        self.wfile.write(output_text)
        print '---Handled request:\n%s'%(output_text)

    def do_POST_inner(self):
        path = self.path[1:]
        content = self.rfile.readline()
        print 'get message:', content
        
        content = jsonlib.read(content,use_float = True)
        session = content['session']
        message = content['message']
        print session, message
        
        ret = ''
        if path == 'dm':
            ret = self._dm_process(session, message)
        else:
            pass
        
        return ret

    def _dm_process(self, session, message):
        #global dms, config
        global last_sys_da, last_task, dialogue_num
        if session not in dms.keys():
            dms[session] = get_class(config.get(self.MY_ID, 'dialogueManagerClassPath'));

        message_type= message['type']
        dm = dms[session]
        ret = {'session': session}
        if message_type == 'new_dialogue':
            dm.new_dialogue()
            sys_da = dm.da_out()
            ret['message'] = {'type':'sys_turn', 'tts': str(sys_da), 'grammar': sys_da.grammar.get_fullname()}
            last_sys_da = sys_da
        elif message_type== 'asr_att_results':
            #update belief space
            asr_hyps = WatsonASRResult.GetASRHypotheses(message['asr'], last_sys_da.grammar)
            dm.da_in(asr_hyps)
            sys_da = dm.da_out()
            last_sys_da = sys_da
            ret['message'] = {'type':'sys_turn', 'tts': str(sys_da), 'grammar': str(sys_da.grammar), 'asr_hps': str(asr_hyps)}
        elif message_type == 'user_turn':
            print 'last_task: ', last_task
            current_task = SimpleTaskClassifier.from_transcript(message['asr_hyps']['0']['transcript'], last_task)
            print 'current_task: ', current_task
            if current_task == 'get_list_appointment':
                dm.new_dialogue()
                sys_da = dm.da_out()
                last_sys_da = sys_da
                ret['message'] = {'type':'sys_turn', 'tts': 'Sure, sir! There\'re three appointments. ' + SimpleNLG.get_natural_text(sys_da), 'grammar': str(sys_da.grammar)}
                last_task = current_task
                print 'last_task: ', last_task
                if sys_da.type == 'end':
                    last_task = 'end_new_dialogue'
            elif current_task == 'appoinment_decision':
                asr_hyps = TranscriptASRResult.get_asr_hypotheses(message['asr_hyps'], last_sys_da.grammar)
                dm.da_in(asr_hyps)
                sys_da = dm.da_out()
                last_sys_da = sys_da
                
                debug= '<b>ASR observations:</b><br>' + str(asr_hyps).replace('\n', '<br>') + '<br><b>Belief_state:</b><br>' + str(dm.belief_tracker.get_belief_space()).replace('\n', '<br>')
                ret['message'] = {'type':'sys_turn', 'tts': SimpleNLG.get_natural_text(sys_da), 'grammar': 'decision', 'debug': debug}
                last_task = current_task
                if sys_da.type == 'end':
                    last_task = 'end_new_dialogue'
            elif current_task=='end_new_dialogue':
                user_goal = TranscriptASRResult.get_user_goal(message['asr_hyps'], last_sys_da)
                print 'detected user_goal', user_goal
                dm.end_dialogue(user_goal)
                
                debug = '<b>Final reward:</b> 5(Satisfied)'
                if 'incorrect' in str(user_goal):
                    debug = '<b>Final reward:</b> -20 (Unsastisfied)'
                
                dialogue_num +=1
                print '---Dialogue num: ', dialogue_num, 'mod=', dialogue_num%10
                if dialogue_num%3==0:
                    dialogue_num = 0
                    print '---SAVING parameters----'
                    dm.save()
                
                dm.new_dialogue()
                sys_da = dm.da_out()
                last_sys_da = sys_da
                ret['message'] = {'type':'sys_turn', 'tts': 'Next appointment. ' + SimpleNLG.get_natural_text(sys_da), 'grammar': str(sys_da.grammar), 'debug': debug}
                last_task = 'get_list_appointment'
                if sys_da.type == 'end':
                    last_task = 'end_new_dialogue'
            elif current_task=='user_end':
                print '---USER END dialogue---'
                user_goal = {'decision': 'incorrect'}
                print 'detected user_goal', user_goal
                dm.end_dialogue(user_goal)
                
                debug = '<b>Final reward:</b> 5(Satisfied)'
                if 'incorrect' in str(user_goal):
                    debug = '<b>Final reward:</b> -20 (Unsastisfied)'
                
                dialogue_num +=1
                print '---Dialogue num: ', dialogue_num, 'mod=', dialogue_num%10
                if dialogue_num%3==0:
                    dialogue_num = 0
                    print '---SAVING parameters----'
                    dm.save()
                
                dm.new_dialogue()
                sys_da = dm.da_out()
                last_sys_da = sys_da
                ret['message'] = {'type':'sys_turn', 'tts': 'Next appointment. ' + SimpleNLG.get_natural_text(sys_da), 'grammar': str(sys_da.grammar), 'debug': debug}
                last_task = 'get_list_appointment'
                if sys_da.type == 'end':
                    last_task = 'end_new_dialogue'
                
        elif message_type=='end_reward':
            pass
        
        #ret['message'] = {'type':'hello', 'tts':'Hello, how may I help you?', 'grammar':''}
        #ret['message'] = {'type':'sys_turn', 'tts': str(sys_da), 'grammar': 'decision'}
        #ret['message'] = {'type':'sys_turn', 'tts': str(sys_da), 'grammar': 'db-1k.all'}
        #ret['message'] = {'type':'sys_turn', 'tts': 'Hi!', 'grammar': 'decision'}
        #ret['message'] = {'type':'sys_turn', 'tts': str(asr_hyps), 'grammar': 'decision'}
        
        
        ret = jsonlib.write(ret)
        return ret
    
def main():
    global dms, config, last_task, dialogue_num
    init_config()
    config = get_config()
    config.read('../config-all-simple.conf')
    dms = {}
    last_task = None
    dialogue_num = 1

    #uuid = 'D24CB19B8EAF11E4ACAFC1AA6AEC2530'
    port = 8080
    
    server_address=('',port)
    httpd = HTTPServer(server_address, StatefulHandler)
    print 'Ready for serving...'
    httpd.serve_forever()

if (__name__ == '__main__'):
  main()
