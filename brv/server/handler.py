#!/usr/bin/python

import sys
if (sys.version_info > (3, 0)):
    from http.server import SimpleHTTPRequestHandler
else:
    from SimpleHTTPServer import SimpleHTTPRequestHandler

from brv.datamanager import DataManager
from .. utils import dbg

try:
    from quik import FileLoader
except ImportError:
    print('Sorry, need quik framework to work.')
    print('Run "pip install quik" or check "http://quik.readthedocs.io/en/latest/"')
    sys.exit(1)

# the tools manager object -- it must be globals,
# since handler is created for each request and we do
# not want to create it again and again
datamanager = DataManager('database.conf')

def _render_template(wfile, name, variables):
    loader = FileLoader('html/templates/')
    template = loader.load_template(name)
    wfile.write(template.render(variables,
                                loader=loader).encode('utf-8'))

def showRoot(wfile, args):
    _render_template(wfile, 'index.html', {'tools' : datamanager.getTools()})

def _parse_args(args):
    opts = {}
    for a in args:
        tmp = a.split('=', 1)
        if len(tmp) != 2:
            print('ERROR: unhandled GET arg: {0}'.format(a))
            continue
        if tmp[0] in opts:
                opts[tmp[0]].append(tmp[1])
        else:
                opts[tmp[0]] = [tmp[1]]

    return opts

def showResults(wfile, args):
    opts = _parse_args(args)
    if not 'run' in opts:
        wfile.write('<h2>No runs of tools given</h2>')
        return

    # list of ToolRunInfo objects
    run_ids = map(int, opts['run'])
    tools = datamanager.getToolRuns(run_ids)
    categories = set()
    for tool in tools:
        tool._stats = datamanager.getToolInfoStats(tool.getID())
        for cat in tool._stats.getBenchmarksSets():
            categories.add(cat)

    cats = [x for x in categories]

    def toolsGETList():
        s = ''
        for x in opts['run']:
            s += '&run={0}'.format(x)
        return s

    def formatStats(run, cat):
        assert not run is None
        assert not cat is None

        stats = run.getStats().getStats(cat).getStats()
        s = ''
        for (classification, cnt) in stats.items():
            s += '{0}: {1}</br>\n'.format(classification, cnt)

        return s

    _render_template(wfile, 'results.html',
                     {'runs':tools, 'categories' : cats,
                      'toolsGETList' : toolsGETList,
                      'formatStats' : formatStats})

def showCategoryResults(wfile, args):
    opts = _parse_args(args)
    if not 'run' in opts:
        wfile.write('<h2>No runs of tools given</h2>')
        return

    if not 'cat' in opts:
        wfile.write('<h2>No category given</h2>')
        return

    _render_template(wfile, 'category_results.html',
                     {'tools':tools, 'results' : results})

def sendStyle(wfile):
    f = open('html/style.css', 'rb')
    wfile.write(f.read())
    f.close()

handlers = {
    'root'              : showRoot,
    'results'           : showResults,
    'category_results'  : showCategoryResults,
    'style.css'         : None, # we handle this specially
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

        global handlers
        if path in handlers.keys():
            return (path, args)
        else:
            return (None, [])

    def _send_headers(self, mimetype = 'text/html'):
        self.send_response(200)
        self.send_header('Content-type', mimetype)
        self.end_headers()

    def do_GET(self):
        act, args = self._parsePath()

        if act is None:
            self._send_headers()
            self.send_error(404, 'Unhandled request')
            print(self.path)
            return
        elif act == 'style.css':
            self._send_headers('text/css')
            sendStyle(self.wfile)
            return

        global handlers
        assert act in handlers.keys()

        self._send_headers()
        handlers[act](self.wfile, args)

