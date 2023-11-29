#!/usr/bin/env python
'''
read, parse csv files made from B2MMS to create info for Public Conference Talks page

  20231129 THESE INSTRUCTIONS WRITTEN and COPIED to ReadMe_Workflow.txt
1. From B2MMS Conference Manager, download Conferences.csv made by Saved Report "ConferenceTalksInfo". 
2. Rename Conferences.csv Conferences_YYYYMMDD.csv in current directory where YYYYMMDDD is today's date
3. From B2MMS Talks Manager, download Talks_new.csv made by "Assigned talks with conference start date"
4. Rename Talks_new.csv Talks_new_YYYYMMDD.csv in current directory. 
5. python makeTalkTable.py Talks_new_YYYYMMDD.csv 


'''
import math
import sys,os
import csv
import datetime
import dateutil.parser as dparser
from pprint import pprint


class makeTalkTable():
    def __init__(self,debug=-1,csvFile=None,when=None):

        self.debug = debug
        if csvFile is None: sys.exit('makeTalkTable: Input csv file not specified')
        if when is None: when = datetime.datetime.today()
        if type(when) is str : when = dparser.parse(when)
        self.csvFile = csvFile
        self.when  = when
        self.ConfcsvFile = 'Conferences_' + csvFile.split('.')[0].split('_')[-1] + '.csv'


        print('makeTalkTable.__init__ debug',debug,'csvFile',csvFile,'when',when)


        return
    def fillConfInfo(self):
        '''
        return dict ConfInfo[confName] = [url, start date, location]
        '''
        debug = self.debug

        filename = self.ConfcsvFile
        reader = csv.DictReader(open(filename,encoding='ISO-8859-1'))
        print('makeTalkTable.fillConfInfo Opened',filename)

        nameList = []
        for word in ['Conference Name','Conference Location','Conference Link','Start Date']:
            i = reader.fieldnames.index(word)
            if i>-1 : nameList.append(word)
        ConferenceName, Location, URL, StartDate = nameList

        ConfInfo = {}
        for row in reader:
            confName = row[ConferenceName]
            ConfInfo[confName] = [ row[URL], row[StartDate], row[Location] ]
        if debug > 1 : print('makeTalkTable.fillConfInfo ConfInfo',ConfInfo)
        return ConfInfo
    def main(self):
        '''
        read self.csvFile as dict
        find all conferences after date specified by when
        print chrono list of conference talks, alphabetized by speaker name

        date format in csv is dd-MMM-YYYY '%d-%b-%Y'
        '''
        ConfInfo = self.fillConfInfo()
        
        tfmt =  '%d-%b-%Y'
        debug = self.debug

        filename = self.csvFile
        reader = csv.DictReader(open(filename,encoding='ISO-8859-1'))
        print('makeTalkTable.main Opened',filename)

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
            url, startDate, location = None, None, None
            if conf in ConfInfo:
                url,startDate,location = ConfInfo[conf]


            print('\n--------- ',conf,"("+date+", "+location+")",url)
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
    
    mTT = makeTalkTable(debug=debug,csvFile=filename,when=when)
    mTT.main()
