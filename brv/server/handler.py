from os.path import join, isfile

from http.server import SimpleHTTPRequestHandler
from urllib.parse import unquote

from .. datamanager import DataManager

from . showfiles import showFiles
from . showfilter import showFilter
from . showtools import showTools
from . showresults import showResults
from . showoutput import showOutput
from . showdiagram import showDiagram
from . showoverall import showOverall
from . manage import manageTools, performDelete, setToolRunAttr, adjustEnviron

# the tools manager object -- it must be globals,
# since handler is created for each request and we do
# not want to create it again and again
datamanager = DataManager('database.conf')

def _parse_args(args):
    opts = {}
    for a in args:
        tmp = a.split('=', 1)
        if len(tmp) != 2:
            print('ERROR: unhandled GET arg: {0}'.format(a))
            continue

        arg = unquote(tmp[1])
        opts.setdefault(tmp[0], []).append(arg)

    return opts

def sendFile(wfile, path):
    f = open(path, 'rb')
    wfile.write(f.read())
    f.close()

handlers = {
    'root'              : showTools,
    'results'           : showResults,
    'diagram'           : showDiagram,
    'overall'           : showOverall,
    'files'             : showFiles,
    'filter'            : showFilter,
    'manage'            : manageTools,
    'delete'            : performDelete,
    'output'            : showOutput,
    'set'               : setToolRunAttr,
    'env'               : adjustEnviron,
}

# see http://www.acmesystems.it/python_httpd
class Handler(SimpleHTTPRequestHandler):
    def _parsePath(self):
        args = []

        tmp = self.path.split('?')
        path = None
        if len(tmp) == 2:
            path = tmp[0].strip()
            args = tmp[1].split('&')
        elif len(tmp) == 1:
            path = tmp[0]

        if not path:
            return (None, [])

        if path == '' or path == '/':
            return ('root', args)
        else:
            path = path[1:]

        return (path, args)

    def _send_headers(self, mimetype = 'text/html'):
        self.send_response(200)
        self.send_header('Content-type', mimetype)
        self.end_headers()

    def _get_handler(self, path):
        global handlers
        return handlers.get(path)

    def _handle_files(self, path):
        if path == 'style.css':
            self._send_headers('text/css')
            sendFile(self.wfile, 'html/style.css')
            return True
        elif path == 'js/brv.js':
            self._send_headers('text/javascript')
            sendFile(self.wfile, 'html/js/brv.js')
            return True
        elif path.endswith('.gif'):
            epath = join('html/', path)
            if isfile(epath):
                self._send_headers('image/gif')
                sendFile(self.wfile, epath)
                return True
            return False

        return False

    def do_GET(self):
        act, args = self._parsePath()
        handler = self._get_handler(act)

        if handler is None:
            if self._handle_files(act):
                # it was a file, we're fine
                return

            self._send_headers()
            self.send_error(404, 'Unhandled request')
            print(self.path)
            return

        self._send_headers()
        opts = _parse_args(args)
        handler(self.wfile, datamanager, opts)

