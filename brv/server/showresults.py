#!/usr/bin/python

from . rendering import render_template
from . util import get_elem, getDescriptionOrVersion
from math import ceil
from .. import groupingmanager
from . results.components import *

class ResultsView:
    def __init__(self, runs, buckets, bucket_components, categories, category_components, groupings, scorings, opts):
        self._runs = runs
        self._buckets = buckets
        self._bucket_components = bucket_components
        self._categories = categories
        self._category_components = category_components
        self._opts = opts
        self._groupings = groupings
        self._scorings = scorings

    # TODO this method is way too long
    @classmethod
    def crunchData(cls, datamanager, runs, times_only_solved, grouping):
        def hasAnswers(runs, bset_id, classif):
            assert not runs is None
            assert not bset_id is None

            for run in runs:
                if bset_id != -1:
                    # get stats for one of the categories
                    stats = run.getStats().getStatsByID(bset_id)
                else:
                    # get the overall stats
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
        # there's few of classifications usually, it will be faster in list
        classifications = []
        for run in runs:
            run._stats = datamanager.getToolInfoStats(run.getID())
            for stats in run._stats.getAllStats().values():
                stats.accumulateTime(times_only_solved)
                # a pair (name, id)
                categories.add(BSet(stats.getBenchmarksName(), stats.getBenchmarksID()))
                for c in stats.getClassifications():
                    if c not in classifications:
                        classifications.append(c)

        # extend the selected grouping to avoid hiding non-configured results
        for c in classifications:
            found = False
            for b in buckets:
                if c in b.getClassifications():
                    found = True
            if not found:
                display_name = c[0]
                if display_name == None or len(display_name) == 0:
                    display_name = "<i>&lt;missing classification&gt;</i>"
                buckets.append(groupingmanager.GroupingBucket(display_name, "classif status-{0}".format(c[1]), [c]))

        # only show buckets with results
        buckets = list(filter(lambda b: bucketHasAnswers(runs, b), buckets))
        buckets = list(zip(buckets, range(len(buckets))))
        # give it some fixed order
        cats = [x for x in categories]
        return (buckets, cats)

    @classmethod
    def assemble(cls, datamanager, opts):
        bucket_components = [BucketCountComponent()]
        category_components = []

        run_ids = list(map(int, opts['run']))
        runs = datamanager.getToolRuns(run_ids)
        # parse opts and add components accordingly
        times_only_solved = 'show_times_only_solved' in opts
        if 'show_times' in opts:
            if 'inline_view' not in opts:
                bucket_components.append(BucketTimeComponent())
            category_components.append(CategoryTimeComponent())

        # prepare grouping and categories
        groupingId = 0
        if 'grouping' in opts:
            groupingId = int(opts['grouping'][0])
        grouping = datamanager.getGrouping(groupingId)
        if grouping is None:
            grouping = datamanager.getGrouping(0)
        (buckets, cats) = ResultsView.crunchData(datamanager, runs, times_only_solved, grouping)
        groupings = datamanager.getGroupingChoices()

        # initialize scoring if requested
        scoringId = 0
        if 'scoring' in opts:
            scoringId = int(opts['scoring'][0])
        scoring = datamanager.getScoring(scoringId)
        if scoring is not None:
            category_components.append(CategoryScoreComponent(scoring))

        category_components = list(zip(category_components, range(len(category_components))))
        bucket_components = list(zip(bucket_components, range(len(bucket_components))))
        return cls(runs, buckets, bucket_components, cats, category_components, datamanager.getGroupingChoices(), datamanager.getScoringChoices(), opts)

    def render(self, wfile):
        def _toolsGETList():
            s = ''
            for x in self._opts['run']:
                s += '&run={0}'.format(x)
            return s

        def _getStats(run, bset_id):
            assert not run is None
            assert not bset_id is None

            return run.getStats().getStatsByID(bset_id)

        def _getTotalStats(run):
            assert not run is None
            return run.getStats().getSummary(times_only_solved)

        def _packStatsFunc(bset_id):
            return (lambda run: _getStats(run, bset_id))

        def _lenPlus(o, a):
            return len(o) + a

        times_only_solved = 'show_times_only_solved' in self._opts
        groupingId = 0
        if 'grouping' in self._opts:
            groupingId = int(self._opts['grouping'][0])

        scoringId = 0
        if 'scoring' in self._opts:
            scoringId = int(self._opts['scoring'][0])

        render_template(wfile, 'results.html',
                     {'runs':self._runs, 'benchmarks_sets' : self._categories,
                      'toolsGETList' : _toolsGETList,
                      'showTimes': 'show_times' in self._opts,
                      'showTimesOnlySolved': 'show_times_only_solved' in self._opts,
                      'getStats' : _getStats,
                      'getTotalStats' : _getTotalStats,
                      'get' : get_elem,
                      'descr' : getDescriptionOrVersion,
                      'buckets': self._buckets,
                      'packStatsFunc': _packStatsFunc,
                      'inlineView': 'inline_view' in self._opts,
                      'bucketComponents': self._bucket_components,
                      'lenPlus': _lenPlus,
                      'categoryComponents': self._category_components,
                      'groupings': self._groupings,
                      'scorings': self._scorings,
                      'scoringId': scoringId,
                      'groupingId': groupingId })

def showResults(wfile, datamanager, opts):
    if not 'run' in opts:
        wfile.write(b'<h2>No runs of tools given</h2>')
        return

    view = ResultsView.assemble(datamanager, opts)
    view.render(wfile)
