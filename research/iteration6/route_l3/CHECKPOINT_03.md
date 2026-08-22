# Checkpoint 03 — spectral audit and a new uniform `W4` slice

- Local checkpoint: `2026-08-22 18:00:02 +08:00` (about 84 minutes after the
  first local clock sample).
- The independent spectral-geometry reconstruction reports
  `PASS_WITH_SCOPE_CORRECTION`:
  `spectral_geometry_hostile_audit.md` and
  `evidence/SPECTRAL_GEOMETRY_HOSTILE_AUDIT.json`.

## Spectral audit

Sections 1.1 and 2b of the stitching route pass after reconstructing the
exterior pair-difference degree, trace-preserving high-variable compression,
both parity endpoints, the rank-three derivative sign pattern, constant-diagonal
projector realization, and the `J2` weak endpoint.  Section 1.1 should state
`n>=3`; `n=2` is separate.  The later bounded-subunit finite-vertex reduction
also passes: throughout the whole low-variable box its compensating eigenvalue
satisfies `L>=2-mu>=1`, so sequential concavity is legitimate.  Its exact
range is `1<=p<=min(s,n-1)`.

## New `W4` slice

`w4_matching_block_slice.md` proves the strong uniform shifted-inverse lemma

```text
L3(C)>=(2/d)[C+(1-mu)I]^-1
```

for every `d>=6` child whose support graph is a matching (arbitrary unequal,
signed `2 x 2` correlation blocks plus singleton identities).  The proof uses
the exact anisotropic identities `H^2=D`, `F=H`, and `S=(d-2)D`, then closes
both eigenlines analytically.  It is internal E3 pending independent audit;
the exact reconstruction script and JSON pass.

## Remaining blocker

The universal shifted-inverse lemma remains open once the support graph has a
vertex of degree two: then `H^2-D` is nonzero and couples distinct edges.  This
is the first combinatorial interaction absent from all proved matching-block
slices and is a sharper next test than another scalar spectral compression.
