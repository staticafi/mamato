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

    d += ' ; {0}, {1:2} GB'.format(run.timelimit(), int(run.memlimit().replace('B', ''))/(10**9))
    return d

def _nonempty_list(l):
    return l != []

def sortToolRuns(truns):
    def _toolRunKey(tr):
        return tr.date()

    return sorted(truns, key=_toolRunKey, reverse=True)

def isIn(lst, elm):
    return elm in lst

def makeKeys(key, vals):
    return list(map(lambda x : '{0}={1}'.format(key, x), vals))

def URIjoin(lst):
    return '&'.join(lst)

def sortToolVersions(vers):
    def _key(r):
        return r[0]

    return sorted(vers, key=_key, reverse=True)

def prepareToolsMap(tools, runs_filter, sort_method):
    if sort_method == 'version':
        tools_grouped = {}
        for t in tools:
            # tools is a list of tool runs where each of the
            # tools has a unique name+version+options attributes
            # We want to divide them to groups according to names
            # and versions. So we have a mapping name -> version -> tools
            nkey = tools_grouped.setdefault(t.name(), {})
            nkey.setdefault(t.version(), []).append(t)

        tools_final = []
        for (name, tls) in tools_grouped.items():
            tools_final.append((name, list(sortToolVersions(tls.items()))))

        tools_final.sort(key=lambda t: t[0])
        return tools_final

    elif sort_method == 'date':
        tools_grouped = {}
        for t in tools:
            # tools is a list of tool runs where each of the
            # tools has a unique name+version+options attributes
            # just squash all of them into a single list
            nkey = tools_grouped.setdefault(t.name(), [])
            nkey += t.getRuns(runs_filter)

        tools_final = []
        for (name, tls) in tools_grouped.items():
            tools_final.append((name, list(sortToolRuns(tls))))

        tools_final.sort(key=lambda t: t[0])
        return tools_final

def showTools(wfile, datamanager, opts):
    def _getTags(run):
        return datamanager.getToolRunTags(run)

    # filter out empty strings, they are not valid filters
    _filter = list(filter(lambda x: x != '', opts.setdefault('filter', [])))
    _tags_filter = list(filter(lambda x: x != '', opts.setdefault('tags-filter', [])))

    filters = []
    tags_filters = []
    for f in _filter:
        try:
            rf = compile(f)
            filters.append((f, rf))
        except Exception as e:
            print('ERROR: Invalid regular expression given in filter: ' + str(e))

    for f in _tags_filter:
        try:
            rf = compile(f)
            tags_filters.append((f, rf))
        except Exception as e:
            print('ERROR: Invalid regular expression given in filter: ' + str(e))

    if filters or tags_filters:
        def _runs_filter(run):
            descr = run.run_description() if run.run_description() else ''
            for (_, rf) in filters:
                # satisfies if all tags matches (AND)
                if not rf.search(descr):
                    return False

            if tags_filters:
                tags = run.tags() if run.tags() else ''
                for (_, rf) in tags_filters:
                    # satisfied if any tag matches (OR)
                    if rf.search(tags):
                        return True

                return False

            return True
    else:
        _runs_filter = None
    tags = list(datamanager.tagsmanager.getTags())

    sort_method = 'version'
    if 'sort' in opts:
        sort_method = opts['sort'][0]

    template = None
    if sort_method == 'date':
        template = 'tools_date.html'
    else:
        template = 'tools_version.html'

    tools_map = prepareToolsMap(datamanager.getTools(), _runs_filter, sort_method)

    render_template(wfile, template,
                     {'tools' : tools_map,
                      'get' : get_elem,
                      'setSize' : _setSize,
                      'getTags' : _getTags,
                      'tags'    : tags,
                      'isIn'    : isIn,
                      'makeKeys': makeKeys,
                      'URIjoin' : URIjoin,
                      'run_details' : _run_details,
                      'runs_filter' : _runs_filter,
                      'filters' : _filter,
                      'tags_filters' : _tags_filter,
                      'nonempty_list': _nonempty_list,
                      'sortToolRuns': sortToolRuns,
                      'descr' : getDescriptionOrVersion})

