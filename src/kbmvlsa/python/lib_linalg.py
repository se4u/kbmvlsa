#!/usr/bin/env python
'''
| Filename    : lib_linalg.py
| Description : Library of Linear Algebra functions
| Author      : Pushpendre Rastogi
| Created     : Mon Dec  5 12:33:48 2016 (-0500)
| Last-Updated: Wed Dec  7 04:33:40 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 2
'''
def arrange(A, B, C, D):
    d
def incremental_pca_update(x, U, S):
    r = U.shape[1]
    b = x.shape[1]
    xh = np.dot(U.T, x)
    H = x - np.dot(U, xh)
    [J, W] = numpy.linalg.QR(H, mode='reduced')
    Q = numpy.concat([numpy.concat([diag(S), xh]), numpy.concat([zeros(b,r), W])])

    U_new, S_new = svd(Q)
    St_new=St_new(1:r);
    Ut_new=[U J] * Ut_new(:, 1:r);

function [Ut_new, St_new]=batch_incremental_pca(x, U, S)
r = size(U, 2);
b = size(x, 2);

xh = U'*x;
H = x - U*xh;
[J, W] = qr(H, 0);
Q = [diag(S)     xh ;...
     zeros(b,r)  W];
[Ut_new, St_new, ~]=fastsvd(Q);
St_new=St_new(1:r);
Ut_new=[U J] * Ut_new(:, 1:r);

end

function [U, S, V]=fastsvd(M) %#ok<INUSD>
% Ideally I want to exploit the c-bordered diagonal structure of the matrix
% (see Matthew Brand's 2002 Incremental SVD paper) however I am taking the
% easy route for now and doing standard SVD. But at least I convert the
% stupid identity matrix to its diagonal form.
[U, S, V]=svd(M);
S=diag(S);
end
