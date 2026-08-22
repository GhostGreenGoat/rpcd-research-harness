# Iteration 5 Route B final report: hostile structured attack

Status: no counterexample to

\[
H_{\lceil n/2\rceil}(A)\succeq {\mu\over2}A^{-1},
\qquad \mu=\lambda_{\min}(A),                            \tag{1}
\]

was found.  The universal problem remains open.  Null searches below are E1;
exact finite identities and proof drafts are identified separately.

## Outcome first

This route replaced the old `2^n` small-Gram search by a full
exchangeable-group Bellman recursion whose states are remaining group counts.
It reached dimension `100,000`, evaluated 9,825 structured parameter points,
and retained the complete generalized minimum across all invariant sectors.

The closest observed half-depth value was

\[
0.5000764878638665                                       \tag{2}
\]

at `n=100000`; it is above the threshold by
`7.64878638665e-5`.  The tight matrix is a large duplicate block plus two
orthogonal duplicate satellite coordinates.  On its tight satellite-difference
direction, a separate exact hypergeometric formula proves the bare prefix
already lies above `1/2` for every finite `n` and `mu`.  Thus (2) is a genuine
near-extremizer but not a hidden floating-point counterexample.

At `n=1000`, a broader 5,000-sample angle/multiplicity search found
`0.5051650140581231`.  Its bare-prefix ratio is `0.5046158003939771`; the
determinant leaf adds only `0.0005392090848011`.  The tight component is the
linear-depth without-replacement prefix, not the leaf.

## 1. New large-dimensional finite engine

For `G` exchangeable coordinate groups, every principal state and Bellman
certificate is represented by group diagonal, within-group, and cross-group
entries.  Exact count-weighted recurrences evaluate the complete
determinant-tail matrix.  The leaf uses a `G by G` group-constant inverse plus
the within-group transverse eigenspaces.  The generalized minimum is the
minimum over every group-transverse coefficient and the full group-constant
block, not a kernel compression.

The derivation is in `family_reduction.md`; the portable implementation is
`reproducer.py`.  Deterministic controls include:

- twelve random three-group cases and both determinant/zero leaves versus a
  generic `2^n` subset DP, worst matrix-entry residual `4.44e-16`;
- recursive versus layered count DP, exact agreement at printed precision;
- whole-group sign conjugation, zero coefficient gap;
- direct full `76 by 76` generalized spectrum, residual `6.11e-16`;
- an independent 3,000-order path Monte Carlo, discrepancy `-1.39` standard
  errors from the DP prediction;
- signed-rank-one `n=1000,mu=0.98`, ratio `0.505509978960384`, reproducing the
  known sharp control.
- twelve exact Fraction checks with unrelated zero-sum satellite vectors,
  `k=3,...,6`, all matching the all-fixed-`k` moment formula identically.

These controls validate the finite implementation at E2, not statement (1).

## 2. Families attacked

### Three/four exchangeable groups

- Three frustrated rank-two groups (`n=60`): best `0.6109017588`.
- Four uneven rank-three multiscale groups (`n=39..116`): local optimization
  reached `0.5662851920` at `n=76`.
- Duplicate pole plus three simplex leaf groups (`n=56`): best `0.6333700888`.
- Five/six heterogeneous one-factor groups (`n<=30`): best `0.6679525409`.

The four-group worst direction was always in the complete group-constant
block.  A fixed geometry decreased toward the half threshold under dimension
scaling but nonmonotonically, so no asymptotic sign was inferred.

### Replicated simplex

Three equal duplicate groups at the vertices of a regular triangle give a
clean non-signed-rank-one family.  At `n=300,mu=0.94`, its ratio is
`0.5184132838`.  The signed-rank-one baseline at the same `n,mu` is slightly
smaller, `0.5167275158`; hence this is a second near-sharp family, not a worse
one there.  Four through six replicated-simplex groups were less hostile at
the accessible dimensions.

### Duplicate triangles and satellites

An optimizer aimed at *excess over signed rank one* found a finite `n=90`
triangle with ratio `0.5949344774`, which is `0.0013800820` below signed rank
one at identical `n,mu`.  Therefore signed rank one is not a pointwise finite
extremizer of the half-depth hierarchy.  The advantage shrinks rapidly under
proportional scaling and stays far from a half violation.

The geometry reduces to a two-group satellite attack at large `n`.  Results:

