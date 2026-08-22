# Iteration 6 Route L3 — final portable report

Date: 2026-08-22 (Asia/Shanghai)

## 1. Main result

The explicit general inequality assigned to this route is proved:

```text
L3(A)>=(2mu/m)A^-1
```

for every real symmetric unit-diagonal SPD `m x m` matrix, every `m>=3`, and
every `0<mu<=lambda_min(A)`.  The proof is exact and has passed a hostile
independent reconstruction with no blocking caveat.  Under the repository
ladder this is an **internal E4 proof candidate**.  It has no Lean/formal
verification and no external peer review.

Primary artifacts:

```text
research/iteration6/route_l3/schur_compensation_proof.md
scripts/iter6_l3_schur_compensation.py
research/iteration6/route_l3/evidence/SCHUR_COMPENSATION_EXACT.json
research/iteration6/route_stitch/L3_HOSTILE_AUDIT.md
research/iteration6/route_stitch/L3_INDEPENDENT_EXACT_AUDIT.json
```

### Proof mechanism

For a child block `A=[[1,b^T],[b,C]]`, put

```text
s=1-b^TC^-1b, c=C^-1b, beta=3mu/[2(m-1)].
```

The scalar child surplus is large enough in every spectral direction to prove
the matrix Schur envelope

```text
P(C)-beta C^-1 >=(beta/s)cc^T.
```

This pays exactly for the missing rank-one part of the parent inverse.  It
retains direction and never invokes inverse Jensen in the wrong direction.
The exceptional child dimension two is closed by an exact piecewise
compensator and two Bernstein certificates.

The formerly discarded anisotropic residual also has the exact coordinate-pair
Gram representation

```text
S-R^2/(m-1)=Diag(diag F^2)-F^2/(m-1)>=0.
```

This identifies the exterior/two-form state that scalar row-Bessel compression
had erased.

## 2. Finite-time consequence for RPCD

Combining the audited `L3` result with `C3>=L3` and the level-two theorem gives,
for every `n>=3`,

```text
J3>=3mu/n A^-1,  K>=J3.
```

Thus one RPCD epoch contracts expected squared `A`-distance by at least
`1-3mu/n`, and Jensen gives the strong expectation-of-distance guarantee

```text
E||x_k||_A <=(1-3mu/n)^(k/2)||x_0||_A.
```

Relative distance `epsilon` is therefore reached within

```text
N <= n ceil{[2n/(3mu)] log(1/epsilon)}
```

coordinate updates.  This is a new all-dimensional
`O(n^2/mu log(1/epsilon))` benchmark; it remains a factor `n` above the target.
For `n<=6`, the half-prefix constants already give
`N<=n ceil{4 log(1/epsilon)/mu}`.  Dimension two is separate:
`N<=2 ceil{2 log(1/epsilon)/mu}`.  Exact constants and the simultaneous
high-probability corollary are in `n_le_6_finite_time.md`.

## 3. General recursion and the minimal `W4` inequality

The Schur mechanism extends abstractly.  If a child surplus is `Q_i` and the
inverse coefficient is `alpha`, its exact recoverable directional coefficient
is

```text
kappa_i=s_i/[c_i^T Q_i^dagger c_i]
```

with the recorded range conventions.  The only remaining aggregate defect is

```text
(1/m)sum_i(alpha-kappa_i)_+D_i,
```

whose allowable budget is

```text
t mu(1-mu)/[2m(m-1)] A^-1.
```

For `W4`, full termwise recovery is equivalent for an actual extension to

```text
L3(C_i)>=[2mu/(m-1)](C_i-b_ib_i^T)^-1.
```

Uniformly over all admissible extensions of a fixed child, it reduces exactly
to the single explicit inequality

```text
L3(C)>=(2/d)[C+(1-mu)I]^-1,  d>=6.                       (W4*)
```

`(W4*)` is the smallest clean general blocker left by this route.  The purely
spectral part of the `L3` surplus cannot prove it; the exact failure is
`-6501/79600`, while the full anisotropic state repairs the realizing parent.

## 4. New analytic `W4` slices

The following families satisfy the strong uniform condition `(W4*)`:

- complete positive and negative equicorrelation for every `d>=6` (internal
  E3);
- arbitrary unequal, signed disjoint `2 x 2` correlation blocks plus isolates,
  for every `d>=6` (internal E4 after independent audit);
- one arbitrary weighted three-vertex path plus isolates, for every `d>=6`
  (internal E4 after an independent reconstruction of the dimension scaling,
  valuations, denominators, and all principal minors).
