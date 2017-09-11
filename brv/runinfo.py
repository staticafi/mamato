#!/usr/bin/env python

from os.path import basename

class RunInfo(object):
    """
    This class represents one instance of a run
    of a tool on a given benchmark.
    """

    # children must override these methods
    def name(self):
        raise NotImplemented

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
        # FIXME: in database it is called 'classification'
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

