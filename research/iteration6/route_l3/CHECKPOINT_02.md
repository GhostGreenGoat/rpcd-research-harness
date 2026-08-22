# Checkpoint 02 — audited `L3`, general recursion, and the `W4` frontier

- Local checkpoint: `2026-08-22 17:29:14 +08:00` (about 54 minutes after the
  first local clock sample).
- All three portable exact scripts compile and report PASS.

## Evidence promotion

The explicit theorem candidate

```text
L3(A)>=(2mu/m)A^-1,   m>=3,
```

passed an independent hostile reconstruction with no blocking caveat:

```text
research/iteration6/route_stitch/L3_HOSTILE_AUDIT.md
research/iteration6/route_stitch/independent_l3_audit.py
research/iteration6/route_stitch/L3_INDEPENDENT_EXACT_AUDIT.json
```

It is therefore internal E4 under the repository evidence ladder.  It remains
without Lean formalization or external peer review.

## General-depth recursion

For a child level with inverse coefficient
`alpha=tmu/[2(m-1)]`, define the exact directional recovery coefficient

```text
kappa_i=s_i/[c_i^TQ_i^dagger c_i]
```

with the range conventions recorded in `general_t_schur_recursion.md`.  The
only unresolved defect at the next weighted level is

```text
(1/m)sum_i(alpha-kappa_i)_+D_i.
```

The exact allowable budget is

```text
[tmu(1-mu)/(2m(m-1))]A^-1.
```

This is the general recursive matrix condition; it neither scalarizes child
floors nor averages inverses in the wrong Jensen direction.

## Exact `W4` state and blocker

```text
L4=I/(2m)+(1/m)sum_i L_i^TL3(C_i)L_i,
Q_i=L3(C_i)-(2mu/(m-1))C_i^-1.
```

For the hierarchy-relevant range `m>=7`, full termwise recovery asks

```text
Q_i >=[2mu/((m-1)s_i)]c_ic_i^T.
```

Equivalently, by Woodbury,

```text
L3(C_i)>=[2mu/(m-1)](C_i-b_ib_i^T)^-1.
```

The global spectral terms of the audited `L3` certificate cannot prove this:
at `d=6,mu=1/100,lambda=1`, their exact Schur-envelope gap is
`-6501/79600`.  On the realizing direct-sum parent, the full anisotropic state
repairs it and has exact ratio `99/199<1`.  Thus the smallest blocker is to
control the retained child `M_j` matrices, not to improve a scalar spectral
constant.

Analytic `W4` slices now proved internally (E3, pending independent audit):

- isolated outer coupling `C=[1] direct_sum B`, `b=re_1`;
- the complete positive-equicorrelation family for child `d>=6`, by positive
  Bernstein coefficients;
- the complete negative-equicorrelation family, by an all-positive rational
  factorization.

Fixed asymmetric rational controls remain E2 only.

## Finite-time consequences

For every `n>=3`,

```text
K>=J3>=(3mu/n)A^-1.
```

Hence expectation of `A`-distance reaches relative tolerance `epsilon` in

```text
N_all<=n ceil{(2n/(3mu))log(1/epsilon)}
```

coordinate updates.  This is an all-dimensional
`O(n^2/mu log(1/epsilon))` strong-expectation benchmark.  For `n<=6`, the
half-prefix coefficient gives the sharper conjectured-order bound
`N<=n ceil{4log(1/epsilon)/mu}`; odd dimensions retain better constants.
