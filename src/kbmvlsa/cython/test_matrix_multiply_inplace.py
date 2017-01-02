import numpy as np
from matrix_multiply_inplace import matmul
a = np.random.randn(6, 3).astype('float32')
b = np.asfortranarray(np.random.randn(3, 3).astype('float32'))
c = np.dot(a, b)
a = matmul(a, b)
assert np.linalg.norm(c -  a) < 1e-7
print "Passed"
