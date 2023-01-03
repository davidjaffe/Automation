#!/usr/bin/env python
'''
20210727 created. parses Public ConferenceTalks text to fill entries used in auto.cfg
        Must be run in /Users/djaffe/Documents/Belle II/SpeakersCommittee/Automation

20211201 improve so only conference URL needs to be input for each conference and so all confernces can be treated in one pass

workflow
1. by hand: cut/paste list of authors, titles from Public Conference talks to 'filler.input'
2. by hand: edit filler.input to add 0th column="#" for lines to ignore, 0th column="*" for line with conference name, date
2. python filler.py
   input from keyboard: conference url
   output will be 'filler.output'
3. insert 'filler.output' into auto.cfg
4. fill talk urls, abstracts, etc. in auto.cfg
5. run auto.py

'''
import math
import sys,os
import datetime
#import numpy
import copy
#import glob # used in __init__
import ConfigParser
import subprocess
import datetime


class filler():
    def __init__(self,debug=0,year=1958):

        self.debug = debug
        self.year  = year
        print 'filler.__init__ debug',self.debug,'year',self.year,' **** NOTE THE YEAR. IMPORTANT TO CHECK IN JAN and FEB of NEW YEAR **** '
        print 'filler.__init__ to set year to 2022 use command `python2 filler.py 0 2022`'

        self.acfg  = 'auto.cfg'
        self.input = 'filler.input'
        self.output= 'filler.output'

        self.fav_items = {}

        self.default_HEADER = '[TEMPLATE_for_cutnpaste]'

        self.global_items = {'date:':'dd/mm/yyyy',
                                 'conference:':'',
                                 'keywords:':'',
                                 'conf_url:':'',
                                 'short_conf_name: ':''
                                 }

        return
    def reset_global_items(self):
        for k in self.global_items: self.global_items[k] = None
        self.global_items['keywords:'] = ''
        return
    def getDayMonth(self,line):
        '''
        line = '(nn-mm Month ...)'
        '''
        if self.debug > 0 : print 'filler.getDayMonth line',line
        imonth = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
        dayMonth, day, month = None, None, None
        lp = max(0,line.find('('))
        rp = line.find(')')
        if rp<0 : rp = len(line)
        if self.debug > 0 : print 'filler.getDayMonth lp,rp,line[lp:rp],line[lp+1].isdigit()',lp,rp,line[lp:rp],line[lp+1].isdigit()
        if line[lp].isdigit():
            if line[lp+1].isdigit() :
                day = line[lp] + line[lp+1]
            else:
                day = '0' + line[lp]
            month = None
            for k in imonth:
                if imonth[k] in line[lp:rp]: month = '%02d' % k

        if self.debug > 0 : print 'filler.getDayMonth day,month',day,month
        if day is not None and month is not None : dayMonth = day + '/' + month
        if self.debug > 0 : print 'filler.getDayMonth dayMonth',dayMonth
        return dayMonth
    def setGlobal(self,line):
        '''
        return self.global_items with global items extracted from input line.

        general format of line is
        line = '* Conference title (short title[optional]) (date, location)'
        '''
        sline = line.split('(')
        if self.debug > 0 : print 'filler.setGlobal sline',sline
        confName = sline[0][1:].strip()
        if len(sline)==2: # no shortName
            dayMonth = self.getDayMonth(sline[1])
            shortName= None
        elif len(sline)==3:
            dayMonth = self.getDayMonth(sline[2])
            shortName= sline[1].replace(')','').strip().replace(" ","_")
        if dayMonth is not None:
            dayMonth += '/' + str(self.year)

        if shortName is None:
            shortName = self.getShortName(confName)

        self.global_items['date:'] = dayMonth
        self.global_items['conference:'] = confName
        self.global_items['short_conf_name: '] = shortName
        if self.debug > 0 : print 'filler.setGlobal dayMonth',dayMonth,'shortName',shortName,'confName',confName
        return
    def getShortName(self,conferenceName):
        '''
        return shortName given conferenceName
        
        if confName is less than 10 characters, 
           then use it as basis for shortName
        if confName is longer than 10 characters, 
           then use upper case letters in confName to form shortName if there is >1 upper case letter in confName, 
           otherwise use first letters

        cribs:
        https://stackoverflow.com/questions/15886340/how-to-extract-all-upper-from-a-string-python#15886375
        https://stackoverflow.com/questions/41191424/extract-first-character-of-each-word-from-the-sentence-string#41191463
        '''
        confName = conferenceName.replace(str(self.year),'').strip()
        if self.debug > 1 : print 'filler.getShortName conferenceName',conferenceName,'confName',confName
        if len(confName)<10:
            u = confName.strip() 
        else:
            u = ''.join([c for c in confName if c.isupper()]) #
            if len(u)<=1 :
                u = ''.join([c[0].upper() for c in confName.split()])
        shortName = u + '_' +  str(self.year)
        shortName = shortName.replace(" ","_") # no blanks
        if self.debug > 1 : print 'filler.getShortName shortName',shortName
        return shortName
    def getTemplate(self):
        '''
        transfer input from template at end of auto.cfg to dict
        '''
        f = open(self.acfg)
        print 'filler.getTemplate Opened',self.acfg
        i = 0
        foundFirstLine = False
        for line in f:
            if self.default_HEADER in line:
                self.fav_items[0] = line[:line.find(':')+1]
                foundFirstLine = True
            else:
                if foundFirstLine:
                    i += 1
                    self.fav_items[i] = line[:line.find(':')+1]
        f.close()
        if self.debug > 1 :
            print 'filler.getTemplate template dict:'
            for k in sorted(self.fav_items):
                print self.fav_items[k]
        return
    def fillGlobal(self):
        '''
        solicit entries to be used globally
        '''
        for k in self.global_items:
            if self.global_items[k] is None:
                v = raw_input('filler.fillGlobal Enter '+k)
                self.global_items[k] = v
        if self.debug > 0 :
            print 'filler.fillGlobal global_items dict:'
            for k in sorted(self.global_items):
                print k,self.global_items[k]
        return
    def fillOne(self,author,title):
        '''
        return one filled dict of items for one talk given author and title
        '''
        one = {}
        
        if self.debug > 1:
            print 'filler.fillOne self.fav_items',self.fav_items,'self.global_items',self.global_items
            
        for i in self.fav_items:
            if i==0:
                sn = self.global_items['short_conf_name: ']
                one[i] = '[' + sn + '_' + author.replace(' ','_') + ']'
            else:
                v = self.fav_items[i]
                if v in self.global_items:
                    one[i] = v + self.global_items[v]
                elif 'author' in v:
                    one[i] = v + author
                elif 'title' in v :
                    one[i] = v + title
                else:
                    one[i] = v
        if self.debug > 1 :
            print 'filler.fillOne for author',author,'title',title
            for k in sorted(one):
                print one[k]
        return one
    def fill(self):
        '''
        read input, produce output
        '''
        self.getTemplate()
        #self.fillGlobal()
        fin = open(self.input,'r')
        fout= open(self.output,'w')
        ctr = 0
        for line in fin:
            if self.debug > 1 : print 'filler.fill line[:-1]',line[:-1]
            if line[0]=='*':
                print line[:-1]
                self.reset_global_items()
                self.setGlobal(line)
                self.fillGlobal()
            elif line[0]=='#':
                continue
            else: 
                ctr += 1
                author,title,junk = line.split('"')
                author = author.strip()
                one = self.fillOne(author,title)
                for k in sorted(one):
                    fout.write(one[k]+'\n')
        fin.close()
        fout.close()
        print 'filler.fill Wrote',ctr,'entries to',self.output
        return
    def testFillOne(self):
        self.fillOne('Jane Day','Relativity for kids')
        return
if __name__ == '__main__' :

    debug = 0
    year = datetime.datetime.now().year
    if len(sys.argv)>1:
        debug = int(sys.argv[1])
    if len(sys.argv)>2:
        year = int(sys.argv[2])
 
    A = filler(debug=debug,year=year)
    A.fill()
    #A.getTemplate()
    #A.fillGlobal()
    #one = A.testFillOne()
