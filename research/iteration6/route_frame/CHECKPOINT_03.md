# Checkpoint 03

Recorded: 2026-08-22 18:04:18 +08:00 (about 89 minutes after observed
start).

## New positive structure

1. A uniform permutation was rewritten exactly as a directed cycle plus a
   cut.  Conditional on the cycle, every nonzero residual row and the whole
   dual tail `T=F^TD` have fixed local-solve coefficients and only
   arc-incidence masks.  The exact cut covariance is the nested matrix Hardy
   form (C6).
2. Conditional dual regression gives a monotone hierarchy
   `C_global<=C_cycle<=K`.  The refinement is exactly Pythagorean:

   ```
   C_H-C_G=E[(W_H-W_G)^TQ_H(W_H-W_G)].
   ```

   Exact enumeration checks both hierarchy steps.
3. The remaining covariance is compressed to the minimal arc-tail estimate
   `S<=C_tail P`; this would give
   `Q<=(1+sqrt(C_tail))^2P`.  A scalar Hardy proof is impossible because the
   bare nested-arc operator has a linear-in-`n` loss.
4. For `A=I+epsilon H`, the actual tail has the all-dimensional second-order
   coefficient

   ```
   p2 H^2+(p1-p2)Diag(diag H^2)<=I/8
   ```

   when `||H||<=1`.  Higher-order adaptation remains.  Separately, every
   local row and residual obey dimension-free nonperturbative row-stability
   estimates when `||A-I||<1`.

## Evidence boundary

The general multirow arc/Bessel inequality is still open.  Pathwise,
reverse-paired, scalar-Hardy, and the remaining-frame inverse Bellman
closures are now exact analytic failures.  The cycle and conditional
hierarchy identities are genuine reductions, not a proof of the RPCD rate.
