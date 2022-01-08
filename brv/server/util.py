#!/usr/bin/python
from os.path import basename

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

def getBenchmarkURL(name):
    base = 'https://gitlab.com/sosy-lab/benchmarking/sv-benchmarks/-/blob/main/'
    try:
        return base + name[name.index('/c/'):]
    except ValueError:
        return None

def getShortName(name):
    return basename(name)
