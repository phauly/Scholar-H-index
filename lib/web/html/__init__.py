# -*- coding: utf-8 -*-
#
# Nicolas Roussel     http://insitu.lri.fr/~roussel/
# In Situ, Université Paris-Sud (LRI) & INRIA Futurs
#
# __init__.py -
#
# See the file LICENSE for information on usage and redistribution of
# this file, and for a DISCLAIMER OF ALL WARRANTIES.

import os, codecs

def read(filename):
    base = os.path.dirname(__file__)
    return codecs.open(os.path.join(base,filename),"r","utf-8").read()
