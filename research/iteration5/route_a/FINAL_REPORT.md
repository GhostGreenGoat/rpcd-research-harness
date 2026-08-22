# Iteration 5 Route A final report

Status: **partial but materially advanced**.  The general inequality

```
H_ceil(n/2)(B) >= (mu/2)B^-1
```

remains open.  This run did not find a counterexample to it.  It produced a
new linearly growing random-order state, proved several restricted/general
lemmas, and exactly closed multiple tempting fixed-memory routes.

## 1. Direct answer from this route

The central lesson is now quantitative rather than heuristic:

- remembering only permutation position or one adjacent edge is insufficient;
- for the natural local-triangular-inverse dual family, every bandwidth
  `q=o(n)` fails the sharp half certificate in the scaling `rho=c/n`;
- bandwidth `q=Theta(n)` survives that obstruction and admits an analytic
  half-limit proof plus a finite positive constant on the complete positive
  equicorrelation family;
- generically, the missing step is a matrix frame bound for the *joint*
  conditional-tail rows.  Each row separately has a sharp Schur-complement
  bound, but scalar summation is exactly too weak.

Internally audited proof candidates establish the requested `O(n/mu)` update
order within two nontrivial regimes:

1. every positive equicorrelation and diagonal-sign conjugate, using the
   half-memory state, with full-epoch constant `25/98`;
2. every unit-diagonal SPD matrix satisfying `n(1-mu)<=1`, using a uniform
   Frobenius/dual bound, with full-epoch constant `1/4`.

The second is a new leaf-free dual certificate on a general all-matrix
spectral slice (not a priority claim, and not a claim that the previously
known determinant-tail high-`mu` recurrence covers less).  In the smaller band
`n(1-mu)<=2-sqrt(2)`, it proves the sharp global half constant and a direct
half-prefix constant `1/4`.  The global spectral-band proof was independently
audited by Route C with no blocker; the later direct-prefix corollary uses the
same pathwise norm bound but was not separately discussed in that audit.

## 2. Avenue A: remaining-gradient/random-prefix potential

The scalar child-floor closure fails even when every actual child floor is
retained.  An exact lifted rational `n=4` Gram example makes its proposed
quadratic form negative on `(1,1,-1,-1)`; see
`evidence/dual_and_potential_controls.json`.

The replacement is the exact generic local-inverse Schur lemma.  If `d` is a
row which exactly solves its recent window `T`, and `r` is its forgotten old
tail, then

```
sigma=dB_Td^T=2-||d||^2,
rB_O^-1r^T <=sigma-mu||d||^2<=1-mu.
```

This is a matrix-valued conditional-variance estimate, valid pathwise for
every matrix/order/window.  However, the hoped-for extra `|O|/n` damping is
false by an exact `n=5,q=2` rational example with ratio `0.9218...>2/5`.
The unresolved work is therefore inter-row cancellation, not a sharper
single-row scalar potential.

## 3. Avenue B: averaged frame/without-replacement structure

For the `q`-step local inverse, let `A_r=J_r-J_(r-1)` be the expected
position-`r` row frame.  Exact window symmetry gives

```
P_q=E[D_q^TD_q]
   =sum_(r<=q)A_r+(n-q)A_(q+1)
   =J_q+(n-q)(J_(q+1)-J_q).
```

The identity was reconstructed with exact rational permutation arithmetic.
It shows why the state is strong, but also why using the desired lower bound
for `J_q` would be circular.  On positive equicorrelation the individual late
increment is `mu^(2r-2)/n` in the parallel block and can be exponentially
weak; a row-by-row lower bound cannot work.

The weighted hierarchy has the exact positive-frame representation

```
C_t=J_t-(1/2)J_(t-1)=A_t+(1/2)sum_(r<t)A_r.
```

Thus its remaining problem is explicitly a second-moment/covariance estimate
for a random frame, not positivity of the mean.

## 4. Avenue C: dual/Rayleigh certificates

Completing a matrix square gives, for any random `R_pi`,

```
K >=P W+W^TP^T-W^TQW,
P=E R_pi,
Q=E[R_pi^T M_pi M_pi^T R_pi].
```

Optimizing deterministic `W` gives `K>=P Q^-1P^T`.  This exact lemma exposes
which random-order information a certificate retains.

Three restricted states were exactly refuted with separate provenance:

- positional diagonal weights: optimum below one half at `n=20` on the
  signed-rank-one boundary;
- direct adjacency `R=D^T`: positive equicorrelation `n=20,rho=1/2`, parallel
  value `9261/18985=1/2-463/37970`;
- weighted adjacency `R=D^TD`: positive equicorrelation `n=50,rho=1/10`,
  parallel value
  `75142223/160062876=1/2-4889215/160062876`.

For fixed `rho`, the last certificate is asymptotic to
`3/[n rho(1-rho)]`, so it cannot prove *any* dimension-free constant.

