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

