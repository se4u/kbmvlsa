#!/usr/bin/env python
'''
| Filename    : class_fold_iterator.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Sat Dec  3 10:42:31 2016 (-0500)
| Last-Updated: Sat Dec  3 10:43:18 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 2
'''
import itertools

class FoldIterator(object):
    def __init__(self, n=5, list_to_fold=None, total=None, return_iterables=False):
        assert not (list_to_fold is None and total is None)
        if total is None:
            total=len(list_to_fold)
        assert total == len(list_to_fold)
        assert total%n == 0, "Can not split %d into %d parts"%(total, n)
        self.n = n
        self.i = 0
        self.d = total / n
        self.total = total
        self.return_iterables = return_iterables
        self.list_to_fold = list(list_to_fold)

    def __iter__(self):
        return self

    def next(self):
        if self.i == self.n:
            raise StopIteration
        else:
            test_start = self.i * self.d
            test_end = test_start + self.d
            if self.list_to_fold is not None:
                if self.return_iterables:
                    return ((self.list_to_fold[e] for e in itertools.chain(xrange(0, test_start), xrange(test_end, self.n))),# Train id
                            (self.list_to_fold[e] for e in xrange(test_start, test_end))) # Test id
                else:
                    return ([self.list_to_fold[e] for e in (range(0, test_start) + range(test_end, self.total))],
                            [self.list_to_fold[e] for e in range(test_start, test_end)])
            else:
                if self.return_iterables:
                    return (itertools.chain(xrange(0, test_start), xrange(test_end, self.n)),# Train id
                            xrange(test_start, test_end)) # Test id
                else:
                    return ((range(0, test_start) + range(test_end, self.total)),
                            range(test_start, test_end))
            pass
        pass
