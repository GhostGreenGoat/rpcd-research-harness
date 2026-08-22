# Iteration 5 route A — checkpoint 04

Time: 2026-08-21 21:38:33 +08:00 (120 minutes 4 seconds from this
worker's observed start, and after the root-observed floor).

## Final state at the active-time floor

The general half-depth target remains open.  The iteration ends with three
clearly separated outcomes:

1. **General high-`mu` region:** for every unit-diagonal SPD matrix, the
   independently audited leaf-free bound
   `K>=[1+n(1-mu)/sqrt(2)]^-2 mu B^-1` holds.  It gives the sharp global half
   constant when `n(1-mu)<=2-sqrt(2)` and a positive quarter constant when
   `n(1-mu)<=1`.  The direct-prefix extension has an exact finite regression
   control but was not separately discussed in the external audit.
2. **Equicorrelation half-memory result:** `q=ceil(n/2)` local inverse gives
   an independently audited finite `25/98` full-epoch constant, and its sharp
   `rho=c/n` limiting parallel certificate is at least one half.  Every
   sublinear bandwidth is analytically refuted for this architecture.
3. **Generic open obstruction:** each forgotten-history row satisfies the
   audited Schur bound
   `rB_O^-1r^T<=sigma-mu||d||^2<=1-mu`, but an exact rational control refutes
   scalar inclusion-fraction damping.  A cross-row matrix frame/covariance
   inequality remains missing.

All exact and numerical controls were rerun.  `result.json` parses, all
listed artifacts exist, and the repository validator reports only the absent
harness-owned sibling invocation timing metadata; none was fabricated.
