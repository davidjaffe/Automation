#!/usr/bin/env python
'''
20200218 created. automating tasks for speakers committee
20200710 copy file from conference site to local 
        Must be run in /Users/djaffe/Documents/Belle II/SpeakersCommittee/Automation

'''
import math
import sys,os
import datetime
#import numpy
import copy
#import glob # used in __init__
import ConfigParser
import subprocess


class auto():
    def __init__(self,debug=0):

        self.debug = debug
        print 'auto.__init__ debug',self.debug

        self.get_dest = '../Talks/ToDo/'

        self.fav_items = {'talk_url': ["curl","URL","-o","DEST"], 
                              'draft_reference':0,
                              'title':1,
                              'author':2,
                              'abstract':3,
                              'date':4
                              }
        m = -1
        for k in self.fav_items:
            v = self.fav_items[k]
            if type(v) is int: m = max(m,v)
        if m>-1:
            self.newRecord_template = range(m+1)
        return
    def first(self,seckey=None,DryRun=True):
        ''' 
        first try at using configparser 
        read in all sections from config file
        loop over sections and process all sections that match input seckey
        for matching sections, 
           check for favorite items, 
           flag missing items and 
           get remote file (if it has not already been downloaded) if this is not a dry run 
        
        '''

        if seckey is None : sys.exit('auto.first input seckey is None. NO ACTION TAKEN')

        if DryRun is True : print 'auto.first Dry run only. Just show commands that would be executed.'
            
        config = ConfigParser.RawConfigParser()
        cf = 'auto.cfg'
        config.read(cf)
        secs = config.sections()
        if self.debug>0: print 'auto.first Opened',cf,'sections=',secs,'seckey=',seckey,'DryRun=',DryRun

        errorLog = {}
        nEntries = 0
        for sec in secs:
            if seckey in sec:
                nEntries += 1
                options = config.options(sec)
                items = config.items(sec)
                if self.debug>1:
                    print 'auto.first',sec
                    print 'auto.first options',options
                    print 'auto.first items=',items
                newRecord = copy.copy(self.newRecord_template)
                getTheFile = False
                for pair in items:
                    k,v = pair
                    if k=='talk_reference':
                        getTheFile = v==''
                for pair in items:
                    k,v = pair
                    for fav in self.fav_items:
                        if k==fav:
                            if self.debug>1: print 'auto.first fav,k,v',fav,k,v
                            if fav=='talk_url' :
                                fn = os.path.basename(v)
                                if self.debug>2: print 'auto.first len(fn)',len(fn)
                                if len(fn)>0:    
                                    d = str(self.get_dest + fn)
                                    if os.path.isfile(d):
                                        print '\nauto.first',sec,'No curl because file exists. File',d
                                    elif not getTheFile:
                                        print '\nauto.first',sec,'No curl because talk_reference exists'
                                    elif v=='NA':
                                        print '\nauto.first',sec,'No curl because talk_reference is NA'
                                    else:
                                        if self.debug>2: print 'auto.first d',d,'self.fav_items[fav]',self.fav_items[fav]
                                        com = copy.copy(self.fav_items[fav])
                                        iURL = com.index('URL')
                                        iDEST= com.index('DEST')
                                        com[iURL] = v
                                        com[iDEST]= d
                                        print '\nauto.first',sec,'com',' '.join(com)
                                        if not DryRun: subprocess.call(com)
                                else:
                                    if getTheFile:
                                        print '\nauto.first',sec,'FILENAME IS ZERO LENGTH. NO TRANSFER'
                                    else:
                                        print '\nauto.first',sec,'No file to transfer because talk_reference already exists'
                            else:
                                newRecord[self.fav_items[fav]] = [fav,v]
                if self.debug>0: print 'auto.first new record for',sec
                for pair in newRecord:
                    secondPart = pair[1]
                    if pair[1]=='':
                        secondPart = ' ----------------- ERROR MISSING INFORMATION -----------------'
                        if sec not in errorLog: errorLog[sec] = []
                        errorLog[sec].append( pair )
                    if self.debug>0 or 'ERROR' in secondPart: print pair[0],secondPart
        print 'auto.first Processed',nEntries,'entries'
                                
        for key in errorLog:
            print 'auto.first ERROR',key,errorLog[key]
        return
if __name__ == '__main__' :

    seckey = "DoesNotMatch"  # required argument
    debug = 0
    DryRun = True    # do not curl remote file, this is only a dry run
    #print 'sys.argv',sys.argv
    if len(sys.argv)>1:
        seckey = sys.argv[1]
    else:
        sys.exit('python auto.py CONFERENCE_SHORT_NAME [DryRun(T/F)] [debug]')
    if len(sys.argv)>2:
        a = sys.argv[2]
        if a.upper()=='T':
            DryRun = True
        elif a.upper()=='F':
            DryRun = False
        else:
            DryRun = bool(sys.argv[2])
    if len(sys.argv)>3:
        debug = int(sys.argv[3])
            
    A = auto(debug=debug)
    A.first(seckey=seckey,DryRun=DryRun)
