#!/usr/bin/python

import sys
if (sys.version_info > (3, 0)):
    import http.server
else:
    import SimpleHTTPServer
    import SocketServer

import os
import socket

from result import RunInfo
from tools import ToolResult, ToolsManager, DirectJoinedToolResults

try:
    from quik import FileLoader
except ImportError:
    print('Sorry, need quik framework to work.')
    print('Run "pip install quik" or check "http://quik.readthedocs.io/en/latest/"')
    sys.exit(1)

PORT = 3000
tm = ToolsManager(sys.argv[1:])

def _render_template(wfile, name, variables):
    loader = FileLoader('html/templates/')
    template = loader.load_template(name)
    wfile.write(template.render(variables,
                                loader=loader).encode('utf-8'))

def showRoot(wfile, tm, args):
    _render_template(wfile, 'index.html', {'tools' : tm.getTools()})

def _parse_args(args):
    opts = {}
    for a in args:
        tmp = a.split('=', 1)
        if len(tmp) != 2:
            print('ERROR: unhandled GET arg: {0}'.format(a))
            continue
        if opts.has_key(tmp[0]):
                opts[tmp[0]].append(tmp[1])
        else:
                opts[tmp[0]] = [tmp[1]]

    return opts

def showResults(wfile, tm, args):
    opts = _parse_args(args)
    if not opts.has_key('tool'):
        wfile.write('<h2>No tool given</h2>')
        return

    tools = tm.getTools(map(int, opts['tool']))
    categories = set()
    for tool in tools:
        for r in tool.getResults():
            categories.add(r.block)
    cats = [x for x in categories]

    def toolsGETList():
        s = ''
        for x in opts['tool']:
            s += '&tool={0}'.format(x)
        return s

    _render_template(wfile, 'results.html',
                     {'tools':tools, 'categories' : cats,
                      'toolsGETList' : toolsGETList})

def showCategoryResults(wfile, tm, args):
    opts = _parse_args(args)
    if not opts.has_key('tool'):
        wfile.write('<h2>No tool given</h2>')
        return

    if not opts.has_key('cat'):
        wfile.write('<h2>No category given</h2>')
        return

    tools = tm.getTools(map(int, opts['tool']))
    results = DirectJoinedToolResults()
    cat = opts['cat']
    for t in tools:
        print('Join', t)
        for r in t.getResults():
            print('    -> ', r.block, cat)
            if r.block == cat[0]:
                print('  Join', cat, r)
                results.join(r)
                # break the inner loop
                break;

    results.dump()
    _render_template(wfile, 'category_results.html',
                     {'tools':tools, 'results' : results})

def sendStyle(wfile):
    f = open('html/style.css')
    wfile.write(f.read())
    f.close()

handlers = {
    'root'              : showRoot,
    'results'           : showResults,
    'category_results'  : showCategoryResults,
    'style.css'         : None, # we handle this specially
}

# see http://www.acmesystems.it/python_httpd
class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
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
        global tm
        assert act in handlers.keys()

        self._send_headers()
        handlers[act](self.wfile, tm, args)

# redefine server_bind so that we do not have TIME_WAIT issue
# after closing the connection
# https://stackoverflow.com/questions/6380057/python-binding-socket-address-already-in-use
class Server(SocketServer.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

httpd = Server(("", PORT), Handler)

print("Serving at port", PORT)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    httpd.shutdown()
    httpd.server_close()
    # explicitly close the socket
    httpd.socket.close()
    print("Stopping...")
