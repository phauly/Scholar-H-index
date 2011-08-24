# -*- coding: utf-8 -*-
#
# Nicolas Roussel     http://insitu.lri.fr/~roussel/
# In Situ, Université Paris-Sud (LRI) & INRIA Futurs
#
# cache.py -
#
# See the file LICENSE for information on usage and redistribution of
# this file, and for a DISCLAIMER OF ALL WARRANTIES.

from lib.aux import texttime
from lib.web.common import showForm, sortReferences, showStats, showResults

import os, datetime

def view_directory_entry(S,now, t,size,filename):
    d = now-t
    if d<S.cachetimeout:
        cls = "valid"
    else:
        cls = "invalid"
    print '<tr class="%s">'%cls
    print '<td>%s ago</td>'%texttime.stringify(d)
    print '<td><code><a href="%s/cache/%s">%s</a></code></td>'%(os.environ.get("SCRIPT_NAME"),filename,filename)
    print '<td>%.02f Kb</td>'%(size/1024.0)
    print '<td>%s</td>'%(t.isoformat())
    #(metadata,references) = S.loadCachedResults(os.path.join(S.cachedir,filename), force=True)
    #ipaddr = metadata.get("ip",None)
    #if ipaddr!=None: print '<td><a href="http://www.hostip.info"><img src="http://api.hostip.info/flag.php?ip=%s"></a></td>'%ipaddr
    print "</tr>"
    
def view_directory(S, path, query):
    now = datetime.datetime.now()
    oneday = datetime.timedelta(days=1)
    filenames = os.listdir(S.cachedir)
    files = []
    for filename in filenames:
        path = os.path.join(S.cachedir,filename)
        t = datetime.datetime.fromtimestamp(os.stat(path).st_ctime)
        if (now-t)>oneday:
            os.unlink(path)
        else:
            size = os.stat(path).st_size
            files.append((t,size,filename))
    files.sort()
    files.reverse()
    print '<h2><a href="%s">scHolar index</a>: %d cached result(s)</h2>'%(os.environ.get("SCRIPT_NAME"), len(filenames))
    print '<table class="cache">'
    if len(files)<100:
        for t,size,filename in files:
            view_directory_entry(S,now, t,size,filename)
    else:
        for t,size,filename in files[:50]:
            view_directory_entry(S,now, t,size,filename)
        print '<tr class="filler"><td>...</td><td>...</td><td>...</td><td>...</td></tr>'
        for t,size,filename in files[-50:]:
            view_directory_entry(S,now, t,size,filename)
    print "</table>"

def view_entry(S, path, query):
    script = os.environ.get("SCRIPT_NAME")
    print '<h2><a href="%s">scHolar index</a> <a href="%s/cache">cache</a>: %s</h2>'%(script,script,path)
    filename = os.path.join(S.cachedir,path)
    t = datetime.datetime.fromtimestamp(os.stat(filename).st_ctime)
    timeleft = S.cachetimeout - (datetime.datetime.now()-t)
    (metadata,references) = S.loadCachedResults(path, force=True)
    print '<div class="status">Last update: %s.'%t.isoformat()
    if timeleft>datetime.timedelta(0):
        print 'Cache entry remains valid for %s.</div>'%texttime.stringify(timeleft)
    else:
        print 'Executing the query will update the cache entry.</div>'
    showForm(metadata.get("query",""))
    references = sortReferences(references)
    showStats(metadata, references)
    showResults(metadata, references)

def view(S, path, query):
    if path:
        view_entry(S, path, query)
    else:
        view_directory(S, path, query)
