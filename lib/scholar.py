# -*- coding: utf-8 -*-
#
# Nicolas Roussel     http://insitu.lri.fr/~roussel/
# In Situ, Université Paris-Sud (LRI) & INRIA Futurs
#
# scholar.py -
#
# See the file LICENSE for information on usage and redistribution of
# this file, and for a DISCLAIMER OF ALL WARRANTIES.

import os, sys, codecs, traceback, pwd
import datetime, cPickle
import re, string
import urllib, urlparse
import glob, ConfigParser, random

import cookielib, urllib2
urlopener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=0),
                                 urllib2.HTTPRedirectHandler(),
                                 urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
urlopener.addheaders = [('User-agent', 'Mozilla/6.0')]

try:
    import hashlib
    myhash = hashlib.sha224
except ImportError:
    import md5
    myhash = md5.new

# http://www.crummy.com/software/BeautifulSoup/
from aux import BeautifulSoup

random.seed()

# ------------------------------------------------------------------------------

class ScholarReference:

    def getURL(self):
        if self.gid==None: return None
        return "http://scholar.google.com/scholar?cluster=%s"%self.gid

    def getCitedByURL(self):
        if self.gid==None: return None
        return "http://scholar.google.com/scholar?cites=%s"%self.gid

    def get(self, key, defval=None):
        if self.__dict__.has_key(key): return self.__dict__[key]
        return defval

# ------------------------------------------------------------------------------

_citedby = re.compile('.*Cited by (\d+).*',re.MULTILINE+re.DOTALL)
_pubyear = re.compile('.*\D(\d\d\d\d)\D.*',re.MULTILINE+re.DOTALL)
_id_cites = re.compile('.*cites=(\d+).*',re.MULTILINE+re.DOTALL)
_id_cluster = re.compile('.*cluster=(\d+).*',re.MULTILINE+re.DOTALL)

def _cleanup(text):
    text = re.sub("\n"," ",text)
    text = re.sub("&nbsp;"," ",text)
    text = re.sub("&#x25ba;","",text)
    text = re.sub("\[[^\]]+\]","",text) # [BOOK], [PDF], etc.
    text = re.sub("<p[^>]*>","",text)
    text = re.sub("</p>","",text)
    text = re.sub("<font[^>]*>","",text)
    text = re.sub("</font>","",text)
    text = re.sub("<b>","",text)
    text = re.sub("</b>","",text)
    text = re.sub("<span[^>]*>","",text)
    text = re.sub("</span>","",text)
    return text.strip()
        
def _tryExp(text,exp,defval):
    m = exp.match(text)
    if m: return m.group(1)
    return defval

def _parseResults(soup):
    result = []
    reference = soup.find('p')
    #reference = soup.find('div', {'class':'gs_r'}) #not good for siblings!
    #print "ref=",reference
    while reference!=None:
        try:
            #print "<p>%s</p>"%unicode(reference)
            r = ScholarReference()
            d = unicode(reference).split("<br />")
            t = reference.find('a').next
            if t:
                r.title = _cleanup(unicode(t))
            else:
                r.title = _cleanup(d[0])
            r.info = _cleanup(d[1]) #+"<br>"+d[-1]
            r.citedby = int(_tryExp(d[-1],_citedby,0))
            if r.citedby==0 and d[-1].find("Cited by")!=-1:
                print "\n<!-- CitedBy REGEXP ERROR: %s -->\n"%d[-1]
                r.citedby = 99999
            r.year = int(_tryExp(d[1],_pubyear,0))
            r.gid = _tryExp(d[-1],_id_cites,None)
            if not r.gid: r.gid = _tryExp(d[-1],_id_cluster,None)
            #print "<p>%s --&gt; %s</p>"%(r.citedby,r.title)
            result.append(r)
        except:
            pass
        reference = reference.nextSibling

    return result

# ------------------------------------------------------------------------------

