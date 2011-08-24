# -*- coding: utf-8 -*-
#
# Paolo Massa   http://www.gnuband.org
#
# See the file LICENSE for information on usage and redistribution of
# this file, and for a DISCLAIMER OF ALL WARRANTIES.

import datetime
import os
import urllib2
import time
import sys

from lib import scholar, web, metrics
from lib import fbk_employees

import optparse
p = optparse.OptionParser(
        usage="usage: %prog schindex_dir")
opts, files = p.parse_args()

if len(files) != 1:
        p.error("Wrong parameters")
   
schindex_dir = files[0]

cache_path=schindex_dir+"/scholarindex_cache"
sleep_seconds = 200

try:
	os.mkdir(cache_path)
except OSError:
	pass
	#print "cache dir ("+cache_path+") already present"

s = scholar.Scholar(cachedir=cache_path,
                    trace=cache_path+"/scholarindex-results.html",
                    cachetimeout=datetime.timedelta(seconds=60*60),
                    configdir=os.path.abspath(schindex_dir+"/cfg"),
#		    verbose=True)
	            verbose=False)

employees = fbk_employees.get_list_of_fbk_employee()
#print employees 

names = [
	'paolo+massa',
	'"paolo+massa"'
]
names = [((e[0].encode('utf8','ignore'))+"+"+(e[1].encode('utf8','ignore'))).replace(' ', '+') for e in employees]
#print names

#print "H-INDEXES and G-INDEXES"
for name in names[1:]:
	(metadata,references,from_cache) = s.query('as_sauthors="%s"'%name)
        #print "\n".join([r.title for r in references])
	#print "from cache ",from_cache
	try:
		hindex = metrics.hindex(references)
		gindex = metrics.gindex(references)
	except:
		hindex = [-1,-1,-1]
		gindex = -1
	if len(references)>0:
                most_cited=references[0]
		most_cited_string = ('Most citations ( %d ) to "%.60s"' % (most_cited.citedby,most_cited.title)).encode('utf8','ignore')
	else:
		most_cited_string = ""
	        #resp = raw_input("no paper?")
	#print "Got the next researcher from cache="+str(from_cache)+(" - waiting "+str(sleep_seconds)+" seconds" if not from_cache else '')
	print "%25.30s | hindex= %3d | gindex= %3d | #papers= %3d | %s | cache= %s"%(name,hindex[0],gindex,len(references),most_cited_string,str(from_cache))
        sys.stdout.flush()
	if not from_cache:
		#print "not from cache, we need to sleep 100 seconds"
		time.sleep(sleep_seconds)
