#!/usr/bin/python

import SimpleHTTPServer
import SocketServer
import socket

import sys, os
from result import Result, ToolRun
from resultsparser import parse_xml

PORT = 3000

def showTools(wfile, args):
  pass

def showTools2(wfile, tools):
    wfile.write('<form action="/results">\n')
    idx = 0
    wfile.write('  <select name="tool" multiple="multiple">\n')

    for toolrun in tools:
        print(toolrun)
        wfile.write('    <option value="{0}">\n'.format(idx, toolrun.tool))
        wfile.write('      <table><tr><td>{0}</td><td>{1}</td><td>{2}</td></tr></table>\n'.format(toolrun.tool,\
                    toolrun.tool_version[:24], toolrun.date[:24]))
        wfile.write('    </option>\n')
        idx += 1

    wfile.write('  </select>\n')
    wfile.write('  </br>\n')
    wfile.write('  <input type="submit">\n')
    wfile.write('</form>\n')

def showRoot(wfile, args):
    tools = []
    for xml in sys.argv[1:]:
        tools.append(parse_xml(xml))
    showTools2(wfile, tools)

def showCmpResults(wfile, args):
    opts = {}

    for a in args:
        tmp = a.split('=', 1)
        opts[tmp[0]] = tmp[1]
    print(opts)

    wfile.write("""
    <form action="cmpresults">
    Tool 1 (id): <input type="text" name="tool1"</br>
    Tool 2 (id): <input type="text" name="tool2"</br>
    Category (id): <input type="text" name="category"</br>
    Only results: <input type="text" name="only_results"</br>
    Only different: <input type="checkbox" name="only_different"</br>
    <input type="submit" value="Show!">
    </form></br></br>
    """)

    # without options just show the form
    if not opts:
        return True

    try:
        q = """
        SELECT tasks.name, t1.result, t1.output, t2.result, t2.output,
               t1.is_correct, t2.is_correct
        FROM task_results as t1 JOIN task_results as t2
          ON t1.task_id = t2.task_id JOIN tasks ON t1.task_id = tasks.id
        WHERE t1.tool_id={0} AND t2.tool_id={1}
        """.format(opts['tool1'], opts['tool2'])

        if opts.has_key('only_different') and opts['only_different'] == 'on':
            q += ' AND t1.result != t2.result'

        if opts.has_key('category'):
            res = opts['category']
            if res != '':
                q +=  "AND category_id={0}".format(res)

        if opts.has_key('only_results'):
            res = opts['only_results']
            if res != '':
                q += ' AND (t1.result = "{0}" or t2.result = "{1}")'\
                     .format(res, res)
    except KeyError:
        wfile.write('Wrong arguments!')
        return False

    rolling = """
    <style>
        .rolled {
            overflow:hidden;
            height:20px;
        }

        .unrolled {
            height: 100%;
        }
    </style>
    <script>
    function toggleRolling(div) {
      var className = div.getAttribute("class");
      if(className=="rolled") {
        div.className = "unrolled";
      }
      else{
        div.className = "rolled";
      }
    }
    </script>
    """;
    wfile.write(rolling);

    res = db.query(q)
    wfile.write('<table>\n')
    for r in res:
        wfile.write('<tr>')
        i = 0
        for t in r:
            if i > 4:
                break

            style='border-bottom: 1px solid black; padding: 4px;'
            brlines = False

            if i == 0 or i == 2:
                style += ' border-right: 1px solid black;'

            if i == 2 or i == 4:
                style += ' font-size: 65%;'
                brlines = True

            if i == 1 or i == 3:
                if t == 'unknown':
                    style += ' color: orange'
                elif t in ['false', 'true']:
                    if i == 1:
                        is_correct = int(r[5])
                    else:
                        is_correct = int(r[6])

                    if is_correct == 1:
                        style += ' color: green;'
                    else:
                        style += ' background-color: red;'

            if style == '':
                wfile.write('<td>')
            else:
                wfile.write('<td style="{0}">'.format(style))


            if i == 0:
                wfile.write('<a href="https://github.com/sosy-lab/sv-benchmarks/blob/master/c/{0}"\
                              target="blank">{1}</a>'.format(t, t))
            elif brlines:
                lines = t.splitlines()
                wfile.write('<div class="rolled" onclick="toggleRolling(this)">')
                for l in lines:
                    wfile.write(l)
                    wfile.write('</br>\n')
                wfile.write('</div>')
            else:
                wfile.write(t)

            wfile.write('</td>')
            i += 1
        wfile.write('</tr>\n')

    wfile.write('</table>\n')

    return True

