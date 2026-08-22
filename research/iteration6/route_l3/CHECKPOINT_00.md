# Checkpoint 00 — Route L3 launch

- Root-observed lower-bound start: `2026-08-22 16:34:10 +08:00`.
- First local clock sample: `2026-08-22 16:35:36 +08:00`.
- Enforced finish threshold (later local start + 120 min): `2026-08-22 18:35:36 +08:00`.
- Objective: prove or refute, for every real symmetric correlation matrix
  `A \succeq \mu I`, `diag(A)=1`, `m>=3`, the explicit inequality
  `L3(A) \succeq (2\mu/m) A^{-1}`.
- Required analytic routes:
  1. full anisotropic residual / matrix SOS or multipliers;
  2. exterior algebra, volume sampling, or Schur-complement representation;
  3. spectral-regime decomposition or induction retaining directional child data.
- Exclusions: no repeat of scalar row-Bessel compression; no bulk numerical search.
- Evidence policy: exact symbolic identities and exact rational counterexamples are allowed; floating-point exploration remains E1 and cannot establish a theorem.

## Initial state

Iteration 5 established the exact formula `C3 \succeq L3`, verified the target on
the compound/equicorrelation family, and exposed that replacing the full residual
`S` by `R^2/(m-1)` loses exactly the amount needed at a rank-one boundary.  This
iteration therefore keeps the uncompressed residual visible from the outset.