The successful replacement is a local inverse with bandwidth `q`.  It is
exact at `q=n-1`.  On positive equicorrelation,

```
D_ij=-rho mu^(i-j-1)  for 1<=i-j<=q,
(D_qM-I)_ij=rho mu^q for i-j>q.
```

For `rho=c/n`, `q/n->alpha`, the certificate has a closed continuum formula.
At `alpha=0` it is below half for
`c>(3+sqrt(21))/2`, proving that `q=o(n)` is impossible.  At
`alpha=1/2`, an all-positive Taylor expansion proves the parallel limit is at
least half.  A separate finite argument proves the explicit `25/98` constant
on every positive equicorrelation.  A float64 all-permutation hostile scan on
200 generic matrices through `n=7` found no violation (minimum `1.0087996`).
Two independent 600-order Monte Carlo batches in dimensions `10,16,24` also
found none; the minimum was `0.7776984` at the expected
`n=24,rho=4/24` equicorrelation control, with batch disagreement `0.00025`.
The independently evaluated exact rational value for that control is
`0.7782995770...`; this quantifies the sampling bias but does not certify any
generic matrix.  Both searches are only E1 outside their exact structured
controls.

## 5. General uniform spectral slice via a new direct certificate

Put `theta=n(1-mu)`.  Trace and the spectral floor give

```
||B-I||_F^2<=n(n-1)(1-mu)^2<=theta^2.
```

Every chronological factor therefore satisfies
`||M_pi-I||<=theta/sqrt(2)`.  The fixed dual test `R=I` yields

```
K(B)>=[1+theta/sqrt(2)]^-2 mu B^-1.
```

The same pathwise norm argument gives simultaneously

```
J_t(B)>=(t/n)[1+theta/sqrt(2)]^-2 mu B^-1,
1<=t<=n.
```

Consequences are the sharp global half constant when
`theta<=2-sqrt(2)`, a half-prefix `1/4` constant in that band, and a global
`1/4` constant whenever `theta<=1`.  No finite search is used in this proof
candidate.

Iteration 4 already had a different scalar determinant-leaf recurrence that
proves the desired half-depth bound in an explicit high-`mu` region.  The
contribution here is an independent leaf-free full-epoch/prefix norm
certificate with a particularly transparent dimension-scaled condition; no
relative priority or region containment is asserted.

## 6. Independent hostile audits performed

- Equicorrelation: PASS, strengthened to every
  `1<=t<=ceil(n/2)`; `rho=0` must be handled separately.
- Identity-local hierarchy: PASS for fixed `n`, one simultaneous neighborhood;
  `t=1`/`n=2` use the global elementary bound.
- Route C weighted two-step SOS: PASS after independent reconstruction.
- Half-linear equicorrelation Taylor proof: PASS.
- Finite equicorrelation `25/98` certificate: PASS.
- Spectral-floor strengthening of the local residual lemma: PASS, including
  the singular-floor continuity direction.
- General high-`mu` spectral band (N1--N7): PASS in an independent Route C
  reconstruction; the simultaneous prefix corollary should still be cited as
  an internal extension of that audited core.

As a regression control for that extension, all 720 orders and every prefix
were reconstructed exactly for a rational six-dimensional matrix with three
unequal signed `2x2` blocks and `theta=1/5`; every target principal minor was
nonnegative.  This is E2 finite evidence, not the quantified proof.

None of these audits promotes the general RPCD conjecture.

## 7. Deepest remaining obstruction and next experiment

The generic tail matrix has individually controlled rows but may have aligned
row directions.  The exact without-replacement average of old-subset energy
still contains a `||h||^2` term, and an exact rational example nearly
saturates a single-row Schur bound.  The next proof should therefore target
an operator inequality for the *sum of cross-row covariances*, perhaps by:

1. grouping complementary half-windows and retaining their matrix cross term;
2. proving a matrix Freedman/Bessel inequality for the revealed local
   residual frame; or
3. combining the positive frame representation of `C_t` with the generic
   `1-mu` row-tail bound in two spectral regimes.

Do not return to fixed `q`, scalar row summation, bare global Jensen, or
word/reverse pairing.

## 8. Timing and reproducibility

Observed start: `2026-08-21 19:38:29 +08:00`.

Finalization time: `2026-08-21 21:39:38 +08:00` (121 minutes 9 seconds
after this worker's observed start, and 101 seconds after the root-observed
minimum threshold).  The same endpoints are recorded in `TIMING.json`.

All task-specific scripts, exact fractions, seeds, float64 scope labels, and
audit artifacts are under this directory.  The generic stress seed is
`529105`; every permutation was enumerated through `n=7`.  No numerical null
search is presented as a quantified proof.

`rpcd_harness validate-result` reports no content/claim-level error in
`result.json`; its sole diagnostic is the absent harness-owned
`active_research_seconds` field in a sibling `invocation.json`.  This subagent
was not launched through that invocation wrapper, so no harness-owned timing
metadata was fabricated.
