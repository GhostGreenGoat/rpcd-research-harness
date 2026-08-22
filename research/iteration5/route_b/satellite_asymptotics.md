# Fixed-satellite asymptotics for the half-depth certificate

Status: E3 proof draft for the fixed two-coordinate satellite limit.  The
general fixed-`k` reduction is derived but has not received a different-run
hostile audit.  Sublinear and linear satellite extensions are explicitly
labelled conjectural/numerical below.

## 1. Family and quantifiers

Let `N` coordinates be copies of a unit vector `p`, and let `k` coordinates be
copies of another unit vector `q`, where

\[
 t=p^Tq\in[-1,1].
\]

Let `C` be their Gram matrix and

\[
 A=\mu I+(1-\mu)C,\qquad 0<\mu<1.                       \tag{1}
\]

Both groups have within-group off-diagonal `alpha=1-mu`, while their cross
entry is `alpha*t`.  If both groups contain at least two coordinates, the
within-group transverse directions show exactly that
`lambda_min(A)=mu`.  We first hold `k,mu,t` fixed and send `N` to infinity;
only afterward may `mu` tend upward to one.

## 2. Relaxation between satellite pivots

Consider a right side supported in the satellite group and let `S_A,S_B` be
the cumulative solved values in the large and satellite groups.  Between two
satellite pivots, a large-group pivot solves

\[
 y_A=-\alpha(S_A+tS_B),
\]

so, with `D=S_A+tS_B`,

\[
 D\longmapsto\mu D.                                      \tag{2}
\]

For fixed `k`, the number of large-group coordinates between successive
satellite coordinates tends to infinity in probability.  Equation (2)
therefore relaxes to `D=0` before the next satellite event.  A satellite solve
then sees the effective previous-satellite coupling

\[
 \eta=\alpha(1-t^2).                                     \tag{3}
\]

There is also energy in the intervening large-group relaxation.  If a
satellite solve has value `y`, it changes `D` by `t y`; summing the subsequent
geometric large-group solve squares gives

\[
 \sum_{j\ge0}\alpha^2t^2y^2\mu^{2j}
 ={\alpha t^2\over1+\mu}y^2.                             \tag{4}
\]

Thus each effective satellite solve energy is multiplied by

\[
 w=1+{\alpha t^2\over1+\mu}
  ={2-\eta\over1+\mu}.                                  \tag{5}
\]

In a uniform half-prefix, every fixed collection of satellite coordinates
has the Bernoulli-`1/2` inclusion law asymptotically, with a uniform relative
order.  The determinant leaf vanishes: the remaining principal matrix has a
large-group transverse eigenvalue `mu` with multiplicity tending to infinity,
so `det(A_S)A_S^{-1}` is exponentially small up to polynomial factors.  These
observations reduce the fixed-`k` limit to a finite satellite-only random
prefix with coupling (3), multiplied by (5).

## 3. Closed form for two satellite coordinates

Take `k=2` and the transverse right side `z=(1,-1)`, whose squared norm is two.
Asymptotically, neither satellite is selected with probability `1/4`, exactly
one with probability `1/2`, and both with probability `1/4`.  If both appear,
their effective solve energy is

\[
 1+(1+\eta)^2.
\]

Consequently the ordinary transverse eigenvalue before the relaxation factor
is

\[
 h_2(\eta)
 ={1\over2}\left[{1\over2}+{1\over4}{1+(1+\eta)^2\}\right]
 ={1\over2}+{\eta\over4}+{\eta^2\over8}.                \tag{6}
\]

Because the corresponding eigenvalue of `A` is `mu`, this ordinary
certificate eigenvalue is exactly the normalized ratio under study.  Using
(5)--(6),

\[
 \boxed{
 R_2(\mu,t)
 ={8-\eta^3\over8(1+\mu)},
 \qquad \eta=(1-\mu)(1-t^2).}                            \tag{7}
\]

For fixed `mu`, (7) is minimized by orthogonal prototypes, `t=0`.  Writing
`alpha=1-mu`,

\[
 R_{2,\min}-{1\over2}
 ={\alpha(1-\alpha^2/4)\over2(2-\alpha)}>0.              \tag{8}
\]

Thus this genuinely rank-two, high-nullity satellite degeneration does not
violate the half constant in its fixed-satellite limit.  It is nevertheless
more hostile than signed rank one at the same `mu`: the collinear value is
`1/(1+mu)`, while the exact improvement at `t=0` is

