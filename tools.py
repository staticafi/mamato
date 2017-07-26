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
        self.results = []

    def getShortName(self):
        return self.tool + self.tool_version[:25]

    def append(self, r):
	"""
	Add a run result to this tool run
	"""
	self.results.append(r)

    def dump(self):
	print('-- Run of a tool --')
	print('{0} {1} -- {2}'.format(self.tool, self.tool_version, self.name))
	print('Date: {0}'.format(self.date))
	print('Block: {0}'.format(self.block))
	print('Timelimit: {0}'.format(self.timelimit))
	print('Results:')
	for r in self.results:
	    r.dump()


class ToolsManager(object):
    """
    Manages a set of tools that are available
    for comparing/browsing.
    """
    def __init__(self, xmls = []):
        self._tools = []
        if xmls:
            self.parseXmls(xmls)

    def parseXmls(self, xmls):
        from resultsparser import parse_xml
        for xml in xmls:
            self.add(parse_xml(xml))

    def add(self, t):
        self._tools.append(t)

    def getTools(self, which = []):
        if not which:
            return self._tools
        else:
            ret = []
            for x in which:
                ret.append(self._tools[x])
            return ret
