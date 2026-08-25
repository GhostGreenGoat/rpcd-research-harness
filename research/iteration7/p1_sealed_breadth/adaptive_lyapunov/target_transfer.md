# Target transfer for the adaptive history/cone route

## Exact target

For every real unit-diagonal SPD `A`, put `mu=lambda_min(A)`.  Each epoch draws a fresh independent
uniform permutation and uses `T_pi=U_(pi_n)...U_(pi_1)`.  The target C050 is a bound, for every
deterministic `x_0` and every integer `k>=0`,

```
E||x_k||_A <= C exp(-c mu k)||x_0||_A
```

with numerical `c,C>0` independent of `A,n,k,x_0`.  This file does not assume C051.

## History-metric transfer

Suppose there are universal `0<c0<1`, `kappa>=1` such that, for
`q=1-c0 mu in (0,1)`, every admissible `A` has permutation-indexed metrics satisfying

```
A <= P_pi <= kappa A,
S(P):=avg_pi T_pi^T P_pi T_pi <= qP_h  for every old label h.
```

Let the boundary metric after epoch `k` be the metric labeled by that epoch's realized permutation.
Freshness and independence give the conditional identity

```
E[x_k^T P_(pi^k)x_k | F_(k-1)] = x_(k-1)^T S(P)x_(k-1).
```

Thus

```
E||x_k||_A^2 <= kappa q^k||x_0||_A^2,
E||x_k||_A   <= sqrt(kappa)exp(-(c0/2)mu k)||x_0||_A.
```

The second line uses Jensen only after controlling the expectation of squared random distance.  It
does not replace it by `||E x_k||_A`.  One epoch costs `n` coordinate updates, so the bound yields
`O((n/mu)log(1/epsilon))` updates, with the additive constant due to `sqrt(kappa)` absorbed because
`kappa` is universal.

## Cone-facet transfer

Let `M(X)=avg_pi T_pi X T_pi^T` and `M*(P)=avg_pi T_pi^T P T_pi`.  Suppose PSD facets and a fixed
row-stochastic routing matrix satisfy

```
P_0=A,
P_j<=kappa A,
M*(P_j)<=q sum_l W_(j,l)P_l.
```

On the PSD covariance cone put `V(X)=max_j tr(P_jX)`.  Then

```
tr(AX) <= V(X) <= kappa tr(AX),
V(M(X)) <= qV(X).
```

For `X_0=x_0x_0^T`, `tr(A M^k(X_0))=E||x_k||_A^2`, so the same expected-distance and update-count
transfer follows.  Individual facets need not dominate `A`; the lower comparison comes from the
distinguished facet `P_0=A`.

The smallest repair uses only two facets.  It is enough to find a PSD tail majorant `R` satisfying

```
R<=kappa A,        M*(A)<=qR,        M*(R)<=qR.
```

Then the preceding argument applies to `V(X)=max{tr(AX),tr(RX)}`.  Moreover any feasible
permutation-history certificate compresses to this form by taking
`R=q^{-1}avg_pi T_pi^T P_pi T_pi`.  Thus the direct target transfer does not require retaining an
`n!`-state metric after the certificate has been found.

This two-facet compression is not lossless for every positive-cone construction.  On the exact
noncommuting rational `n=3` instance recorded in `exact_tail_dual_output.json`, the five-phase max
certificate has `q=3/20,kappa=6/5`, while a rational rank-one Farkas witness proves the two-facet
tail SDP infeasible at the same constants and gives

```
kappa_tail(A,3/20)
 >=211356802264686441/174023970826141000 > 6/5.
```

Thus the relevant direct-C050 repair must allow genuine phase/facet dependence if it is to preserve
the best available comparison constants.  This finite separator changes only the sufficient
architecture: it neither proves nor refutes C050.  Because every feasible permutation-history
certificate with `A<=P_pi<=kappa A` compresses to a two-facet tail with the same `q,kappa`, the
dual witness also refutes that history architecture at `q=3/20,kappa=6/5`.  The five-phase max
escapes because only its maximum, through `P_0=A`, must dominate the target energy; its other
facets are not individually required to dominate `A`.

## Why the non-normal prefactor is mandatory

Both adaptive certificates imply, for all `m>=1`,

```
(M*)^m(A) <= kappa q^m A.
```

Therefore `kappa` controls the full finite-time transient, not merely the spectral radius.  This is
also forced by C050 itself.  Coordinate descent decreases `A`-distance pathwise, so with
`Z_k=||x_k||_A` one has `Z_k<=Z_0`.  Hence

```
E Z_k <= C exp(-c mu k)Z_0
  => E Z_k^2 <= Z_0 E Z_k <= C exp(-c mu k)Z_0^2
  => (M*)^k(A) <= C exp(-c mu k)A.
```

Conversely the last matrix inequality gives C050 by Jensen, with prefactor `sqrt(C)` and exponent
`c/2`.  Thus a bare asymptotic covariance spectral radius without a uniform transient bound does not
complete the target.

## Bounded-horizon phase-reset transfer

The phase route does not need a dimension-uniform number of facets.  Suppose universal
`theta in (0,1)` and `B>0` have the following property: for every admissible `A`, some integer
`1<=m<=B/mu` satisfies

```
(M*)^m(A)<=theta A.
```

Put `q=theta^(1/m)` and define `P_j=q^(-j)(M*)^j(A)` for `j=0,...,m-1`.
Pathwise energy monotonicity gives `(M*)^j(A)<=A`, so every phase satisfies

```
0<=P_j<=q^(-(m-1))A<=theta^(-1)A.
```

The pullback routing is the deterministic cycle

```
M*(P_j)=qP_(j+1)  (j<m-1),       M*(P_(m-1))<=qP_0.
```

Thus `V(X)=max_j tr(P_jX)` has `V(MX)<=qV(X)` and yields, for every deterministic initial point,

```
E||x_k||_A
 <=theta^(-1/2)exp(-[-log(theta)]mu k/(2B))||x_0||_A.
```

This gives the C050 update order directly, with a universal non-normal prefactor.  Conversely,
C050 with constants `C,c` implies `(M*)^k(A)<=C exp(-c mu k)A` by the preceding pathwise argument.
Taking `m=ceil(log(2C)/(c mu))` proves the block condition with `theta=1/2` and
`m<=[log(2C)/c+1]/mu` (using `mu<=1`).  Hence the bounded-horizon block condition and C050 are
quantitatively equivalent up to explicit constant changes.  This equivalence does not assume C051.

For fixed rational `A,m,theta`, failure has the exact PSD-dual certificate

```
X>=0,       <X,theta A-(M*)^m(A)><0.
```

A rank-one `X=zz^T` can be chosen.  Refuting a proposed finite horizon bound requires one such
separator for every allowed `m`; a universal refutation requires a quantified family, not a finite
null search.

## Scope warning

The exact `n=2` and `n=3` artifacts verify this transfer on their stated certificates.  The universal
existence of bounded history metrics or bounded-comparison cone/reset facets remains open.  Failure of
either sufficient architecture would not by itself refute C050, and the frozen identity
`H_[n]=K(A)` does not make C050 and C051 equivalent.

The corrected live edge is the bounded-horizon block contraction above.  Its universal existence is
exactly as hard as C050 under the proved transfer; the finite and symbolic phase-reset controls do
not close that edge.
