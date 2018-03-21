#!/usr/bin/python

from . rendering import render_template
from . util import get_elem, getDescriptionOrVersion
from os.path import basename
from re import compile

def _getBenchmarkURL(name):
    base='https://github.com/sosy-lab/sv-benchmarks/tree/master'
    try:
        return base + name[name.index('/c/'):]
    except ValueError:
        return None

def _getShortName(name):
    return basename(name)

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
    render_template(wfile, 'files.html',
                     {'runs' : runs,
                      'get' : get_elem,
                      'getBenchmarkURL' : _getBenchmarkURL,
                      'getShortName' : _getShortName,
                      'showDifferent' : _showDifferent,
                      'descr' : getDescriptionOrVersion,
                      'filters' : _filter,
                      'results': results})