\[
 -{(1-\mu)^3\over8(1+\mu)}.                              \tag{9}
\]

At `mu` tending downward to zero, (7) gives `7/8`, explaining the numerical
`-1/8` excess found by the broad search.  Sending `mu` upward to one after the
`N` limit makes (7) approach `1/2` from above, giving a second asymptotically
sharp family for the half-depth hierarchy.

## 4. All fixed satellite counts in the transverse sector

The two-coordinate calculation extends to every fixed `k>=2` on the
satellite zero-sum subspace.  This subsection always fixes `k,mu,t` first and
only then sends the large-block count `N` to infinity.  It does not make a
statement uniform in growing `k`.

Let `z in R^k` satisfy `sum_i z_i=0`, and let `S~Binomial(k,1/2)` be the number
of satellites present in the limiting Bernoulli half-prefix.  Conditional on
`S>=j`, the first `j` pivots `pi_1,...,pi_j` are a uniform ordered sample
without replacement.  Put `rho=1-eta`.  The effective equicorrelation solve
recursion and its explicit form are

\[
y_j=z_{\pi_j}-\eta\sum_{\ell<j}y_\ell
   =z_{\pi_j}-\eta\sum_{\ell<j}
      \rho^{j-1-\ell}z_{\pi_\ell}.                       \tag{10}
\]

For `j>=1`, define

\[
W_j=\sum_{r=0}^{j-2}\rho^r,\qquad
Q_j=\sum_{r=0}^{j-2}\rho^{2r},                         \tag{11}
\]

with empty sums zero at `j=1`.  Exchangeable sampling of a zero-sum vector
gives, for distinct sampled positions,

\[
\mathbb E z_{\pi_j}^2={\lVert z\rVert^2\over k},\qquad
\mathbb E z_{\pi_\ell}z_{\pi_m}
=-{\lVert z\rVert^2\over k(k-1)}.                       \tag{12}
\]

Consequently, if `p_j=Pr(S>=j)`, direct expansion of (10) gives

\[
{\mathbb E[y_j^2\mid S\ge j]\over\lVert z\rVert^2}
={1\over k}
+{\eta^2(kQ_j-W_j^2)\over k(k-1)}
+{2\eta W_j\over k(k-1)}.                              \tag{13}
\]

Here `eta,rho,W_j>=0`, and Cauchy gives
`W_j^2 <= (j-1)Q_j <= kQ_j`.  Every correction to `1/k` in (13) is therefore
nonnegative.  Moreover, the tail-sum identity yields

\[
\sum_{j=1}^k p_j=\mathbb E S={k\over2}.                 \tag{14}
\]

Thus the normalized limiting transverse prefix coefficient satisfies

\[
h_k(\eta)=\sum_{j=1}^k p_j
 {\mathbb E[y_j^2\mid S\ge j]\over\lVert z\rVert^2}
\ge {1\over2}.                                         \tag{15}
\]

The majority-relaxation weight obeys

\[
w={2-\eta\over1+\mu}
 =1+{(1-\mu)t^2\over1+\mu}\ge1.                       \tag{16}
\]

Combining (15)--(16) gives `R_k=w h_k>=1/2` for the satellite-transverse
sector of the fixed-`k` limiting family.  `fixed_k_satellite_exact.py`
independently enumerates all ordered prefixes for `k=2,...,8`, reproduces
(13) symbolically with zero residual, and supplies nonnegative rational
Bernstein coefficients on `eta in [0,1]`.  The derivation was initially E3;
the separate hostile audit cited below independently reconstructed the
second-moment calculation and marked the stated sector PASS.  It is therefore
E4 within this repository's ladder (not a formal or external validation).
The symbolic enumerations are E2 finite certificates.

The same moment formula gives a local comparison with signed rank one.  For
fixed `k`, binomial factorial moments in (13) give

\[
h_k(\eta)={1\over2}+{\eta\over4}
 +{k+1\over24}\eta^2+O_k(\eta^3).                      \tag{17}
\]

Writing `alpha=1-mu` and `u=1-t^2`, expansion of the weight gives

\[
R_k={1\over2}+{\alpha\over4}
 +\alpha^2\left[{1\over8}+{k-2\over24}u^2\right]
 +O_k(\alpha^3).                                       \tag{18}
\]

