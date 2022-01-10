from . rendering import render_template
from . util import get_elem, getDescriptionOrVersion, getBenchmarkURL, getShortName
from re import compile
import sys

def None2Empty(s):
    return s if s else ''

def showFilter(wfile, datamanager, opts):
    if not 'run' in opts:
        wfile.write(b'<h2>No runs of tools given</h2>')
        return

    if not 'bucket' in opts:
        wfile.write(b'<h2>No buckets of results given</h2>')
        return

    if not 'grouping' in opts:
        wfile.write(b'<h2>No grouping given</h2>')
        return

    grouping = datamanager.getGrouping(int(opts['grouping'][0]))
    buckets = grouping.getBuckets()

    run_ids = list(map(int, opts['run']))
    bucket_names = list(opts['bucket'])

    run_bucket = {}
    for (run_id, bucket_name) in zip(run_ids, bucket_names):
        run_bucket[run_id] = bucket_name

    runs = datamanager.getToolRuns(run_ids)
    # sort the runs according to their ID's,
    # (and sort also the ID's)
    # so that we have always the same order
    # in the header and in the results
    run_ids.sort()
    sorted(runs, key=lambda r : r.getID())

    _showDifferentStatus = 'different_status' in opts
    _showDifferentClassif = 'different_classif' in opts
    _showIncorrect = 'incorrect' in opts
    _differentTimes10 = 'time_diff_10' in opts
    _differentTimes50 = 'time_diff_50' in opts
    _filter = opts.setdefault('filter', [])

    # list of tuples (bset, RunInfosTable)
    output_tables = []
    bsets = datamanager.getBenchmarksSets()
    # the filtering must be done by category
    for bset in bsets:
        results = datamanager.getRunInfos(bset.id, run_ids).getRows().items()

        if _showDifferentStatus:
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

        def correct_buckets(x):
            L = x[1]
            stay = True
            for r, run_id in zip(L, run_ids):
                if r is None:
                    return False
                desired_bucket_name = run_bucket[run_id]
                sc = (r.status(), r.classification())
                found = False
                for bucket in buckets:
                    if sc in bucket.getClassifications() and bucket.getDisplayName() == desired_bucket_name:
                        found = True
                stay = stay and found
            return stay
        results = filter(correct_buckets, results)
        results = list(results)
        if results:
            assert len(runs) == len(results[0][1])
        if len(results) > 0:
            output_tables.append((bset, results))

    outputs = [None2Empty(r.outputs()) for r in runs]
    render_template(wfile, 'filter.html',
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
                      'outputTables': output_tables})

