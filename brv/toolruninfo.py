#!/usr/bin/env python

class ToolRunInfo(object):
    """
    Represents one tool in a given version with provided settings and environment
    (like CPAchecker of version XX ran with these params on this data)
    """

    def __init__(self, idtf = None, tool = None, vers = None, date = None,
                 opts = None, tlimit = None, mlimit = None):
        # a descriptor of this run
        self.id = idtf
        self.tool = tool
        self.tool_version = vers
        self.date = date
        self.options = opts
        self.timelimit = tlimit
        self.memlimit = mlimit
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