| scale | samples/grid | smallest `H/mu` |
|---:|---:|---:|
| `n=300` | 1,200 stochastic | `0.5153289714` |
| `n=1000` | 5,000 stochastic | `0.5051650141` |
| `n=3000` | threshold grid | `0.5019105946` |
| `n=10000` | threshold grid | `0.5006400436` |
| `n=30000` | threshold grid | `0.5002343174` |
| `n=100000` | threshold grid | `0.5000764879` |

The threshold parameterization was `1-mu=c log(n)/n`.  The quantity
`n(H/mu-1/2)/log(n)` decreased from about `0.745` to `0.664`, consistent with
a positive `Theta(log(n)/n)` approach.  This is a fit, not a proof of the
optimal finite-dimensional scaling.

Allowing a distinct satellite internal eigenvalue scale in 1,500 additional
`n=1000` trials gave minimum `0.5051846706`, slightly worse than the pure
duplicate satellite.

To separate multiplicity scales rather than letting a log-uniform sampler
choose them, 108 further points used `k=2`, `round(sqrt(n))`,
`round(n^(3/4))`, and `floor(n/4)`.  A boundary-layer fit over
`n=100,200,400,800,1600` then minimized four prototype cosines at
`1-mu=2.5 log(n)/n`.  The last-three log-log slopes of the positive margin
were `-0.903,-0.901,-0.901,-0.900`; the corresponding means of
`n(H/mu-1/2)/log(n)` were `0.763,0.792,0.793,0.793`.  Thus all four finite
scales are consistent with a positive `log(n)/n` boundary layer.  Fixed two
satellites remained slightly below signed rank one, while growing and linear
satellites approached it from essentially the same scale.  These are E1
fits, not asymptotic proofs.

## 3. New analytic information from the hostile family

Let the large and satellite prototype cosine be `t`, set
`alpha=1-mu`, and keep the satellite size fixed while the large group tends to
infinity.  Between satellite pivots the large-group deviation decays by
`D -> mu D`.  The limiting satellite coupling and energy weight are

\[
\eta=\alpha(1-t^2),\qquad
w=1+{\alpha t^2\over1+\mu}={2-\eta\over1+\mu}.           \tag{3}
\]

For two satellite coordinates the Bernoulli-half prefix sums exactly to

\[
R_2(\mu,t)={8-\eta^3\over8(1+\mu)}.                      \tag{4}
\]

It is minimized at orthogonal prototypes and

\[
R_{2,\min}-{1\over2}
={(1-\mu)[1-(1-\mu)^2/4]\over2(1+\mu)}>0.               \tag{5}
\]

Equations (3)--(5) are an E3 fixed-satellite asymptotic proof draft.  They
explain why the satellite can beat signed rank one finitely without crossing
one half.

The fixed-count calculation now extends to every `k>=2` in the satellite
zero-sum sector.  If `S~Binomial(k,1/2)`, `p_j=Pr(S>=j)`, `rho=1-eta`,
`W_j=sum_{r=0}^{j-2}rho^r`, and `Q_j=sum rho^(2r)`, exchangeable
without-replacement moments give

\[
{E[y_j^2\mid S\ge j]\over\lVert z\rVert^2}
={1\over k}+{\eta^2(kQ_j-W_j^2)+2\eta W_j\over k(k-1)}. \tag{5a}
\]

Cauchy makes the correction nonnegative, while
`sum_j p_j=E[S]=k/2`; hence `h_k>=1/2`.  Since the relaxation weight
`w=(2-eta)/(1+mu)>=1`, the limiting transverse ratio is at least one half for
all fixed `k`.  Exact enumeration through `k=8` reproduces this identity and
has nonnegative rational Bernstein certificates.  This new E3 argument is
strictly scoped to fixed `k` followed by `N->infinity` and the zero-sum
satellite sector.  A separate run independently reconstructed the moment
calculation and marked this scoped result PASS, promoting it to E4 on the
repository ladder; it is not a formal or external validation.

Expanding the audited formula also explains the split from signed rank one.
For `alpha=1-mu`, `u=1-t^2`, and fixed `k`,

\[
R_k={1\over2}+{\alpha\over4}
+\alpha^2\left[{1\over8}+{k-2\over24}u^2\right]
+O_k(\alpha^3).                                         \tag{5b}
\]

