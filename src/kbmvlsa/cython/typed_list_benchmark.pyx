# %load_ext Cython
# %%cython --cplus
'''
| Filename    : typed_list_benchmark.pyx
| Description :
| Author      : Pushpendre Rastogi
| Created     : Sat Dec 24 03:02:29 2016 (-0500)
| Last-Updated: Sat Dec 24 03:04:08 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 3
A benchmark that can be run in an ipython notebook that
shows the difference between a typed list in a class,
and a list object that is casted in reference.
'''

cdef class A:
    cdef public int x

cdef class Alist:
    def __init__(self):
            self.inner = []
    cdef list inner
    cdef void append(self, A a):
        self.inner.append(a)
    cdef A get(self, int i):
        return <A> self.inner[i]
    def __len__(self):
        return len(self.inner)

cdef Alist make_typed_list(int N):
    cdef A a
    cdef int i
    cdef Alist L = Alist()
    for i in range(N):
        a = A()
        a.x = 1
        L.append(a)
    return L

cdef list make_python_list(int N):
    cdef A a
    cdef int i
    cdef list L = []
    for i in range(N):
        a = A()
        a.x = 1
        L.append(a)
    return L

cdef long test_python_list(list L) except -1:
    cdef int i
    cdef long sum = 0
    for i in range(len(L)):
        sum += L[i].x
    return sum

cdef long test_python_list_casted(list L) except -1:
    cdef int i
    cdef long sum = 0
    for i in range(len(L)):
        sum += (<A>L[i]).x
    return sum


cdef long test_python_list_casted_natural(list L) except -1:
    cdef int i
    cdef long sum = 0
    for a in L:
        sum += (<A>a).x
    return sum

cdef long test_python_list_casted_natural_typechecked(list L) except -1:
    cdef int i
    cdef long sum = 0
    for a in L:
        sum += (<A?>a).x
    return sum

cdef long test_typed_list(Alist L) except -1:
    cdef int i
    cdef long sum = 0
    for i in range(len(L)):
        sum += L.get(i).x
    return sum

from time import time
L = make_python_list(10000000)
start = time(); z = test_python_list(L); end = time(); print "Python list", end - start, "s"
start = time(); z = test_python_list_casted(L); end = time(); print "Python list _casted", end - start, "s"
start = time(); z = test_python_list_casted_natural(L); end = time(); print "Python list _casted_natural", end - start, "s"
start = time(); z = test_python_list_casted_natural_typechecked(L); end = time(); print "Python list _casted_natural_typechecked", end - start, "s"

L = make_typed_list(10000000)
start = time()
z = test_typed_list(L)
end = time()
print "Typed list", end - start, "s"

# Python list 0.746551036835 s
# Python list _casted 0.147969007492 s
# Python list _casted_natural 0.127753019333 s
# Python list _casted_natural_typechecked 0.126861095428 s
# Typed list 0.173035860062 s
