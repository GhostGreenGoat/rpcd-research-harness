# Failed lemmas and exact route boundaries

Date: 2026-08-22

These are failures of proposed certificates, not counterexamples to RPCD or to
the half-depth target unless explicitly stated otherwise.  Exact witnesses are
reproduced by `scripts/iter6_l3_exact_barriers.py` and
`evidence/EXACT_ROUTE_BARRIERS.json`.

## F1. Full child compensation does not extend to `d=2`

The `d>=3` proof uses `beta=3mu/(2d)`.  For the positive-equicorrelation
parent of size three at `mu=1/4`, the corresponding size-two child gap has an
exact negative witness `-3/80` and the proposed rank-one compensated matrix
has determinant `-99/5120`.  The universal scalar child lemma therefore fails
at `d=2`.  The final `m=3` proof needs the separate piecewise compensator in
`schur_compensation_proof.md`.

## F2. The exterior residual cannot dominate the old square state

For size four, take `F=11^T-I`.  The exact pair-difference residual

```text
Z_F=Diag(diag F^2)-F^2/(m-1)
```

vanishes on the all-ones direction, while `F^2` has witness value `36` there.
Thus no universal `c>0` can satisfy `Z_F>=cF^2`.  The exact SOS identity is
useful only when its orientation is retained; collapsing it back to the older
square repeats the failed Bessel route.

## F3. The spectral part of the `L3` surplus cannot close `W4`

For `d=6,mu=1/100,lambda=1`, the global spectral proxy for the next Schur
envelope has exact gap

```text
-6501/79600.
```

A direct-sum unit-diagonal parent realizes this point.  The full anisotropic
state passes on that parent with exact normalized ratio `99/199<1`, so this is
a barrier specifically to discarding the retained child matrices `M_j`.

## F4. A shallow all-dimension shortcut is false

If the full `W4` termwise recovery is incorrectly asserted already for parent
size four, positive equicorrelation at `mu=1/4` has exact ratio
`2304/1859>1`.  This does not touch the hierarchy-relevant range `m>=7`, but it
rules out induction from an unrestricted small-dimension base lemma.

## F5. The universal shifted-inverse lemma remains unresolved

The clean sufficient condition

```text
L3(C)>=(2/d)[C+(1-mu)I]^-1,  d>=6,
```

is proved here only on structured slices: positive/negative equicorrelation,
matching support, a single weighted three-vertex path plus isolates, and
equal-magnitude stars.  The next unsupported exact states are a four-vertex
path, a signed cycle, and an unequal-weight degree-three star.  No negative
witness to the universal condition was found or claimed in this route.
