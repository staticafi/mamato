#!/usr/bin/python

from sys import version_info
from argparse import ArgumentParser

if version_info < (3, 0):
    from brv.server.server import createServer
else:
    from brv.server.server import BRVServer

def parse_cmd():
    parser = ArgumentParser()
    parser.add_argument('--outputs', default=None,
                        help='Name of the .zip archive with tool\'s outputs')
    parser.add_argument('--results-dir', default=None,
                        help='Directory with benchexec outputs (xml/bzip2 files + .zip with outputs)')
    parser.add_argument('--description', default=None,
                        help='Description of the run given in xml files')
    parser.add_argument('files', nargs="*", metavar="FILES",
                        help="XML files. If given, no server is run and the files are parsed and stored to dtabase")
    return parser.parse_args()


if __name__ == "__main__":
    import sys
    args = parse_cmd()

    if args.results_dir:
        print(args.results_dir)
    elif args.files:
        from brv.xml.parser import XMLParser
        parser = XMLParser('database.conf')

        total = 0
        for xmlfile in args.files:
            print('Parsing: {0}'.format(xmlfile))
            cnt = parser.parseToDB(xmlfile, args.outputs, args.description)
            print('Got {0} results from {1}'.format(cnt, xmlfile))
            total += cnt

        print('Added {0} results in total'.format(total))

    else:
        if version_info < (3, 0):
            createServer()
        else:
            BRVServer.establish()
