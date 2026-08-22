# Iteration 5 Route C final report

## Bottom line

The general RPCD half-depth inequality remains open.  This route produced a
new all-dimensional weighted two-prefix proof candidate, an exact
anisotropic state for the third Bellman level, and a precise
all-dimensional barrier showing why the successful level-two compression
cannot simply be repeated.

The clean surviving third-level target is

```
L_3(A) >= (2mu/m)A^-1,                                   (F1)
```

where `L_3` is the explicit degree-four matrix in
`higher_bellman_closure.md` (B5).  Since `C_3>=L_3`, (F1) would prove
`J_3>=(3mu/m)A^-1` and settle the desired half certificate through dimension
six.  Since `H_t>=J_t`, this exact-prefix result would be stronger than the
determinant-seeded target.  It survived 17,920 hostile numerical cases,
including mixed direct sums, but has not been proved.

## 1. Exact/proof-level progress

### 1.1 Weighted level two (internal E4)

For every unit-diagonal SPD `m x m` matrix `A`, `m>=2`,

```
J_2-(1/2)J_1 >= (3mu/(2m))A^-1.                          (F2)
```

The proof uses the exact `J_2` formula and the zero-diagonal row-square
lemma

```
H^2 <=(m-1)Diag(diag H^2),  H=A-I,
```

followed by a two-branch exact scalar argument using both the spectral floor
and the trace upper endpoint.  Full details are in
`weighted_prefix_sos.md`.  Route A independently reconstructed and
hostile-audited every algebraic and scalar step with outcome PASS, so claim
C036 has internal E4 status.  It is not Lean/formally verified and has not
received external mathematical review.

Combining (F2) with `J_1=I/m>=(mu/m)A^-1` gives the known-strength
consequence `J_2>=(2mu/m)A^-1`, hence the desired half certificate for
`m<=4`.

### 1.2 Exact third-prefix algebra

The exact codimension-two formula is

```
J_3=I/m+{(2m-3)[mI-2A+D_2]-2[mA-2A^2+D_3]+T(A)}
         /[m(m-1)(m-2)],
```

with the PSD ordered-pair frame

```
T(A)=sum_{i!=j}[(A^2)_jj-A_ij^2]
     (e_j-A_ij e_i)(e_j-A_ij e_i)^T.
```

This was reconstructed exactly against the Bellman recursion on rational
matrices.

### 1.3 Adaptive square state

Lifting the matrix polynomial behind (F2), rather than its scalar
consequence, produces

```
S=sum_i L_i^T(C_i-I)^2L_i
 =(m-3)H^2-2H^3+HD+DH+Diag(diag F^2),
F=H+H^2-D.
```

It gives the explicit lower state `C_3>=L_3` in (F1).  This retains the
anisotropy lost by all earlier child-scalar lifts.  The identity and closed
formula were checked in exact rational arithmetic in dimensions four and
five.  A companion exact bound
`-(1-mu)D<=Diag(diag H^3)<=(m-2)(1-mu)D` follows from child
interlacing; it is sharp but insufficient without the fourth-moment state.

### 1.4 Structured and exterior results

The stronger sufficient adaptive inequality `(F1)` itself holds exactly on
the full compound correlation family

```
A=(1-a)I+a11^T,  -1/(m-1)<a<1,
```

for `m>=3`, by parallel/transverse factorization and Bernstein-positive polynomials.
Therefore the weighted third-level inequality also holds there.  This is an
E3 structured proof candidate.

For arbitrary `A`, conditioning on the unordered prefix support gives the
exact exterior certificate

```
A^(1/2)J_t(A)A^(1/2)
 >=A grad e_t(A)/binom(m,t).
```

This is dimension-uniform, but its exact rank-one barrier below shows it is
not sufficient at low `mu`.

## 2. Exact hostile barriers (E2)

All five records in `evidence/EXACT_ROUTE_BARRIERS.json` refute auxiliary
proof compressions, not RPCD itself.

1. A three-dimensional rational matrix refutes uniform new gain
   `J_2-J_1>=(mu/3)A^-1`; the exact gap determinant is
   `-1624139/2499268608`.
2. A size-two rank-one block plus a size-three simplex block refutes lifting
   only exact child scalar half floors; normalized ratio
   `4129401/10100000<1/2`.
