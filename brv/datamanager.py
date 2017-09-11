#!/usr/bin/python

from brv.toolsmanager import ToolsManager

class DataManager(object):
    """
    Instance of this class manages all data (either from xml
    or database) that we know about, so this is the top
    class wrapping all retrieved data
    """

    def __init__(self, db_conf = None, xmls = []):
        self.toolsmanager = ToolsManager()
        self._db = None

        if db_conf:
            from brv.database.reader import DatabaseReader
            self._db = DatabaseReader(db_conf)

            tool_runs = self._db.getToolRuns()
            for run in tool_runs:
                self.toolsmanager.add(run)

        if xmls:
            # XXX: NOT SUPPORTED YET. load the xml into database first
            pass

    def getTools(self):
        return self.toolsmanager.getTools()

    def getToolRuns(self, which = []):
        return self.toolsmanager.getToolRuns(which)


