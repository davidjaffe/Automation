#
# Workflow
# 0. 20230823 converted filler.py and auto.py from python2 to python3 with 2to3. filler.py was tested. auto.py was not, but only 1 non-print statement changed in conversion. 
# 1. cut/paste from Public Conference talks page into filler.input (more info in filler.py and filler.input
# 2. edit filler.input to add '*' for conference and '#' for blank lines. (more info in filler.input)
# 3. python filler.input
# 3.1 Add conference URLs from links on Public Conference talks page when requested by filler.py
# 4. insert filler.output into auto.cfg 
# 5. Starting from links on Public Conference talks page, obtain links for all talks as provided by conference websites and insert in talk_url: 
# 5.1 If available, obtain abstract and title from conference website and insert at abstract: and title: . Note that title sometimes differs from original
# 5.1.1 If no abstract is available, use the title as abstract
# 5.2 Contact speaker directly if link to talk not available at conf website
# 6. From Belle II Document Server, obtain and insert draft_reference: for all talks. Easiest way is to search all draft talks with display = 100 results & single list and output format = HTML detailed output.
# 6.1 obtain abstract from doc server if it wasn't available from conf website
# 6.2 sometimes speakers didn't upload a draft. leave draft_reference: empty in that case
# 7. python auto.py [SHORT CONF NAME]
# 7.1 First pass is usually dry run so missing files can be identified
# 7.2 Set dryrun=False for second pass. It should download all files for [SHORT CONF NAME]
# 8. Submit new Belle II Conference Talk for each entry in auto.cfg
# 8.1 Easiest way is to cut/paste into a single text box on page and the cut/paste each entry from that text box.
# 8.2 BE SURE TO EDIT single text box after cut/paste exercise
# 8.3 Upload talk [Doesn't always work with firefox browser]. May be useful to cut/paste the 'submission number' into this file in case the doc server misbehaves
# 9. Wait for doc server to process new entries so they appear in the Doc Server. Usually <1 hour, sometimes longer. If >24h, Doc Server may be busted.
# 10. Edit Public Conference talks page to include links to slides
# 11. Add new conferences, talks, speakers from B2MMS 'Talk Manager' list. I only add 'accepted' talks. Can configure B2MMS 'Talk Manager' to show only relevant columns for current year. 
# 12. Proofread Public Conference talks page
## added 20230309 for email reminder to speakers concerning proceedings
##  may need to download new .csv of the list of members from B2MMS
# 13. python auto.py [SHORT CONF NAME] T -1 T
# 14. cut/paste email, subject and email text into email message. (Would like to automate this part, too)
#
#
#
