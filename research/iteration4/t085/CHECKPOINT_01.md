# Iteration 4 / T085 checkpoint 01

- Wall-clock interval: 2026-08-21 17:24:56--18:00 (Asia/Shanghai).
- Evidence policy: formulas labelled exact below were reconstructed algebraically and checked by
  `scripts/verify_iter4_t085_exact.py`; floating searches remain E1/E2 only.

## Positive results

1. The second Schur-loss moment has an exact ordered-pair rank-one representation.  With
   `G=B^{-1}`, `s_{j|i}=1/(G_jj-G_ij^2/G_ii)`, and

   `w_{j|i}=(G-I)e_j-(G_ij/G_ii)(G-I)e_i+B_ij e_i`,

   one has

   `R_B=[m(m-1)]^{-1} sum_{i != j} s_{j|i} w_{j|i}w_{j|i}^T`.

   This retains the child leverage and ordered-pair orientations exactly.

2. If `E=B^{1/2}R_BB^{1/2}`, `t=tr(E)`, and `p=tr(E^2)`, then

   `R_B <= phi_m(t,p) B^{-1}`,

   where `phi_m(t,p)=[t+sqrt((m-1)(mp-t^2))]/m`.  This is an exact
   trace/trace-square compression.  Unlike childwise scalarization, it first aggregates the
   oriented pair frame and is within a factor below two on both tested singular structured limits.

3. The exact two-step prefix formula implies the stronger universal proof draft

   `J_2(B) >= (2 mu/m) B^{-1}`,

   improving the previous coefficient `2mu/m-mu^2/m^2`.  It is not multiplied across dependent
   pairs.

4. On `B_m(mu)=mu I+(1-mu)11^T`, for `1 <= r <= m-3`, the determinant-tail level obeys the exact
   asymptotic

   `lim_{mu -> 0} c_r(B_m(mu))/mu=(2r-1-1/m)/(m-1)`.

   Hence fixed depth, and more generally `r=o(m)`, cannot yield a universal positive constant.
   Linear depth is necessary for this hierarchy.

## Exact barriers

1. `R_B <= bar(D)_B` is false.  For the 3-by-3 regular-simplex lift with `mu=1/5`, the transverse
   eigenvalue of `bar(D)_B-R_B` is exactly `-32/5625`.

2. No finite scalar `C` can make `R_B <= C bar(D)_B` universal.  For

   `B=[[1,1/3,1/4],[1/3,1,0],[1/4,0,1]]`, whose spectrum is
   `{7/12,1,17/12}`, the vector `v=(0,1/4,-1/3)` satisfies
   `bar(D)_B v=0` but `v^T R_B v=263/124416>0`.

3. Childwise compression `bar(D)_{C_i}<=eta_i C_i^{-1}`, even with exact best `eta_i`, loses a
   factor `m(m-2)^2` on the regular-simplex singular limit.  Parallel-summing that upper bound with
   `G-bar(D)-I/m` does not repair the loss.

4. Full operator Kadison, `K=E[X_pi^T X_pi] >= (E X_pi)^T(E X_pi)`, is dimensionally too weak.
   On the signed rank-one family its coefficient divided by `mu` tends to zero like
   `1/[m mu(1-mu)]` for fixed `mu`.

5. The PSD advantage of without-replacement over with-replacement updates is already false for
   prefixes of length three.  Therefore the valid two-step theorem cannot be iterated as a Loewner
   comparison.

## Current lead

The finite search `research/evidence/ITER4_T085_HALF_DEPTH_SEARCH.json` found no violation of
`H_{ceil(m/2)} >= c mu B^{-1}` with `c=0.8` for `3 <= m <= 10`, but this is only a null search.
The signed rank-one scalar recursion suggests its half-depth constant tends to `1/2`, making
`c=1/2` a plausible sharp target.  The missing step is a universal matrix inequality that preserves
the ordered-pair frame rather than scalarizing each child.
