#!/usr/bin/python

from os import unlink
from . rendering import render_template
from . util import get_elem, getDescriptionOrVersion

from zipfile import ZipFile

def showOutput(wfile, datamanager, args):
    outputs_dir = 'outputs/'

    archive = args.get('arch')
    assert archive and len(archive) == 1
    name = args.get('file')
    assert name and len(name) == 1

    archive = archive[0]
    name = name[0]


    try:
        zip_ref = ZipFile(outputs_dir + archive, "r")
        try:
            # the file name is archive name (without .zip) + the name
            filename = '{0}/{1}'.format(archive[:-4], name)
            path = zip_ref.extract(filename, path='/tmp')
        except KeyError as e:
            wfile.write(str(e).encode('utf-8'))
            zip_ref.close()
            return

        zip_ref.close()

        print('Got file ' + name)
        output_file = open(path, 'rb')
        wfile.write(output_file.read())
        output_file.close()
        unlink(path)
    except IOError as e:
        wfile.write(str(e).encode('utf-8'))

