#!/usr/bin/env python

class ToolRunInfo(object):
    """
    Represents one tool in a given version with provided settings and environment
    (like CPAchecker of version XX ran with these params on this data)
    """
    def __init__(self, _id = None):
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
    def __init__(self, idtf, tool = None, vers = None, date = None,
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
    def __init__(self, cat, bset_id):
        # 'classification' -> count
        self._stats = {}
        self._benchmarks_name = cat
        self._benchmarks_id = bset_id

    def addStat(self, classification, cnt):
        # XXX: can python do it in one step? Find out
        if classification in self._stats:
            self._stats[classification] += cnt
        else:
            self._stats[classification] = cnt

    def get(self, classification):
            return self._stats.get(classification)

    def getCount(self, classification):
        n = self._stats.get(classification)
        if n is None:
            return 0
        else:
            return n

    def getStats(self):
        return self._stats

    def getBenchmarksName(self):
        return self._benchmarks_name

    def getBenchmarksID(self):
        return self._benchmarks_id

    def getClassifications(self):
        return list(self._stats.keys())

class ToolRunInfoStats(object):
    def __init__(self):
        self._stats = {}
        # mapping of names of categories to id's
        # of the benchmark sets
        self._name_to_id = {}

    def getAllStats(self):
        return self._stats

   #def getStatsByName(self, cat):
   # FIXME: there can be more ids
   #    n = self._name_to_id[cat]
   #    return self._stats[n]

    def getStatsByID(self, bset_id):
        return self._stats.get(bset_id)

    def _addNameToIDMapping(self, cat, bset_id):
        if cat in self._name_to_id:
            self._name_to_id[cat].add(bset_id)
        else:
            self._name_to_id[cat] = set([bset_id])

    def getOrCreateStats(self, bset_id, cat):
        if bset_id in self._stats:
            stats = self._stats[bset_id]
        else:
            stats = RunsStats(cat, bset_id)
            self._stats[bset_id] = stats
            self._addNameToIDMapping(cat, bset_id)

        return stats

    def getBenchmarksSetsNames(self):
        return self._name_to_id.keys()

    def getBenchmarksSets(self):
        return self._stats.keys()


class RunInfosTable(object):
    """
    Table of RunInfo objects:

                 tool1  tool2  ...
    benchmark1   ri11    ri12  ...
    benchmark2   ri21    ri22  ...
       ...       ...     ...
    """

    def __init__(self):
        # benchmarks_name -> list of runinfos
        self._benchmarks = {}
        self._tools_num = 0

    def add(self, runinfos):
        """ add results from one tool run"""

        for info in runinfos:
            name = info.fullname()
            infos = self._benchmarks.setdefault(name, [])

            ## missing some tools? Fill in the gap
            l = len(infos)
            while l < self._tools_num:
                infos.append(None)

            assert len(infos) == self._tools_num

            infos.append(info)

        self._tools_num += 1

    def getRunInfos(self, benchmark):
        info = self._benchmarks[benchmark]
        assert len(info) == self._tools_num

        return info

    def getRows(self):
        return self._benchmarks

