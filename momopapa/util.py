from collections import defaultdict


class RownumMaker(object):
    cols = defaultdict(int)
    col = None
    rownum = 0

    @classmethod
    def increment(cls, col):
        cls.cols[col] += 1
        return cls.cols[col]

    @classmethod
    def increment_turbo(cls, col):
        if cls.col == col:
            cls.rownum += 1
        else:
            cls.col = col
            cls.rownum = 1

        return cls.rownum
