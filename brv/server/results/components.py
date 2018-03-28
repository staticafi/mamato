#!/usr/bin/python

from math import ceil

# define utility functions here
def formatTime(time, round_to_largest):
    "Transform time in seconds to hours, minutes and seconds"
    if not time:
        return '0 s'
    ret = ''
    time = ceil(time)
    if time >= 3600:
        hrs = time // 3600
        time = time - hrs*3600
        ret = '{0} h'.format(int(hrs))
        if round_to_largest:
            return ret
    if time >= 60 or ret != '':
        mins = time // 60
        time = time - mins*60
        ret += ' {0} min'.format(int(mins))
        if round_to_largest:
            return ret
    if ret != 0:
        return ret + ' {0} s'.format(int(time))
    else:
        return '0 s'

class CategoryComponent:
    def __init__(self):
        pass

    def getDisplayName(self):
        pass

    def render(self, run, stats):
        return self.getValue(run, stats)

    def getValue(self, run, stats):
        pass

    def getStyle(self):
        return ''

class CategoryTimeComponent(CategoryComponent):
    def __init__(self, round_to_largest):
        self._round_to_largest = round_to_largest

    def getDisplayName(self):
        return 'CPU Time'

    """
    Return String
    """
    def getValue(self, run, stats):
        result = '0 s'
        if stats:
            result = formatTime(stats.getAccTime(), self._round_to_largest)
        return result

    def getStyle(self):
        return 'background-color: #A5D5E6;'

class CategoryScoreComponent(CategoryComponent):
    def __init__(self, scoring):
        self._scoring = scoring

    def getDisplayName(self):
        return 'Score'

    def getValue(self, run, stats):
        if not stats:
            return '0'
        classifications = stats.getClassifications()
        score = 0
        for classif in classifications:
            score += stats.getCount(classif) * self._scoring.getPoints(classif)
        return str(score)

    def getStyle(self):
        return 'background-color: #A5D5E6;'

# define CategoryComponent-s here

class BucketComponent:
    def __init__(self):
        pass

    def getDescription(self):
        pass

    """
    Return string
    """
    def render(self, run, bucket, stats):
        return self.getValue(run, bucket, stats)

    """
    Return String
    """
    def getValue(self, run, bucket, stats):
        pass

class BucketCountComponent(BucketComponent):
    def __init__(self):
        pass

    def getDescription(self):
        return 'count of results'

    def render(self, run, bucket, stats):
        return ''.join([
                '<span class="', bucket.getNameClass(), '">',
                '<abbr title="', bucket.getDisplayName(), '">',
                self.getValue(run, bucket, stats),
                '</abbr></span>'
        ])

    def getValue(self, run, bucket, stats):
        result = 0
        if stats:
            for classif in bucket.getClassifications():
                result += stats.getCount(classif)
        return str(result)

class BucketTimeComponent(BucketComponent):
    def __init__(self):
        pass

    def getDescription(self):
        return 'Time elapsed'

    def render(self, run, bucket, stats):
        return ''.join([
            '<span style="font-size: 11px">',
            self.getValue(run, bucket, stats),
            '</span>'
        ])

    def getValue(self, run, bucket, stats):
        result = 0
        if stats:
            for classif in bucket.getClassifications():
                result += stats.getTime(classif)
        return formatTime(result, False)

# define BucketComponent-s here
