# Iteration 4 / T085 final report

Conservative root-observed active interval: `2026-08-21 17:31:54 +08:00`--
`2026-08-21 19:32:53 +08:00` (`120.996` minutes, `7260` seconds).  All universal statements not
explicitly proved below remain conjectures.

## Outcome

The desired `O(n/mu log(1/epsilon))` coordinate complexity remains open.  This iteration produced
three material advances and two sharp route failures:

1. an exact leverage-aware compression of the second Schur-loss moment, with complementary
   pre-lift/post-lift bounds and a valid parallel-sum or adaptive combination;
2. an exact proof that fixed or sublinear determinant-tail depth cannot give a universal constant,
   plus structured evidence that half deletion depth with constant `1/2` is the right target;
3. a rigorous no-prefactor transfer from any such matrix certificate to expectation of squared
   distance, expectation of distance, fixed-time high probability, and a Ville all-time envelope;
4. exact counterexamples to the boundary constant-two/T080 and its finite positive-`mu` M1 lift;
5. exact sharpness barriers showing that no global one-step constant above `1/2` is possible and
   that bare Jensen cannot prove any positive dimension-uniform constant.

None of these counterexamples refutes the original covariance-map spectral-radius conjecture
C001.  They refute stronger auxiliary one-step certificates or particular proof compressions.

## Proved algebraic components (proof-draft status)

- The ordered-pair representation of the second Schur moment and the trace/trace-square spectral
  compression are in `compression_lemma.md`.
- The complementary bounds `R<=U`, `R<=W`, and hence `R<=2(U:W)`, are deterministic Loewner
  inequalities.  Their finite float tests are implementation checks, not their proof.
- The unconditional two-step certificate
  `J_2(B)>=(2mu/m)B^{-1}` gives
  `E||x_t||_A^2<=(1-2mu/n)^t||x_0||_A^2`, hence
  `O(n^2/mu log(1/epsilon))` coordinate updates.
- On signed rank one,
  `lim_{mu->0}c_r/mu=(2r-1-1/m)/(m-1)` for `r<=m-3`; therefore every `r=o(m)` determinant-tail
  proof fails.
- For block-diagonal unions of signed-rank-one blocks, the half-depth coefficient has boundary
  `liminf` at least `1/2` by an exact hypergeometric calculation.
- For a single signed-rank-one block, the stronger all-`mu` statement is now exact:
  `H_{ceil(n/2)}>=(mu/2)A^{-1}`.  The transverse proof counts distinguished coordinates in the
  prefix; the parallel proof solves the scalar lift recurrence.

## Sharp surviving conjecture

The remaining certificate is

`H_{ceil(n/2)}(A)>=(mu/2)A^{-1}`.

If true, it implies

```
E||x_t||_A^2 <= (1-mu/2)^t ||x_0||_A^2,
E||x_t||_A   <= (1-mu/2)^(t/2)||x_0||_A,
N_squared <= (2n/mu)log(1/epsilon),
N_expected_distance <= (4n/mu)log(1/epsilon),
N_high_probability <= (2n/mu)[2log(1/epsilon)+log(1/delta)]
```

for the two respective relative tolerances.  In particular, the second line is the stronger
user-requested expectation of distance, not distance of the expected iterate.  The constant cannot be improved within a universal
one-step energy inequality: for `A=mu I+(1-mu)11^T`, the parallel direction gives an iterated
large-`n`, `mu->1` upper limit `gamma(A)/mu<=1/2`.  A matching elementary lower bound proves that
this family's exact infimum is `1/2` (the parallel ratio stays above `1/2`, and every transverse
ratio is at least one).

The search through `n=1000` on signed rank one approaches `0.505351`; random/structured searches
through dimension ten found no half-depth violation.  These are E1 null searches, not proof.

## Exact hostile-audit results

- `docs/ITER4_AUDIT_T080_SIMPLE_SUBSET_DP.md` independently reconstructs the small-fraction
  `2/3,1/3` example with a full `2^8` Fraction Bellman DP.  It checks the actual Schur reducing
  line and an exact `mu=1/100` positive-definite M1 failure.
- `docs/ITER4_AUDIT_T080_EXACT_COUNTEREXAMPLE.md` independently reconstructs the separate
  `4/5,71/125` example by all `8!` generic forward/back solves, including update-product
  orientation, category multiplicities, reducing action, and an exact `mu=1/1000` M1 failure.
- `docs/ITER4_T090_CONSTANT_ASSESSMENT.md` records the sharp repaired constants.  Boundary `3/2`
  remains open and asymptotically sharp.  Global constant one is false at exact `n=9,mu=9/10`;
  no global constant above `1/2` is possible.  The bare Jensen ratio is already
  `20000/42671<1/2` in a transverse direction at `n=12,mu=1/100` (and
  `3200/6401<1/2` in the parallel direction at `n=21,mu=9/20`); it tends to zero at fixed `mu`
  as dimension grows.

## Main blocker

The second moment can now be compressed without losing either canonical singular geometry, but a
third Bellman lift contains the nonlinear average

`mean_i L_i^T [2(U_{C_i}:W_{C_i})] L_i`.

No dimension-uniform inequality closes this state.  Scalarizing the children loses an unbounded
factor on the simplex family; fixed shallow moment/Bessel states also have counterexamples; and
pathwise complementary-half pairing is exactly false.  The next viable attack must retain
anisotropic variance across a linear number of deletion levels or find a new averaged prefix
inequality proving the half-depth target directly.

## Reproduction

Key exact commands:

```
python scripts/verify_iter4_t085_exact.py
python scripts/verify_iter4_t080_simple_subset_dp.py
python scripts/verify_iter4_t080_counterexample_independent.py
python scripts/iter4_t090_constant_attack.py
python scripts/verify_iter4_t090_signed_rank_one_interior.py
python scripts/verify_iter4_t090_bare_jensen_barrier.py
python -m unittest discover -s tests -v
```

Key numerical commands and fixed seeds are recorded in the individual evidence JSON files and
checkpoints.  The two temporary smoke evidence files were removed after the full runs superseded
them.  Exact pass/fail outcomes are collected in `VALIDATION_LOG.md`.
