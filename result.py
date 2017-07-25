#!/usr/bin/env python

from os.path import basename

class Result(object):
    """
    This class represents one instance of a run
    of a tool on a given benchmark.
    """

    def __init__(self, name):
        self.fullname = name
        self.name = basename(name)

        self.status = None
        self.cputime = None
        self.walltime = None
        self.memusage = None
        self.resultcategory = None
        self.property = None
        self.exitcode = None
        self.returnvalue = None
        # other attributes
        #self.others = {}

    def dump(self):
	print(' -- Result --')
	print('  {0} ({1})'.format(self.name, self.fullname))
	print('  Result category: {0}'.format(self.resultcategory))
	print('  Property: {0}'.format(self.property))
	print('  Cpu (wall) time: {0} ({1})'.format(self.cputime, self.walltime))
	print('  Memory usage: {0}'.format(self.memusage))
	print('  Exit code, return value: {0} {1}'.format(self.exitcode, self.returnvalue))

class ToolRun(object):
    """
    Represents a run of a tool
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
        # list of results
        self.results = []

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


