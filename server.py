#!/usr/bin/python

import SimpleHTTPServer
import SocketServer
import socket

import sys, os
from result import RunInfo
from tools import ToolResult, ToolsManager

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
        if opts.has_key(tmp[0]):
                opts[tmp[0]].append(tmp[1])
        else:
                opts[tmp[0]] = [tmp[1]]

    return opts

def showResults(wfile, tm, args):
    opts = _parse_args(args)
    tools = tm.getTools(map(int, opts['tool']))
    _render_template(wfile, 'results.html', {'tools':tools})

handlers = {
    'root'       : showRoot,
    'results'    : showResults,
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

    def _send_headers(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

    def do_GET(self):
        self._send_headers()

        act, args = self._parsePath()
        if act is None:
            self.send_error(404, 'Unhandled request')
            print(self.path)
            return

        global handlers
        assert act in handlers.keys()
        print('DBG', act, args)
	global tm
        handlers[act](self.wfile, tm, args)

# redefine server_bind so that we do not have TIME_WAIT issue
# after closing the connection
# https://stackoverflow.com/questions/6380057/python-binding-socket-address-already-in-use
class Server(SocketServer.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

httpd = Server(("", PORT), Handler)

print("serving at port", PORT)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    httpd.shutdown()
    httpd.server_close()
    # explicitly close the socket
    httpd.socket.close()
    print("Stopping...")
