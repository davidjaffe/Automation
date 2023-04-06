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
import readB2MMS


class auto():
    def __init__(self,debug=0):

        self.debug = debug
        print 'auto.__init__ debug',self.debug

        #### for generating reminder email
        self.readB2MMS = readB2MMS.readB2MMS()

        self.B2Members = self.readB2MMS.readB2M()
        if debug > 1 : print self.B2Members
        for B2id in self.B2Members:
            fn,ln,email,category,inst = self.B2Members[B2id]
            if debug > 1 : print 'self.B2Members[B2id]',B2id,self.B2Members[B2id],fn,ln,email,category,inst
            if int(B2id)%100==0:
                if debug > 0 : print '{:}, {:} {:}'.format(ln,fn,email)

                    


        self.reminderTemplate =     "Dear {colleague},\n\n \
    Thank you for your presentation at {conference} on behalf of the Belle II collaboration.\n\n \
    If you plan to submit a paper for the conference Proceedings (which might be required or optional, depending on the conference), please notify {responsiblePCmember} {rPCemail} of the Belle II Publications Committee (PC). The PC is now making an effort to ensure that conference proceedings submitted on behalf of Belle II are clear, and that results and plots included are all approved. We appreciate your help with this.\n\n \
    Further instructions can be found in the PC Review of Conference Proceedings at {link} .\n\n \
    Best regards,\n \
    {rSCmember} on behalf of the Speakers Committee"
    #The PC is responsible for conference Proceedings submitted on behalf of the Belle II Collaboration.
        self.responsiblePCmember = 'Alan Schwartz'
        self.responsibleSCmember  = 'David Jaffe'
        self.PClink = 'https://confluence.desy.de/display/BI/Review*of*conference*proceedings'
        self.PClink = 'https://confluence.desy.de/x/zhuyCw'



        self.get_dest = '../Talks/ToDo/'

        self.fav_items = {'talk_url': ["curl","URL","-o","DEST"], 
                              'draft_reference':0,
                              'title':1,
                              'author':2,
                              'abstract':3,
                              'date':4,
                              'conference':5,
                              }
        m = -1
        for k in self.fav_items:
            v = self.fav_items[k]
            if type(v) is int: m = max(m,v)
        if m>-1:
            self.newRecord_template = range(m+1)
        return
    def first(self,seckey=None,DryRun=True,Reminder=False):
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
                                    if ('?' in fn) or ('&' in fn) or ('%' in fn) or fn=='0.pdf' or fn=='pres.pdf' or (len(fn)==5 and fn.split('.')[1]=='pdf'):  # protection against indico naming all files 0.pdf or 1.pdf, or weird paths defined by indico, etc.
                                        d = str(self.get_dest + sec + '.pdf')
                                    else:
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
                conferenceName = seckey
                for pair in newRecord:
                    if pair[0]=='conference' : conferenceName = pair[1]
                for pair in newRecord:
                    secondPart = pair[1]
                    if pair[1]=='':
                        secondPart = ' ----------------- ERROR MISSING INFORMATION -----------------'
                        if sec not in errorLog: errorLog[sec] = []
                        errorLog[sec].append( pair )
                    if self.debug>0 or 'ERROR' in secondPart: print pair[0],secondPart
                    if Reminder and pair[0]=='author':
                        self.composeReminder(secondPart,conferenceName)
        print 'auto.first Processed',nEntries,'entries'
                                
        for key in errorLog:
            print 'auto.first ERROR',key,errorLog[key]
        return
    def composeReminder(self,author,conference):
        '''
        compose reminder email for author and conference
        '''
        subject = 'Conference proceedings reminder'
        email = self.getEmail(author)
        if email is None : email = 'NO EMAIL FOUND FOR THIS SPEAKER'
        rPCemail = self.getEmail(self.responsiblePCmember)
        reminder = self.reminderTemplate.format(colleague=author, \
                    conference=conference,responsiblePCmember=self.responsiblePCmember, \
                    rPCemail=rPCemail,rSCmember=self.responsibleSCmember,link=self.PClink)
        print '\n',email,'\n', subject, '\n', reminder, '\n'
        return
    def getEmail(self,author):
        '''
        return email address given author name
    
        B2Members[B2id] =[firstname,middlename,lastname,lastnameprefix,inst]
        B2MemberEmail[B2id] = email

        '''
        s = author.split()
        firstn = s[0]
        lastn = s[-1]
        middlen = None
        if len(s)>2 : mn = s[1]
        matches = []
        for B2id in self.B2Members:
            fn,ln,email,category,inst = self.B2Members[B2id]
            if ln.lower()==lastn.lower() :
                if fn.lower()==firstn.lower() :
                    matches.append(B2id)

        if self.debug > 0 :
            print 'auto.getEmail author',author,'# matches',len(matches)
            for B2id in matches: print self.B2Members[B2id][2]
        email = None
        if len(matches) > 0 : email = self.B2Members[matches[0]][2]
        return email
    
                    
if __name__ == '__main__' :

    seckey = "DoesNotMatch"  # required argument
    DryRun = True    # do not curl remote file, this is only a dry run
    debug = 0
    Reminder = False # print conference proceedings reminder message
    #print 'sys.argv',sys.argv
    if len(sys.argv)>1:
        seckey = sys.argv[1]
    else:
        sys.exit('python auto.py CONFERENCE_SHORT_NAME [DryRun([T]/F)] [debug] [Reminder([F]/T)]')
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
    if len(sys.argv)>4:
        a = sys.argv[4]
        if a.upper()=='T' :
            Reminder = True
        elif a.upper()=='F' :
            Reminder = False
        else:
            Reminder = bool(a)
            
    A = auto(debug=debug)
    A.first(seckey=seckey,DryRun=DryRun,Reminder=Reminder)