def showResults(wfile, args):
    opts = {}

    for a in args:
        tmp = a.split('=', 1)
        opts[tmp[0]] = tmp[1]
    print(opts)

    wfile.write("""
    <form action="results">
    Tool 1 (id): <input type="text" name="tool1"</br>
    Category (id): <input type="text" name="category"</br>
    Only results: <input type="text" name="only_results"</br>
    <input type="submit" value="Show!">
    </form></br></br>
    """)

    # without options just show the form
    if not opts:
        return True

    try:
        q = """
        SELECT tasks.name, t1.result, t1.output, t1.is_correct
        FROM task_results as t1 JOIN tasks ON tasks.id = t1.task_id
        WHERE t1.tool_id={0}
        """.format(opts['tool1'])

        if opts.has_key('category'):
            res = opts['category']
            if res != '':
                q +=  "AND category_id={0}".format(res)

        if opts.has_key('only_results'):
            res = opts['only_results']
            if res != '':
                q += ' AND (t1.result = "{0}")'.format(res, res)
    except KeyError:
        wfile.write('Wrong arguments!')
        return False

    rolling = """
    <style>
        .rolled {
            overflow:hidden;
            height:20px;
        }

        .unrolled {
            height: 100%;
        }
    </style>
    <script>
    function toggleRolling(div) {
      var className = div.getAttribute("class");
      if(className=="rolled") {
        div.className = "unrolled";
      }
      else{
        div.className = "rolled";
      }
    }
    </script>
    """;
    wfile.write(rolling);

    res = db.query(q)
    wfile.write('<p>Got {0} results:</p>'.format(len(res)))
    wfile.write('<table>\n')
    for r in res:
        wfile.write('<tr>')
        i = 0
        for t in r:
            if i > 4:
                break

            style='border-bottom: 1px solid black; padding: 4px;'
            brlines = False

            if i == 0:
                style += ' border-right: 1px solid black;'

            if i == 2:
                style += ' font-size: 65%;'
                brlines = True

            if i == 1:
                if t == 'unknown':
                    style += ' color: orange'
                elif t in ['false', 'true']:
                    is_correct = int(r[3])

                    if is_correct == 1:
                        style += ' color: green;'
                    else:
                        style += ' background-color: red;'

            if style == '':
                wfile.write('<td>')
            else:
                wfile.write('<td style="{0}">'.format(style))


            if i == 0:
                wfile.write('<a href="https://github.com/sosy-lab/sv-benchmarks/blob/master/c/{0}"\
                              target="blank">{1}</a>'.format(t, t))
            elif brlines:
                lines = t.splitlines()
                wfile.write('<div class="rolled" onclick="toggleRolling(this)">')
                for l in lines:
                    wfile.write(l)
                    wfile.write('</br>\n')
                wfile.write('</div>\n')
            else:
                wfile.write(t)

            wfile.write('</td>')
            i += 1
        wfile.write('</tr>\n')

    wfile.write('</table>\n')

    return True



handlers = {
    'root'       : showRoot,
    'tools'      : showTools,
    'results'    : showResults,
    'cmpresults' : showCmpResults,
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
        handlers[act](self.wfile, args)

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
