'''
A HTTP Server for the simple VPA
'''

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__),'../../'))

from BaseHTTPServer import HTTPServer
from CGIHTTPServer import CGIHTTPRequestHandler
import jsonlib
from logging import getLogger

from utils.globalconfig import *
from utils.design_pattern import *
from asr.watson_asr_result import WatsonASRResult

import pdb

global dms, config, logger, last_sys_da
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
        global last_sys_da
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
    global dms, config
    init_config()
    config = get_config()
    config.read('../../config-all-simple.conf')
    dms = {}

    #uuid = 'D24CB19B8EAF11E4ACAFC1AA6AEC2530'
    port = 8000
    
    server_address=('',port)
    httpd = HTTPServer(server_address, StatefulHandler)
    print 'Ready for serving... with AT&T ASR'
    httpd.serve_forever()

if (__name__ == '__main__'):
  main()
