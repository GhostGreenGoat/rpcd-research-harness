# Exact counterexample to the special covariance-lift Bellman potential

Status: exact analytic refutation of the remaining-frame inverse inequality
even for the structured RPCD covariance lift.  This refutes the proposed
potential, not RPCD convergence.

## 1. A rational realization of the RPCD lift

Take `n=9` and

```
A=(I+J)/2,   mu=1/2.                                     (S1)
```

Realize its unit Gram vectors in `R^10` as

```
v_i=(e_0+e_i)/sqrt(2),   1<=i<=9.                        (S2)
```

Their span `S` has dimension nine and Gram matrix `A`; hence an isometry
from `S` to `R^9` gives exactly the usual columns of a square root of `A`.
Although (S2) contains a square root, every rank-one projector

```
R_i=v_i v_i^T=(e_0+e_i)(e_0+e_i)^T/2
```

is rational.  On `Sym(S)` define the genuine covariance-lift projections

```
Pi_i(X)=(I-R_i)X(I-R_i),   Q_i=Id-Pi_i.                  (S3)
```

Each `Pi_i` is an orthogonal projection for the Frobenius inner product and
each `Q_i` has the required RPCD lift form and rank nine.

## 2. Exact symmetry reduction

The subspace of `Sym(S)` fixed by permutations of labels `2,...,9` has the
following rational basis.  Put

```
w_i=e_0+e_i,
a=w_1,
t=2 sum_(i=2)^9 w_i-8w_1,

B_1=aa^T/<a,a>,
B_2=tt^T/<t,t>,
B_3=at^T+ta^T,
B_4=P_S-B_1-B_2.                                        (S4)
```

The full Bellman average commutes with `S_9`.  Its standard-isotypic fixed
subspace inside (S4) has the rational coordinate basis

```
c_1=(-160,160,1,0)^T,
c_2=(28,-35,0,1)^T.                                     (S5)
```

To calculate a leave-one-out inverse it is enough to use the seven
dimensional subspace fixed by permutations of labels `3,...,9`: the three
trivial vectors `w_1,w_2,sum_(3)^9w_i` give six symmetric products and the
seventh basis vector is the projector onto the remaining standard space.
All operator matrices on this block are rational.

For the proposed gap

```
Delta=(Id+sum_i Q_i)^-1
 -(1/9)sum_i Pi_i(Id+sum_(j!=i)Q_j)^-1Pi_i,              (S6)
```

the exact quadratic-form matrix on (S5) is

```
[[ -2212480/7293,      404824/7293       ],
 [    404824/7293,    -252182/36465      ]].             (S7)
```

Its determinant is

```
-121894976/123981<0.                                    (S8)
```

More directly, take `c=c_1+c_2`, or the (S4) coefficient vector

```
c=(-132,125,1,1)^T.
```

The corresponding rational symmetric matrix `X=sum_k c_kB_k` is supported
on `S`, is orthogonal to both fully permutation-invariant directions, and
satisfies the original, untransformed Bellman quadratic inequality with

```
<X,Delta X>_F=-2422114/12155<0.                           (S9)
```

No rank-one embedding shortcut is used: the `Q_i` in (S3) are precisely
the rank-nine structured lift projections.  Equation (S9) therefore closes
the remaining-frame inverse potential both for arbitrary projections and
for the intended special RPCD lift.  It does not imply that the averaged
RPCD epoch lacks an `O(mu)` gap; it only shows that this particular inverse
Bellman majorant cannot prove it.

`scripts/verify_special_lift_bellman_counterexample.py` reconstructs the
seven-dimensional inverses, checks their full ambient residual equations,
and records (S7)--(S9) with exact rational arithmetic.
