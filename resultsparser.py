#!/usr/bin/env python

from result import RunInfo, DirectRunInfo
from tools import ToolResult

import sys
import os

from xml.dom import minidom

def parse_run_elem(run):
    " Parse a <run>...</run> elements from xml"

    r = DirectRunInfo(run.getAttribute('name'))
    r._property = run.getAttribute('properties')

    NUMBER_OF_ITEMS = 7
    n = 0
    for col in run.getElementsByTagName('column'):
	title = col.getAttribute('title')
	value = col.getAttribute('value')

	if title == 'status':
	    r._status = value
	    n += 1
	elif title == 'cputime':
	    r._cputime = value
	    n += 1
	elif title == 'walltime':
	    r._walltime = value
	    n += 1
	elif title == 'memUsage':
	    r._memusage = value
	    n += 1
	elif title == 'category':
	    r._resultcategory = value
	    n += 1
	elif title == 'exitcode':
	    r._exitcode = value
	    n += 1
	elif title == 'returnvalue':
	    r._returnvalue = value
	    n += 1
	#else:
	#    r.others[title] = value

        # do not go over all columns when we found
        # what we are looking for
	if n == NUMBER_OF_ITEMS:
            break

    return r

def createToolResult(xmlfl):
    """
    Parse xml attributes that contain the information
    about tool, property and so on
    """

    roots = xmlfl.getElementsByTagName('result')
    assert len(roots) == 1
    root = roots[0]

    tr = ToolResult()
    tr.tool = root.getAttribute('tool')
    tr.tool_version = root.getAttribute('version')
    tr.date = root.getAttribute('date')
    tr.options = root.getAttribute('options')
    tr.timelimit = root.getAttribute('timelimit')
    tr.name = root.getAttribute('name')
    tr.block = root.getAttribute('block')

    return tr


def parse_xml(filePath):
    """
    Return a ToolRun object created from a given xml file.
    """

    xmlfl = minidom.parse(filePath)
    ret = createToolResult(xmlfl)

    for run in xmlfl.getElementsByTagName('run'):
	r = parse_run_elem(run)
	ret.append(r)

    return ret

if __name__ == "__main__":
    import sys
    tr = parse_xml(sys.argv[1])
    tr.dump()
