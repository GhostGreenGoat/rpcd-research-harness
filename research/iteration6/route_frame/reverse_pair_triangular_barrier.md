# Reverse-order pairing still does not control the covariance

Status: analytic counterexample family to the proposed **pairwise** estimate
`Q_pi+Q_rev <= Gamma (R_pi+R_rev)`.  This is not a counterexample to the
full permutation average.

Use the bipartite skew-Hilbert family of
`pathwise_triangular_projection_barrier.md`, with `n=2a`, `q=a`,
`tau=1/4`, and write

```
C=G+U,   G=stril(C,-1),   U=-G^T.
```

For the order which puts the two bipartite groups consecutively, in the
original coordinates

```
D=[[I,0],[tau G^T,I]],   E=DM=[[I,0],[tau G,I]].          (V1)
```

The matrix `A` is invariant under reversal of all `2a` positions: internal
reversal sends `C` to `-C` while reversal also exchanges the two groups.
Consequently the matrices for the reversed order, embedded back in the same
coordinates, are exactly

```
D_rev=D^T,   E_rev=E^T.                                  (V2)
```

Let `u=1 in R^a` and `x=(u,0)`.  Put

```
h=G^T u,   k=(G^T)^2 u.
```

The paired frame denominator and covariance numerator are

```
x^T(R+R_rev)x = 2a+tau^2 ||h||^2,                        (V3)

x^T(Q+Q_rev)x
 = ||u+tau^2 k||^2+tau^2||h||^2
   +||u||^2+tau^2||Gu||^2
 >=tau^4||k||^2.                                        (V4)
```

All entries involved in the lower bound are nonnegative.  Suppose that
`a>=8` is divisible by four.  With zero-based indices,

```
h_i=H_(a-1-i),
k_j=sum_(i=j+1)^(a-1) h_i/(i-j).
```

For each `0<=j<a/4`, restricting the last sum to
`j+1<=i<=a/2` gives

```
k_j >= log(a/2) log(a/4).                                (V5)
```

Also `||h||^2<=a(1+log a)^2`.  Hence the generalized paired Rayleigh
quotient is at least

```
 [tau^4 log(a/2)^2 log(a/4)^2]
 -------------------------------------------------- ,    (V6)
 4[2+tau^2(1+log a)^2]
```

which diverges like a positive multiple of `log(a)^2`.  Since the spectral
floor of this family obeys `mu>=1-pi/4>0`, even allowing a factor `1/mu`
does not save a dimension-free reverse-pair inequality.

Thus a complement argument cannot stop after coupling an order only with
its reversal.  It must average over the internal early/late ranks (or use a
stronger martingale/Gram mechanism).  The full average has `(2a)!` orders,
so (V6) does not refute the desired averaged covariance inequality.

`scripts/verify_reverse_pair_barrier.py` reconstructs (V1)--(V4) exactly
for finite rational examples.
