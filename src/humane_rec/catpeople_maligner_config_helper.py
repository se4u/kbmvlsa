class Sequential_Policy(object):

    def __init__(self):
        self.prev_call = -1

    def __call__(self, maxcall):
        ret = (self.prev_call + 1) % maxcall
        self.prev_call = ret
        return ret

    @classmethod
    def __str__(cls):
        return cls.__name__


class Fixed_Iter_Convergence(object):

    ''' When called this function object returns "True"
    if we have converged.
    '''

    def __init__(self, max_iter=10):
        self.max_iter = max_iter
        self._call_count = 0

    def __call__(self, _blfs):
        ret = (self._call_count >= self.max_iter)
        self._call_count += 1
        return ret

    def reset(self):
        self._call_count = 0

    def __str__(self):
        return 'Fixed_Iter_Convergence(max_iter=%d)'% self.max_iter
