#!/usr/bin/env python
#
# This script distributes task between computers. The task
# is to be run the Symbiotic tool on given benchark.
#
# (c)oded 2015, 2017 Marek Chalupa
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
#

from .. utils import err, dbg

try:
    import MySQLdb
except ImportError:
    err('Couldn\'t use database from python, please install MySQLdb package '\
        '("pip install mysql-python" or "pip install mysqlclient" with python3)')

from os.path import abspath

class QueryResult(object):
    """
    Simple wrapper around cursor that contains also iterators
    """
    def __init__(self, cursor):
        self._cursor = cursor

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        row = self._cursor.fetchone()
        if row is None:
            raise StopIteration
        else:
            return row

class DatabaseConnection(object):
    def __init__(self, conffile = None):
        self._conffile = conffile
        self._connect()

    def __del__(self):
        # if creating the database failed, then the attribute _conn
        # is not created either and we would get exception
        # in this destructor
        if hasattr(self, '_conn') and not self._conn is None:
            self._conn.close()
        del self

    def _connect(self):
        self._conn, self._cursor = _database_connect(self._conffile)

    def _execute(self, q):
        try:
            self._cursor.execute(q)
        except MySQLdb.Error as e:
            print("Got exception: '{0}'".format(str(e)))
            print("args: '{0}'".format(e.args))
            print("args[0]: '{0}'".format(e.args[0]))
            if e.args[0] == 2006: # "MySQL server has gone away"
                print("Connection closed, sending ping to re-establish")
                # NOTE: this can do rollback, but if the connection
                # is down, we probably don't care
                self._conn.ping(True)
                if self._conn.open == 0:
                    print("Ping didn't work, reconnecting")
                    self._connect()

                assert self._conn.open == 1
            else:
                print("Reraising exception")
                # different exception, re-raise it
                raise e

    def query_unchecked(self, q):
        """
        Execute a query on the database and return an array with the result.
        Throws MySQLdb.Error exception if the query fails.
        """
        self._execute(q)
        return self._cursor.fetchall()

    def query_noresult(self, q):
        """
        Execute a query on the database. Do not execept any result.
        Throws MySQLdb.Error exception if the query fails.
        """
        self._execute(q)

    def queryInt(self, q):
        """
        Execute a query on the database and return the result interpreted
        as an int. Abort if the query fails.
        """

        try:
            self._execute(q)
            ret = self._cursor.fetchone()
            assert self._cursor.fetchone() is None
        except MySQLdb.Error as e:
            err('Failed querying db: {0}\n\n{1}'.format(e.args[1], q))

        if not ret is None:
            return int(ret[0])

    def query(self, q):
        """
        Execute a query on the database and return an array with the result.
        Abort if the query fails. The database is not actually modified
        until commit() is called.
        """
        try:
            return self.query_unchecked(q)
        except MySQLdb.Error as e:
            err('Failed querying db: {0}\n\n{1}'.format(e.args[1], q))

    def query_lazy(self, q):
        """
        Execute a query on the database and return a QueryResult object.
        The query result object has iterators that can be used
        to iterate over results in lazy manners. Aborts if the query fails.
        """
        try:
            return QueryResult(self._cursor)
        except MySQLdb.Error as e:
            err('Failed querying db: {0}\n\n{1}'.format(e.args[1], q))

    def query_with_exception_handler(self, q, handler, data):
        """
        Execute a query on the database and return an array with the result.
        If query fails, call given handler that takes two arguments.
        The first argument are arguments from exception with error cause
        and the other argumet are user's data.
        """
        try:
            return self.query_unchecked(q)
        except MySQLdb.Error as e:
            handler(e.args, data)

    def commit(self):
        """
        Commit database's state
        """
        self._conn.commit()

def _get_db_credentials(path):
    absp = abspath(path)
    try:
        f = open(absp, 'r')
    except IOError as e:
        err("Failed opening file with database configuration: {0}".format(e.strerror))

    host = None
    user = None
    db = None
    pw = None

    for l in f:
        l = l.lstrip()
        if l[0] == '#':
            continue

        k,v = l.split('=', 1)
        k = k.strip()
        v = v.strip()

        if k == 'host':
            host = v
        elif k == 'user':
            user = v
        elif k == 'password':
            pw = v
        elif k == 'database':
            db = v
        else:
            err('Unknown key in {0}: \'{1}\''.format(absp, k))

    f.close()

    return host, user, pw, db

def _check_db_credentials(host, user, passwd, db):
    if host is None or host == '':
        err('Missing \'host\' for database')
    if user is None or user == '':
        err('Missing \'user\' for database')
    if passwd is None or passwd == '':
        err('Missing \'password\' for database')
    if db is None or db == '':
        err('Missing \'database\' for database')

def _database_connect(conffile):
    host, user, passwd, db = _get_db_credentials(conffile)
    _check_db_credentials(host, user, passwd, db)

    try:
        conn = MySQLdb.connect(host = host, user = user,
                               passwd = passwd, db = db)
        cursor = conn.cursor()
    except MySQLdb.Error as e:
        err('{0}\n'.format(str(e)))

    return conn, cursor
