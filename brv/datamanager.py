#!/usr/bin/python

from brv.toolsmanager import ToolsManager
from brv.tagsmanager import TagsManager
from brv.toolruninfo import RunInfosTable

class DataManager(object):
    """
    Instance of this class manages all data (either from xml
    or database) that we know about, so this is the top
    class wrapping all retrieved data
    """

    def __init__(self, db_conf = None, xmls = []):
        self.toolsmanager = ToolsManager()
        self.tagsmanager = TagsManager()
        self._db_reader = None
        self._db_config = db_conf

        if db_conf:
            from brv.database.connection import DatabaseConnection
            from brv.database.reader import DatabaseReader
            from brv.database.writer import DatabaseWriter
            conn = DatabaseConnection(db_conf)
            self._db_reader = DatabaseReader(conn)
            self._db_writer = DatabaseWriter(conn)

            self.reloadData()

        if xmls:
            # XXX: NOT SUPPORTED YET. load the xml into database first
            pass

    def reloadData(self):
        """
        Relad data from database
        """
        assert self._db_reader
        print('Reloading data from DB')

        tool_runs = self._db_reader.getToolRuns()
        self.toolsmanager.reset()
        for run in tool_runs:
            self.toolsmanager.add(run)
            self.tagsmanager.addToolRunTags(run)

    def getTools(self):
        return self.toolsmanager.getTools()

    def getToolRuns(self, which = []):
        return self.toolsmanager.getToolRuns(which)

    def getToolInfoStats(self, which):
        return self._db_reader.getToolInfoStats(which)

    def getRunInfos(self, bset_id, toolruns_id):
        table = RunInfosTable()
        for tid in toolruns_id:
            table.add(self._db_reader.getRunInfos(bset_id, tid))

        return table

    def getToolRunTags(self, run):
        return self.tagsmanager.getToolRunTags(run)

    def deleteToolRuns(self, runs):
        for run in runs:
            self._db_writer.deleteTool(run.getID())
            self.toolsmanager.remove(run)
            self.tagsmanager.remove(run)
        self._db_writer.commit()

    def _updateToolRun(self, newrun):
        self.toolsmanager.updateToolRun(newrun)
        self.tagsmanager.resetToolRunTags(newrun)

    def setToolRunDescription(self, run_id, descr):
        self._db_writer.setToolRunDescr(run_id, descr)
        self._db_writer.commit()
        # get the updated tool run (we could change it just loacally,
        # but until it is some efficiency issue, this is better for debugging
        newrun = self._db_reader.getToolRun(run_id)
        self._updateToolRun(newrun)

    def setToolRunTags(self, run_id, tags):
        self._db_writer.setToolRunTags(run_id, tags)
        self._db_writer.commit()

        newrun = self._db_reader.getToolRun(run_id)
        self._updateToolRun(newrun)


