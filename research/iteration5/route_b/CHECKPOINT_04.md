# Route B checkpoint 04

Timestamp: `2026-08-21 21:38:05 +08:00` (past the required two-hour gate).

## Final-stage additions

- Split satellite multiplicities into fixed, `sqrt(n)`, `n^(3/4)`, and
  linear-quarter regimes; 188 deterministic fit/grid evaluations found no
  float64 violation.
- Derived the exact all-fixed-`k` transverse moment identity after fixing `k`
  and sending the majority size to infinity.  Cauchy and the binomial tail
  sum give `h_k>=1/2`, while the relaxation weight is at least one.
- Independently enumerated ordered-prefix polynomials through `k=8` and
  obtained zero symbolic residual against the moment formula plus
  nonnegative Bernstein certificates.
- Added twelve exact Fraction controls for unrelated zero-sum vectors,
  `k=3,...,6`; every explicit prefix enumeration matched the formula.
- The separate hostile audit in
  `docs/ITER5_AUDIT_TWO_SATELLITE_ASYMPTOTICS.md` independently reconstructed
  and passed the all-fixed-`k` transverse result.
- Derived the pointwise fixed-`k` local expansion explaining why `k=2` can
  beat signed rank one while `k>=3` returns toward collinearity.

## Final validation state

- No counterexample found; closest E1 ratio remains
  `0.5000764878638665` at `n=100000`.
- 29 JSON artifacts parsed successfully.
- 27 repository unit tests passed.
- Symmetry-vs-subset regression residual: `4.44e-16`.
- Required T097 artifacts are present.