Thus all fixed counts have the same first-order `alpha/4` margin.  For
`k>=3`, the collinear signed boundary `u=0` is locally best through second
order.  For `k=2`, all angles tie through second order and the cubic term in
(7) makes the orthogonal satellite more hostile.  This explains why two
satellites beat the signed baseline while growing satellite counts
numerically optimize near collinearity.  Equations (17)--(18) are an E3
algebraic consequence of the audited moment formula, pointwise in fixed `k`.
In the searched boundary layer `alpha=c log(n)/n`, fixed `k` therefore
predicts `n(R_k-1/2)/log(n) -> c/4`; for `c=2.5` this is `0.625`.  The finite
fit `0.763` is decreasing toward, but does not establish, that limit because
the finite determinant tail and nonuniform remainder are still visible.

## 5. What remains for other satellite scales

There is also an exact finite statement on the orthogonal two-satellite ray
`t=0`.  Put `n=N+2`, `r=ceil(n/2)` and `a=2-mu`.  For
`z=e_{N+1}-e_{N+2}`, cross-block independence makes every majority solve
zero.  If the half-prefix selects zero, one, or both satellite coordinates,
the prefix energies are respectively

\[
 0,\qquad1,\qquad1+a^2.                                  \tag{19}
\]

For even `n=2h`, the corresponding hypergeometric probabilities satisfy

\[
 P_0=P_2={h-1\over2(2h-1)},\qquad P_1={h\over2h-1}.
\]

Consequently the normalized bare-prefix ratio in this transverse direction is

\[
 R_J={1\over2}+{h-1\over4(2h-1)}(a^2-1)\ge{1\over2}.     \tag{20}
\]

For odd `n=2h+1`,

\[
 P_2={h+1\over2(2h+1)},\qquad P_1=2P_2,
\]

and

\[
 R_J={(h+1)(3+a^2)\over4(2h+1)}>{1\over2}.              \tag{21}
\]

The determinant tail is PSD, so `R_H>=R_J`.  Equations (20)--(21) are exact
finite formulas on the experimentally tight direction, not merely limiting
evidence.  They do not cover the other invariant sectors or nonorthogonal
satellites.  `orthogonal_satellite_exact.py` checks the combinatorics and
rational instances independently of the float threshold scan.

- **Fixed `k>2`:** equations (10)--(16) close every satellite-transverse
  direction for all fixed `k`.  The other invariant sectors of the full
  two-group certificate remain unaudited and are not claimed.
- **`k=o(N)`, `k` growing:** a typical fraction of satellite gaps still
  contains divergingly many large-group coordinates, suggesting the same
  effective reduction.  Turning this into a uniform matrix bound requires
  controlling clusters of adjacent satellite pivots and is open.
- **`k=Theta(N)`:** gaps remain order one, so the relaxation reduction is
  invalid.  The exact two-count Bellman DP was used instead.  The `n=300`
  broad search found its tightest ratio at satellite size three, not at a
  linear-sized second group; this is E1 evidence only.

A separate deterministic scale grid (`satellite_scale_regimes.json`) made
this comparison explicit at 108 points.  It used `k=2`, `round(sqrt(n))`,
`round(n^(3/4))`, and `floor(n/4)`, three `mu` values, and three prototype
cosines.  No float64 violation occurred.  In the boundary layer
`1-mu=2.5 log(n)/n`, a second five-dimension scan minimized over four cosines.
For `n=400,800,1600`, the fitted log-log slopes of the positive margin were
respectively `-0.903`, `-0.901`, `-0.901`, and `-0.900` for the four count
regimes.  The last-three means of

```
n * (H/mu - 1/2) / log(n)
```

were `0.763`, `0.792`, `0.793`, and `0.793`.  The fixed-two family stayed
strictly below the signed-rank-one finite baseline, whereas the growing and
linear families optimized near the collinear boundary and tracked that
baseline to small error.  These finite fits are E1 diagnostics, not a
uniform result in growing `k`; the apparent slope is also compatible with a
positive `log(n)/n` law and cannot distinguish lower-order corrections.

The fixed-`k=2` calculation closes one hostile asymptotic avenue but does not
prove the universal half-depth conjecture.  The all-fixed-`k` transverse
extension likewise leaves growing `k`, the other sectors, and general
matrices open.

The independent hostile audit
`docs/ITER5_AUDIT_TWO_SATELLITE_ASYMPTOTICS.md` passes equations (2)--(9),
independently reconstructs and passes the all-fixed-`k` transverse extension
(10)--(16), and passes the finite orthogonal ray (19)--(21).  The local
expansion (17)--(18) was added after that audit.
