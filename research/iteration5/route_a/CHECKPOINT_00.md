# Iteration 5 route A — checkpoint 00

Observed start: 2026-08-21 19:38:29 +08:00.  This worker will not close the
iteration before 2026-08-21 21:37:57 +08:00.

## Target and evidence status

For every unit-diagonal SPD `B` of size `m`, with
`mu=lambda_min(B)` and `r=ceil(m/2)`, test the open Loewner inequality

```
H_r(B) >= (mu/2) B^{-1}.
```

Here `H_0(B)=det(B)B^{-1}` and

```
H_{s+1}(B)=m^{-1} sum_i [e_i e_i^T+L_i^T H_s(B_{-i,-i})L_i].
```

Nothing in this directory is a theorem unless its evidence level and audit
status say so.  The general target is open; it is proved only through `m=4`
and on the signed-rank-one family.

## Read-in from Iteration 4

The following were read before attempting a new proof:

- `research/problem.md`, `research/tasks/T095-uniform-boundary-constant.json`,
  `docs/METHOD.md`, and the researcher/common prompts;
- the Iteration 4 synthesis, Bellman-closure, structured-asymptotic, and
  finite-time documents;
- the hostile audits of global half-sharpness, signed-rank-one half-depth,
  signed-rank-one interior sharpness, and the `J_2` low-dimensional result;
- the second-Schur-moment compression and the exact bare-Jensen/reverse-word
  barriers.

Exact failures that must not be retried as proof steps are: bare inverse
Jensen, word/reverse-word or complementary-prefix pathwise pairing, fixed
shallow determinant depth, `R_2 <= C R_1`, and scalar child induction.

## Three planned analytic avenues

1. A remaining-gradient potential for the random prefix, keeping both the
   prefix energy and a remaining-frame observable.
2. An averaged projection/frame inequality for sampling strongly without
   replacement, with exact tests of every proposed conditional step.
3. A dual/Rayleigh formulation in which the adversarial right side is exposed
   before the random order, followed by minimax or subset symmetrization.

Numerical searches will only falsify intermediate lemmas.  Any surviving
identity will be reconstructed with exact rational arithmetic when finite.
