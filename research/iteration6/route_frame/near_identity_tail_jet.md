# Uniform second-order jet of the half-memory tail covariance

Status: exact all-dimensional leading-order proof candidate.  The
`O(epsilon^3)` remainder is only fixed-dimensional, so this is not a uniform
neighborhood theorem and does not close RPCD.

Let

```
A=I+epsilon H,
```

where `H=H^T`, `diag(H)=0`, and use `q=ceil(n/2)`.  For a chronological
order, split the strict lower triangle of the permuted `H` into

```
L=L_near+L_far,
```

where `L_far` keeps exactly the entries whose positional gap exceeds `q`.
Local triangular inversion gives, for fixed `n,H`,

```
D=I-epsilon L_near+O(epsilon^2),
F=DM-I=epsilon L_far+O(epsilon^2),
T=F^TD=epsilon L_far^T+O(epsilon^2).                     (J1)
```

Hence the arc-tail covariance from (A3) has the jet

```
S(epsilon)=epsilon^2 E[L_far L_far^T]+O(epsilon^3).      (J2)
```

Put `m=n-q-1`.  Exact sampling without replacement gives

```
p_1=m(m+1)/[2n(n-1)],
p_2=m(m+1)(m-1)/[3n(n-1)(n-2)].                         (J3)
```

For every symmetric zero-diagonal `H`, embedded back in label coordinates,

```
E[L_far L_far^T]
 =p_2 H^2+(p_1-p_2)Diag(diag H^2).                       (J4)
```

Indeed, a fixed ordered pair is separated by more than `q` with probability
`p_1`.  For two distinct row labels and a common column label, both gaps
exceed `q` with probability `p_2`: if the column is at position `r`, there
are `ell=n-q-r` choices for each later row, and
`sum_(ell=1)^m ell(ell-1)=m(m+1)(m-1)/3`.

The coefficients are nonnegative and `p_1<1/8`.  Therefore, if
`||H||<=1`,

```
E[L_far L_far^T]<=p_1 I< I/8.                            (J5)
```

This proves a dimension-free coefficient for the first nonzero covariance
tail term of the *actual* local inverse, not merely the frozen model.  It
also shows that adaptation begins only in the higher-order remainder.

## Uniform row stability beyond the formal jet

There is a useful nonperturbative companion estimate.  Suppose

```
||A-I||<=delta<1.
```

For any local window, write its last inverse row as `d=(a,1)`.  In block
form the triangular solve gives

```
a=-c^T M_prev^-1,
```

where `c` is the current-to-previous cross row and `||c||<=delta`.  The
reverse-order energy inequality (N10) gives

```
M_prev^-1M_prev^-T<=A_prev^-1<=(1-delta)^-1I.
```

Consequently, in every dimension and for every order/window,

```
||d-e_current||<=delta/sqrt(1-delta).                    (J6)
```

If `r=d(A-I)_(window,old)` is a forgotten residual row, then also

```
||r||<=delta sqrt(1+delta^2/(1-delta)).                  (J7)
```

These are dimension-free row estimates.  They do not control the operator
norm of the stack: the skew-Hilbert pathwise barrier shows that many stable
rows can still align logarithmically.  Their role is to constrain the
coefficients in the arc Hardy target (A5), where the leading current-coordinate
parts are mutually orthogonal and only the `O(delta)` row corrections can
align.

The remaining limitation is essential: (J6)--(J7) are rowwise, while
triangular stacks can accumulate with dimension.  Thus (J2) alone does not
provide a radius in `epsilon` uniform over `n`.  Promoting (J5) to a global
theorem requires resumming the higher-order local-solve paths with multirow
orthogonality, precisely the arc/Bessel problem isolated in (A5).

`scripts/verify_near_identity_tail_jet.py` exactly enumerates (J4) for
rational zero-diagonal test matrices in finite dimensions.
