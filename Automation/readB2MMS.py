#!/usr/bin/env python
'''
read, parse B2MMS spreadsheet
taken from newBelleII/Climate 20230308

'''
import math
import sys,os
#import random

import datetime
import numpy
import copy

import re
import glob # used in __init__

from lxml.html import parse  # used by readB2GM

#import matplotlib.pyplot as plt



class readB2MMS():
    def __init__(self,debug=-1):

        self.debug = debug

        self.B2MembersFile = 'Members_List_20230531.csv' ##20230308.csv'
        print('readB2MMS.__init__ debug',debug)
        
        
        return
    def readB2M(self):
        '''
        read Belle II members to get Belle II ID, name and institution name
        return dict B2Members
        B2Members[B2id] =[firstname,lastname,email,category,inst]
        20230308 mods to handle .csv format
        20230830 python3 mod to use encoding='ISO-8859-1' in open() because it didn't work without it
        see chardet use in https://stackoverflow.com/questions/55563399/how-to-solve-unicodedecodeerror-utf-8-codec-cant-decode-byte-0xff-in-positio
        '''
        debug = self.debug
        f = open(self.B2MembersFile,'r',encoding='ISO-8859-1') ## 20230830
        B2Members = {}
        qqq = '"""' # 3 double quote surrounds short name of institution
        for line in f:
            if 'B2ID' not in line: # avoids header
                s = line[:-1].split(',')
                for i,x in enumerate(s):
                    y = x.replace('"','')
                    if y=='-': y = ''
                    s[i] = y
                B2id = s[0]
                firstn = s[1]
                lastn  = s[2]
                email  = s[3]
                category=s[4]
                sname  = s[5].replace('"','') # institution short name (this does not always work because some fields have ',' in them)

                B2Members[B2id] = [firstn,lastn,email,category,sname]

                if debug>0: print('climate.ReadB2M B2id',B2id,'B2Members[B2id]',B2Members[B2id])
        f.close()
        print('readB2MMS.ReadB2M Processed',len(B2Members),'members in',self.B2MembersFile)
        return B2Members
    def goodMatch(self,a,b,ch='',inIt=False):
        A = a.strip().replace(ch,'').lower()
        B = b.strip().replace(ch,'').lower()
        if self.debug>2: print('readB2MMS.goodMatch a',a,'b',b,'A',A,'B',B,'ch',ch,'inIt',inIt)
        if A==B and len(A)>0: return True
        if inIt:
            if (A in B or B in A) and len(A)>0 and len(B)>0: return True
        return 
    def matchMtoI(self,Insts,Members,Parps):
        '''
        try to match participants Parps to Members and determine their institutions
        Result should be list of participants with their institutions including city, country

        Matching attempts:
        1. one of the names of the participants matches the first or last name of a member
        2. both of the names of the participants matches both names (first and last) of a member
        3. same as 2, but remove all dashes from names

        '''
        debug = 0
        TooFew,TooMany,JustRight = 0,0,0
        spacers = ['','-',' '] # single character spacers between names
        ParpToInst = [] # list of pairs (Participant, B2id)
        for P in Parps:
            name1,name2,inst = self.unpackParticipants(P)
            if debug>1: print('Search for name1',name1,'name2',name2)
            Matches = [] # list of B2id of potential matches
            for B2id in Members:
                firstn,middlen,lastn,lastnpre,sname = Members[B2id]
                if debug>2: print('readB2MMS.matchMtoI first/middle/last/pre/sname',firstn,'/',middlen,'/',lastn,'/',lastnpre,'/',sname)
                if self.goodMatch(name1,lastn):
                    Matches.append(B2id)
                if self.goodMatch(name2,lastn):
                    if B2id not in Matches: Matches.append(B2id)

            if len(Matches)>1: # see if we can get a name1=firstn and name2=lastn or vice-versa
                newMatch = []
                for ch in spacers:
                    for B2id in Matches:
                        firstn,middlen,lastn,lastnpre,sname = Members[B2id]
                        for initial,final in [ [firstn,lastn], [firstn+middlen,lastn], [firstn,middlen+lastn] ]:
                            if self.goodMatch(name1,initial,ch=ch) and self.goodMatch(name2,final,ch=ch) and B2id not in newMatch: newMatch.append(B2id)
                            if self.goodMatch(name2,initial,ch=ch) and self.goodMatch(name1,final,ch=ch) and B2id not in newMatch: newMatch.append(B2id)
                    if len(newMatch)>0: Matches = newMatch
                    if len(Matches)==1: break

            if len(Matches)>1 and inst!=None: # try to match one name and institution
                for ch in spacers:
                    newMatch = []
                    if debug>1: print('readB2MMS.matchMtoI name1/name2/inst',name1,'/',name2,'/',inst,'try to match one name and institution to resolve multi-match'.upper())
                    for B2id in Matches:
                        firstn,middlen,lastn,lastnpre,sname = Members[B2id]
                        for name in [firstn,lastn,firstn]:
                            if debug>1: print('readB2MMS.matchMtoI B2id,name/sname',B2id,name,'/',sname)
                            if self.goodMatch(name1,name,ch=ch) and (sname in inst): newMatch.append(B2id)
                            if self.goodMatch(name2,name,ch=ch) and (sname in inst): newMatch.append(B2id)
                    if len(newMatch)>0: Matches = newMatch
                    if len(Matches)==1: break
                        
            if len(Matches)==0 and inst!=None: # no matches, desperation time
                Matches = []
                if debug>1: print('readB2MMS.matchMtoI name1/name2/inst',name1,'/',name2,'/',inst,'try to match one name and institution to resolve 0 match'.upper())
                for B2id in Members:
                    if self.desperateMatch(Members[B2id],P):
                        Matches.append(B2id)
                        if debug>1: print('readB2MMS.matchMtoI potential match B2id,name/sname',B2id,Members[B2id])
                        
            if len(Matches)>1:
                newMatch = self.bestMatch(Matches,Members,P)
                Matches = newMatch
                        
            L = len(Matches)
            
            if L==0:   # --------------> NO MATCH
                if debug>0:
                    self.printAsUnicode([ 'readB2MMS.matchMtoI name1/name2/inst',name1,'/',name2,'/',inst,'*** NO MATCHES *** '])
                TooFew += 1
                ParpToInst.append( [P, None] ) # no match
            elif L==1: # --------------> One match
                JustRight += 1
                B2id = Matches[0]
                sname = Members[B2id][-1]
                if debug>1: print('readB2MMS.matchMtoI B2id',B2id,'sname',sname,'Members[B2id]',Members[B2id])
                if sname not in Insts:
                    print('readB2MMS.matchMtoI ERROR dict Insts does not contain key',sname,'for participant',P)
                ParpToInst.append( [P, Insts[sname]] )  # participant and Institution (city,country,longname,shortname)
            else:  # --------------> TOO MANY MATCHES
                if debug>-1:
                    self.printAsUnicode([ 'readB2MMS.matchMtoI',name1,'/',name2,'/',inst,L,'matches',Matches])
                    self.printMatches(Matches,Members) 
                TooMany += 1
                ParpToInst.append( [P, None] ) # too many matches
        print('readB2MMS.matchMtoI',len(Parps),'participants,',JustRight,'single matches,',TooMany,'multi-matches,',TooFew,'No matches')
        
        if debug>1: # report participants and their institutions
            for pair in ParpToInst:
                P,Home = pair
                name1,name2,inst = self.unpackParticipants(P)
                print('readB2MMS.matchMtoI',name1,name2, end=' ')
                if Home is not None:
                    city,country,lname,sname = Home
                    print('is from',sname,'(',lname,') in ',city,',',country)
                else:
                    print('has no identified home institution')
                
        return ParpToInst
    def printAsUnicode(self,wordList):
        '''
        given an input list, try to print it as unicode
        if that fails, ignore error and print as ascii
        '''
        #print 'readB2MMS.printAsUnicode wordList',wordList
        r = []
        for x in wordList:
            if type(x) is float or type(x) is int: x=str(x)
            if type(x) is list:
                r.append(x)
            else:
                try:
                    X = x.encode('utf-8')
                except UnicodeDecodeError:
                    X = x.decode('ascii','ignore')
                r.append( X )
        for x in r:print(x, end=' ')
        print('')
        return
    def printMatches(self,idList,Members):
        for i,B2id in enumerate(idList):
            firstn,middlen,lastn,lastnpre,sname = Members[B2id]
            print(' match#',i,B2id,firstn,'/',middlen,'/',lastn,'/',lastnpre,'/',sname)
        return
    def bestMatch(self,Matches,Members,P):
        '''
        return best match among multiple matches, require at least 2 identifying bits of info to match
        Matches = list of B2id
        Members[B2id] = firstn,middlen,lastn,lastnpre,sname
        P = name1,name2,inst
        '''
        spacers = ['','-',' ']
        
        debug = 0
        
        name1,name2,inst = P
        inIt = {}
        newMatch = []
        storeI = {}
        for B2id in Matches:
            imatch = []
            for inIt in [False,True]:
                for x in P:
                    if x is not None:
                        for i,L in enumerate(Members[B2id]):
                            for ch in spacers:
                                if self.goodMatch(x,L,ch=ch,inIt=inIt):
                                    if i not in imatch:
                                        imatch.append(i)
                                        #print 'readB2MMS.bestMatch inIt,ch,x,L,i,imatch',inIt,ch,x,L,i,imatch
            

            if len(imatch)>1: newMatch.append(B2id)
            storeI[B2id] = imatch
                
        if len(newMatch)==0:
            pass
        else:
            wL = ['readB2MMS.bestMatch']
            wL.extend(P)
            wL.append('matched to')
            for B2id in newMatch:
                wL.extend(Members[B2id])
                if B2id!=newMatch[-1]: wL.append('or')
            if debug>0:
                self.printAsUnicode(wL)
                #print 'readB2MMS.bestMatch storeI',storeI
        return newMatch
        
    def desperateMatch(self,Member,P):
        '''
        try some desperate matching. One name of participant and one name in B2MMS iff instition somehow matches.
        Member is from B2MMS
        P is participant at a B2GM
        return True is deperate match is possible
        '''
        name1,name2,inst = self.unpackParticipants(P)
        if inst is None: return False 
        spacers = ['',' ','-']
        firstn,middlen,lastn,lastnpre,sname = Member
        for mname in Member:
            if mname!=sname and len(mname)>0:
                OK = False
                for ch in spacers:
                    for name in [name1,name2]:
                        if self.goodMatch(name1,mname,ch=ch) : OK = True
                    if OK: 
                        ilz = inst.lower().replace(' ','')
                        slz = sname.lower().replace(' ','')
                        if ilz in slz or slz in ilz: return True
        return False
if __name__ == '__main__' :
   
    ct = readB2MMS()
    B2members = ct.readB2M()
    
#        B2Members[B2id] =[firstname,middlename,lastname,lastnameprefix,inst]
#        B2MemberEmail[B2id] = email
    for B2id in B2members:
        fn,ln,email,category,inst = B2members[B2id]

        print('{:}, {:} {:}'.format(ln,fn,email))
 
