#!/usr/bin/python

from . rendering import render_template
from . util import get_elem, getDescriptionOrVersion
from os.path import basename
from re import compile
import sys

def _getBenchmarkURL(name):
    base='https://github.com/sosy-lab/sv-benchmarks/tree/master'
    try:
        return base + name[name.index('/c/'):]
    except ValueError:
        return None

def _getShortName(name):
    return basename(name)

def None2Empty(s):
    return s if s else ''

def showFiles(wfile, datamanager, opts):
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

    _showDifferent = 'different_only' in opts
    _showIncorrect = 'incorrect' in opts
    _differentTimes10 = 'time_diff_10' in opts
    _differentTimes50 = 'time_diff_50' in opts
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

    if _differentTimes10:
        def time_diff_10(x):
            L = x[1]
            min_x = min(L, key=lambda x: sys.float_info.max if x is None else x.cputime())
            max_x = max(L, key=lambda x: -1 if x is None else x.cputime())
            if min_x.cputime() > 1 and max_x.cputime() > min_x.cputime() * 1.1:
                return True

            return False

        results = filter(time_diff_10, results)

    if _differentTimes50:
        def time_diff_50(x):
            L = x[1]
            min_x = min(L, key=lambda x: sys.float_info.max if x is None else x.cputime())
            max_x = max(L, key=lambda x: -1 if x is None else x.cputime())
            if min_x.cputime() > 1 and max_x.cputime() > min_x.cputime() * 1.5:
                return True

            return False

        results = filter(time_diff_50, results)

    if _showIncorrect:
        def some_incorrect(x):
            L = x[1]
            for r in L:
                if r is not None and r.classification() == 'wrong':
                    return True

            return False

        results = filter(some_incorrect, results)

    if _filter:
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
    if results:
        assert len(runs) == len(results[0][1])
    outputs = [None2Empty(r.outputs()) for r in runs]
    render_template(wfile, 'files.html',
                     {'runs' : runs,
                      'outputs' : outputs,
                      'get' : get_elem,
                      'getBenchmarkURL' : _getBenchmarkURL,
                      'getShortName' : _getShortName,
                      'showDifferent' : _showDifferent,
                      'showIncorrect' : _showIncorrect,
                      'timeDiff10' : _differentTimes10,
                      'timeDiff50' : _differentTimes50,
                      'descr' : getDescriptionOrVersion,
                      'filters' : _filter,
                      'results': results})

