# Independent audit of the conditional dual-regression hierarchy

Date: 2026-08-22.

Target: `../route_frame/conditional_dual_martingale_hierarchy.md`.

Verdict: **PASS** for the finite-dimensional SPD/local-inverse setting used
here.  The hierarchy is an exact lower-certificate theorem; it does not yet
supply a dimension-free rate.

## 1. Regression orientation

With `X=M^-1`, `R=D^TD`, and `Y=M^TR`, direct multiplication gives

```
X^T Y=M^-T M^T R=R,
Y^T Y=RMM^TR.
```

For a coefficient `W` measurable with respect to a sigma-field `G`, the
conditional square expands to

```
E[(X-YW)^T(X-YW)|G]
 =E[X^TX|G]-P_GW-W^TP_G+W^TQ_GW.
```

Here `D` is unit triangular and hence `R>0`; `M` is invertible, so `Q_G>0`.
The optimizer is exactly `W=Q_G^-1P_G`, with conditional improvement
`P_GQ_G^-1P_G`.  Averaging proves the claimed lower bound.  No transpose or
distance/expected-iterate swap is present.

## 2. Monotonicity under refinement

The epigraph of `phi(P,Q)=PQ^-1P` is the Schur-complement LMI

```
[[Q,P],[P,T]]>=0.
```

Thus `phi` is jointly matrix convex on `Q>0`.  If `G` is coarser than `H`,
conditional Jensen gives

```
phi(P_G,Q_G)<=E[phi(P_H,Q_H)|G].
```

Taking expectations proves `C_G<=C_H`.  At the full-order sigma-field,

```
R(RMM^TR)^-1R=M^-TM^-1=X^TX,
```

so the endpoint is exactly `K`, not merely another relaxation.

## 3. Scope

- The proof is exact for the finite uniform permutation space; no numerical
  limit or independence approximation is used.
- If a future feature permits singular `R`, the statement must use supported
  ranges/pseudoinverses and recheck the range conditions.  The present
  local-inverse feature has `R>0`, so this caveat is inactive.
- The cycle-conditioned level is strictly more informative in Loewner order
  than the global regression certificate, but a uniform lower coefficient
  remains open.  The audit does not promote the arc Hardy/Copson estimate to
  a rate theorem.

The sibling exact enumeration verifier was run after this independent
algebraic reconstruction and passed.
