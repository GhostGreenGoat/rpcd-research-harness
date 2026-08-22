# Initial finite RPCD audit (E2 ceiling)

Date: 2026-08-19. Environment: Python 3.12.13, NumPy 2.3.5, Windows 11. All checks use float64.

Command:

```text
python scripts/verify_rpcd_identities.py
```

For six deterministic matrices (`I_3`, three structured/sign-flipped cases and two seeded random
correlation matrices), the verifier enumerated every permutation and checked:

- product-coordinate and triangular-factor epoch operators agree, maximum residual
  `3.05e-16`;
- `A - T_p^T A T_p = A(M_pM_p^T)^{-1}A`, maximum residual `4.44e-16`;
- `E[M_pM_p^T] = A + S`, maximum residual `4.44e-16` in the random cases and
  `6.66e-16` in the separate search;
- the Jensen upper-matrix residual was positive semidefinite within tolerance `2e-10`;
- the exact-permutation covariance rate lay below both the ICML conjectured bound and the C010
  matrix-Jensen bound in every listed case.

A separate command

```text
python scripts/search_rpcd_counterexample.py --n 4 --sigma 0.4 --samples 12 --seed 7
```

evaluated 16 matrices (structured, random-correlation and block families), with all 24 permutations
per matrix. It found no float64 candidate violation. The smallest C001 margin was
`0.10988215417832248` at the structured matrix; the smallest C010 margin was
`0.0527214811447978` at a random-correlation matrix with recorded seed `11307154`.

An additional 6,000-matrix cheap scan over `n=2,...,7` and ten sigma values found a route barrier:
for `n=4`, `sigma=0.1`, seed `52`, ridge `0.001539926526059492`, the exact RPCD rate was
`0.7561575734438027`, below the conjectured `0.8166518036622619`, but the matrix-Jensen scalar
bound was `0.8530487636870818`. Therefore the raw comparison `r_MJ <= conjectured bound` is false
at float64 resolution. This does not refute either C001 or the C010 energy inequality; it shows C010
needs a sharper second stage to solve C001. Task T015 asks for a rational/interval certificate.

Rounding that witness to denominator-1000 off-diagonal entries preserves and slightly enlarges the
route gap: the rational candidate in `C011_RATIONAL_CANDIDATE.json` has float64 minimum eigenvalue
`0.10018415...`, exact-permutation rate `0.75576074...`, conjectured target `0.81634337...`, and
Jensen bound `0.85277990...`. Only outward-rounded interval certification remains.

This document is **not** a proof and does not upgrade C001 or C010. Its purpose is to establish a
regression baseline and to catch sign, transpose, order and Jensen-direction mistakes in future proof
runs. Machine-readable certificates can be regenerated with the scripts' `--out` option.
