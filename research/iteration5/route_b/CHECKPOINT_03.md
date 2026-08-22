# Route B checkpoint 03

- Interval covered: `2026-08-21 20:38:10--21:08:07 +08:00`.
- The universal half-depth claim remains open; no negative half-margin was
  found.

## Direct threshold search at n=1000

A targeted 5,000-evaluation search with satellite sizes at most twenty found

```
counts                 = (998,2)
mu                     = 0.9817838119961547
prototype cosine       = 0.3326843828628556
H ratio                = 0.5051650140581231
H margin over 1/2      = 0.0051650140581231
signed-rank baseline   = 0.5053514928210651
```

The complete generalized minimum is the two-coordinate satellite transverse
sector.  Thus the rank-two perturbation is slightly more hostile than signed
rank one at finite `n`, but does not cross the target.

At the same candidate the bare half-prefix is `0.5046158003939771`; the
determinant leaf contributes `0.0005392090848011` on the worst `H` direction,
about `0.109%` of its quadratic value.  The prefix is therefore the tight
component, not a hidden leaf repair.

## Fixed-satellite limiting recurrence

For a large duplicate group and `k` fixed satellite duplicates, put
`alpha=1-mu` and let `t` be the prototype cosine.  Between satellite pivots,
the large-group deviation obeys `D -> mu D`.  Hence, as the large group tends
to infinity, the satellite-only effective coupling and solve-energy weight
are

\[
 \eta=\alpha(1-t^2),\qquad
 w=1+{\alpha t^2\over1+\mu}={2-\eta\over1+\mu}.
\]

For `k=2` the Bernoulli-half prefix can be summed exactly:

\[
 R_2(\mu,t)={8-\eta^3\over8(1+\mu)}.
\]

Its minimum over `t` occurs at orthogonal prototypes and satisfies

\[
 R_{2,\min}-{1\over2}
 ={(1-\mu)[1-(1-\mu)^2/4]\over2(1+\mu)}>0.
\]

This is an E3 fixed-satellite proof draft, not yet hostile-audited.  It
explains both the finite negative excess over signed rank one and why that
excess does not create a half violation.

## Exact finite surrogate on the tight ray

For two orthogonal satellite coordinates, exact hypergeometric counting gives
the bare-prefix transverse ratio.  If `n=2h`,

\[
 R_J={1\over2}+{h-1\over4(2h-1)}[(2-\mu)^2-1]\ge{1\over2};
\]

if `n=2h+1`,

\[
 R_J={(h+1)[3+(2-\mu)^2]\over4(2h+1)}>{1\over2}.
\]

Since `H>=J`, the tight direction is safe for every finite `n,mu`, not merely
on the float grid.  `orthogonal_satellite_exact.py` verifies rational
instances through `n=1000`.

## Threshold scaling

With `1-mu=c log(n)/n`, the smallest structured `H` ratios were

```
n=1,000      0.5051452282464350
n=3,000      0.5019105945805915
n=10,000     0.5006400435693003
n=30,000     0.5002343174177569
n=100,000    0.5000764878638665
```

No value crossed `1/2`.  For the first four points the grid chose `c=2.6`;
at `n=100000` it chose `c=2.4`.  The scaled values
`n(H-1/2)/log(n)` decrease from `0.745` to `0.664`, consistent with a positive
`Theta(log n/n)` approach.  On the same orthogonal ray the exact prefix
formula supplies the sign.

## Multiscale stress

Allowing the satellite group to have its own internal mass/eigenvalue scale
produced minimum `0.5051846706475910` in 1,500 additional `n=1000` tests,
slightly worse than the pure duplicate satellite.  No rational
counterexample reconstruction was triggered.
