from . rendering import render_template
from .. import groupingmanager

class RunsData:
    def __init__(self, datamanager, run_ids, grouping, times_only_solved=False):
        def hasAnswers(runs, bset_id, classif):
            assert not runs is None
            assert not bset_id is None

            for run in runs:
                if bset_id != -1:
#get stats for one of the categories
                    stats = run.getStats().getStatsByID(bset_id)
                else:
#get the overall stats
                    stats = run.getStats().getSummary(times_only_solved)
                if not stats is None and stats.getCount(classif) != 0:
                    return True

            return False

        def bucketHasAnswers(runs, bucket):
            classifs = bucket.getClassifications()
            for classif in classifs:
                if hasAnswers(runs, -1, classif):
                    return True
            return False

        class BSet(object):
            def __init__(self, name, bid):
                self.name = name
                self.id = bid

            def __hash__(self):
                return self.id

            def __eq__(self, oth):
                return self.id == oth.id

        categories = set()
        buckets = grouping.getBuckets()
#there's few of classifications usually, it will be faster in list
        self.classifications = []
        runs = datamanager.getToolRuns(run_ids)
        for run in runs:
            run._stats = datamanager.getToolInfoStats(run.getID())
            for stats in run._stats.getAllStats().values():
                stats.accumulateTime(times_only_solved)
#a pair(name, id)
                categories.add(BSet(stats.getBenchmarksName(), stats.getBenchmarksID()))
                for c in stats.getClassifications():
                    if c not in self.classifications:
                        self.classifications.append(c)

#extend the selected grouping to avoid hiding non - configured results
        for c in self.classifications:
            found = False
            for b in buckets:
                if c in b.getClassifications():
                    found = True
            if not found:
                display_name = c[0] + c[1]
                if display_name == None or len(display_name) == 0:
                    display_name = "<i>&lt;missing classification&gt;</i>"
                buckets.append(groupingmanager.GroupingBucket(display_name, "classif status-{0}".format(c[1]), [c]))

#only show buckets with results
        buckets = list(filter(lambda b: bucketHasAnswers(runs, b), buckets))
        self.buckets = list(zip(buckets, range(len(buckets))))
#give it some fixed order
        self.cats = [x for x in categories]
        self.runs = runs

class FilesData:
    def __init__(self, datamanager, run_ids, runs, cats, buckets):
        tables = []
#retrieve tables for all categories
        for cat in cats:
            tables += list(datamanager.getRunInfos(cat.id, run_ids).getRows().items())
        self.tables = tables
        self.buckets = buckets
        self.runs = runs

    def getBucket(self, runInfo):
        for bucket in self.buckets:
            for (result, classif) in bucket.getClassifications():
                if runInfo.status() == result and runInfo.classification() == classif:
                    return bucket
        assert False, "no bucket found"

    def calculate(self, different_only):
        transitions = {}
        for runInfosTable in self.tables:
            benchmark = runInfosTable[0]
            runInfos = runInfosTable[1]
            prev = None

            valid = True
            tempTransitions = {}

            for (toolRun, runInfo) in zip(self.runs, runInfos):
                # if the benchmark was not run with some version of a tool, it should not be included
                if runInfo is None:
                    valid = False
                    break

                now = (toolRun, self.getBucket(runInfo).getDisplayName())
                if prev is not None:
                    # if they belong in the same bucket, discard the transition
                    if different_only and prev[1] == now[1]:
                        continue
                    if not (prev, now) in tempTransitions:
                        tempTransitions[(prev, now)] = 0
                    tempTransitions[(prev, now)] += 1
                prev = now

            # only if the transitions are valid, add them to the result
            if valid:
                for (k, v) in tempTransitions.items():
                    if not k in transitions:
                        transitions[k] = 0
                    transitions[k] += v

        return transitions

class DiagramView:

    def __init__(self, runs, groupingId, blacklist, grouping, groupings, buckets, cats, transitions):
        self.runs = runs
        self.blacklist = blacklist
        self.groupingId = groupingId
        self.groupings = groupings
        self.grouping = grouping
        self.buckets = buckets
        self.cats = cats
        self.transitions = transitions

    @classmethod
    def assemble(cls, datamanager, opts):
        blacklist = []
        if 'blacklist' in opts:
            blacklist = opts['blacklist']
        groupingId = 0
        if 'grouping' in opts:
            groupingId = int(opts['grouping'][0])
        grouping = datamanager.getGrouping(groupingId)
        run_ids = list(map(int, opts['run']))
        runs = RunsData(datamanager, run_ids, grouping)
        files = FilesData(datamanager, run_ids, runs.runs, runs.cats, grouping.getBuckets())
        transitions = files.calculate(True)
        result = cls(runs.runs, groupingId, blacklist, grouping, datamanager.getGroupingChoices(), runs.buckets, runs.cats, transitions)
        return result

    def render(self, wfile):
        def get_elem(a, n):
            return a[n]

        def print_row_mapping(transitions):
            result = ''
            for (i, (k, v)) in zip(range(len(transitions)), transitions.items()):
                result += str(i) + ': {'
                result += 'runs: ['
                for t in k:
                    result += '{'
                    result += 'toolrun: ' + str(t[0].getID()) + ','
                    result += 'bucket: "' + t[1] + '"'
                    result += '},'
                result = result [:-1]
                result += ']'
                result += '},'
            result = result [:-1]
            return result

        def print_transitions(transitions):
            result = ''
            for (k, v) in transitions.items():
                result += '['
                for t in k:
                    result += '"' + (t[1].upper() + ' ' + t[0].run_description()).replace('"', '\"') + '"' + ',' + '\n'
                result += str(v) + '],'
            result = result [:-1]
            return result

        render_template(wfile, 'diagram.html', {
            'get': get_elem,
            'runs': self.runs,
            'printTransitions': lambda: print_transitions(self.transitions),
            'printRowMapping': lambda: print_row_mapping(self.transitions),
            'buckets': self.buckets,
            'grouping': self.grouping,
            'groupingId': self.groupingId,
            'groupings': self.groupings,
        })

def showDiagram(wfile, datamanager, opts):
    if not 'run' in opts:
        wfile.write(b'<h2>No runs of tools given</h2>')
        return

    view = DiagramView.assemble(datamanager, opts)
    view.render(wfile)
