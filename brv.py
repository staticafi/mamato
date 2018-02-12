#!/usr/bin/python

from sys import version_info

if version_info < (3, 0):
    from brv.server.server import createServer
else:
    from brv.server.server import BRVServer

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        from brv.xml.parser import XMLParser

        parser = XMLParser('database.conf')
        total = 0
        for xmlfile in sys.argv[1:]:
            print('Parsing: {0}'.format(xmlfile))
            cnt = parser.parseToDB(xmlfile)
            print('Got {0} results from {1}'.format(cnt, xmlfile))
            total += cnt

        print('Added {0} results in total'.format(total))

    else:
        if version_info < (3, 0):
            createServer()
        else:
            BRVServer.establish()
