#!/usr/bin/env python

class ResultsSummary(object):
    def __init__(self):
        self.correct = 0
        self.incorrect = 0
        self.unknown = 0
        self.errors = 0

    def add(self, rhs):
       self.correct += rhs.correct
       self.incorrect += rhs.incorrect
       self.unknown += rhs.unknown
       self.errors += rhs.errors 

    def dump(self):
        print('{0}/{1}/{2}/{3}'.format(self.correct, self.incorrect,
                                       self.unknown, self.errors))

def summaryFromToolRunInfo(res):
    summary = ResultsSummary()
    # FIXME: divide to correct true/false, etc.
    for r in res.getResults():
        resultcategory = r.resultcategory()
        if resultcategory == 'error':
            summary.errors += 1
        elif resultcategory == 'correct':
            summary.correct += 1
        elif resultcategory == 'incorrect':
            summary.incorrect += 1
        elif resultcategory == 'unknown':
            summary.unknown += 1

    return summary

class ToolResult(object):
    """
    Results of a tool of different categories
    (list of ToolRunInfo objects)
    """
    def __init__(self, nm, i):
        # list of tool results
        self.tool = nm
        self._results = []
        self._id = i

    def getID(self):
        return self._id

    def getResults(self):
        return self._results

    def add(self, tr):
        """
        Add results for a set of benchmarks to this tool
        """
        #XXX: debugging only
        for r in self._results:
            assert r.block != tr.block

        self._results.append(tr)

    def getResultsSummaryForCat(self, cat):
        for r in self._results:
            if r.block == cat:
                s = summaryFromToolRunInfo(r)
                return s

        return ResultsSummary()

    def getResultsSummary(self, cat):
        summary = ResultsSummary()
        for r in self._results:
            summary.add(summaryFromToolRunInfo(r))
        return summary

class ToolsManager(object):
    """
    Manages a set of tools that are available for comparing/browsing.
    """

    class Tool(object):
        def __init__(self, nm, ver):
            self.name = nm
            self.ver = version
            # XXX: we can add mapping to _tool_runs where this
            # tool is used

    def __init__(self, db_conf = None, xmls = []):
        # list of tools (tool name + version)
        self._tools = []

        # list of runs of tools (run of a tool in a given settings)
        self._tool_runs = []

        # mapping from tool's identifier -> index in _tool_runs
        # The index in tools uniquely identifies the tool
        # in this object and on the HTML pages (can be passed to GET)
        self._identifier_to_run = {}

    def _add_tool(self, t):
        found = False
        for tool in self._tools:
            if tool.equals(t):
                found = True
                break

        if not found:
            self._tools.append(t)

    def add(self, t):
        self._add_tool(Tool(t.tool, t.tool_version))

        nm = t.getToolIdentifier()

        if self._identifier_to_run.has_key(nm):
            i = self._identifier_to_run[nm]
            self._tool_runs[i].add(t)
        else:
            i = len(self._tool_runs)
            self._tool_runs.append(ToolResult(nm, i))
            self._tool_runs[i].add(t)
            self._identifier_to_run[nm] = i

    def getTools(self):
        return self._tools

    def getToolRuns(self, which = []):
        if not which:
            return self._tool_runs
        else:
            ret = []
            for x in which:
                ret.append(self._tool_runs[x])
            return ret