3. The volume-adjugate subset certificate on `m=6,t=3,mu=1/10` has
   parallel coefficient `11/400`, short of `mu/2` by `9/400`.
4. The local triple proxy
   `K(C)-J_2(C)/2>=(3I-C)/3` has exact witness value `-11/48`.
5. The valid second row-Bessel compression
   `S>=R^2/(m-1)` misses `(F1)` for every `m>3` near the signed-rank-one
   boundary.  Its exact limiting ratio is

   ```
   (3m-1)/[2m(m-1)]
    = (1/m)[3/2+1/(m-1)],
   ```

   with gap `-(m-3)/[2m(m-1)]` to `2/m`.

Barrier 5 is the crisp final blocker: the residual
`S-R^2/(m-1)` cannot be scalarized away.  A two-feature adaptive
matrix-fractional lift was derived, but it becomes rank-one and collapses to
the same failed compression on equal-correlation rows.  Coordinate-resolving
feature rank therefore has to grow with dimension, or the full `S` state
must remain in the recursion.

A calibrated fallback remains open: the compressed state survived the
weaker target `tilde L_3>=(3mu/(2m))A^-1`, whose rank-one boundary surplus
is exactly `1/[m(m-1)]`.  Proving it would already settle the requested half
certificate through dimension five, but current support is only E1.

## 3. Independent cross-route audits

These audits were performed from the definitions, not by trusting the
originating scripts.

* `P=E[D_pi^TD_pi]=[(n+1)I-2B+Diag(diag B^2)]/n` and
  `P>=mu B^-1` were independently reconstructed.  The proposed fixed
  adjacency closure is false, and in fact no universal larger constant can
  save it: for fixed positive equicorrelation its normalized parallel
  coefficient is asymptotic to `3/[n rho(1-rho)]`.
* The half-linear-memory dual proof on positive equicorrelation was audited
  through its exact defect formula, scaling-limit Taylor certificate,
  finite `S_q` bound, even/odd dimensions, `n=2`, norm direction, and
  Loewner inversion.  No blocker was found.  Its scope is that family only.
* The general near-identity band proof
  `n(1-mu)<=1 => K(B)>=(mu/4)B^-1` was audited.  The eigenvalue-simplex
  extremum, triangular Frobenius factor, and inverse direction are correct.
  Its direct-prefix corollary was also audited: if
  `n(1-mu)<=2-sqrt(2)`, then
  `H_ceil(n/2)>=J_ceil(n/2)>=(mu/4)B^-1` for every such matrix.  This
  prefix statement is distinct from the sharper full-epoch `K` certificate.

Audit details are in `route_a_preconditioner_cross_audit.md`,
`linear_memory_dual_hostile_audit.md`, and
`near_identity_band_audit.md`.

## 4. Evidence and reproducibility

Main exact verifiers:

```
scripts/verify_iter5_route_c_weighted_prefix.py
scripts/iter5_route_c_exact_barriers.py
scripts/verify_iter5_route_c_route_a_cross_audit.py
scripts/verify_iter5_route_c_fixed_adjacency_asymptotic.py
scripts/verify_iter5_route_c_linear_memory_audit.py
```

Main hostile searches:

```
scripts/iter5_route_c_j3_sos_search.py
scripts/iter5_route_c_adaptive_state_search.py
```

All outputs, seeds, evidence levels, and scope warnings are under
`research/iteration5/route_c/evidence/`.  Python byte-compilation,
`git diff --check`, and all exact verifier runs passed in the final
validation.

## 5. Recommended next attack

Attack (F1) directly, retaining

```
S=sum_i W_i^TW_i
```

rather than replacing it by its first aggregate moment.  The most promising
finite next step is a permutation-invariant SOS with matrix-valued
multipliers for the orthogonal residual `S-R^2/(m-1)` and the spectral
constraints `A-mu I` and `[m-(m-1)mu]I-A`.  Any fixed collection of scalar
row features is unlikely to close because it degenerates on the exact
signed-rank-one barrier.  In parallel, the dual architecture should use
linearly growing memory; fixed adjacency cannot yield any dimension-free
constant.

## 6. Timing

The root-observed start bound was `2026-08-21 19:37:57 +08:00`.  Final
validation completed at `2026-08-21 21:39:03 +08:00`, for an elapsed
`02:01:06` (7,266 seconds).  `TIMING.json` records the timestamps and confirms
that the required two-hour threshold was satisfied.
