# Route Stitch checkpoint 03

- Local start: `2026-08-22T16:35:07.9149419+08:00`.
- Checkpoint time: `2026-08-22T18:06:51.0547771+08:00` (91 minutes 43 seconds).

## Independently reconstructed positive regions

The exterior-prefix argument now has hostile-audit support for four exact
claims: the at-most-two-subunit spectral region, the constant-diagonal
rank-two and rank-three low-projector families, and the finite vertex
reduction for a bounded number of subunit modes.  The last reduction sends
each low coordinate separately to `mu` or `1`; its precise vertex range is
`1<=p<=min(s,n-1)`.  These are internal E4 proof candidates only (no Lean or
external review).

## Exact hostile barriers

- Rank four is a genuine limit of the isotropic exterior argument: at
  `n=9, mu->0` its normalized coefficient is `729/1750<1/2`.
- A nonsymmetric three-low spectrum already defeats the exterior certificate:
  `(0,0,0,1,1,1,1,4)` gives `2/5`.
- The exact `n=2` boundary ray has chord gap
  `-mu(1-mu)I/2`; endpoint interpolation is not a Loewner-concavity proof.
- A non-signed rank-two extreme correlation matrix shows that kernel
  compression is strictly larger than the full Loewner shorted coefficient.

These are failures of proof routes, not counterexamples to RPCD.

## Current audit subroute

I am independently reconstructing the proposed matching-support slice of the
uniform `W4` shifted-inverse lemma.  The key checks are the retained-state
identity `S=(d-2)D`, both signed block eigenlines, the exact quadratic Taylor
expansion in `d-6`, and the equivalence between the shifted-inverse inequality
and the outer Schur-envelope condition.  No sibling checker is being used as
a premise.
