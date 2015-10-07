#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgitb
import cgi
import os

# modo debug - traceback para cgi
cgitb.enable()

print "Content-Type: text/html\n"

print '<html><head><meta charset="utf-8"></head><body>'

method = os.environ['REQUEST_METHOD']

if method == "POST":
    print "TODO"
    
else:
    # caso método não seja POST, negar acesso
    print "PERMISSION DENIED"

print '</body></html>'