- every equal-magnitude star `K_(1,p)` plus isolates, for all
  `p>=3,d>=max(6,p+1)` (internal E4 after independent audit).  Its
  center/uniform and transverse sectors have symbolic nonnegative-coefficient
  Bernstein certificates, with no finite `p,d` scan.

The matching proof uses `H^2=D`.  The path proof goes beyond that identity:
after `k=d-6`, every coefficient of every one of the seven active principal
minors has a nonnegative tensor-Bernstein certificate in the path magnitude
and orientation.  Complete tables are in
`evidence/W4_THREE_PATH_ALL_D_EXACT.json`; the audit is
`research/iteration6/route_stitch/W4_THREE_PATH_ALL_D_HOSTILE_AUDIT.md`.

The next minimal unsupported combinatorial state is therefore a four-vertex
path (two overlapping interactions), a signed cycle, or a degree-three star,
not merely a single degree-two vertex.

The equal-weight degree-three star is therefore closed by the star theorem.
For unequal weights, three deliberately fixed near-singular rational directions
pass all 15 active principal minors exactly.  They are E2 controls only, not a
null-search theorem; see `w4_degree3_star_controls.md`.  The new orientation
variable is a two-dimensional simplex `q_i=w_i^2/||w||^2`, suggesting simplex
Bernstein coefficients as the next finite algebraic state.

## 5. Independent cross-audits

This route independently audited two other stitching results:

- `spectral_stitching.md` Sections S3--S5 and S11--S12: PASS after adding the
  scope convention `Q_tau!=0` or `r_tau=+infinity` for the empty high spectral
  subspace.  See `spectral_stitching_hostile_audit.md`.
- `spectral_geometry_region.md`: the exterior ordering, the broad
  `#{lambda<1}<=2` region, its bounded-subunit finite-vertex reduction, the
  rank-two/rank-three projector families, and the `J2` endpoint all PASS.
  Minor scope clarifications are `n>=3` and
  `p<=min(s,n-1)`.  See `spectral_geometry_hostile_audit.md` and its exact
  JSON.

These audits do not amount to Lean or external verification.

## 6. Exact barriers and failures

Two hostile exact barriers to the original three proof avenues are retained:

- full `beta` Schur compensation is false at child dimension two (witness
  `-3/80`, determinant `-99/5120`);
- no positive constant can bound the pair-difference residual below by `F^2`
  (all-ones witness `0` versus `36`).

Further `W4` route boundaries are the exact spectral-only gap
`-6501/79600` and the irrelevant shallow-size ratio `2304/1859>1`.
`failed_attempts.md` distinguishes each certificate failure from the still-open
RPCD target.

## 7. Evidence map and reproducibility

The three genuinely different assigned avenues were all pursued:

1. full anisotropic matrix SOS and Schur multipliers — this produced the E4
   `L3` theorem candidate;
2. exterior/volume and subset-complement geometry — this produced an exact
   pair-difference state and independent spectral-region audits;
3. spectral-regime decomposition/induction preserving child directions — this
   produced the low/high scalar factorizations, general `kappa` recursion, and
   the structured `W4` slices.

All task-specific sources, scripts, exact JSON, checkpoints, failures, and this
report are under `research/iteration6/route_l3` or `scripts/iter6_*`.  No
credential or account-local state is used, so the artifacts are portable to a
different account after copying the repository and installing Python/SymPy.

From the repository root, the main reconstructions are:

```powershell
python scripts/iter6_l3_schur_compensation.py
python scripts/iter6_l3_exact_barriers.py
python scripts/iter6_w4_schur_recovery_exact.py
python scripts/iter6_spectral_geometry_hostile_audit.py
python scripts/iter6_w4_matching_block_exact.py
python scripts/iter6_w4_three_path_all_d_exact.py
python scripts/iter6_w4_equal_star_symbolic.py
python scripts/iter6_w4_degree3_star_controls.py
python research/iteration6/route_stitch/independent_l3_audit.py
python research/iteration6/route_stitch/independent_w4_matching_audit.py
python research/iteration6/route_stitch/independent_w4_three_path_all_d_audit.py
python research/iteration6/route_stitch/independent_w4_equal_star_audit.py
```

## 8. Timing

- Root-observed start bound: `2026-08-22 16:34:10 +08:00`.
- First local clock sample: `2026-08-22 16:35:36 +08:00`.
- Required local no-finish threshold: `2026-08-22 18:35:36 +08:00`.
- Actual final validation/end: `2026-08-22 18:37:07.758 +08:00`.
- Elapsed from the first local sample: `7291.758` seconds
  (2 h 1 min 31.758 s).  The threshold was satisfied.  Full machine-readable
  timing is in `TIMING.json`.
