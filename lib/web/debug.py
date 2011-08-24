# -*- coding: utf-8 -*-
#
# Nicolas Roussel     http://insitu.lri.fr/~roussel/
# In Situ, Université Paris-Sud (LRI) & INRIA Futurs
#
# debug.py -
#
# See the file LICENSE for information on usage and redistribution of
# this file, and for a DISCLAIMER OF ALL WARRANTIES.

from lib.web.common import sortReferences, showStats, showResults

import os, codecs, cgitb

def view(S, path, query):
    print '<h2><a href="%s">scHolar index</a>: debug</h2>'%os.environ.get("SCRIPT_NAME")
    if path:
        print '<div class="status">'
        (metadata,references) = S.fakeQuery("misc/scholar/examples/%s.html"%path)
        print '</div>'
        #S.cacheResults((metadata,references))
        references = sortReferences(references)
        showStats(metadata,references)
        showResults(metadata, references)
    else:
        print codecs.open(S.trace,"r","utf-8").read()
        
