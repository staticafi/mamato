#!/usr/bin/python

from sys import version_info, stdout
from argparse import ArgumentParser

import os

if version_info < (3, 0):
    from brv.server.server import createServer
else:
    from brv.server.server import BRVServer

def parse_cmd():
    parser = ArgumentParser()
    parser.add_argument('--outputs', default=None,
                        help='Name of the .zip archive with tool\'s outputs')
    parser.add_argument('--results-dir', default=None, metavar='DIR',
                        help='Load results (.zip and .xml/bz2 files) from DIR')
    parser.add_argument('--description', default=None,
                        help='Description of the run given in xml files')

    parser.add_argument('--append-vers', default=None,
                        help='Append the given string to the version of the tool. Can be used to store another run on the same version and distinguish it')
    parser.add_argument('--allow-duplicates', action='store_true', default=False,
                        help='Store also results that we already have')
    parser.add_argument('files', nargs="*", metavar="FILES",
                        help="XML files. If given, no server is run and the files are parsed and stored to dtabase")
    return parser.parse_args()

# make the xml parser global such that we open
# just one connection to the database
xmlparser = None

COLORS = {
    'DARK_BLUE': '\033[0;34m',
    'CYAN': '\033[0;36m',
    'BLUE': '\033[1;34m',
    'PURPLE': '\033[0;35m',
    'RED': '\033[1;31m',
    'GREEN': '\033[1;32m',
    'BROWN': '\033[0;33m',
    'YELLOW': '\033[1;33m',
    'WHITE': '\033[1;37m',
    'GRAY': '\033[0;37m',
    'DARK_GRAY': '\033[1;30m',
    'RESET': '\033[0m'
}

def print_col(msg, color=None):
    # don't print color when the output is redirected
    # to a file
    if not stdout.isatty():
        color = None

    if not color is None:
        stdout.write(COLORS[color])

    stdout.write(msg)

    if not color is None:
        stdout.write(COLORS['RESET'])

    stdout.write('\n')
    stdout.flush()

#def commonprefix(s1, s2):
#    idx = 0
#    for i in range(0, len(s1)):
#        if s1[i] != s2[i]:
#            idx = i
#            break
#
#    if idx == 0:
#        return None
#
#    return s1[:idx]

def getrundescr(s):
    """
    Return a string that describes the run
    """
    splt = s.split('.')
    # tool + date
    return ('.'.join(splt[:2]), splt[3])

def load_data_with_prefix(path, prefix, xmls, bz2s, outputs, descr = None):
    outputs = list(filter(lambda s : s.startswith(prefix), outputs))
    # we must have only one file with outputs
    assert len(outputs) <= 1

    # filter the xmls and prefix with the directory path
    tmp = []
    for x in xmls:
        if not x.startswith(prefix):
            continue

        tmp.append(os.path.join(path, x))
    xmls = tmp

    # unpack the bz2s files
    from bz2 import BZ2File, decompress
    from tempfile import NamedTemporaryFile
    bz2xmls = []
    for bz in bz2s:
        if not bz.startswith(prefix):
            continue

        bzfile = BZ2File(os.path.join(path,bz))
        data = bzfile.read()
        tmpfile = NamedTemporaryFile(suffix='.xml', delete=False)
        tmpfile.write(data)
        bz2xmls.append(tmpfile.name)
        xmls.append(tmpfile.name)
        tmpfile.close()
        bzfile.close()

        print_col("Decompressed '{0}' to '{1}'".format(bz, tmpfile.name), 'CYAN')


    outfile = outputs[0] if outputs else None
    total = load_xmls(xmls, outfile, descr or args.description,
                      args.append_vers, args.allow_duplicates)
    print('Added {0} results'.format(total))

    # copy the archive with outputs
    if outfile:
        if not os.path.isdir('outputs'):
            os.mkdir('outputs')

        from shutil import copyfile
        copyfile(os.path.join(path, outfile), os.path.join('outputs/', outfile))
        print_col('Copied the output: {0}'.format(outputs[0]), 'CYAN')

    # clean the temporary xml files
    for f in bz2xmls:
        os.unlink(f)

    return total

def load_dir(path):
    print("Loading results from {0}".format(path))

    from os import listdir

    xmls = []
    bz2s = []
    outputs = []
    prefixes = set()

    for fl in listdir(path):
        if fl.endswith('.zip'):
            outputs.append(fl)
        elif fl.endswith('.xml'):
            xmls.append(fl)
            prefixes.add(getrundescr(fl))
        elif fl.endswith('.bz2'):
            bz2s.append(fl)
            prefixes.add(getrundescr(fl))

    total = 0
    for (prefix, descr) in prefixes:
        print("Found results for: {0}.{1}".format(prefix, descr))
        total += load_data_with_prefix(path, prefix, xmls, bz2s, outputs, descr)

    return total

def load_xmls(xmls, outputs = None, descr = None,
              append_vers = None, allow_duplicates = False):

    global xmlparser
    if not xmlparser:
        from brv.xml.parser import XMLParser
        xmlparser = XMLParser('database.conf')

    total = 0
    for xmlfile in xmls:
        print_col('Parsing: {0}'.format(xmlfile), 'CYAN')
        cnt = xmlparser.parseToDB(xmlfile, outputs, descr, append_vers, allow_duplicates)
        print('Got {0} results from {1}'.format(cnt, xmlfile))
        total += cnt

    return total

if __name__ == "__main__":
    import sys
    args = parse_cmd()

    if args.results_dir:
        total = load_dir(args.results_dir)
        print_col('Added {0} results in total'.format(total), 'GREEN')
    elif args.files:
        total = load_xmls(args.files, args.outputs, args.description,
                          args.append_vers, args.allow_duplicates)
        print_col('Added {0} results in total'.format(total), "GREEN")

    else:
        if version_info < (3, 0):
            createServer()
        else:
            BRVServer.establish()
