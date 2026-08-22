# Iteration 4 / T085 checkpoint 02

- Wall-clock interval covered: 2026-08-21 18:00--18:33 (Asia/Shanghai).
- This checkpoint records proof drafts separately from null searches.

## New certified compression

For each lifted child loss `X_i=L_i^T bar(D)_{C_i}L_i`, two complementary upper bounds are now
available:

1. **Pre-lift:** `bar(D)_{C_i}<=alpha_i C_i^{-1}`, retaining the entire weighted lift in the
   anisotropic parent matrix `U_B`.
2. **Post-lift:** normalize only after lifting.  The nonzero spectrum of
   `B^{1/2}X_iB^{1/2}` is that of
   `bar(D)_{C_i}^{1/2}(C_i-b_i b_i^T)bar(D)_{C_i}^{1/2}`.  Its trace and trace-square give
   `X_i<=beta_iG`, hence `R_B<=W_B=mean(beta)G`.

Thus `R_B<=2(U_B:W_B)` by parallel-sum monotonicity.  A sharper adaptive selector chooses `U_B`
when its parent normalized rate is at most `mean(beta)`, and otherwise chooses `W_B`; either branch
is a valid PSD upper bound.

The 240-instance reproducible float run (seed `20260831`, dimensions 3--8) exercised both branches
(`202/38`), found minimum selector-minus-`R` eigenvalue `4.8e-13`, and maximum normalized-rate
overhead `1.96044`.  These figures test the implementation only; the PSD validity is algebraic.

The trace-power refinement

`lambda_max(Y)<=tr(Y^q)^(1/q)<=d^(1/q)lambda_max(Y)`

shows that adaptive moment order `q=ceil(log_2 d)` approximates each exact local spectral rate within
a factor two.  Fixed `q` cannot do this for arbitrary PSD spectra (`Y=I_d`).  This controls local
compression error but does not yet close higher Bellman lifts.

## Half-depth attack

The candidate under attack is

`H_{ceil(m/2)}(B)>=(mu/2)B^{-1}`.

No counterexample has been found in the following E1 searches:

- original random boundary search, `m=3..10`, 250 samples/dimension: minimum `0.825668`;
- two exchangeable blocks: minimum `0.920601` at `m=8`;
- weighted star boundary: minimum above `1.02`;
- two-pole ring grid: minimum `0.835124` at `m=10`;
- differential evolution over rank-two Gram boundaries: `0.831507` at `m=8` and `0.841064` at
  `m=10`;
- two rank-one blocks: minimum `0.805532` in the tested `m<=10` grid.

The exact two-scalar recurrence on the signed-rank-one family was scanned through `m=1000`.  Its
half-depth infimum decreases to `0.505351` at `m=1000`, strongly suggesting that `1/2` would be sharp
if the candidate is true.  This is not a proof.

## Depth-scale comparison

The exact formula

`lim_{mu->0}c_r/mu=(2r-1-1/m)/(m-1)`

already proves that determinant-tail depth `r=o(m)` is impossible.  Root's independent block-Bessel
experiments now also show fixed shallow `q=2` and `q=3` failures.  The two obstructions agree on the
main design conclusion: a surviving certificate must have depth/order growing with dimension.
Current evidence points specifically to linear deletion depth, while logarithmic trace-power order
is sufficient only to keep each local spectral compression within a constant factor.
