# Route B checkpoint 01

- Root-observed start: `2026-08-21 19:37:57 +08:00`.
- Checkpoint timestamp: `2026-08-21 20:08:57 +08:00`.
- Evidence rule: every optimization and Monte Carlo value below is E1; the
  finite implementation controls are E2 at most.

## Failure record read before the search

The route began by reading `research/problem.md`, `docs/METHOD.md`, T095/T097,
the complete Iteration-4 synthesis, T085 final report/Bellman closure/
compression/asymptotics/checkpoints, the complete chronological T080 report
and exact counterexample audit, and the signed-rank-one half-depth and global
half-sharpness audits.  Consequently this run does not retry fixed shallow
depth, bare Jensen/Kadison, scalar child induction, word/reverse-word pairing,
complementary-prefix pathwise pairing, or compression of every Schur loss into
the first loss.

## New finite engine

`reproducer.py` implements the complete determinant-tail Bellman recursion for
block-exchangeable matrices in remaining-group-count coordinates.  It retains
the full invariant matrix and evaluates every transverse sector plus the full
group-constant generalized block.  The derivation is in
`family_reduction.md`.

Controls passed:

- three-group `n=6` result versus generic `2^6` subset DP:
  maximum entry residual `2.220446049250313e-16`;
- whole-group sign conjugation gap: exactly zero at printed precision;
- identity coefficient: exactly one;
- signed-rank-one sharp control `n=1000, mu=0.98`: ratio
  `0.505509978960384 > 1/2`;
- leading `n=76` candidate, reduced versus full `76 by 76` generalized
  eigenproblem: gap `6.106226635438361e-16`;
- independent 3,000-order prefix-plus-leaf Monte Carlo: DP discrepancy
  `-1.386` standard errors.

## Four distinct hostile avenues so far

1. Three frustrated rank-two groups, `n=60`: best ratio `0.6109017588`.
2. Four uneven multiscale groups, `n=76`: first global-search ratio
   `0.6045138631`.
3. Duplicate pole plus three simplex-arranged leaf groups, `n=56`: best ratio
   `0.6333700888`.
4. Five/six heterogeneous one-factor groups, `n=27..30`: best ratio
   `0.6679525409`.

Local four-group optimization improved the value to `0.5835669076` at `n=58`
and then to `0.5662851920` at `n=76`.  The latter has actual spectral floor
`0.8022398655`; its worst sector is the complete four-group constant block.
No value is below `1/2`, so no counterexample or exact-rational sign claim is
made.

## Current interpretation and next attacks

The all-collinear one-factor family is less hostile than a genuinely
rank-three four-group geometry.  The leading candidate is also not explained
by a single group-transverse direction.  The next checkpoint will:

- re-optimize both group proportions and continuous parameters at larger `n`;
- isolate the determinant-leaf contribution by comparing `H_r` with the bare
  prefix `J_r` on the same candidates;
- probe a deliberate two-small-singular-value degeneration separately from
  the unconstrained frustrated optimum;
- attempt a smaller rational surrogate only if a robust negative half-margin
  appears.
