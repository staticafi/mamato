#!/usr/bin/env python

class ToolsManager(object):
    """
    Manages a set of tools that are available for comparing/browsing.
    """

    class Tool(object):
        def __init__(self, toolrun):
            self._tool_run = toolrun
            self._runs = []

        def version(self):
            return self._tool_run.tool_version()

        def name(self):
            return self._tool_run.tool()

        def options(self):
            return self._tool_run.options()

        def getRuns(self):
            """ Return the list of results for this tool """
            return self._runs

        def equalsToolRun(self, tr):
            return self.version() == tr.tool_version() and\
                   self.name() == tr.tool() and\
                   self.options() == tr.options()

       #def equals(self, oth):
       #    return self.version() == oth.version() and\
       #           self.name() == oth.name() and\
       #           self.options() == oth.options()

    def __init__(self):
        # list of tools (tool name + version + options and mapping to single runs)
        self._tools = []

        # list of runs of tools (run of a tool in a given settings)
        self._tool_runs = []

        # mapping from tool's identifier -> index in _tool_runs
        # The index in tools uniquely identifies the tool
        # in this object and on the HTML pages (can be passed to GET)
        #self._identifier_to_run = {}

    def reset(self):
        if self._tools:
            self._tools = []
        if self._tool_runs:
            self._tool_runs = []

    def remove(self, t):
        self._tool_runs.remove(t)
        tool = self._find_tool(t)
        assert tool
        tool._runs.remove(t)
        if not tool._runs:
            self._tools.remove(tool)
        
    def _find_tool(self, toolrun):
        for tool in self._tools:
            if tool.equalsToolRun(toolrun):
                return tool

        return None

    def _add_tool(self, toolrun):
        found = self._find_tool(toolrun)

        if found:
            found._runs.append(toolrun)
        else:
            t = self.Tool(toolrun)
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
