# Checkpoint 04: two-hour closeout

## Auditable timing

- Conservative root-observed active start: `2026-08-21 17:31:54 +08:00`.
- Actual closeout timestamp from `Get-Date`: `2026-08-21 19:32:53 +08:00`.
- Root-observed active interval: `120.996` minutes (`7260` seconds).

This deliberately does not claim an earlier start.  The closeout was written only after the
root-observed two-hour threshold had elapsed.

## Results at closeout

1. The universal half-depth certificate
   `H_{ceil(n/2)}(A)>=(mu/2)A^{-1}` remains open.  Exact shallow signed-rank-one asymptotics prove
   that depth `o(n)` cannot suffice for the determinant-tail hierarchy, while the half-depth
   coefficient is at least `1/2` on disjoint signed-rank-one boundary blocks.
2. For the single equicorrelation/signed-rank-one family
   `A=mu I+(1-mu)11^T`, the all-`mu` half-depth certificate is proved algebraically.  The
   transverse block follows from distinguished-coordinate prefix counting; the parallel block
   follows from `q_k=1+mu^2 q_{k-1}` and the geometric lower sum.  A separate hostile audit was
   dispatched at closeout; until that reconstruction reports, this remains labelled a structured
   proof candidate rather than a universally audited theorem.
3. Exact rational examples refute the stronger T080 constant-two claim, its finite positive-`mu`
   M1 transfer, the global one-step constant-one candidate, and the bare-Jensen route.  These do
   not refute the covariance-map spectral-radius conjecture C001.
4. The one-step signed-rank-one family has exact universal infimum `gamma/mu=1/2`; hence no
   universal one-step energy constant greater than `1/2` is possible.  Bare Jensen is worse: its
   dimension-uniform ratio tends to zero, so Bellman/variance information is essential.
5. Any certificate `H>=gamma A^{-1}` gives, without an additional prefactor,
   `E||x_t||_A^2<=(1-gamma)^t||x_0||_A^2` and
   `E||x_t||_A<=(1-gamma)^(t/2)||x_0||_A`.  Markov yields the fixed-time high-probability bound;
   Ville applied to the normalized energy supermartingale gives the stated all-time envelope.

## Verification at closeout

The following commands had passed before this checkpoint:

```text
python scripts/verify_iter4_t085_exact.py
python scripts/verify_iter4_t080_simple_subset_dp.py
python scripts/verify_iter4_t080_counterexample_independent.py
python scripts/iter4_t090_constant_attack.py
python scripts/verify_iter4_t090_signed_rank_one_interior.py
python scripts/verify_iter4_t090_bare_jensen_barrier.py
python -m unittest tests.test_iteration4 -q
python scripts/run_all_verifiers.py
```

The repository-wide verifier reported 25 passing tests.  A later direct standard-library
`unittest` run reported seven passing iteration-4 tests after concurrent additions.  The bundled
runtime lacks `pytest`; that missing optional runner is recorded as an environment limitation, not
as evidence of failure.  All floating-point searches remain E1 numerical evidence; the exact
scripts certify only their displayed finite rational identities and signs.
