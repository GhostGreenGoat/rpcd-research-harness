# Iteration 6 portable handoff

Final handoff: the general `L3` Schur-compensation theorem has passed an
independent hostile audit; see `route_l3/schur_compensation_proof.md` and
`route_stitch/L3_HOSTILE_AUDIT.md`.  The universal remaining-frame inverse
potential is refuted exactly; see
`root/remaining_frame_inverse_potential.md`.  The unrestricted conjecture
remains open.

## Portable result index

- Full synthesis: `docs/ITER6_MATRIX_INEQUALITY_SYNTHESIS.md`.
- Route reports and timing: `root/FINAL_REPORT.md`,
  `route_l3/FINAL_REPORT.md`, `route_stitch/FINAL_REPORT.md`, and
  `route_frame/FINAL_REPORT.md`, with one `TIMING.json` in each route.
- Weighted third level and finite-time transfer:
  `route_l3/schur_compensation_proof.md`,
  `route_l3/n_le_6_finite_time.md`, claims `C043`--`C044`.
- Structured `W4` Schur recovery: arbitrary signed matching-support children
  in `route_l3/w4_matching_block_slice.md` (audit
  `route_stitch/W4_MATCHING_BLOCK_HOSTILE_AUDIT.md`), and weighted
  three-vertex paths in every `d>=6` in
  `route_l3/w4_three_path_all_d_slice.md` (audit
  `route_stitch/W4_THREE_PATH_ALL_D_HOSTILE_AUDIT.md`), and equal-magnitude
  signed stars in `route_l3/w4_equal_star_all_d_slice.md` (audit
  `route_stitch/W4_EQUAL_STAR_ALL_D_HOSTILE_AUDIT.md`); claim `C049`.
- Exterior spectral regions (at most two subunit eigenvalues; isotropic low
  rank at most three): `route_stitch/spectral_geometry_region.md`, audit
  `route_l3/spectral_geometry_hostile_audit.md`, claim `C045`.
- Boundary-ray interpolation and shorted stitching:
  `route_stitch/spectral_stitching.md`, audit
  `route_l3/spectral_stitching_hostile_audit.md`, claim `C047`.
- Projection covariance lift and exact inverse-potential failures:
  `root/projection_lift.md`, `root/remaining_frame_inverse_potential.md`,
  `route_frame/special_lift_bellman_counterexample.md`, claim `C046`.
- Conditional regression/cycle-cut hierarchy:
  `route_frame/conditional_dual_martingale_hierarchy.md`,
  `route_frame/cyclic_cut_freezing.md`, root audit
  `root/conditional_dual_hierarchy_audit.md`, claim `C048`.

All paths are repository-relative and all finite checks use the active Python
environment with dependencies declared in `pyproject.toml`.  No artifact depends on account-local
credentials or an external mutable service.

Status: complete for Iteration 6.  Every route met its two-hour active-time
floor and recorded a post-threshold final validation.  The unrestricted
conjecture and general `W4` inequality remain open.

Primary inherited reading:

1. `docs/ITER5_FAILURE_MAP_AND_ROUTES.md`
2. `docs/ITER5_MATRIX_INEQUALITY_SYNTHESIS.md`
3. `research/iteration5/PORTABLE_HANDOFF.md`
4. `docs/ITER3_ROUTE_M3_OPERATOR_LYAPUNOV.md`
