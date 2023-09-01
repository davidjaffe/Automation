#!/usr/bin/env python
'''
read, parse Talks.csv made from B2MMS 


'''
import math
import sys,os
import csv
import datetime
import dateutil.parser as dparser


class makeTalkTable():
    def __init__(self,debug=-1,cvsFile=None,when=None):

        self.debug = debug
        if cvsFile is None: sys.exit('makeTalkTable: Input cvs file not specified')
        if when is None: when = datetime.datetime.today()
        if type(when) is str : when = dparser.parse(when)
        self.cvsFile = cvsFile
        self.when  = when


        print('makeTalkTable.__init__ debug',debug,'cvsFile',cvsFile,'when',when)


        return
    def main(self):
        '''
        read Talks.csv as dict
        find all conferences after date specified by when
        print chrono list of conference talks, alphabetized by speaker name

        date format in csv is dd-MMM-YYYY '%d-%b-%Y'
        '''
        tfmt =  '%d-%b-%Y'
        debug = self.debug

        reader = csv.DictReader(open(filename,encoding='ISO-8859-1'))

        nameList = []
        for word in ['Conference Name', 'Member', 'Title', 'Status', 'Email', 'Talk Type', 'Conference Start Date']:
            i = reader.fieldnames.index(word)
            if i>-1 : nameList.append(word)
        ConfName, Speaker, Title, Status, Email, TalkType, StartDate = nameList
        Table = {}
        ConfStart = {}
        for row in reader:
            date = row[StartDate]
            dtdate = dparser.parse(date)
            if dtdate>=when:
                conf,speaker,title,talktype = row[ConfName],row[Speaker],row[Title],row[TalkType]
                if conf not in Table:
                    Table[conf] = []
                    ConfStart[dtdate] = conf
                Table[conf].append( [row[Speaker], row[Title], row[TalkType], date ] )

        for dtdate in sorted(ConfStart,reverse=True):
            date = dtdate.strftime(tfmt)
            conf = ConfStart[dtdate]

            print('\n--------- ',date,conf)
            for a in  sorted(Table[conf]):
                n = ' '.join(a[0].split())
                t = '"' + ' '.join(a[1].split()) + '"'
                p = '(plenary)'
                if 'plenary' not in a[2].lower() : p = '(invited)'
                print(n,t,p)

        
        return
if __name__ == '__main__' :


    ### python makeTalkTable.py [filename] [debug] [date]
    debug = -1
    when = datetime.datetime.today()
    if len(sys.argv)<2:
        print('USAGE: python makeTalkTable.py [filename](required) [debug]('+str(debug)+') [date]('+when.strftime('%d-%b-%Y')+')')
        sys.exit(' ')
    filename = sys.argv[1]

    
    if len(sys.argv)>2 : debug = int(sys.argv[2])
    if len(sys.argv)>3 : when  = sys.argv[3]
    
    mTT = makeTalkTable(debug=debug,cvsFile=filename,when=when)
    mTT.main()
