'''
Class for extracting features from WATSON ASR output.

This module extracts features from AT&T WATSON ASR output.  These 
features are used by a regression model to estimate probability of 
correctness for N-Best lists output by WATSON.  This module is used
only in the interactive demonstration (when output from AT&T WATSON
ASR is present).

This module requires that global logging has been initialized.  
See main README file.

Part of the AT&T Statistical Dialog Toolkit (ASDT).  

Jason D. Williams
jdw@research.att.com
www.research.att.com/people/Williams_Jason_D
'''
import pdb

import sys
from math import log
import logging

MY_ID = 'WatsonFeatures'

class MissingFieldError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def _SafeGet(root,args):
    for arg in args:
        if (type(arg) == type(1)):
            if (len(root) <= arg):
                raise MissingFieldError("Array not long enough: %s" % (args))
        else:
            if (arg not in root):
                raise MissingFieldError("Missing dict key: %s" % (args))
        root = root[arg]
    return float(root)    

def extract_features(reco):
    appLogger = logging.getLogger(MY_ID)
    features = []
    try:
        featureFields = [
            ['recoResults','nbest',0,'score'],
            ['recoResults','nbest',0,'udelta'],
            ['recoResults','nbest',0,'gdelta'],
            ['recoResults','nbest',0,'normCost'],
            ['recoResults','nbest',0,'normSpeechLhood'],
            ['recoResults','nbest',0,'numFrames'],
            ['recoResults','nbest',0,'numSpeechFrames'],
            ['recoResults','nbest',0,'ulhood'],
            ['recoResults','nbest',0,'glhood'],
        ]
        for featureField in featureFields:
          features.append( _SafeGet(reco,featureField))          
        worstAltProb = 0
        if ('recoResults' in reco and 'wcn' in reco['recoResults'] and 'network' in reco['recoResults']['wcn']):
            length = len(reco['recoResults']['wcn']['network'])
            pathCount = 1
            for segment in reco['recoResults']['wcn']['network']:
                pathCount *= len(segment['word'])
                if (len(segment['prob']) > 0):
                    if (segment['prob'][0] > worstAltProb):
                        worstAltProb = segment['prob'][0]
        else:
            pathCount = 0
            length = 0
        features.append(float(length))
        features.append( min(float(pathCount),100.0) )
        features.append( log(1.00001 - float(worstAltProb) ))
        return features
    except MissingFieldError, e:
        appLogger.warn('%s\n%s' % (e,MissingFieldError))
        print 'Error!!!!!Thanh'
        pdb.set_trace()
        return None
    
