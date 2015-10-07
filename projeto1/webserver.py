#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import cgitb
import cgi
import os

# modo debug - traceback para cgi
cgitb.enable()

method = os.environ['REQUEST_METHOD']

if method=="GET":
    # se metodo for GET

    # header da entidade que indica o tipo de midia do corpo da entidade
    print "Content-Type: text/html\n"

    # print no webserver.html. Pagina estatica
    print codecs.open("webserver.html", "r").read()

elif method=="POST":
    # se metodo for POST

    # executa backend.py
    import backend
