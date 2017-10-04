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

class DatabaseWriter(DatabaseProxy):
    """
    DatabaseProxy specialized for updating the database
    """

    def __init__(self, conffile = None):
        DatabaseProxy.__init__(self, conffile)


    def _getToolID(self, name, version):
        q = """
        SELECT id FROM tool
        WHERE name = '{0}' AND version = '{1}';
        """.format(name, version)

        return self.queryInt(q)

    def createToolInfoID(self, toolinfo):
        """
        Add a new tool_run into database, return its ID.
        If such tool_run already exists, return None.
        """

        tool_id = self._getToolID(toolinfo.tool, toolinfo.tool_version)
        if tool_id is None:
            # update the 'tool' table if needed
            q = """
            INSERT INTO tool
            (name, version) VALUES ('{0}', '{1}');
            """.format(toolinfo.tool, toolinfo.tool_version)
            self.query_noresult(q)

            tool_id = self.queryInt("SELECT LAST_INSERT_ID();")

        q = """
        SELECT id FROM tool_run WHERE
          tool_id = '{0}' AND options = '{1}' AND memlimit = '{2}' AND
          cpulimit = '{3}' AND date = '{4}';
        """.format(tool_id, toolinfo.options, toolinfo.memlimit,
                   toolinfo.timelimit, toolinfo.date)
        tool_run_id = self.queryInt(q)

        if tool_run_id:
            return None

        # add a new tool_run record
        q = """
        INSERT INTO tool_run
          (tool_id, options, memlimit, cpulimit, date)
          VALUES ('{0}', '{1}', '{2}', '{3}', '{4}');
        """.format(tool_id, toolinfo.options, toolinfo.memlimit,
                   toolinfo.timelimit, toolinfo.date)
        self.query_noresult(q)

        return self.queryInt("SELECT LAST_INSERT_ID();")

    def getOrCreateBenchmarksSetID(self, name):
        q = """
        SELECT id FROM benchmarks_set WHERE
            name = '{0}'
        """.format(name)
        benchmarks_id = self.queryInt(q)

        if benchmarks_id is None:
            q = """
            INSERT INTO benchmarks_set (name)
              VALUES ('{0}');
            """.format(name)
            self.query_noresult(q)

            benchmarks_id = self.queryInt("SELECT LAST_INSERT_ID();")

        return benchmarks_id

    def writeRunInfo(self, tool_run_id, benchmarks_set_id, runinfo):
        q = """
        INSERT INTO run
        (status, cputime, walltime, memusage, classification, exitcode, exitsignal,
         terminationreason, tool_run_id, benchmarks_set_id, property, options, file)
        VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}',
        '{10}', '{11}', '{12}');
        """.format(runinfo.status(), runinfo.cputime(), runinfo.walltime(),
                   runinfo.memusage(), runinfo.classification(), runinfo.exitcode(),
                   0, 0, #FIXME
                   tool_run_id, benchmarks_set_id,
                   runinfo.property(), None, #FIXME
                   runinfo.fullname())
                    #FIXME: what return value?
        self.query_noresult(q)

    def deleteTool(self, tool_run_id):
        q = """
        DELETE FROM run
        WHERE tool_run_id = '{0}';
        """.format(tool_run_id)
        self.query_noresult(q)

        q = """
        DELETE FROM tool_run
        WHERE id = '{0}';
        """.format(tool_run_id)
        self.query_noresult(q)
