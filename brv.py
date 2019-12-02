#!/usr/bin/python

from sys import version_info, stdout
from argparse import ArgumentParser

if version_info < (3, 0):
    from brv.server.server import createServer
else:
    from brv.server.server import BRVServer

def parse_cmd():
    parser = ArgumentParser()
    parser.add_argument('--tag', default=[], metavar='TAGS', nargs='*',
                        help='Tags to use with the added set of runs')
    parser.add_argument('--db', default='database.conf', metavar='FILE',
                        help='Name of file that contains database configuration')
    parser.add_argument('--outputs', default=None,
                        help='Name of the .zip archive with tool\'s outputs')
    parser.add_argument('--results-dir', default=None, metavar='DIR',
                        help='Load results (.zip and .xml/bz2 files) from DIR')
    parser.add_argument('--svcomp', nargs='*', default=None, metavar='FILES',
                        help='Download and import results from SV-COMP emails')
    parser.add_argument('--description', default=None,
                        help='Description of the run given in xml files')

    parser.add_argument('--append-vers', default=None,
                        help='Append the given string to the version of the tool. Can be used to store another run on the same version and distinguish it')
    parser.add_argument('--allow-duplicates', action='store_true', default=False,
                        help='Store also results that we already have')
    parser.add_argument('files', nargs="*", metavar="FILES",
                        help="XML files. If given, no server is run and the files are parsed and stored to dtabase")
    return parser.parse_args()

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

def create_parser(config_file):
    from brv.xml.parser import XMLParser
    parser = XMLParser(config_file)
    return parser

def add_from_dir(args):
    from brv.importer.dir import load_dir
    parser = create_parser(args.db)
    return load_dir(parser, args.results_dir, args.description, args.append_vers, args.allow_duplicates, args.tag)

def add_from_files(args):
    from brv.importer.xml import load_xmls
    parser = create_parser(args.db)
    return load_xmls(parser, args.files, args.outputs, args.description,
                      args.append_vers, args.allow_duplicates, args.tag)

def add_from_svcomp(args):
    from brv.importer.svcomp import load_svcomp
    parser = create_parser(args.db)
    return load_svcomp(parser, args.svcomp, args.description, args.append_vers, args.allow_duplicates, args.tag)

def start_server(args):
    if version_info < (3, 0):
        createServer()
    else:
        BRVServer.establish()

def create_importer(args):
    if args.results_dir:
        return add_from_dir
    elif args.files:
        return add_from_files
    elif args.svcomp:
        return add_from_svcomp

    return None

def tag_runs(toolrun_ids, args):
    if not args.tag:
        return

    from brv.database.writer import DatabaseWriter

    db = DatabaseWriter(args.db)
    tags_str = ';'.join(args.tag)
    for trid in toolrun_ids:
        db.setToolRunTags(trid, tags_str)

    db.commit()
    print_col('Tagged {0} tool runs using {1}'.format(len(toolrun_ids), ','.join(args.tag)), "GREEN") 

def perform_import(args):
    importer = create_importer(args)
    total, toolrun_ids = importer(args)

    print_col('Added {0} results in total'.format(total), "GREEN")
    tag_runs(toolrun_ids, args)

def is_importing_results(args):
    return args.results_dir or args.files or args.svcomp

if __name__ == "__main__":
    import sys
    args = parse_cmd()

    if is_importing_results(args):
        perform_import(args)
    else:
        start_server(args)