class Scholar:

    def __init__(self,
                 cachedir="/tmp/scholar",
                 cachetimeout=datetime.timedelta(seconds=60*60),
                 configdir="",
                 querytimeout=5.0,
                 trace=None, verbose=True):
        cachedir = cachedir+"-"+pwd.getpwuid(os.geteuid())[0]
        if not os.path.exists(cachedir): os.makedirs(cachedir)
        self.cachedir = cachedir
        self.cachetimeout = cachetimeout
        self.configdir = configdir
        self.querytemplate = "/scholar?as_q=&num=%d&"
        self.querytimeout = querytimeout
        self.trace = trace
        self.verbose = verbose

    # ------------------------------------------------------------------
    
    def debugInfo(self, text):
        if not self.verbose: return
        print " ------  # "+text+"\n",
        sys.stdout.flush()

    # ------------------------------------------------------------------

    def getCacheEntry(self, query):
        global myhash
        return myhash(query).hexdigest()
         
    def saveResults(self, results, filename):
        cPickle.dump(results,file(filename,"w"))

    def loadResults(self, filename):
        return cPickle.load(file(filename,"r"))

    def cacheResults(self, results, entry=None):
        try:
            if not entry: entry = self.getCacheEntry(results[0]["query"])
            filename = os.path.join(self.cachedir, entry)
            self.saveResults(results, filename)
        except:
            traceback.print_exc()
            pass

    def loadCachedResults(self, entry, force=False):
	self.debugInfo("loadCachedResults")
        try:
            filename = os.path.join(self.cachedir, entry)
	    #print "filename="+filename
            timestamp = datetime.datetime.fromtimestamp(os.stat(filename).st_mtime)
	    #print "timestamp"+str(timestamp)
	    self.debugInfo("filename="+filename+" timestamp="+str(timestamp))
	    #print("filename="+filename+" timestamp="+str(timestamp))
     	    self.debugInfo("minore"+str(datetime.datetime.now()-timestamp<self.cachetimeout))
	    #print("minore"+str(datetime.datetime.now()-timestamp<self.cachetimeout))
            if force or datetime.datetime.now()-timestamp<self.cachetimeout:
    	        self.debugInfo("veramente da cache")
		#print("veramente da cache")
                return self.loadResults(filename)
        except:
	    #traceback.print_exc()
            pass
        return ({},[])

    # ------------------------------------------------------------------

    # we can limit per year! From as_ylo up to as_yhi! as_ylo=1990&as_yhi=1990
    def query(self, query):
        cacheentry = self.getCacheEntry(query)
        (metadata,references) = self.loadCachedResults(cacheentry)
	from_cache=False
        #references = []
	self.debugInfo("references="+str(references))
        if references:
            self.debugInfo("Using cached data...")
            from_cache = True
            return (metadata,references,from_cache)
        (metadata,references) = self._doQuery(query)
        if references and metadata.get("nocache",False)==False:
            self.debugInfo("Caching results...")
            tmplist = [(x.citedby, x.year, x) for x in references]
            tmplist.sort()
            references = [x for (key1, key2, x) in tmplist]
            references.reverse()
            self.cacheResults((metadata,references), entry=cacheentry)
        return (metadata,references,from_cache)
    
    def fakeQuery(self, filename):
        b = os.path.basename(filename)
        self.debugInfo(u'Opening %s...'%b)
        data = open(filename).read()
        soup = BeautifulSoup.BeautifulSoup(data)
        references = _parseResults(soup)
        return ({"query":"fake:%s"%b},references)

    def _doQuery(self, query):
	metadata = {"query":query, "ip":os.environ.get("REMOTE_ADDR",None)}
        references = []
        offset, inc = 0, 100
        cfg = ConfigParser.ConfigParser()
        cfg.read(glob.glob("%s/*.cfg"%self.configdir))
        choice = random.choice(cfg.sections())
	self.debugInfo(str(cfg.get(choice, "server")))
        while True:
            q = self.querytemplate%inc+query
            if offset!=0: q = q+"&start=%d"%offset
            server = cfg.get(choice, "server")
            port = cfg.getint(choice, "port")
            service = cfg.get(choice, "service")%q           
            targetUrl = "http://%s:%s%s"%(server,port,service)
            if offset==0:
                self.debugInfo('<a href="http://scholar.google.com(or other)%s">Querying</a> %s... [precisely %s]'%(q,choice,str(targetUrl)))
            # -------------------------------                
            try:
                fd = urlopener.open(targetUrl)
                data = fd.read()
            except:
		self.debugInfo("PROBLEM downloading citations from google")
                traceback.print_exc()
                data = ""
            # -------------------------------
            if self.trace:
                try:
                    f = codecs.open(self.trace,"w","utf-8")
                    f.write("server: %s:%s\nservice: %s\n"%(server,port,service))
                    f.write("-"*80+"\n")
                    f.write(data.decode("utf-8"))
                    f.close()
                    f = None
                except:
                    pass
            self.debugInfo("parsing...")
	    self.debugInfo(data)
            soup = BeautifulSoup.BeautifulSoup(data)
            morerefs = _parseResults(soup)
            references = references + morerefs
            if len(morerefs)!=inc:
                if len(morerefs)==0 and data.find("<h1>We're sorry...</h1>")!=-1:
                    metadata["nocache"] = True
                    self.debugInfo('query stopped. Try again later, <a href="tryagain.html">after reading this</a>')
                break
            offset = offset+inc
        return (metadata,references)

# ------------------------------------------------------------------------------

if __name__=="__main__":
    name = sys.argv[1]
    name = name.replace(" ","+")
    name = name.replace('"',"%22")
    s = Scholar(cachetimeout=datetime.timedelta(seconds=60),configdir="cfg",trace="/tmp/scholarindex-results.html")
    #s = Scholar(cachetimeout=datetime.timedelta(seconds=60),configdir="cfg")#,trace="/tmp/scholarindex-results.html")
    (metadata,references) = s.query("as_sauthors=%s"%name)
    s.debugInfo("done")
    print "-->",len(references),"references"
	
    import math, datetime
    from aux import statistics
    from lib import metrics
    print "h-index: %d (a=%.2f, m=%.2f)"%metrics.hindex(references)

