# Checkpoint 01 — exact Schur compensation closes the candidate algebra

- Local checkpoint: `2026-08-22 17:03:24 +08:00` (about 28 minutes after the
  first local clock sample).
- Evidence status: internal E3 proof candidate; independent hostile audit is
  running.  No Lean/external validation.

## Main development

An exact proof candidate now covers the full stated range `m>=3`:

```text
L3(A) >=(2mu/m)A^-1.
```

For a child block `A=[[1,b^T],[b,C]]`, put
`s=1-b^TC^-1b`, `c=C^-1b`, `d=m-1`, and
`beta=3mu/(2d)`.  The child polynomial surplus satisfies, for `d>=3`,

```text
P_d(C)-beta C^-1 >=(beta/s)cc^T.
```

After lifting, the right side is exactly the rank-one Schur defect discarded
by scalar child induction.  Summation leaves the positive parent surplus
`3mu(1-mu)/[2m(m-1)] A^-1`.  The exceptional child size `d=2` closes with a
piecewise smaller rank-one multiplier and exact Bernstein certificates.

Full derivation:
`schur_compensation_proof.md`.  Portable exact checker:
`scripts/iter6_l3_schur_compensation.py`; current output is PASS.

## Three analytic avenues at this checkpoint

1. **Full anisotropic residual / SOS.**  Derived the exact identity
   `S-R^2/(m-1)=Diag(diag F^2)-F^2/(m-1)` and its complete coordinate-pair
   Gram representation.  This retains, rather than deletes, the transverse
   variance missing from the failed Iteration-5 compression.
2. **Schur-complement representation.**  Used the PSD Schur complement of
   `A-mu I` and the exact inverse defect direction `cc^T/s` to construct a
   matrix-valued multiplier for each child.  No Jensen or child scalar floor
   is used in the pivotal step.
3. **Spectral-regime decomposition.**  Proved the child scalar comparison by
   low/high spectral splitting for `d>=4`, a tensor Bernstein proof for
   `d=3`, and two tensor Bernstein branches for `d=2`.  The spectral surplus
   is then converted back into directional child information by Schur
   complementation.

## Exact hostile controls

`evidence/EXACT_ROUTE_BARRIERS.json` records two strict auxiliary failures:

- full `beta` compensation is false for `d=2`; at
  `A=(1/4)I+(3/4)11^T`, the child gap has witness value `-3/80` and
  determinant `-99/5120`;
- the anisotropic residual `Z_F` cannot satisfy `Z_F>=cF^2` for any `c>0`:
  for `F=11^T-I` in size four, the all-ones witness has `Z_F` value zero and
  `F^2` value `36`.

Neither refutes `L3`; both explain why the successful multipliers must be
directional and why the `m=3` branch is genuinely exceptional.

## Audit blockers to watch

- Moore--Penrose handling when a child eigenvalue equals `mu`;
- the `beta/s` factor in rank-one domination;
- the reversed inequality after multiplying by the negative coefficient
  `q=(2-3mu)/12` in the high-`mu`, `m=3` branch;
- exact equality between the child definition of `L3` and formula B5.
