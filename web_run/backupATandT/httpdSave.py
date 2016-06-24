'''
A very simple webserver to facilitate and demonstrate dialog control.

Usage:

  > python httpd.py <port> <dmWrapperModule> <SpeechMashupsKey>
  
Example:

  > python httpd.py 8000 example-301-100k-directed.py 335DE3760D15B4A11DE2988072A73D62

Then point a browser to:

  http://localhost:8000/index.html
  
Note: the AT&T Speech Mashup Key listed above is bogus; you need to get
your own.  To do this, sign up for an AT&T Speech Mashup account by visiting:

  https://service.research.att.com/smm/
  
For GET and HEAD request, this webserver behaves as python's 
HTTPServer. For POST requests, this webserver assumes the 'path'
points to a python module, which contains a method called 
NewSession(), that returns a Dialog Manager object.  On the 
first request, the module is imported, and it persists for all 
subsequent requests.  The Init() and TakeTurn() methods of the dm
are called as appropriate.  The data in the POST request is assumed
to contain the ASR result in JSON format, which this webserver
vivifies and uses to create an ASRResult object.

Note that if the target module (or any of the modules that it 
imports) are modified, the webserver needs to be stopped and
re-started.

Jason D. Williams
jdw@research.att.com
www.research.att.com/people/Williams_Jason_D
'''
#Thanh:
#import pdb

# Extend sys.path to include src directory
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__),'../../src'))

from BaseHTTPServer import HTTPServer
from CGIHTTPServer import CGIHTTPRequestHandler
import jsonlib
from DB import GetDB
from DialogModules import ASRResult

global db, dm, prevSysAction, dmModuleName, uuid

class _StatefulHandler(CGIHTTPRequestHandler):
  def do_POST(self):
    outputText = self.do_POST_inner()
    
    # add http header
    outputText = 'HTTP/1.0 200 OK\nContent-Type: application/json\n\n' + outputText + '\n'
    self.log_message("Returning message: %s" % (outputText))
    
    # serve result
    self.wfile.write(outputText)

  def do_POST_inner(self):    
    global db, dm, prevSysAction, dmModuleName, uuid
    
    # strip of leading '/'
    path = self.path[1:]

    # read in body content
    inputText = self.rfile.readline()
    self.log_message("Got message: %s" % (inputText))
    
    # vivify into json
    try:
      inputJSON = jsonlib.read(inputText,use_float = True)
    except:
      self.log_error("Could not parse JSON: %s\nError: %s" % (inputText,sys.exc_info()))
      return '{"status": "error","error": "input-JSON-decoding","error_msg": "Could not parse input JSON"}\n' 
      
    if (path == 'dm'):#clien yeu cau cai gi? dua vao path cua url
      # dm request
      if (inputJSON['session'] == 'new'):#phien moi thi tao dm moi, gui ve askaction va luu he thong cu
        sysAction = dm.Init()
        prevSysAction = sysAction
        asrProbs = None
      elif (prevSysAction == None):#yeu cau lai ma he thong chua tung khoi toa, loi vi dm chua cod
        self.log_error("DM not ready; resetting connection")
        return '{"status": "error","error": "dm", "error_msg": "DM not ready"}\n'
      else:#dua nhan dang dong noi vao de DM tinh toan
        #pdb.set_trace()
        asrResult = ASRResult.FromWatson(inputJSON['message'],prevSysAction.grammar)#grammar is firt/last... or all
        asrProbs = asrResult.GetProbs()
        sysAction = dm.TakeTurn(asrResult)
        prevSysAction = sysAction
      messageJSON = {
        'sysAction': sysAction.GetJSON(),
        'asrProbs': asrProbs,
        'dialogResult': dm.GetDisplayJSON(),
      }
    elif (path == 'sampleName'):
      # sample a name
      listing = db.GetRandomListing()
      nameString = '%s %s in %s, %s' % (listing['first'],listing['last'],listing['city'],listing['state'])
      messageJSON = {'nameText': nameString, }
    elif (path == 'info'):
      # config info
      messageJSON = {
        'dmModuleName': dmModuleName,
        'uuid':uuid,
      }
    else:
      self.log_error("Dont recognize path %s" % (path))
      return '{"status": "error","error": "path", "error_msg": "Dont recognize path %s"}\n' % (path)
    
    # add session & status
    outputJSON = {}
    outputJSON['status'] = 'ok'
    outputJSON['message'] = messageJSON
      
    # textify result
    try:
      outputText = jsonlib.write(outputJSON)
    except:
      self.log_error("Could not parse JSON into text: %s\nError: %s" % (outputJSON,sys.exc_info()))
      return '{"status": "error","error": "output-JSON-encoding","msg": "Could not parse JSON: %s\nError: %s."}\n' % (outputJSON,sys.exc_info()[0])

    return outputText      
 
def main():
  global db, dm, prevSysAction, dmModuleName, uuid
  
  #sys.argv = ['httpd.py', '8000', 'example-300-1k-rigid.py', 'D24CB19B8EAF11E4ACAFC1AA6AEC2530']
  #sys.argv = ['httpd.py', '8000', 'example-302-1k-directed.py', 'D24CB19B8EAF11E4ACAFC1AA6AEC2530']
  sys.argv = ['httpd.py', '8000', 'example-304-1k-open.py', 'D24CB19B8EAF11E4ACAFC1AA6AEC2530']
  
  assert (len(sys.argv)==4),'Usage: httpd.py <port> <top-level-module> <uuid>'
  dmModuleName = sys.argv[2]
  port = int(sys.argv[1])
  uuid = sys.argv[3]

  # remove trailing .py, if present
  if (dmModuleName[-3:] == '.py'):
    dmModuleName = dmModuleName[0:-3]
  
  dmModule = __import__(dmModuleName)
  dm = dmModule.GetDM()
  prevSysAction = None
  db = GetDB()
   
  server_address=('',port)
  httpd = HTTPServer(server_address, _StatefulHandler)
  httpd.serve_forever()
  

if (__name__ == '__main__'):
  main()
  
