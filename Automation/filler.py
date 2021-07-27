#!/usr/bin/env python
'''
20210727 created. parses Public ConferenceTalks text to fill entries used in auto.cfg
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


class filler():
    def __init__(self,debug=0):

        self.debug = debug
        print 'filler.__init__ debug',self.debug

        self.acfg  = 'auto.cfg'
        self.input = 'filler.input'
        self.output= 'filler.output'

        self.fav_items = {}

        self.default_HEADER = '[TEMPLATE_for_cutnpaste]'

        self.global_items = {'date:':'dd/mm/yyyy',
                                 'conference:':'',
                                 'keywords:':'',
                                 'conf_url:':'',
                                 'short_conf_name':''
                                 }

        return
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
        for i in self.fav_items:
            if i==0:
                sn = self.global_items['short_conf_name']
                one[i] = '[' + sn + '_' + author + ']'
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
        self.fillGlobal()
        fin = open(self.input,'r')
        fout= open(self.output,'w')
        ctr = 0
        for line in fin:
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
    if len(sys.argv)>1:
        debug = int(sys.argv[1])
 
    A = filler(debug=debug)
    A.fill()
    #A.getTemplate()
    #A.fillGlobal()
    #one = A.testFillOne()
