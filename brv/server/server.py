#!/usr/bin/python

import sys
if (sys.version_info > (3, 0)):
    import http.server as httpserver
    import socketserver
else:
    import SimpleHTTPServer as httpserver
    import SocketServer as socketserver

import socket

from .. utils import dbg
from . handler import Handler

class BRVServer(socketserver.TCPServer):
    # redefine server_bind so that we do not have TIME_WAIT issue
    # after closing the connection
    # https://stackoverflow.com/questions/6380057/python-binding-socket-address-already-in-use
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

    def establish(nm = "", port = 3000):
        httpd = BRVServer((nm, port), Handler)
        dbg("Serving at port {0}".format(port))

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.shutdown()
            httpd.server_close()
            # explicitly close the socket
            httpd.socket.close()
            print("Stopping...")
