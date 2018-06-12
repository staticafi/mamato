#!/usr/bin/python

from . rendering import render_template
from . util import get_elem, getDescriptionOrVersion

def manageTools(wfile, datamanager, args):
    tools = datamanager.getTools()
    tools_sorted = {}
    for t in tools:
        # tools is a list of tool runs where each of the
        # tools has a unique name+version+options attributes
        # We want to divide them to groups according to names
        # and versions. So we have a mapping name -> version -> tools
        nkey = tools_sorted.setdefault(t.name(), {})
        nkey.setdefault(t.version(), []).append(t)
    tools_final = []
    for t in tools_sorted.items():
        tools_final.append((t[0], list(t[1].items())))

    def _none2Empty(x):
        return x if x else ''

    tags_config_file = open('brv/tags.conf')
    tags_config = filter(lambda x: x, map(lambda x: x.strip(), tags_config_file.readlines()))
    tags = list(datamanager.tagsmanager.getTags())

    render_template(wfile, 'manage.html',
                     {'tools' : tools_final,
                      'None2Empty': _none2Empty,
                      'get' : get_elem,
                      'tags': tags,
                      'tags_config': list(tags_config),
                      'descr' : getDescriptionOrVersion})

    tags_config_file.close()

def performDelete(wfile, datamanager, opts):
    run_ids = list(map(int, opts['run']))
    runs = datamanager.getToolRuns(run_ids)

    print("Deleting tool runs '{0}'".format(str(runs)))
    datamanager.deleteToolRuns(runs)

def setToolRunAttr(wfile, datamanager, opts):
    _tags_config = 'tags_config' in opts
    if _tags_config:
       tags_config = open('brv/tags.conf', 'w')
       tags_config.write(opts['tags_config'][0])
       tags_config.close()
       datamanager.tagsmanager.reloadTags()

       return

    if len(opts['run']) != 1:
        print('Incorrect number of tools')
        return

    run_id = int(opts['run'][0])

    _descr = 'description' in opts
    _tags = 'tags' in opts
    if _descr:
        assert len(opts['description']) == 1
        descr = opts['description'][0]
        datamanager.setToolRunDescription(run_id, descr)
    if _tags:
        assert len(opts['tags']) == 1
        tags = opts['tags'][0]
        datamanager.setToolRunTags(run_id, tags)

def adjustEnviron(wfile, datamanager, opts):
    _reload = 'reload' in opts
    if _reload:
        datamanager.reloadData()

