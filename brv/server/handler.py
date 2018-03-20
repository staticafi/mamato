#!/usr/bin/python

import sys
from os.path import basename, join, isfile
from math import ceil, floor
from re import compile

if (sys.version_info > (3, 0)):
    from http.server import SimpleHTTPRequestHandler
    from urllib.parse import unquote
else:
    from urllib import unquote
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

def getDescriptionOrVersion(toolr):
    descr = toolr.run_description()
    if descr is None:
        return toolr.tool_version()
    else:
        return descr

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

def _get(p, idx):
    return p[idx]

def showRoot(wfile, args):
    def _setSize(lst):
        sz = 0
        for (x, tr) in lst:
            sz += len(tr)
        return "size=15" if sz > 10 else "size=10" if sz > 5 else ""

    def _run_details(run):
        d = ''
        if run.options():
            d += run.options()

        d += ' ; {0}, {1:2} GB'.format(run.timelimit(), int(run.memlimit())/(10**9))
        return d

    def _getTags(run):
        return datamanager.getToolRunTags(run)

    opts = _parse_args(args)
    _filter = opts.setdefault('filter', [])
    _tags_filter = opts.setdefault('tags-filter', [])

    filters = []
    tags_filters = []
    for f in _filter:
        try:
            rf = compile(f)
            filters.append((f, lambda x : rf.search(x)))
        except Exception as e:
            print('ERROR: Invalid regular expression given in filter: ' + str(e))

    for f in _tags_filter:
        try:
            rf = compile(f)
            tags_filters.append((f, lambda x : rf.search(x)))
        except Exception as e:
            print('ERROR: Invalid regular expression given in filter: ' + str(e))

    if filters or tags_filters:
        def _runs_filter(run):
            descr = run.run_description() if run.run_description() else ''
            for (_, f) in filters:
                if f(descr) is None:
                    return False

            tags = run.tags() if run.tags() else ''
            for (_, f) in tags_filters:
                if f(tags) is None:
                    return False

            return True
    else:
        _runs_filter = None

    tools = datamanager.getTools()
    tools_sorted = {}
    for t in tools:
        # tools is a list of tool runs where each of the
        # tools has a unique name+version+options attributes
        # We want to divide them to groups according to names
        # and versions. So we have a mapping name -> version -> tools
        nkey = tools_sorted.setdefault(t.name(), {})
        nkey.setdefault(t.version(), []).append(t)

    tools_final = []
    for (name, tls) in tools_sorted.items():
        tools_final.append((name, list(tls.items())))

    def _nonempty_list(l):
        return l != []

    _render_template(wfile, 'index.html',
                     {'tools' : tools_final,
                      'get' : _get,
                      'setSize' : _setSize,
                      'getTags' : _getTags,
                      'run_details' : _run_details,
                      'runs_filter' : _runs_filter,
                      'filters' : _filter,
                      'tags_filters' : _tags_filter,
                      'nonempty_list': _nonempty_list,
                      'descr' : getDescriptionOrVersion})


