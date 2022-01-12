from . rendering import render_template
from . util import get_elem, getDescriptionOrVersion, getBenchmarkURL, getShortName
from os.path import basename
from re import compile
import sys

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
    runs = datamanager.getToolRuns(run_ids)
    # sort the runs according to their ID's,
    # (and sort also the ID's)
    # so that we have always the same order
    # in the header and in the results
    run_ids.sort()
    sorted(runs, key=lambda r : r.getID())

    try:
        bset_id = int(opts['benchmarks'][0])
    except ValueError or KeyError:
        wfile.write(b'<h2>Invalid benchmarks</h2>')
        return

    _showDifferentStatus = 'different_status' in opts
    _showDifferentClassif = 'different_classif' in opts
    _showIncorrect = 'incorrect' in opts
    _differentTimes10 = 'time_diff_10' in opts
    _differentTimes50 = 'time_diff_50' in opts
    _filter = opts.setdefault('filter', [])

    results = datamanager.getRunInfos(bset_id, run_ids).getRows().items()

    bsets = datamanager.getBenchmarksSets()
    bset = None

    for bs in bsets:
        if bs.id == bset_id:
            bset = bs

    if _showDifferentStatus:
        def some_different(x):
            L = x[1]
            if L[0] is None:
                status = None
                classification = None
            else:
                status = L[0].status()
                classification = L[0].classification()

            for r in L:
                if r is None:
                    if status is not None:
                        return True
                    if classification is not None:
                        return True
                elif r.status() != status:
                    return True
                elif r.classification() != classification:
                    return True

            return False

        results = filter(some_different, results)

    if _showDifferentClassif:
        def some_different(x):
            L = x[1]
            if L[0] is None:
                classif = None
            else:
                classif = L[0].classification()

            for r in L:
                if r is None:
                    if classif is not None:
                        return True
                elif r.classification() != classif:
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

    results = sorted(list(results), key=lambda x: basename(x[0]))
    if results:
        assert len(runs) == len(results[0][1])
    outputs = [None2Empty(r.outputs()) for r in runs]
    render_template(wfile, 'files.html',
                     {'runs' : runs,
                      'outputs' : outputs,
                      'get' : get_elem,
                      'getBenchmarkURL' : getBenchmarkURL,
                      'getShortName' : getShortName,
                      'showDifferentStatus' : _showDifferentStatus,
                      'showDifferentClassif' : _showDifferentClassif,
                      'showIncorrect' : _showIncorrect,
                      'timeDiff10' : _differentTimes10,
                      'timeDiff50' : _differentTimes50,
                      'descr' : getDescriptionOrVersion,
                      'filters' : _filter,
                      'bset': bset,
                      'results': results})

