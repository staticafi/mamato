#!/usr/bin/env python
#
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


from os.path import basename
from .. utils import err, dbg

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
    def __init__(self, conffile = None):
        self._db = DatabaseConnection(conffile)

        # self check
        ver = self._db.query('SELECT VERSION()')[0][0]
        dbg('Connected to database: MySQL version {0}'.format(ver))

    def connection(self):
        return self._db

    def commit(self):
        self._db.commit()

    def getToolID(self, tool, version, tool_params, year_id):
        q = """
        SELECT id FROM tools
        WHERE name = '{0}' and version = '{1}'
              and params = '{2}' and year_id = '{3}';
        """.format(tool, version, tool_params, year_id)
        res = self._db.query(q)
        if not res:
            return None

        assert len(res) == 1
        return res[0][0]

    def getCategoryID(self, year_id, category_name):
        q = """
        SELECT id FROM categories
        WHERE
            year_id = '{0}' and name = '{1}';
        """.format(year_id, category_name)
        res = self._db.query(q)
        if not res:
            return None

        return res[0][0]

    def getTaskID(self, category_id, name):
        q = """
        SELECT id FROM tasks
        WHERE name = '{0}' and category_id = '{1}';
        """.format(basename(name), category_id)
        res = self._db.query(q)
        if not res:
            return None

        return res[0][0]

