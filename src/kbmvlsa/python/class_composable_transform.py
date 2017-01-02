#!/usr/bin/env python
'''
| Filename    : class_composable_transform.py
| Description : A General class to compose transforms
| Author      : Pushpendre Rastogi
| Created     : Mon Dec  5 11:48:58 2016 (-0500)
| Last-Updated: Mon Jan  2 15:53:03 2017 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 5
ComposableTransform provides a way to register unit-callables to strings.
It is a natural way to compose functions on the basis of string concatenations.

unit-callables are (single input, single output) functions.
'''
class ComposableTransform(object):
    def __init__(self, callables, language, sep='_'):
        '''
        callables : A dictionary of component to function maps
                    Example: dict(IDENTITY=(lambda _: _),
                                  SQROOT=(lambda x: sqrt(x, out=x)))
        language  : A set of acceptable compositions of functions.
        sep       : The string used to separate components in the string
                    representation (default '_')
        --- OUTPUT ---
        '''
        self.callables = callables
        self.language = language
        self.sep = sep
        for k in callables:
            callables[k].name = k
        self.NS = Exception()
        for e in language:
            setattr(self.NS, e, e)
        return

    @staticmethod
    def compose(chain):
        def compose_impl(arg):
            for f in reversed(chain):
                arg = f(arg)
            return arg
        compose_impl.chain = chain
        return compose_impl

    def parse(self, s):
        '''Take a string from language and create a callable corresponding to it.
        The returned callable is capable of taking a matrix and modifying it inplace.
        '''
        assert s in self.language
        f = self.compose([self.callables[_e]
                             for _e
                             in s.split(self.sep)])
        f.__doc__ = s
        return f

    def decompile(self, composition):
        return self.sep.join(e.name for e in composition.chain)
