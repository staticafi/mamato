
class Tag(object):
    """
    A tag associated to a tool run
    """
    def __init__(self, tag, css=''):
        self._name = tag
        self._css = css

    def setCSS(self, css):
        self._css = css

    def getName(self):
        return self._name

    def getCSS(self):
        return self._css

class TagsManager(object):
    def __init__(self, tags_conf_path='brv/tags.conf'):
        # tool_run_id -> [tags]
        self._mapping = {}
        # tag name -> Tag object
        self._tags = {}
        self._tags_conf_path = tags_conf_path
        # read tags from a file and create
        # css properties describe in the file to them
        self._tagsFromFile(tags_conf_path)

    def _tagsFromFile(self, path):
        f = open(path)
        for line in f:
            line = line.strip()
            if not line:
                continue

            splt = line.split('=')
            assert len(splt) == 2
            name = splt[0].strip()
            self._tags[name] = Tag(name, splt[1].strip())
        f.close()

    def reset(self):
        self._mapping = {}

    def reloadTags(self):
        self._tags = {}
        self._tagsFromFile(self._tags_conf_path)

    def _getOrCreateTag(self, name, css = ''):
        return self._tags.setdefault(name, Tag(name, css))

    def getTags(self):
        return self._tags.values()

    def getToolRunTags(self, toolrun):
        tgs = self._mapping.get(toolrun.getID())
        return tgs if tgs else []

    def addToolRunTag(self, toolrun, tag):
        self._mapping.setdefault(toolrun.getID(), []).append(self._getOrCreateTag(tag))

    def addToolRunTags(self, toolrun):
        if toolrun.tags() is None:
            return

        for tag in toolrun.tags().split(';'):
            self.addToolRunTag(toolrun, tag)

    def setToolRunTags(self, toolrun):
        if self._mapping.get(toolrun.getID()):
            self.remove(toolrun)

        if toolrun.tags() is None:
            return

        for tag in toolrun.tags().split(';'):
            self.addToolRunTag(toolrun, tag)

    def remove(self, toolrun):
        try:
            del self._mapping[toolrun.getID()]
        except KeyError:
            print('No tags for tool {0}'.format(toolrun.getID()))

