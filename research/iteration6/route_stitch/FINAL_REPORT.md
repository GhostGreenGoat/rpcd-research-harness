# Iteration 6 Route C final report: spectral stitching and extremal geometry

Date: 2026-08-22 (Asia/Shanghai)

Status: completed after the required two-hour active interval.  All theorem
language below means an **internal proof candidate at the stated evidence
level**.  There is no Lean/formal proof or external review, and the
unrestricted RPCD half-depth conjecture remains open.

## Executive result

This route did not prove the general target and found no RPCD counterexample.
It did substantially shrink and reorganize the unresolved region:

1. A dimension-free boundary-ray comparison and a tunable low/high shorted
   stitch were proved exactly.
2. The exterior certificate was converted into a one-scalar spectral test and
   then proved on broad new all-dimensional regions: at most two subunit
   eigenvalues, arbitrary constant-diagonal rank-two or rank-three isotropic
   low projectors, and a finite extremal reduction for any fixed number of
   subunit modes.
3. Exact hostile controls show why compression, convex endpoint interpolation,
   orbit symmetrization, and scalar spectral mixing cannot close the remaining
   case.
4. I independently reconstructed the general `L3` proof candidate and four
   structured `W4` slices.  In particular the uniform shifted-inverse lemma
   now passes independent audit for a weighted three-vertex path plus isolates
   in every child dimension `d>=6`.

## Avenue A: spectral projection and boundary stitching

For a singular unit-diagonal correlation matrix `C`, put
`A_mu=mu I+(1-mu)C`.  The chronological factors satisfy the exact pathwise
identity

```text
M_pi(mu)=M_pi(0)[(1-mu)I+mu M_pi(0)^-1].
```

Since `Sym M_pi(0)=(I+C)/2>=I/2`, one gets

```text
K(A_mu)>=(1+mu)^(-2)K(C),
||K(A_mu)-K(C)||<=12mu(2+mu)/(1+mu)^2.
```

If the full Loewner shorted boundary certificate is
`K(C)>=kappa P_tau`, combining it with the exact `J2` high-space polynomial
gives a harmonic-mean coefficient

```text
c_stitch=b r_tau/(b+r_tau),  b=kappa/(1+mu)^2,
```

with the empty-high-space case explicitly defined by `r_tau=+infinity`.
For a fixed boundary ray this yields an explicit bridge out to
`mu<=delta_+/(n-1+delta_+)`.  The result is exact but conditional on the full
shorted low-space certificate; mere compression is insufficient.

## Avenue B: convex/extremal correlation geometry

An exact rank-two extreme elliptope point disproves reduction to signed
rank-one boundary matrices and quantifies the gap between low-space
compression and Loewner shorting.  The extremal rank count
`r(r+1)/2<=n` further shows that large-dimensional extreme points naturally
create a low spectral layer of dimension `n-O(sqrt(n))`.

The positive outcome is a new exterior spectral region.  If
`r=ceil(n/2)` and `mu=lambda_min(A)`, the exterior certificate is sufficient
exactly when

```text
e_(r-1)(lambda_2,...,lambda_n)>=binom(n,r)/2.
```

Its coefficients obey the pair-difference identity

```text
v_i-v_j=(lambda_i-lambda_j)e_(r-1)(lambda excluding i,j)/binom(n,r),
```

so the only bottleneck is the minimum eigenspace.  Independent hostile audit
passes the following internal E4 candidates:

- every matrix with at most two eigenvalues strictly below one;
- constant-diagonal rank-two low projectors, all `n>=3` and all `mu`;
- constant-diagonal rank-three low projectors, all `n>=4` and all `mu`;
- the finite vertex reduction for at most `s` subunit modes, with exact vertex
  range `1<=p<=min(s,n-1)`.

Rank-four isotropic and arbitrary three-low exact examples mark the boundary
of this exterior route.

## Avenue C: interpolation and continuation

