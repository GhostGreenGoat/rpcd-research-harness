# Iteration 5 portable handoff

This handoff contains no credentials or Codex account state.  The normalized
parameter is always

```
mu=lambda_min(D^{-1/2} Q D^{-1/2}),  D=Diag(Q).
```

## Main reading order

1. `docs/ITER5_FAILURE_MAP_AND_ROUTES.md`
2. `docs/ITER5_MATRIX_INEQUALITY_SYNTHESIS.md`
3. `research/iteration5/route_c/weighted_prefix_sos.md`
4. `research/iteration5/route_a/linear_memory_dual.md`
5. `research/iteration5/route_a/local_inverse_schur_residual.md`
6. `research/iteration5/route_b/satellite_asymptotics.md`

The promoted internal proof candidates are C035--C042.  None is a claimed
solution of the general RPCD problem.  C041 proves the target order for every
matrix in an explicit high-`mu` band; C035 and C040 prove stronger or
complementary statements on equicorrelation families, while C042 closes one
asymptotically hostile satellite-transverse sector at every fixed satellite
count.

## Reproduction commands

Use the bundled Python runtime or any Python 3.11+ environment with the
project requirements installed.

```text
python -m unittest discover -s tests -v
python -m rpcd_harness.cli audit-ledger
python scripts/iter5_equicorrelation_half_prefix.py
python scripts/iter5_prefix_identity_jet.py --max-n 7
python scripts/verify_iter5_route_c_weighted_prefix.py
python scripts/iter5_linear_memory_half_limit_proof.py
python scripts/iter5_linear_memory_finite_certificate.py
python research/iteration5/route_a/scripts/verify_local_inverse_schur_residual.py
python research/iteration5/route_a/scripts/stress_linear_memory_generic.py
```

## Closed proof shortcuts

- fixed positional or fixed adjacency dual features;
- per-position `mu/n` gain and chronological monotonicity;
- scalar child-half lifting and determinant-volume-only closure;
- rowwise cardinality damping of the local-inverse Schur residual;
- shallow row-Bessel compression of the third weighted Bellman state.

These have exact artifacts and should be used as regression tests rather than
retried without a new state that restores the discarded covariance.

## Next falsifiable tasks

First attack the explicit degree-four Bellman state
`L_3>=(2mu/n)A^{-1}` in
`research/iteration5/route_c/higher_bellman_closure.md`.  The target has
survived 17,920 hostile cases and is exact on the full equicorrelation
interval; any proof must retain the anisotropic residual discarded by the
known-false row-Bessel scalarization.

In parallel, for `q=ceil(n/2)`, prove or refute a multirow random-frame inequality for the
local inverse `D_(pi,q)` that bounds its conditional-tail second moment.  A
successful statement may take either form

```text
Q_q <=(C/mu)P_q A P_q
```

with universal finite `C`, or directly

```text
P_q Q_q^{-1}P_q >=c mu A^{-1}.
```

It must exploit cancellation between residual rows.  The pathwise single-row
bound `rB_O^{-1}r^T<=1-mu` is not summable by worst-case scalar estimates.
