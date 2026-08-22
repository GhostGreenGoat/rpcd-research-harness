# Portable runbook for Iteration 6 Route C

The route is account-independent.  It reads and writes only repository files
and does not require web access, credentials, `.codex`, `auth.json`, or an
`.env` file.

## Requirements

- Python 3.10 or newer;
- SymPy available in that Python environment;
- run commands from the repository root.

The exact proofs are in the Markdown notes.  The scripts are regression and
finite-certificate checkers; a `PASS` does not replace the quantified
analytic argument.

## One-account / one-machine reproduction

```powershell
python research/iteration6/route_stitch/verify_extremal_geometry.py
python research/iteration6/route_stitch/verify_spectral_rank2_region.py
python research/iteration6/route_stitch/verify_continuation_obstructions.py
python research/iteration6/route_stitch/independent_l3_audit.py
python research/iteration6/route_stitch/independent_w4_matching_audit.py
python research/iteration6/route_stitch/independent_w4_three_path_audit.py
python research/iteration6/route_stitch/independent_w4_three_path_all_d_audit.py
python research/iteration6/route_stitch/independent_w4_equal_star_audit.py
```

Expected result: every command exits zero and prints a JSON object containing
`PASS`.  The all-dimensional three-path audit is the slowest exact check.

## Splitting across accounts

The eight commands are independent and may be assigned to different accounts
or machines.  Copy the repository (including this directory and
`research/iteration6/route_l3`) and preserve relative paths.  No command
depends on output from a different command.  Compare printed output with the
committed `*_AUDIT.json` or `*_EXACT.json` snapshot bearing the same topic.

The independent audit scripts deliberately do not import the sibling source
checkers.  This prevents an algebraic bug in a source checker from being
silently reused by its audit.

## Result map

| Topic | Analytic note | Independent evidence |
|---|---|---|
| Extreme elliptope / shorting gap | `extremal_geometry.md` | `EXTREMAL_GEOMETRY_EXACT.json` |
| Exterior spectral regions | `spectral_geometry_region.md` | `SPECTRAL_RANK2_EXACT.json`; sibling hostile audit in `route_l3` |
| Boundary continuation failures | `continuation_obstructions.md` | `CONTINUATION_EXACT_BARRIERS.json` |
| General `L3` | `L3_HOSTILE_AUDIT.md` | `L3_INDEPENDENT_EXACT_AUDIT.json` |
| Matching-support `W4` | `W4_MATCHING_BLOCK_HOSTILE_AUDIT.md` | `W4_MATCHING_BLOCK_INDEPENDENT_AUDIT.json` |
| Three-path `d=6` | `W4_THREE_PATH_D6_HOSTILE_AUDIT.md` | `W4_THREE_PATH_D6_INDEPENDENT_AUDIT.json` |
| Three-path all `d>=6` | `W4_THREE_PATH_ALL_D_HOSTILE_AUDIT.md` | `W4_THREE_PATH_ALL_D_INDEPENDENT_AUDIT.json` |
| Equal-weight stars | `W4_EQUAL_STAR_ALL_D_HOSTILE_AUDIT.md` | `W4_EQUAL_STAR_ALL_D_INDEPENDENT_AUDIT.json` |

## Interpretation guardrail

Exact finite arithmetic is E2 unless paired with a quantified analytic proof.
The audited universal statements in their explicitly stated scopes are
internal E4 candidates.  None of these artifacts proves unrestricted `W4`,
the all-depth Bellman hierarchy, or the full RPCD conjecture.
