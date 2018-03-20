#!/usr/bin/python

from . rendering import render_template
from . util import get_elem, getDescriptionOrVersion
from re import compile

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

def showTools(wfile, datamanager, opts):
    def _getTags(run):
        return datamanager.getToolRunTags(run)

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

    render_template(wfile, 'index.html',
                     {'tools' : tools_final,
                      'get' : get_elem,
                      'setSize' : _setSize,
                      'getTags' : _getTags,
                      'run_details' : _run_details,
                      'runs_filter' : _runs_filter,
                      'filters' : _filter,
                      'tags_filters' : _tags_filter,
                      'nonempty_list': _nonempty_list,
                      'descr' : getDescriptionOrVersion})


