# Copyright (c) 2015, 2017 Marek Chalupa
# E-mail: statica@fi.muni.cz, mchalupa@mail.muni.cz
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


from .. utils import dbg

from . connection import DatabaseConnection

def None2Zero(x):
    if x is None:
        return 0
    return x

def Empty2Null(x):
    if x == '':
        return 'NULL'

    return '\'{0}\''.format(x.strip())

class DatabaseProxy(object):
    def __init__(self, conffile_or_conn):
        assert not conffile_or_conn is None
        if type(conffile_or_conn) is str:
            self._db = DatabaseConnection(conffile_or_conn)

            # self check
            ver = self._db.query('SELECT VERSION()')[0][0]
            dbg('Connected to database: MySQL version {0}'.format(ver))
        else:
            assert type(conffile_or_conn) is DatabaseConnection
            self._db = conffile_or_conn

    ## Shortcuts for convenience
    def query_noresult(self, q):
        return self._db.query_noresult(q)

    def queryInt(self, q):
        return self._db.queryInt(q)

    def query(self, q):
        return self._db.query(q)

    def commit(self):
        self._db.commit()

    def getRunCount(self, tool_run_id, bset_id):
        q = """
        SELECT count(*) FROM run
        WHERE tool_run_id = '{0}' AND benchmarks_set_id = '{1}';
        """.format(tool_run_id, bset_id)

        return self.queryInt(q)

