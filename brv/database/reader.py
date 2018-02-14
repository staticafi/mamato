#!/usr/bin/env python
#
# (c) 2017 Marek Chalupa
# E-mail(s): statica@fi.muni.cz, mchalupa@mail.muni.cz
#
# Permission to use, copy, modify, distribute, and sell this software and its
# documentation for any purpose is hereby granted without fee, provided that
# the above copyright notice appear in all copies and that both that copyright
# notice and this permission notice appear in supporting documentation, and
# that the name of the copyright holders not be used in advertising or
# publicity pertaining to distribution of the software without specific,
# written prior permission. The copyright holders make no representations
# about the suitability of this software for any purpose. It is provided "as
# is" without express or implied warranty.
#
# THE COPYRIGHT HOLDERS DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO
# EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.

from . proxy import DatabaseProxy
from brv.toolruninfo import DBToolRunInfo, ToolRunInfoStats, RunsStats
from brv.runinfo import DBRunInfo

class DatabaseReader(DatabaseProxy):
    """
    DatabaseProxy specialized for reading the database
    """

    def __init__(self, conffile = None):
        DatabaseProxy.__init__(self, conffile)

    def getToolRuns(self):
        q = """
        SELECT tool_run.id, tool.name, tool.version, date,
               options, cpulimit, memlimit, tool_run.description
        FROM tool JOIN tool_run ON tool.id = tool_id;
        """
        res = self.query(q)

        ret = []
        for r in res:
            info = DBToolRunInfo(r[0])
            # FIXME -- do not set private attributes
            info._tool = r[1]
            info._tool_version = r[2]
            info._date = r[3]
            info._options = r[4]
            info._timelimit = r[5]
            info._memlimit = r[6]
            info._run_description = r[7]

            ret.append(info)

        return ret

    def getToolInfoStats(self, tool_run_id):
        q = """
        SELECT name, status, classification, benchmarks_set_id, count(classification), sum(cputime)
        FROM run JOIN benchmarks_set ON benchmarks_set_id = benchmarks_set.id
        WHERE tool_run_id='{0}' GROUP BY classification, status, benchmarks_set_id;
         """.format(tool_run_id)
        res = self.query(q)
        ret = ToolRunInfoStats()
        for r in res:
            cat = r[0]
            bset_id = r[3]
            stats = ret.getOrCreateStats(bset_id, cat)

            cnt = r[4]
            time = r[5]
            classif = (r[1], r[2])
            stats.addStat(classif, cnt, time)

        return ret

    def getRunInfos(self, bset_id, tool_run_id):
        # 0 -> status
        # 1 -> cputime
        # 2 -> walltime
        # 3 -> memusage
        # 4 -> classification
        # 5 -> exitcode
        # 6 -> property
        # 7 -> file name

        q = """
        SELECT status, cputime, walltime, memusage,
               classification, exitcode, property, file
        FROM run WHERE tool_run_id = '{0}' AND benchmarks_set_id = '{1}'; 
        """.format(tool_run_id, bset_id);
        print(q)
        # FIXME: use fetchone
        res = self.query(q)
        ret = []
        for r in res:
            # FIXME: do this lazily -- return an object with this query
            # and return DBRunInfo when iterating over this object
            ret.append(DBRunInfo(r))

        return ret

