#!/usr/bin/env python

from result import Result, ToolRun

import sys
import os

from xml.dom import minidom

def parse_run_elem(run):
    " Parse a <run>...</run> elements from xml"

    r = Result(run.getAttribute('name'))
    r.property = run.getAttribute('properties')

    NUMBER_OF_ITEMS = 7
    n = 0
    for col in run.getElementsByTagName('column'):
	title = col.getAttribute('title')
	value = col.getAttribute('value')

	if title == 'status':
	    r.status = value
	    n += 1
	elif title == 'cputime':
	    r.cputime = value
	    n += 1
	elif title == 'walltime':
	    r.walltime = value
	    n += 1
	elif title == 'memUsage':
	    r.memusage = value
	    n += 1
	elif title == 'category':
	    r.resultcategory = value
	    n += 1
	elif title == 'exitcode':
	    r.exitcode = value
	    n += 1
	elif title == 'returnvalue':
	    r.returnvalue = value
	    n += 1
	#else:
	#    r.others[title] = value

        # do not go over all columns when we found
        # what we are looking for
	if n == NUMBER_OF_ITEMS:
            break

    return r

def createToolRun(xmlfl):
    """
    Parse xml attributes that contain the information
    about tool, property and so on
    """

    roots = xmlfl.getElementsByTagName('result')
    assert len(roots) == 1
    root = roots[0]

    tr = ToolRun()
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
    ret = createToolRun(xmlfl)

    for run in xmlfl.getElementsByTagName('run'):
	r = parse_run_elem(run)
	ret.append(r)

    return ret

if __name__ == "__main__":
    import sys
    tr = parse_xml(sys.argv[1])
    tr.dump()
