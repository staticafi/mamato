#!/usr/bin/env python

from os.path import basename

class RunInfo(object):
    """
    This class represents one instance of a run
    of a tool on a given benchmark.
    """

    def name(self):
        return basename(self.fullname())

    # children must override these methods
    def fullname(self):
        raise NotImplemented

    def status(self):
        raise NotImplemented

    def cputime(self):
        raise NotImplemented

    def walltime(self):
        raise NotImplemented

    def memusage(self):
        raise NotImplemented

    def classification(self):
        " Was this result in category correct/incorrect/error or unknown?"
        raise NotImplemented

    def exitcode(self):
        raise NotImplemented

    def returnvalue(self):
        raise NotImplemented

    def property(self):
        raise NotImplemented

    def dump(self):
        print(' -- Result --')
        print('  {0} ({1})'.format(self.name(), self.fullname()))
        print('  Result category: {0}'.format(self.classification()))
        print('  Property: {0}'.format(self.property()))
        print('  Cpu (wall) time: {0} ({1})'.format(self.cputime(), self.walltime()))
        print('  Memory usage: {0}'.format(self.memusage()))
        print('  Exit code, return value: {0} {1}'.format(self.exitcode(), self.returnvalue()))

class DBRunInfo(RunInfo):
    """
    This class represents one instance of a run
    of a tool on a given benchmark. It keeps the information
    in a result of a database query and retrieves the information
    using the getters
    """

    def __init__(self, res):
        self._query_result = res
        assert self.fullname() != ''

    # the data in the query result are supposed to be
    # indexed as follows:
    # 0 -> status
    # 1 -> cputime
    # 2 -> walltime
    # 3 -> memusage
    # 4 -> classification
    # 5 -> exitcode
    # 6 -> property
    # 7 -> file name

    def status(self):
        return self._query_result[0]

    def cputime(self):
        return self._query_result[1]

    def walltime(self):
        return self._query_result[2]

    def memusage(self):
        return self._query_result[3]

    def classification(self):
        return self._query_result[4]

    def exitcode(self):
        return self._query_result[5]

    def property(self):
        return self._query_result[6]

    def fullname(self):
        return self._query_result[7]


class DirectRunInfo(RunInfo):
    """
    This class represents one instance of a run
    of a tool on a given benchmark. It stores the information
    directly in attributes
    """

    def __init__(self, nm):
        self._fullname = nm
        self._name = basename(nm)

        self._status = None
        self._cputime = None
        self._walltime = None
        self._memusage = None
        self._classification = None
        self._property = None
        self._exitcode = None
        self._returnvalue = None
        # other attributes
        #self.others = {}

    def name(self):
        return self._name

    def fullname(self):
        return self._fullname

    def status(self):
        return self._status

    def cputime(self):
        return self._cputime

    def walltime(self):
        return self._walltime

    def memusage(self):
        return self._memusage

    def classification(self):
        return self._classification

    def exitcode(self):
        return self._exitcode

    def returnvalue(self):
        return self._returnvalue

    def property(self):
        return self._property

