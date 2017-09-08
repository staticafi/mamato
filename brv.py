#!/usr/bin/python

from os.path import abspath

from brv.server.server import BRVServer
from brv.database.proxy import DatabaseProxy
from brv.xml.parser import XMLParser

import sys

if __name__ == "__main__":

    if len(sys.argv) > 1:
        parser = XMLParser('database.conf')
        for xmlfile in sys.argv[1:]:
            print('Parsing: {0}'.format(xmlfile))
            parser.parseToDB(xmlfile)

    BRVServer.establish()
