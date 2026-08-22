# Iteration 6 root synthesis report

Date: 2026-08-22 (Asia/Shanghai)

Status: the requested analytic iteration is complete.  The unrestricted RPCD
finite-time conjecture remains open.  Every theorem below is an internal
candidate at the stated evidence level; none has Lean/formal verification or
external peer review.

## Main advances

1. The exact anisotropic third-level Bellman state now satisfies, for every
   real unit-diagonal SPD matrix and every dimension `n>=3`,

   ```text
   C3(A)=J3(A)-J2(A)/2 >= L3(A) >= (2mu/n)A^-1.
   ```

   A separate route rebuilt the proof from definitions.  Consequently
   `J3>=(3mu/n)A^-1`, giving a strong expectation-of-distance finite-time
   bound of `O(n^2/mu log(1/epsilon))` coordinate updates in all dimensions.
   For `n<=6` the half-prefix certificate reaches the conjectured
   `O(n/mu log(1/epsilon))` order.

2. The next hierarchy step is reduced to the explicit directional `W4`
   shifted-inverse inequality.  It remains open in general, but independent
   exact audits prove it for three dimension-uniform families:

   - arbitrary signed, unequal matching-support blocks plus isolates;
   - an arbitrarily weighted three-vertex path plus isolates;
   - an equal-magnitude signed star plus isolates.

   Thus an isolated degree-two interaction and symmetric high vertex degree
   are not the obstruction.  The smallest live geometries are an overlapping
   four-path, a sign-frustrated cycle, and an unequal-weight star.

3. The exterior/volume certificate now has a scalar spectral criterion.  It
   proves the target for every matrix with at most two eigenvalues below one,
   and for constant-diagonal isotropic low projectors of rank at most three.
   A rank-four exact example shows the bare exterior certificate is already
   insufficient, without being an RPCD counterexample.

4. A boundary-ray comparison and low/high shorted spectral stitch were proved.
   The remaining hypothesis is a full Loewner shorting inequality; compression
   alone is exactly insufficient.

5. The covariance dynamics were rewritten as a fully symmetrized product of
   structured orthogonal projections on `Sym_n`.  A natural remaining-frame
   inverse Bellman potential was then refuted exactly, including on a genuine
   RPCD covariance lift.  This closes the potential, not the conjecture.

6. The random-window route produced a conditional regression hierarchy with
   an exact Pythagorean refinement identity.  Directed-cycle/cut conditioning
   freezes the adaptive half-window rows and reduces the remaining covariance
   question to an arc-incidence Hardy/Copson kernel.  Pathwise, reversal-only,
   and fixed-memory bounds were separately ruled out by analytic examples.

## Evidence and portability

The claim ledger entries `C043`--`C049`, exact JSON evidence, hostile audits,
failed lemmas, and reproduction commands contain no credentials or mutable
external state.  The complete entry point is
`research/iteration6/PORTABLE_HANDOFF.md`; the mathematical narrative is
`docs/ITER6_MATRIX_INEQUALITY_SYNTHESIS.md`.

Final validation used the bundled Python 3.12 runtime.  The repository's 27
unit tests passed, all new matching/path/star production and independent
checkers passed, 64 Iteration-6/claim JSON files parsed, and `git diff --check`
reported no whitespace error (only existing Windows line-ending warnings).

## Timing

- Root-observed active start: `2026-08-22T16:34:10+08:00`.
- Required root threshold: `2026-08-22T18:34:10+08:00`.
- Final validation end: `2026-08-22T18:45:50.5976230+08:00`.
- Active wall-clock interval: `7900.597623` seconds (about 131.68 minutes).
- Machine-readable record: `research/iteration6/root/TIMING.json`.
