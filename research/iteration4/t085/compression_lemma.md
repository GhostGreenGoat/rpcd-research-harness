# T085 compression lemma (proof draft, E3; not hostile-audited)

## Scope and notation

Let `B` be an `m x m` unit-diagonal SPD matrix, `m>=3`, and put `G=B^{-1}`.  For a first deletion
`i`, write

```
B = [[1,b_i^T],[b_i,C_i]],       L_i=[-b_i I],
s_i=1/G_ii,                      bar(D)_B=(G-I)Diag(s)(G-I)/m.
```

The second Schur-loss moment is

`R_B=m^{-1} sum_i L_i^T bar(D)_{C_i}L_i`.

All inequalities below are Loewner inequalities.  They are deterministic statements about `B`;
no floating-point search is part of their proof.

## 1. Exact ordered-pair frame

For distinct `i,j`, define

```
s_{j|i} = 1/(G_jj-G_ij^2/G_ii),
w_{j|i} = (G-I)e_j-(G_ij/G_ii)(G-I)e_i+B_ij e_i.
```

Then

```
R_B = 1/[m(m-1)] sum_{i != j} s_{j|i} w_{j|i}w_{j|i}^T.       (1)
```

In particular, `R_B` is PSD and (1) retains both the child leverage and the ordered-pair
orientation.  Also

`s_{j|i}=s_j/(1-rho_ij^2)>=s_j`, where `rho_ij=G_ij/sqrt(G_ii G_jj)`.

### Proof

The inverse of `C_i` is

`Q_i=G_{-i,-i}-G_{-i,i}G_{i,-i}/G_ii`.

Therefore its leverage at the original coordinate `j` is `s_{j|i}`.  The first-loss formula in the
child is

`bar(D)_{C_i}=(m-1)^{-1} sum_{j != i} s_{j|i}(Q_i-I)e_j e_j^T(Q_i-I)`.

Block inversion gives

`L_i^T(Q_i-I)e_j=w_{j|i}`.

Substitution and averaging over `i` proves (1).  The formula for `s_{j|i}` follows by factoring
`G_jj` from its denominator.  `square`

## 2. The eigenvalue two-moment bound

For a `d x d` PSD matrix `Y`, let `t=tr(Y)` and `p=tr(Y^2)`.  Then

```
lambda_max(Y) <= Phi_d(t,p)
 := [t+sqrt((d-1)(d p-t^2))]/d.                              (2)
```

Indeed, if `lambda_1` is the largest eigenvalue, Cauchy--Schwarz on the other `d-1` eigenvalues
gives `(t-lambda_1)^2 <= (d-1)(p-lambda_1^2)`; solving the resulting quadratic gives (2).

Applied after aggregating the frame (1), let

```
E_B=B^{1/2}R_BB^{1/2},  t_B=tr(BR_B),  p_B=tr(BR_BBR_B).
```

Then the exact pair-frame scalar compression is

```
R_B <= Phi_m(t_B,p_B) G.                                    (3)
```

The traces in (3) can be evaluated directly from the pair vectors in (1); forming `R_B` first is
not logically required.

## 3. Complementary pre-lift and post-lift bounds

The following construction avoids the fatal step of using one child scalar in both singular
geometries.

For the child first loss `D_i^c=bar(D)_{C_i}`, one may use either its exact pre-lift rate
`alpha_i^eig=lambda_max(C_i^{1/2}D_i^cC_i^{1/2})` or the certified two-moment upper
`alpha_i^(2)` obtained by applying (2), capped by `1-mu_i`, where
`mu_i=lambda_min(C_i)`.  Write `alpha_i` for either certified choice.  Thus

`D_i^c <= alpha_i C_i^{-1}`.

The trace data do not require a square root.  If `Q_i=C_i^{-1}`, `S_i^c=Diag(1/diag(Q_i))`, and
`F_i=(m-1)^{-1}(S_i^c)^{1/2}(Q_i-2I+C_i)(S_i^c)^{1/2}`, then

`tr(F_i)` and `tr(F_i^2)` are the two inputs to (2).

Lifting this childwise bound and retaining every weight gives

```
R_B <= U_B
 := mean(alpha)G-Diag(alpha)/m
    -(G-I)Diag(alpha_i s_i)(G-I)/m.                          (4)
```

Formula (4) uses the exact identity

`L_i^T C_i^{-1}L_i=G-e_i e_i^T-s_i(G-I)e_i e_i^T(G-I)`.

For the complementary post-lift rate, set

```
E_i^s=C_i-b_i b_i^T=L_i B L_i^T,
tau_i=tr(E_i^s D_i^c),
pi_i=tr(E_i^s D_i^c E_i^s D_i^c),
beta_i^(2)=min{Phi_{m-1}(tau_i,pi_i),1-mu_i}.
```

The exact alternative `beta_i^eig` is the largest eigenvalue of
`(D_i^c)^{1/2}E_i^s(D_i^c)^{1/2}`.  Again write `beta_i` for either certified choice.

The nonzero eigenvalues of

`B^{1/2}L_i^T D_i^c L_iB^{1/2}`

