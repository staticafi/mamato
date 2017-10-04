#!/usr/bin/env python

class ToolsManager(object):
    """
    Manages a set of tools that are available for comparing/browsing.
    """

    class Tool(object):
        def __init__(self, nm, ver):
            self.name = nm
            self.version = ver

            self._runs = []

        def getRuns(self):
            return self._runs

        def equals(self, oth):
            return self.version == oth.version and self.name == oth.name 

    def __init__(self, db_conf = None, xmls = []):
        # list of tools (tool name + version and mapping to single runs)
        self._tools = []

        # list of runs of tools (run of a tool in a given settings)
        self._tool_runs = []

        # mapping from tool's identifier -> index in _tool_runs
        # The index in tools uniquely identifies the tool
        # in this object and on the HTML pages (can be passed to GET)
        #self._identifier_to_run = {}

    def _add_tool(self, toolrun):
        found = None
        for tool in self._tools:
            if tool.version == toolrun.tool_version() and tool.name == toolrun.tool():
                found = tool
                break

        if found:
            found._runs.append(toolrun)
        else:
            t = self.Tool(toolrun.tool(), toolrun.tool_version())
            self._tools.append(t)
            t._runs.append(toolrun)

    def add(self, t):
        self._add_tool(t)
        self._tool_runs.append(t)

    def getTools(self):
        return self._tools

    def getToolRuns(self, which = []):
        if not which:
            return self._tool_runs
        else:
            return [run for run in self._tool_runs if run.getID() in which]
