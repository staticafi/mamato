#!/usr/bin/python

def getDescriptionOrVersion(toolr):
    descr = toolr.run_description()
    if descr is None:
        return toolr.tool_version()
    else:
        return descr

def get_elem(p, idx):
    return p[idx]