def showResults(wfile, args):
    opts = _parse_args(args)
    if not 'run' in opts:
        wfile.write(b'<h2>No runs of tools given</h2>')
        return

    class BSet(object):
        def __init__(self, name, bid):
            self.name = name
            self.id = bid

        def __hash__(self):
            return self.id

        def __eq__(self, oth):
            return self.id == oth.id

    _showTimes = 'show_times' in opts
    _showTimesOnlySolved = 'show_times_only_solved' in opts
    groupingId = 0
    if 'grouping' in opts:
        groupingId = int(opts['grouping'][0])
    grouping = datamanager.getGrouping(groupingId)
    if grouping is None:
        grouping = datamanager.getGrouping(0)
    buckets = grouping.getBuckets()
    # list of ToolRun objects
    run_ids = list(map(int, opts['run']))
    runs = datamanager.getToolRuns(run_ids)
    categories = set()
    # there's few of classifications usually, it will be faster in list
    classifications = []
    classifications_types = []
    for run in runs:
        run._stats = datamanager.getToolInfoStats(run.getID())
        for stats in run._stats.getAllStats().values():
            stats.accumulateTime(_showTimesOnlySolved)
            stats.prune()
            # a pair (name, id)
            categories.add(BSet(stats.getBenchmarksName(), stats.getBenchmarksID()))
            for c in stats.getClassifications():
                if c not in classifications:
                    classifications.append(c)

    # give it some fixed order
    cats = [x for x in categories]

    def _toolsGETList():
        s = ''
        for x in opts['run']:
            s += '&run={0}'.format(x)
        return s

    def _getStats(run, bset_id):
        assert not run is None
        assert not bset_id is None

        return run.getStats().getStatsByID(bset_id)

    def _getCount(stats, classif):
        if stats:
            return stats.getCount(classif)
        else:
            return 0

    def _getTime(stats, classif):
        if stats:
            return ceil(stats.getTime(classif))
        else:
            return 0

    def _getBucketTime(stats, bucket):
        if stats:
            result = 0
            for classif in bucket.getClassifications():
                result += _getTime(stats, classif)
            return result
        else:
            return 0

    def _getTotalStats(run):
        assert not run is None

        return run.getStats().getSummary(_showTimesOnlySolved)

    def _hasAnswers(runs, bset_id, classif):
        assert not runs is None
        assert not bset_id is None

        for run in runs:
            if bset_id != -1:
                # get stats for one of the categories
                stats = run.getStats().getStatsByID(bset_id)
            else:
                # get the overall stats
                stats = run.getStats().getSummary(_showTimesOnlySolved)
            if not stats is None and stats.getCount(classif) != 0:
                return True

        return False

    def _bucketHasAnswers(runs, bset_id, bucket):
        classifs = bucket.getClassifications()
        for classif in classifs:
            if _hasAnswers(runs, bset_id, classif):
                return True
        return False

    def _formatTime(time):
        "Transform time in seconds to hours, minutes and seconds"
        if not time:
            return '0 s'
        ret = ''
        time = ceil(time)
        if time >= 3600:
            hrs = time // 3600
            time = time - hrs*3600
            ret = '{0} h'.format(int(hrs))
        if time >= 60 or ret != '':
            mins = time // 60
            time = time - mins*60
            ret += ' {0} min'.format(int(mins))
        if ret != 0:
            return ret + ' {0} s'.format(int(time))
        else:
            return ret + '{0} s'.format(int(time))

    #def _tagsToCSS(tags):

    _render_template(wfile, 'results.html',
                     {'runs':runs, 'benchmarks_sets' : cats,
                      'toolsGETList' : _toolsGETList,
                      'getStats' : _getStats,
                      'getTotalStats' : _getTotalStats,
                      'hasAnswers': _hasAnswers,
                      'bucketHasAnswers': _bucketHasAnswers,
                      'getCount' : _getCount,
                      'getTime' : _getTime,
                      'getBucketTime' : _getBucketTime,
                      'get' : _get,
                      'showTimes' : _showTimes,
                      'showTimesOnlySolved' : _showTimesOnlySolved,
                      'formatTime' : _formatTime,
                      'descr' : getDescriptionOrVersion,
                      'classifications' : classifications,
                      'buckets': buckets,
                      'groupingId': groupingId,
                      'groupings': datamanager.getGroupingChoices() })


def manageTools(wfile, args):
    tools = datamanager.getTools()
    tools_sorted = {}
    for t in tools:
        # tools is a list of tool runs where each of the
        # tools has a unique name+version+options attributes
        # We want to divide them to groups according to names
        # and versions. So we have a mapping name -> version -> tools
        nkey = tools_sorted.setdefault(t.name(), {})
        nkey.setdefault(t.version(), []).append(t)
    tools_final = []
    for t in tools_sorted.items():
        tools_final.append((t[0], list(t[1].items())))

    def _none2Empty(x):
        return x if x else ''

    tags_config_file = open('brv/tags.conf')
    tags_config = tags_config_file.readlines()

    tags = list(datamanager.tagsmanager.getTags())

    _render_template(wfile, 'manage.html',
                     {'tools' : tools_final,
                      'None2Empty': _none2Empty,
                      'get' : _get,
                      'tags': tags,
                      'tags_config': tags_config,
                      'descr' : getDescriptionOrVersion})

    tags_config_file.close()

