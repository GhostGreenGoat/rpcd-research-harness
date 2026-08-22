# Iteration 5 root checkpoint 01

Start observation: 2026-08-21 19:37:57 +08:00.

## Routes attempted

1. A custom differential-evolution attack on the stronger half-prefix target
   `J_ceil(n/2)>=(mu/2)A^{-1}` was added.  The completed `n=6` and `n=8` runs
   converged toward identity from above; these are E1 null results.
2. The full positive/negative equicorrelation family was symmetry-reduced and
   proved to satisfy the stronger leaf-free target.  A Fraction verifier
   matches the invariant recurrence with all permutations through `n=6`.
3. The first matrix jet at identity was derived for arbitrary zero-diagonal
   directions.  It shows a strictly positive first-order margin at every fixed
   dimension, with a nonuniform-in-dimension neighborhood.

## Two exact shortcut failures

For `A=(1/5)I+(4/5)J` in dimension three, the parallel eigenvalue of `J_2` is
`26/75`.  Therefore

`lambda_parallel(J_2-2I/3)=-8/25`.

So the stronger ordinary-coordinate floor `J_t>=(t/n)I` is false even though
the normalized target has exact positive margin `96/125`.  The same example
also refutes monotonicity of chronological position contributions: position
two minus position one has parallel eigenvalue `-8/25`.

These failures show that a proof must use the spectral coupling with `A`, not
an unweighted prefix-energy floor or an assertion that later solve rows are
larger.

## Checkpoint 02 — 2026-08-21 20:37:57 +08:00

1. The exact all-dimensional weighted two-prefix inequality

   `J_2-(1/2)J_1 >= (3mu/(2n))A^{-1}`

   was derived on Route C and independently reconstructed on Route A.  The
   proof uses `H^2 <= (n-1)Diag(diag H^2)` for symmetric zero-diagonal `H`,
   followed by a scalar spectral endpoint argument.  No blocker was found.
2. Fixed-`mu` differential-evolution attacks now cover low-rank `n=8`,
   full-rank boundary parameterizations in `n=6` and `n=8`, and
   `mu in {0.01,0.1,0.5,0.9}`.  All completed runs remain strictly above
   one half.  The full-rank `n=8` minima were approximately
   `0.7940, 0.7599, 0.6262, 0.5222`.  These remain E1 null evidence.
3. The equicorrelation proof appears to give the stronger simultaneous
   curve `J_t >= (t mu/n)A^{-1}` for every `t<=ceil(n/2)`.  This stronger
   quantifier is under independent audit and is not yet promoted.
4. Two fixed-adjacency random-dual shortcuts have exact large-dimensional
   equicorrelation counterexamples.  The direct state `R=D^T` fails in
   `n=20`; the richer fixed state `R=D^T D` also fails in `n=50`.  The
   general random-test dual lemma and the preconditioner
   `E[D^T D] >= mu A^{-1}` survive, but a bounded adjacency depth does not
   retain enough long-range permutation variance.
5. The identity-local proof was corrected at `n=2`: there `d=0`, so strict
   first-order separation is unavailable, while the target follows directly
   from `J_1=I/2` and `A>=mu I`.  The strict jet argument applies for `n>=3`.

## Final checkpoint — 2026-08-21 21:39:05 +08:00

The root-observed active interval was `19:37:57--21:39:05`, or 121 minutes
8 seconds.  The three parallel routes remained active through their own
two-hour thresholds.  The final promoted internal proof candidates are
`C035--C042`; the unrestricted general SPD conjecture remains open.
