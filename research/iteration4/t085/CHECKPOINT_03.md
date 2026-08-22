# Iteration 4 / T085 checkpoint 03

- Wall-clock interval covered: 2026-08-21 18:34--19:06 (Asia/Shanghai).
- This checkpoint includes the requested hostile audits and the repaired-constant assessment.

## Exact T080 audits

Two independent audits now separate the two examples cleanly.

1. The `4/5,71/125` example was reconstructed by generic full `8!` Fraction solves, including
   direct coordinate-update product orientation, 56 labelled pole-position multiplicities,
   exact reducing action, and an explicit positive `mu=1/1000` M1 failure.  A provenance warning
   records that the current similarly named discovery script contains a different example.
2. The simpler `2/3,1/3` example was reconstructed by a different full `2^8` first-pivot Bellman
   recursion.  Its coefficient is `1057837/531441<2`; the pole-odd line is an actual Schur reducing
   line.  At `mu=1/100`, the same subset DP gives a strict rational M1 violation.

Neither audit computes or refutes the covariance-map spectral radius C001.

## Repaired constants

The pole/simplex family proves that a boundary constant above `3/2` is impossible.  A moment-DP
scan retaining both kernel directions and the even kernel/range Schur correction found no finite
violation of the sharp `3/2` candidate, but this is only E1 evidence.

The tempting global certificate `gamma(A)>=mu` is exactly false.  For
`A=mu I+(1-mu)11^T`, the parallel solve gives

`gamma/mu <= [n-(n-1)mu](1-mu^(2n))/[n mu(1-mu^2)]`.

At `n=9,mu=9/10` this is strictly below one by exact rational arithmetic.  Sending first `n` to
infinity and then `mu` to one shows no universal global constant above `1/2` is possible.
Therefore the surviving T085 half-depth target with coefficient `mu/2` is asymptotically optimal
for a global one-step energy certificate, not merely sufficient.

Full formulas and scope are in `docs/ITER4_T090_CONSTANT_ASSESSMENT.md`.