def performDelete(wfile, args):
    opts = _parse_args(args)

    # XXX: this should be done in datamanager

    run_ids = list(map(int, opts['run']))
    runs = datamanager.getToolRuns(run_ids)

    print("Deleting tool runs '{0}'".format(str(runs)))
    datamanager.deleteToolRuns(runs)

def setToolRunAttr(wfile, args):
    opts = _parse_args(args)

    _tags_config = 'tags_config' in opts
    if _tags_config:
       tags_config = open('brv/tags.conf', 'w')
       tags_config.write(opts['tags_config'][0])
       tags_config.close()
       datamanager.tagsmanager.reloadTags()

       return

    if len(opts['run']) != 1:
        print('Incorrect number of tools')
        return

    run_id = int(opts['run'][0])

    _descr = 'description' in opts
    _tags = 'tags' in opts
    if _descr:
        assert len(opts['description']) == 1
        descr = opts['description'][0]
        datamanager.setToolRunDescription(run_id, descr)
    if _tags:
        assert len(opts['tags']) == 1
        tags = opts['tags'][0]
        datamanager.setToolRunTags(run_id, tags)

def showFiles(wfile, args):
    opts = _parse_args(args)
    if not 'run' in opts:
        wfile.write(b'<h2>No runs of tools given</h2>')
        return

    if not 'benchmarks' in opts:
        wfile.write(b'<h2>No benchmarks to show given</h2>')
        return

    run_ids = list(map(int, opts['run']))
    run_ids.sort()
    runs = datamanager.getToolRuns(run_ids)

    try:
        bset_id = int(opts['benchmarks'][0])
    except ValueError or KeyError:
        wfile.write(b'<h2>Invalid benchmarks</h2>')
        return

    def _getBenchmarkURL(name):
        base='https://github.com/sosy-lab/sv-benchmarks/tree/master'
        try:
            return base + name[name.index('/c/'):]
        except ValueError:
            return None

    def _getShortName(name):
        return basename(name)

    _showDifferent = 'different_only' in opts
    _filter = opts.setdefault('filter', [])

    results = datamanager.getRunInfos(bset_id, run_ids).getRows().items()
    if _showDifferent:
        def some_different(x):
            L = x[1]
            if L[0] is None:
                status = None
            else:
                status = L[0].status()

            for r in L:
                if r is None:
                    if status is not None:
                        return True
                elif r.status() != status:
                    return True

            return False

        results = filter(some_different, results)

    if _filter:
        from re import compile
        filters = []
        for f in _filter:
            try:
                rf = compile(f)
            except Exception as e:
                print('ERROR: Invalid regular expression given in filter: ' + str(e))
                continue
            filters.append((f, lambda x : rf.search(x)))

        for (pattern, f) in filters:
            def match(x):
                L = x[1]
                for r in L:
                    if r and f(r.status()):
                        return True
                return False

            print('Applying {0}'.format(pattern))
            results = filter(match, results)

    results = list(results)
    assert len(runs) == len(results[0][1])
    _render_template(wfile, 'files.html',
                     {'runs' : runs,
                      'get' : _get,
                      'getBenchmarkURL' : _getBenchmarkURL,
                      'getShortName' : _getShortName,
                      'showDifferent' : _showDifferent,
                      'descr' : getDescriptionOrVersion,
                      'filters' : _filter,
                      'results': results})

def sendFile(wfile, path):
    f = open(path, 'rb')
    wfile.write(f.read())
    f.close()

handlers = {
    'root'              : showRoot,
    'results'           : showResults,
    'files'             : showFiles,
    'manage'            : manageTools,
    'delete'            : performDelete,
    'set'               : setToolRunAttr,
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
        handler(self.wfile, args)

