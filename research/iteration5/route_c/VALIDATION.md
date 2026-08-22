# Final validation log

Validation date: 2026-08-21 (Asia/Shanghai).

The bundled workspace Python executable was used.  The following exact
verifiers completed with exit code zero:

```
scripts/verify_iter5_route_c_weighted_prefix.py
scripts/iter5_route_c_exact_barriers.py
scripts/verify_iter5_route_c_route_a_cross_audit.py
scripts/verify_iter5_route_c_fixed_adjacency_asymptotic.py
scripts/verify_iter5_route_c_linear_memory_audit.py
```

They reconstructed the `J_3` Bellman formula, adaptive `S` state, compound
Bernstein certificates, five rational route barriers, weighted-adjacency
path average and Bernstein coefficients, fixed-memory asymptotic decay, and
finite linear-memory parity/endpoints.

The independently produced hostile audit
`research/iteration5/route_a/ROUTE_C_W2_HOSTILE_AUDIT.md` reports PASS for
the weighted two-prefix proof; ledger claim C036 records internal E4 with
formalization and external-review gates still false.

Both float hostile scripts also completed and wrote their seeds and sample
counts:

```
scripts/iter5_route_c_j3_sos_search.py
scripts/iter5_route_c_adaptive_state_search.py
```

The current adaptive search contains 17,920 evaluations.  It is E1 only.
All modified Python files passed `py_compile`, and `git diff --check`
reported no whitespace errors.
