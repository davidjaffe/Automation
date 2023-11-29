#!/usr/bin/env python
'''
read, parse Talks.csv made from B2MMS 


'''
import math
import sys,os
import csv
import datetime
import dateutil.parser as dparser
from pprint import pprint


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
        if debug > 1 : print('makeTalkTable.main ConfName',ConfName)
        Table = {}
        ConfStart = {}
        for row in reader:
            date = row[StartDate]
            dtdate = dparser.parse(date)
            if dtdate>=when:
                conf,speaker,title,talktype = row[ConfName],row[Speaker],row[Title],row[TalkType]
                if debug > 1 : print('makeTalkTable.main conf',conf)
                if conf not in Table:
                    Table[conf] = []
                    ConfStart[conf] = dtdate
                Table[conf].append( [row[Speaker], row[Title], row[TalkType], date ] )

        if debug > 1 :
            print('makeTalkTable.main ConfStart',ConfStart)
            print('makeTalkTable.main Table.keys()')
            print(*Table.keys(),sep='\n')
        for conf in sorted(ConfStart, key=ConfStart.get,reverse=True):
            if debug > 0 : print('makeTalkTable.main conf',conf,'dtdate',dtdate)
            dtdate = ConfStart[conf]
            date = dtdate.strftime(tfmt)


            print('\n--------- ',conf,"("+date+")")
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
    if len(sys.argv)>3 :
        when  = sys.argv[3]
        when  = datetime.datetime.strptime(when,'%d-%b-%Y')
    
    mTT = makeTalkTable(debug=debug,cvsFile=filename,when=when)
    mTT.main()
