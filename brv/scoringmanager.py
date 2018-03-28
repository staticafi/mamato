import json

class ScoringEntry:
    def __init__(self, classification, points):
        """
        Classification is a pair (result, classif)
        Points is an integer
        """
        self._classification = classification
        self._points = points

    @classmethod
    def fromConfig(cls, config):
        return cls((config["result"], config["class"]), config["points"])

    def getClassification(self):
        return self._classification

    def getPoints(self):
        return self._points

class ScoringScheme:
    def __init__(self, display_name, entries):
        self._display_name = display_name
        self._entries = entries

    @classmethod
    def fromConfig(cls, conf):
        entries = []
        entries = list(map(lambda x: ScoringEntry.fromConfig(x), conf["scoring"]))
        return cls(conf["displayName"], entries)

    def getDisplayName(self):
        return self._display_name

    def getPoints(self, classification):
        for entry in self._entries:
            if entry.getClassification() == classification:
                return entry.getPoints()
        return 0

class ScoringManager:
    def __init__(self):
        self._schemes = []
        self._config = {}
        self._choices = []
        self._loadSchemes()

    def _loadSchemes(self):
        schemes = []
        with open('brv/scoring.json') as scoring_file:
            self._config = json.load(scoring_file)
            schemes = self._config["schemes"]

        if schemes is None:
            schemes = []

        for (s, i) in zip(schemes, range(1, 1+len(schemes))):
            scheme = ScoringScheme.fromConfig(s)
            self._schemes.append(scheme)
            self._choices.append((scheme.getDisplayName(), i))

    def getScoringScheme(self, i):
        if i == 0:
            return None
        return self._schemes[i-1]

    def getScoringChoices(self):
        return self._choices
