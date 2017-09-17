#!/usr/bin/env python

class ToolRunInfo(object):
    """
    Represents one tool in a given version with provided settings and environment
    (like CPAchecker of version XX ran with these params on this data)
    """
    def __init__(self, _id):
        self._id = _id

    def getID(self):
        return self._id

    def tool(self):
        raise NotImplemented

    def tool_version(self):
        raise NotImplemented

    def date(self):
        raise NotImplemented

    def options(self):
        raise NotImplemented

    def timelimit(self):
        raise NotImplemented

    def memlimit(self):
        raise NotImplemented

    def getResults(self):
        return self._runs

    def getStats(self):
        return self._stats

    def addRun(self, r):
        """
        Add a run result to this tool run
        """
        self._runs.append(r)

class DBToolRunInfo(ToolRunInfo):
    def __init__(self, idtf = None, tool = None, vers = None, date = None,
                 opts = None, tlimit = None, mlimit = None):
        ToolRunInfo.__init__(self, idtf)

        # a descriptor of this run
        # FIXME: store only the query and use the query
        self._tool = tool
        self._tool_version = vers
        self._date = date
        self._options = opts
        self._timelimit = tlimit
        self._memlimit = mlimit
        # list of results (RunInfo objects)
        self._stats = None 
        self._runs = []

    def tool(self):
        return self._tool

    def tool_version(self):
        return self._tool_version

    def date(self):
        return self._date

    def options(self):
        return self._options

    def timelimit(self):
        return self._timelimit

    def memlimit(self):
        return self._memlimit

    def getRuns(self):
        return self._runs

    def getStats(self):
        return self._stats


class RunsStats(object):
    def __init__(self):
        # 'classification' -> count
        self._stats = {}

    def addStat(self, classification, cnt):
        # XXX: can python do it in one step? Find out
        if classification in self._stats:
            self._stats[classification] += cnt
        else:
            self._stats[classification] = cnt

    def getStats(self):
        return self._stats

class ToolRunInfoStats(object):
    def __init__(self):
        self._catToSum = {}

    def getStats(self, cat):
        return self._catToSum[cat]

    def getBenchmarksSets(self):
        return self._catToSum.keys()

