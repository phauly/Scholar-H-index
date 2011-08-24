# -*- coding: utf-8 -*-
#
# Nicolas Roussel     http://insitu.lri.fr/~roussel/
# In Situ, Université Paris-Sud (LRI) & INRIA Futurs
#
# metrics.py -
#
# See the file LICENSE for information on usage and redistribution of
# this file, and for a DISCLAIMER OF ALL WARRANTIES.

import math, datetime

from aux import statistics

# ------------------------------------------------------------------------------

def filterOut(seq,key,ignore):
    result = []
    for r in seq:
        val = r.get(key,ignore)
        if val!=ignore: result.append(val)
    return result

def hindex(references):
    h = 0
    while True:
        h = h + 1
        n = 0
        for r in references:
            if r.citedby>=h: n = n+1
        if n<h:
            h = h-1
            break
    citations = statistics.Statistics([r.citedby for r in references])
    years = filterOut(references,"year",0)
    if years:
        Yrange = statistics.Statistics(years).range
    else:
        Yrange = 0
    try:
        a = citations.sum/math.pow(h,2)
    except ZeroDivisionError:
        a = float("inf")
    try:
        m = float(h)/Yrange
    except ZeroDivisionError:
        m = float("inf")
    return (h,a,m)

def gindex(references):
    refs = [r.citedby for r in references]
    refs.sort()
    refs.reverse()
    g, citations = 0, 0
    while g<len(refs) and refs[g]>0:
        citations += refs[g]
        if citations<g*g: break
        g = g+1
    if not citations: return 0
    return g-1

# ------------------------------------------------------------------------------

if __name__=="__main__":
    import sys
    import scholar
    name = sys.argv[1]
    name = name.replace(" ","+")
    name = name.replace('"',"%22")
    s = scholar.Scholar(cachetimeout=datetime.timedelta(seconds=60))
    (metadata,references) = s.query("as_sauthors=%s"%name)
    s.debugInfo("done")
    print
    print "h-index: %d (a=%.2f, m=%.2f)"%hindex(references)
    print "g-index:",gindex(references)