The multiplicative comparison above survives hostile checks, but simpler
interpolation principles fail already for `n=2`.  The endpoint chord gap is
exactly `-mu(1-mu)I/2`, and the change from the identity endpoint is
indefinite.  Thus a successful continuation proof must preserve separate
low/high sectors or chronological-factor geometry; it cannot be a scalar
convex interpolation.

The determinant-tail high-`mu` band has the exact scaling limit

```text
D(c)=(1-e^(-c/2))/c +(1/2)e^(-c)(1+c/2),
```

for `mu=1-c/n`.  It is strictly decreasing and crosses `1/2` once at
`c_*=1.7298443299...` (decimal diagnostic).  The unresolved mesoscale starts
beyond this band and also escapes the fixed-boundary norm stitch.

## Independent Bellman audits

The sibling `L3` Schur-compensation proof was rebuilt from definitions,
including the `d=3` and `d=2` exceptional Bernstein branches, Schur range
conditions, the `beta/s` factor, and the negative-`q` high-`mu` direction.
Verdict: PASS as an internal E4 candidate for

```text
L3(A)>=(2mu/m)A^-1,  m>=3.
```

This closes the half-depth target for every `n<=6`.

Four further uniform shifted-inverse slices passed independent audit:

- arbitrary matching-support child matrices, every `d>=6`;
- a weighted three-vertex path plus three isolates at `d=6`;
- the same weighted path plus `d-3` isolates for every `d>=6`.
- an equal-magnitude `K_(1,p)` star plus isolates for every
  `p>=3,d>=max(6,p+1)`.

For the all-dimensional path theorem I independently checked the positive
scaling, all powers of `k=d-6`, positive denominators, exact `t` valuations,
and every one of the seven principal-minor Bernstein certificates.  These
remain structured `W4` results, not the universal fourth-level lemma.

## Current regime map

Any counterexample to the half-depth matrix target must now satisfy all of

```text
n>=7,
negative_inertia(A-I)>=3,
a_(n,r)(mu)<mu/2,
e_(r-1)(lambda_2,...,lambda_n)<binom(n,r)/2.
```

For `mu=1-c/n`, it must also have `c>=c_*+o(1)` to escape the scalar tail.
This identifies the remaining case as genuinely multi-low-mode and
multiscale, with nontrivial low/high cross geometry.

## Evidence levels and unresolved issue

- Internal E4: independently reconstructed `L3`; at-most-two-subunit,
  rank-two/rank-three and finite-extremal exterior regions; matching and
  weighted-three-path `W4` slices.
- E3: the general conditional low/high shorted stitch and exact analytic
  regime deductions where no second reconstruction was requested.
- E2: exact rational/symbolic barriers and fixed examples.

No numerical null search is used as proof.  The next smallest unsupported
`W4` geometries include a four-vertex path, a cycle, and unequal-weight
degree-three stars.
At half depth, the central missing object remains a growing-depth certificate
that transports the full shorted low-space state rather than a scalar bound.

## Portable reproduction

From the repository root, using Python 3 with SymPy:

```powershell
python research/iteration6/route_stitch/verify_extremal_geometry.py
python research/iteration6/route_stitch/verify_spectral_rank2_region.py
python research/iteration6/route_stitch/verify_continuation_obstructions.py
python research/iteration6/route_stitch/independent_l3_audit.py
python research/iteration6/route_stitch/independent_w4_matching_audit.py
python research/iteration6/route_stitch/independent_w4_three_path_audit.py
python research/iteration6/route_stitch/independent_w4_three_path_all_d_audit.py
python research/iteration6/route_stitch/independent_w4_equal_star_audit.py
```

The Markdown proofs and committed JSON snapshots make the route transferable
between accounts; no credentials, `.codex`, `auth.json`, or `.env` data are
used.

## Timing

- Root-observed start bound: `2026-08-22T16:34:10+08:00`.
- Local observed start: `2026-08-22T16:35:07.9149419+08:00`.
- Required local threshold: `2026-08-22T18:35:07.9149419+08:00`.
- Actual final verification end: `2026-08-22T18:35:47.1038278+08:00`.
- Active elapsed time through final verification: `02:00:39.1888859`
  (`7239.1888859` seconds).
