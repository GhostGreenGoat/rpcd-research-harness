# Random-window decomposition of the linear-memory frame

Status: exact identity (E2/E3 proof candidate) and an exact structured
obstruction to row-by-row lower bounds.  This clarifies, but does not close,
the generic preconditioner lemma.

Let `A_r(B)` denote the expected outer product of the solve row at position
`r` of a uniform random order, embedded in the original coordinates.  Then

```
J_t(B)=sum_(r=1)^t A_r(B),
A_r(B)=J_r(B)-J_(r-1)(B) >=0.                             (W1)
```

For the `q`-step local inverse `D_(pi,q)`, the row at position `k` is the full
last solve row on its ordered window of `min(k,q+1)` most recent labels.  A
window in a uniform permutation is itself a uniform ordered tuple.  Therefore

```
P_q(B):=E[D_(pi,q)^T D_(pi,q)]
 =sum_(r=1)^q A_r(B)+(n-q)A_(q+1)(B)
 =J_q(B)+(n-q)[J_(q+1)(B)-J_q(B)].                        (W2)
```

This is an exact, all-dimensional without-replacement identity.  In
particular `P_q>=J_q`, which explains the strong small-dimensional scans of
the new feature.  But using a conjectured half-prefix lower bound for `J_q`
to prove the same lower bound for `P_q` would be circular.  A successful
generic argument must exploit the repeated last-window term in (W2), or a
different mixture of window lengths.

## A rowwise marginal lower bound is impossible

For positive equicorrelation, the parallel eigenvalue of the position-`r`
increment is exactly

```
lambda_parallel(A_r)=mu^(2(r-1))/n.                       (W3)
```

Indeed, a parallel right side produces chronological solves
`1,mu,mu^2,...`.  For fixed `0<mu<1` and `r=ceil(n/2)`, the normalized
parallel strength of this individual row is

```
[n-(n-1)mu] mu^(2r-2)/mu ->0.                             (W4)
```

Thus no proof can assign a dimension-free share of the target separately to
each late local window.  The surviving equicorrelation lower bound comes
from the whole geometric sum in `J_q`, not from the amplified last-window
term.

## Mixtures and the weighted hierarchy

A position-weighted local frame can realize any nonnegative combination of
the increments `A_r`.  In particular

```
C_t=J_t-(1/2)J_(t-1)
   =A_t+(1/2)sum_(r<t)A_r.                                (W5)
```

So the weighted-prefix hierarchy is exactly a positive random-frame mixture,
not merely a formal subtraction of matrices.  It can be inserted into the
general dual/Rayleigh lemma by taking the corresponding position-weighted
random `R_pi`.  What remains is its second moment
`Q=E[R_pi M_pi M_pi^T R_pi]`: a lower bound on the mean frame `P=C_t` alone
does not control this covariance.  The exact direct- and weighted-adjacency
counterexamples show why replacing that covariance by a scalar/Jensen term
is unsafe.

`scripts/verify_window_mixture_identity.py` independently reconstructs (W2)
with exact rational arithmetic.  The identity neither proves the weighted
hierarchy nor the RPCD conjecture; it identifies the precise random-frame
object to which a future martingale or matrix-Bessel estimate must apply.