All fixed counts share the leading `alpha/4`.  When `k>=3`, collinearity is
best through second order; when `k=2`, angles tie through second order and
the cubic term favors the orthogonal satellite.  This matches the observed
fact that two satellites slightly beat signed rank one while growing counts
track it.  The expansion is E3 and pointwise in fixed `k`.
For the fitted boundary layer `alpha=2.5 log(n)/n`, it predicts the fixed-`k`
limit `n(R_k-1/2)/log(n)->0.625`; the observed fixed-two value `0.763` over
the last three finite dimensions is consistent with slow positive corrections.

On the orthogonal two-satellite ray there is also an exact finite prefix
formula.  For `n=2h`,

\[
R_J={1\over2}+{h-1\over4(2h-1)}[(2-\mu)^2-1]\ge{1\over2}; \tag{6}
\]

for `n=2h+1`,

\[
R_J={(h+1)[3+(2-\mu)^2]\over4(2h+1)}>{1\over2}.          \tag{7}
\]

Since `H>=J`, (6)--(7) close the tight direction exactly.  The rational
surrogate `n=1000,mu=49/50` gives

\[
R_J={5045399\over9990000}>{1\over2}.
\]

This is not a proof for the other invariant sectors, arbitrary satellite
sizes, or general matrices.

## 4. Exact failed route

A tempting extension of the signed-rank-one proof would assert pathwise that
the second distinguished coordinate always has solve magnitude at least one.
It is false on the replicated simplex.  For three groups at `mu=1/5`, after a
positive special in group zero and ordinary pivot groups `(1,0,0,2)`, the
negative special solves to

\[
-{2889\over3125},
\]

whose magnitude is below one by `236/3125`.  This exact Fraction certificate
kills the pathwise shortcut but does not refute the averaged inequality.

## 5. Evidence boundary and next work

What advanced:

- a portable large-`n` full-matrix family DP;
- a genuinely non-rank-one near-sharp family;
- proof that signed rank one is not a pointwise finite extremizer;
- an exact fixed-satellite limit and exact finite formula on the tightest ray;
- an all-fixed-`k` limiting lower bound in the satellite-transverse sector;
- isolation of the half-prefix as the tight component.

What remains open:

- the all-matrix inequality (1), already from general `n=5`;
- a uniform treatment of satellite size `k=o(n)` with growing `k`, where
  clustered satellite pivots must be controlled;
- linear-size coupled blocks, for which relaxation (3) is invalid;
- a proof that some structured lower envelope controls every general matrix;
- hostile audit of the remaining invariant sectors, growing-`k` regimes, and
  the local expansion (5b).

The two-satellite derivation, the all-fixed-`k` transverse extension, and the
finite orthogonal ray received an independent hostile audit in
`docs/ITER5_AUDIT_TWO_SATELLITE_ASYMPTOTICS.md`.  The audit does not cover
growing `k` or the other invariant sectors.

The next counterexample-oriented step should optimize growing sublinear
satellites (`k=n^beta`) against the exact fixed-`k` formula, while the proof
route should attempt to lift the hypergeometric prefix argument into a
matrix-valued comparison for arbitrary child blocks.

## Reproduction

Main commands include:

```text
python research/iteration5/route_b/regression_checks.py
python research/iteration5/route_b/reproducer.py --mode controls --output research/iteration5/route_b/controls.json
python research/iteration5/route_b/two_group_satellite_search.py --n 1000 --evaluations 5000 --max-satellite 20 --high-mu-only --seed 202608224 --output research/iteration5/route_b/two_group_satellite_n1000.json
python research/iteration5/route_b/satellite_threshold_scan.py --dimensions 1000,3000,10000,30000 --output research/iteration5/route_b/satellite_threshold_scan.json
python research/iteration5/route_b/orthogonal_satellite_exact.py
python research/iteration5/route_b/satellite_asymptotic_check.py
python research/iteration5/route_b/fixed_k_satellite_exact.py
python research/iteration5/route_b/fixed_k_random_z_audit.py
python research/iteration5/route_b/satellite_scale_regimes.py
python research/iteration5/route_b/satellite_scaling_fit.py
python research/iteration5/route_b/consolidate.py
```

## Timing

- Root-observed start: `2026-08-21 19:37:57 +08:00`.
- Final timing seal: `2026-08-21 21:38:56.4190814 +08:00`.
- Active wall-clock interval recorded: `7,259.4190814` seconds
  (`120.9903180` minutes), exceeding the required two hours.
