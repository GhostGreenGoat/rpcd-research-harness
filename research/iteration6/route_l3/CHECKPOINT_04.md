# Checkpoint 04 — final post-threshold validation

- Root-observed start bound: `2026-08-22 16:34:10 +08:00`.
- First local clock sample: `2026-08-22 16:35:36 +08:00`.
- Required local threshold: `2026-08-22 18:35:36 +08:00`.
- Final validation end from `Get-Date`:
  `2026-08-22 18:37:07.758 +08:00`.
- Elapsed from first local sample: `7291.758` seconds (2 h 1 min 31.758 s).
- Threshold satisfied: **yes**.

The post-threshold run passed all nine selected universal/exact scripts:

```text
iter6_l3_schur_compensation.py
iter6_l3_exact_barriers.py
iter6_w4_matching_block_exact.py
iter6_w4_three_path_all_d_exact.py
iter6_w4_equal_star_symbolic.py
independent_l3_audit.py
independent_w4_matching_audit.py
independent_w4_three_path_all_d_audit.py
independent_w4_equal_star_audit.py
```

Final evidence status:

- general `L3` inequality: internal E4;
- all-dimensional `J3` finite-time transfer: exact consequence of internal E4
  premises;
- matching, weighted-three-path, and equal-weight-star uniform `W4` slices:
  internal E4;
- unrestricted uniform `W4` shifted-inverse inequality: open;
- no Lean/formal or external peer review.
