# Iteration 4 / T085 validation log

All commands were run from the repository root with the bundled Python 3.12 runtime on
`2026-08-21`.

| Command | Outcome |
|---|---|
| `python scripts/verify_iter4_t085_exact.py` | pass; ordered-pair identities, rational barriers, and recurrences agree |
| `python scripts/verify_iter4_t080_simple_subset_dp.py` | pass; `2^8` exact DP recovers `1057837/531441` and the finite M1 violation |
| `python scripts/verify_iter4_t080_counterexample_independent.py` | pass; two full `8!` Fraction enumerations, orientation/reducing checks, finite M1 violation |
| `python scripts/iter4_t090_constant_attack.py` | pass; exact `c=1` and bare-Jensen barriers plus labelled E1 scans |
| `python scripts/verify_iter4_t090_signed_rank_one_interior.py` | pass; independent exact `n=9,mu=9/10` reconstruction |
| `python scripts/verify_iter4_t090_bare_jensen_barrier.py` | pass; independent full `12 by 12` Fraction reconstruction |
| `python -m unittest tests.test_iteration4 -q` | 5 tests passed |
| `python scripts/run_all_verifiers.py` | 25 tests passed; identity verifier and seeded smoke search completed |
| `python -m py_compile ...` on all new T085/T080/T090 scripts | pass |
| JSON parse over all task-local and new audit evidence | pass |
| exact-recurrence grid for signed-rank-one half depth, `3<=n<=100` and seven `mu` values | every ratio at least `1/2`; diagnostic only, while the quantified result rests on the algebra in `structured_asymptotics.md` |

An initial `python -m pytest tests/test_iteration4.py -q` attempt could not start because the
bundled runtime does not include `pytest`.  This is an environment-only issue: the same file is
standard-library `unittest`, and both the direct module invocation and the repository-wide verifier
passed.

The float searches remain E1 regardless of test success.  Exact verifier success certifies only
the displayed finite rational identities and signs, not a universal theorem.
