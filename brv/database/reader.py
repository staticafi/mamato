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
from brv.toolruninfo import ToolRunInfo

class DatabaseReader(DatabaseProxy):
    """
    DatabaseProxy specialized for updating the database
    """

    def __init__(self, conffile = None):
        DatabaseProxy.__init__(self, conffile)

    def getToolRuns(self):
        q = """
        SELECT tool.id, tool.name, tool.version, date, options, cpulimit, memlimit
        FROM tool JOIN tool_run ON tool.id = tool_id;
        """
        res = self.query(q)

        ret = []
        for r in res:
            info = ToolRunInfo()
            info.id = r[0]
            info.tool = r[1]
            info.tool_version = r[2]
            info.date = r[3]
            info.options = r[4]
            info.timelimit = r[5]
            info.memlimit = r[6]

            ret.append(info)

        return ret
