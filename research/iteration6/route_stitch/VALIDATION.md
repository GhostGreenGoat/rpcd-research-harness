# Validation record

Date: 2026-08-22 (Asia/Shanghai)

The final regression suite was run with the bundled Python runtime and SymPy
from the repository root.  All checks are deterministic and exact except the
displayed decimal location of `c_*`, which is only a diagnostic.

## Static checks

- all route Python files compile with `py_compile`;
- all eight committed route JSON files parse successfully;
- every path listed in `PORTABLE_RUNBOOK.md` exists;
- no script reads credentials or account-local configuration.

## Exact checkers

| Checker | Expected scope | Final verdict |
|---|---|---|
| `verify_extremal_geometry.py` | one exact extreme/shorting obstruction | PASS |
| `verify_spectral_rank2_region.py` | exact regression for audited spectral formulas | PASS |
| `verify_continuation_obstructions.py` | exact `n=2` interpolation barriers | PASS |
| `independent_l3_audit.py` | pivotal scalar/operator identities for general `L3` | PASS |
| `independent_w4_matching_audit.py` | arbitrary matching-support child, `d>=6` | PASS |
| `independent_w4_three_path_audit.py` | weighted path at `d=6` | PASS |
| `independent_w4_three_path_all_d_audit.py` | weighted path for all `d>=6` | PASS |
| `independent_w4_equal_star_audit.py` | equal-weight stars for all stated `p,d` | PASS |

Final-suite completion timestamp: `2026-08-22T18:35:47.1038278+08:00`.

Passing these checkers does not enlarge the scope of the analytic statements.
In particular, the last three rows do not prove universal `W4`.
