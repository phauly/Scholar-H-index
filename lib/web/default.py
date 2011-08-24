# -*- coding: utf-8 -*-
#
# Nicolas Roussel     http://insitu.lri.fr/~roussel/
# In Situ, Université Paris-Sud (LRI) & INRIA Futurs
#
# default.py -
#
# See the file LICENSE for information on usage and redistribution of
# this file, and for a DISCLAIMER OF ALL WARRANTIES.

from lib.web import html
from lib.web.common import sortReferences, showForm, showStats, showResults

import os, cgi
    
def view(S, path, query):
    print '<table class="title"><tr>'
    print '<td>'
    print html.read("title.html")
    this = os.environ.get("SCRIPT_NAME")
    print '<p class="menu"><a href="%s">home</a> - <a href="mailto:roussel@lri.fr?subject=[scHolar index]">contact</a></p>'%this
    print "</td>"
    print '<td>'
    args = showForm(query)
    print "</td>"
    print "</tr></table>"
    if query:
        print '<div class="status">'
        (metadata,references) = S.query(query)
        if metadata.get("nocache",False):
            print '</div>'
        else:
            S.debugInfo("done")
            print '</div>'
            references = sortReferences(references)
            showStats(metadata, references)
            minr = args.get("x_minr","")
            if minr:
                minr = int(minr)
            else:
                minr = 0
            showResults(metadata, references, minr)
    else:
        print html.read("about.html")
