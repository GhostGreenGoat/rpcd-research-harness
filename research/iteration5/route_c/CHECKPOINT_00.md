# Iteration 5 / Route C: start and inherited constraints

- Root-observed start bound: no later than `2026-08-21 19:37:57 +08:00`.
- Local first clock sample: `2026-08-21 19:38:56 +08:00`.
- Do not finalize before `2026-08-21 21:37:57 +08:00`.
- Target: a dimension-uniform proof, or exact structural progress, toward
  `H_{ceil(m/2)}(B) >= (mu/2) B^{-1}`.

The route began by reading `research/problem.md`, task T095, `docs/METHOD.md`,
the Iteration-4 synthesis, all three assigned T085 notes, the Iteration-3 M2
route and hostile audit, and the exact failure records cited by those notes.

Hard inherited constraints:

1. `R_2` does not lie below any finite scalar multiple of `R_1`.
2. Childwise scalarization loses an unbounded (cubic on the simplex) factor.
3. Parallel-sum concavity has the wrong direction for the required next lift.
4. Fixed shallow Bessel/determinant-tail depth is asymptotically insufficient.
5. Bare Jensen, word/reverse-word pairing, and pathwise complementary-prefix
   pairing have exact counterexamples.

Planned avenues are (i) an adaptive anisotropic matrix-state lift, (ii) an
ordered-prefix subset/complement or exterior-algebra representation, and
(iii) fixed-size SDP/SOS dual certificates intended to reveal a reusable
dimension-free algebraic inequality.
