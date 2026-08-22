# Iteration 6 root checkpoint 00

- Root-observed start: `2026-08-22 16:34:10 +08:00`.
- Do not finalize before `2026-08-22 18:34:10 +08:00`.
- Primary route: covariance superoperator and adaptive Lyapunov metrics.
- Required distinction: a failure of fixed `A`-energy contraction does not
  refute the covariance spectral-radius target.

The root first reread the Iteration-5 failure map, synthesis, portable
handoff, the Iteration-3 operator-Lyapunov route, the exact Iteration-4
strong-energy counterexample, and the Iteration-5 half-window construction.

Planned analytic avenues:

1. compare the covariance map with a randomized prefix/tail decomposition;
2. construct a nontrivial adaptive Lyapunov metric from half-prefix Bellman
   matrices rather than a scalar resolvent;
3. split the covariance space into Hessian spectral blocks and control
   off-diagonal operator blocks separately.