are those of `(D_i^c)^{1/2}E_i^s(D_i^c)^{1/2}`.  Equations (2) and `E_i^s<=C_i` therefore prove

```
L_i^T D_i^cL_i <= beta_i G,
R_B <= W_B := mean(beta)G.                                  (5)
```

The Schur factor `E_i^s=C_i-b_i b_i^T` is essential.  On a simple-null parent it removes the
dangerous child direction that the pre-lift scalar bound mistakenly retains.

## 4. Parallel-sum compression

For PSD matrices, write `X:Y=(X^{-1}+Y^{-1})^{-1}`, extended to singular matrices by the
Moore--Penrose/continuous definition.  Parallel sum is monotone in each argument.  From (4)--(5),

`R_B:R_B <= U_B:W_B`.

Since `R_B:R_B=R_B/2`, this proves the leverage- and child-floor-aware compression

```
boxed:  R_B <= P_B := 2(U_B:W_B).                            (6)
```

Both `U_B` and `W_B` are also bounded by `(1-mu)G`; monotonicity consequently gives
`P_B<=(1-mu)G`.  More important than this scalar corollary is that (6) retains the anisotropic
matrix `U_B` whenever it is informative and automatically switches to the post-lift Schur bound
in the complementary geometry.

There is also a sharper discontinuous adaptive selector.  Let

`u_B=lambda_max(B^{1/2}U_BB^{1/2})` and `w_B=mean(beta)`, and define

```
C_B = U_B  if u_B<=w_B,
      W_B  if u_B>w_B.                                      (7)
```

Then `R_B<=C_B` and `rate_B(C_B)<=min(u_B,w_B)`.  The selector uses only an eigenvalue of the
explicit parent matrix; it chooses the anisotropic pre-lift matrix on the high-nullity boundary and
the post-lift scalar on the simple-null boundary.  With the trace-square child rates it has limiting
overhead below two on the signed-rank-one family and exactly two on the regular-simplex family.
Its cost is a data-dependent branch in the Bellman state; (6) is smooth but has a larger
trace-square-only overhead (bounded by four on the two structured limits).

## 5. What (6) does and does not close

### Higher-moment refinement

The trace/trace-square rate is not dimension-uniformly close to the exact spectral rate for an
arbitrary PSD frame.  A controlled adaptive replacement is available.  For any integer `q>=2`,
set

```
alpha_i^(q)=min{tr[(C_i D_i^c)^q]^(1/q),1-mu_i},
beta_i^(q) =min{tr[(E_i^s D_i^c)^q]^(1/q),1-mu_i}.           (8)
```

The products inside the traces are similar to PSD matrices, so the traces are nonnegative and (8)
upper-bounds the corresponding largest eigenvalues.  If `d=m-1`, then

```
lambda_max(Y) <= tr(Y^q)^(1/q) <= d^(1/q)lambda_max(Y).      (9)
```

Choosing `q=ceil(log_2 d)` makes the loss in either scalar rate at most two, uniformly in the
dimension.  Conversely, a fixed Schatten moment cannot give a dimension-free approximation for
arbitrary PSD spectra: `Y=I_d` has ratio `d^(1/q)`.  Thus logarithmic moment order is the natural
generic cost of replacing the exact child eigenvalue by finitely many power traces.  The sharper
two-moment formula (2) should still be intersected with (8) in practice.

This logarithmic-order refinement controls the **local spectral compression error**.  It does not
by itself control the number of deletion/Bellman levels needed in (1) of `bellman_closure.md`.

Equations (6)--(7) are valid second-level PSD compressions into a finite set of explicitly computable
objects: the parent leverage vector, the child floors, two trace moments per child, and one parallel
sum.  It passes both canonical singular tests (see `sharpness_families.json`).

It is **not yet a Bellman-closed proof of `c_r>=c mu`**.  A further lift contains
`m^{-1}sum_i L_i^T P_{C_i}L_i`; no proved inequality currently reduces this nonlinear average back
to `P_B`, `bar(D)_B`, and `G` with a dimension-uniform coefficient.  Scalarizing `P_{C_i}` at that
point recreates the exact barriers in `bellman_closure.md`.  Thus (6) is a reusable compression
lemma and a concrete new state for the next hierarchy, not a solution of the RPCD conjecture.

## Reproducibility

- Exact rational identities/counterexamples: `scripts/verify_iter4_t085_exact.py`.
- Floating stress tests: `scripts/iter4_schur_moment_search.py`, seed `20260831`.
- Main output: `research/evidence/ITER4_T085_SCHUR_MOMENT_SEARCH.json`.

The 240-instance search over `3<=m<=8` found minimum float64 residual
`lambda_min(P_B-R_B)=2.4e-9` and maximum observed normalized-rate overhead below `3.47`.  For the
adaptive selector (7), the corresponding residual was `4.8e-13`, the maximum overhead was below
`1.961`, and the two branches were both exercised (`202` pre-lift and `38` post-lift).  This is only
E1/E2 numerical corroboration; validity of (6)--(7) rests on the algebra above.
