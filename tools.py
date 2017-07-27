#!/usr/bin/env python

class ToolResult(object):
    """
    Represents a run of a tool on a set of benchmarks
    """

    def __init__(self):
        # a descriptor of this run
        self.name = None
        self.tool = None
        self.tool_version = None
        self.date = None
        self.options = None
        self.timelimit = None
        self.block = None
        # list of results (RunInfo objects)
        self._results = []

    def getShortName(self):
        return self.tool + self.tool_version[:25]

    def getResults(self):
        return self._results

    def append(self, r):
        """
        Add a run result to this tool run
        """
        self._results.append(r)

    def getToolIdentifier(self):
       return '{0}-{1}'.format(self.tool, self.tool_version)

    def dump(self):
        print('-- Run of a tool --')
        print('{0} {1} -- {2}'.format(self.tool, self.tool_version, self.name))
        print('Date: {0}'.format(self.date))
        print('Block: {0}'.format(self.block))
        print('Timelimit: {0}'.format(self.timelimit))
        print('Results:')
        for r in self._results:
            r.dump()

 
class ResultsSummary(object):
   #def __init__(self):
   #    self.correct_true = 0
   #    self.incorrect_true = 0
   #    self.correct_false = 0
   #    self.incorrect_false = 0
   #    self.errors = 0
   #    self.unknown = 0
   #    self.timeouts = 0

   #def add(self, rhs):
   #    self.correct_true += rhs.correct_true
   #    self.incorrect_true += rhs.incorrect_true
   #    self.correct_false += rhs.correct_false 
   #    self.incorrect_false += rhs.incorrect_false
   #    self.errors += rhs.errors 
   #    self.unknown += rhs.unknown
   #    self.timeouts += rhs.timeouts

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

def summaryFromToolResult(res):
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


class ToolResults(object):
    """
    Results of a tool of different categories
    (list of ToolResult objects)
    """
    def __init__(self, nm):
        # list of tool results
        self.tool = nm
        self._results = []

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
                s = summaryFromToolResult(r)
                return s
        
        return ResultsSummary()

    def getResultsSummary(self, cat):
        summary = ResultsSummary()
        for r in self._results:
            summary.add(summaryFromToolResult(r))
        return summary

class ToolsManager(object):
    """
    Manages a set of tools (ToolResults objects) that are available
    for comparing/browsing.
    """
    def __init__(self, xmls = []):
        self._tools = []
        # mapping from tool's identifier -> index in tools
        # The index in tools uniquely identifies the tool
        # in this object and on the HTML pages (can be passed to GET)
        self._mapping = {}

        if xmls:
            self.parseXmls(xmls)

    def parseXmls(self, xmls):
        """
        Load results from xml files
        """
        from resultsparser import parse_xml
        for xml in xmls:
            self.add(parse_xml(xml))

    def loadDatabase(self):
        """
        Load available tools from database
        """
        raise NotImplemented

    def add(self, t):
        nm = t.getToolIdentifier()

        if self._mapping.has_key(nm):
            i = self._mapping[nm]
            self._tools[i].add(t)
        else:
            i = len(self._tools)
            self._tools.append(ToolResults(nm))
            self._tools[i].add(t)
            self._mapping[nm] = i

    def getTools(self, which = []):
        if not which:
            return self._tools
        else:
            ret = []
            for x in which:
                ret.append(self._tools[x])
            return ret
