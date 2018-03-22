#!/usr/bin/python

def getDescriptionOrVersion(toolr):
    descr = toolr.run_description()
    if descr:
        return descr
    name = toolr.name()
    if name:
        return name

    return toolr.tool_version()

def get_elem(p, idx):
    return p[idx]

