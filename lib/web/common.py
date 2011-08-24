# -*- coding: utf-8 -*-
#
# Nicolas Roussel     http://insitu.lri.fr/~roussel/
# In Situ, Université Paris-Sud (LRI) & INRIA Futurs
#
# common.py -
#
# See the file LICENSE for information on usage and redistribution of
# this file, and for a DISCLAIMER OF ALL WARRANTIES.

from lib import metrics
from lib.aux import statistics
from lib.web import html

import os, sys
import cgi
import math
import re

# ---------------------------------------------------------------------------------------

def sortReferences(references):
    tmplist = [(x.citedby, x.year, x) for x in references]
    tmplist.sort()
    references = [x for (key1, key2, x) in tmplist]
    references.reverse() 
    return references

# ---------------------------------------------------------------------------------------

def showStats(metadata, references):
    print
    print """<table class="statistics"><tr>"""
    print "<td>%d references"%len(references),
    if references:
        citations = statistics.Statistics([r.citedby for r in references])
        years = metrics.filterOut(references,"year",0)
        if years:
            y = statistics.Statistics(years)
            print "between %s and %s<br>"%(y.min,y.max)
        hindex = metrics.hindex(references)
        metadata["hnumber"] = hindex[0]
        cited = metrics.filterOut(references,"citedby",0)
        if cited:
            pcitations = statistics.Statistics(cited)
            print "%d references cited (%d citations)<br><br>"%(pcitations.N,citations.sum)
            print "%.02f citations per reference (median=%.02f)</br>"%(citations.mean,citations.median)
            print "%.02f citations per cited reference (median=%.02f)"%(pcitations.mean,pcitations.median)
        print "</td><td>"
        print '<a target="_blank" href="http://en.wikipedia.org/wiki/Hirsch_number">h-index</a>: %d (a=%.02f, m=%.02f)<br>'%hindex
        print '<a target="_blank" href="http://en.wikipedia.org/wiki/G-index">g-index</a>:',metrics.gindex(references)
    print "</td>"
    print "</tr></table>"
    print

# ---------------------------------------------------------------------------------------
    
def showResults(metadata, references, minr=0):
    print
    #references = sortReferences(references)
    hnumber = metadata.get("hnumber",0)
    nbok = 0
    for r in references:
        if r.citedby<minr: continue
        nbok +=1
    if nbok==0:
        if minr>0:
            print '<div class="status">No reference with more than %d citations</div>'%minr
        else:
            print '<div class="status">No result</div>'
    elif minr>0:
        print '<div class="status">%d reference(s) with more than %d citation(s)</div>'%(nbok,minr)
    print '<table width="100%" class="references">'
    for r in references:
        if r.citedby<minr: continue
        if r.citedby==0:
            cls = "notcited"
        elif hnumber>0 and r.citedby<hnumber:
            cls = "hinf"
        elif hnumber>0 and r.citedby==hnumber:
            cls = "hlim"
        else:
            cls = "normal"
        print "<tr>"
        if r.citedby>0:
            width = 30*math.log(1+100.0*r.citedby/references[0].citedby)
            print '<td align="right"><div class="hbar" style="width: %spx"></div></td>'%width
            print '<td align="right"><a href="%s">%s</a></td>'%(r.getCitedByURL(),r.citedby)
        else:
            print '<td colspan="2"></td>'
        if r.gid!=None:
            print '<td class="%s"><a href="%s">%s</a><div class="reference-details">%s</div></td>'%(cls,r.getURL(),r.title,r.info)
        else:
            print '<td class="%s">%s<div class="reference-details">%s</div></td>'%(cls,r.title,r.info)
        print "</tr>"
    print "</table>"
    print
    
# ---------------------------------------------------------------------------------------

def getDefaultFormParams():
    return {
        "as_sauthors":("text",[],[]),
        "as_subj":("checkbox",[],["bio", "bus", "chm", "eng", "med", "phy", "soc"]),
        "as_q":("text",[],[]), # with all the words
        "as_oq":("text",[],[]), # with at least one of the words
        "as_eq":("text",[],[]), # without the words
        "as_publication":("text",[],[]), # published in
        "as_ylo":("text",[],[]), # between lo and text:hi
        "as_yhi":("text",[],[]),
        "x_minr":("text",[],[]),
        }

def showForm(query=""):
    args = {}
    params = getDefaultFormParams()
    qs = cgi.parse_qs(query)
    for key, (input_type, defval, choices) in params.items():
        values = qs.get(key,defval)
        values = map(lambda v: re.sub(u'"',u'&quot;',v.decode("utf-8")), values)
        params[key] = (input_type,values,choices)
    #print "<p>%s</p>"%qs
    #print "<p>%s</p>"%params
    form = html.read("form.html")
    i = 0
    for key,(input_type,values,choices) in params.items():
        if input_type=="text":
            if not values:
                repl = u""
            else:
                #print key
                if key!="as_sauthors": i += 1
                repl = values[0]
            #print "<p>Subst: %s --> %r</p>"%(key,repl)
            args[key] = repl
            k = u"[-["+key+u"]-]"
            v = u"\""+repl+u"\""
            #print repr(k),repr(v)
            form = form.replace(k, v)
        elif input_type=="checkbox":
            d = {}
            for c in choices:
                if c in values:
                    i += 1
                    #print key
                    repl = 'checked="true"'
                else:
                    repl = ''
                #print "<p>Subst: %s(%s) --> %r</p>"%(key,c,repl)
                form = form.replace("[-["+key+"-"+c+"]-]",repl)
                d[c] = (repl!='')
            args[key] = d
    form = form.replace("[--[ACTION]--]",os.environ.get("SCRIPT_NAME"))
    print form
    if i>0:
        print """<script>showHideDetails("block")</script>"""
    else:
        print """<script>showHideDetails("none")</script>"""
    return args
