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
        self.memlimit = None
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
                s = summaryFromToolResult(r)
                return s
        
        return ResultsSummary()

    def getResultsSummary(self, cat):
        summary = ResultsSummary()
        for r in self._results:
            summary.add(summaryFromToolResult(r))
        return summary


#FIXME: move to new file
class JoinedToolResult(object):
    def __iter__(self):
        raise NotImplemented

    def next(self):
        raise NotImplemented
    
class JoinedToolResults(object):
    """
    Table of joined tool results. Will be derived either
    from database or by joining directly the results
    on some identifier.
    """

    def getResults(self):
        """ Return an iterator to  results (rows of the table).
            A row is represented by JoinedToolResult object.
        """
        raise NotImplemented

    def join(self, tr):
        raise NotImplemented

    def __iter__(self):
        raise NotImplemented


class DirectJoinedToolResultsRowIterator(object):
    def __init__(self, obj):
        self._name = obj[0]
        self._it = iter(obj[1])

    def __iter__(self):
        return self

    def __len__(self):
        return 0

    def __getitem__(self):
        if self._name:
            return self._name
        else:
            return self.it.__getitem__()

    def next(self):
        # let name be the first element
        if self._name:
            tmp = self._name
            self._name = None
            return tmp
        return self._it.next()

class DirectJoinedToolResultsIterator(object):
    def __init__(self, obj):
        self._it = obj._results.iteritems()

    def __iter__(self):
        return self

    def __getitem__(self):
        return self._it.__getitem__()

    def __len__(self):
        return 0

    def next(self):
        return DirectJoinedToolResultsRowIterator(self._it.next())


class DirectJoinedToolResults(JoinedToolResults):
    def __init__(self):
        # a map from benchmark identifier to a list of results
        self._results = {}
        self._columns = 0
        self._no_tool_result = ToolResult()

    def _init(self, tr):
        for result in tr.getResults():
            self._results[result.fullname()] = [result]

        self._columns = 1

    def join(self, tr):
        if not self._results:
            self._init(tr)
            return

        print('Joining')
        for result in tr.getResults():
            if self._results.has_key(result.fullname()):
                row = self._results[result.fullname()]
                for i in range(0, self._columns - len(row)):
                    row.append(self._no_tool_result)
            else:
                self._results[result.fullname()]\
                    = [self._no_tool_result for x in range(0,self._columns)]
                self._results[result.fullname()].append(tr)

            print(result.fullname(), self._results[result.fullname()])
            self._columns += 1
            assert len(self._results[result.fullname()]) == self._columns
        print(self._results)

    def getResults(self):
        return DirectJoinedToolResultsIterator(self)

    def __iter__(self):
        return self.getResults()

    def dump(self):
        print("Dumping join")
        i = 0
        from sys import stdout
        for row in self:
            stdout.write('{0}:'.format(i))
            for col in row:
                stdout.write(' {0}'.format(col))
            stdout.write('\n')
            i += 1

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
            self._tools.append(ToolResults(nm, i))
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
