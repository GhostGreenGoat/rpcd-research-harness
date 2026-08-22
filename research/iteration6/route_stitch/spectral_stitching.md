# Spectral stitching through a singular correlation ray

Status: E3 proof draft for the interpolation and stitching lemmas below.
The proposed boundary spectral-layer inequality is explicitly open.  No
general RPCD complexity theorem is claimed here.

## 1. Quantified setting

Let `C` be an `n by n` singular correlation matrix and, for `0<mu<=1`, set

\[
A_\mu=\mu I+(1-\mu)C.                                    \tag{S1}
\]

Then `diag(A_mu)=I` and `lambda_min(A_mu)=mu`.  Conversely,
every unit-diagonal SPD matrix with minimum eigenvalue `mu<1` has the unique
representation (S1), with `C=(A_mu-mu I)/(1-mu)` a singular correlation
matrix.

For an order `pi`, let `M_pi(mu)` be its chronological unit-lower factor,
`X_pi(mu)=M_pi(mu)^(-1)`, and

\[
K(A_\mu)=\mathbb E_\pi X_\pi(\mu)^T X_\pi(\mu).          \tag{S2}
\]

## 2. Dimension-free multiplicative interpolation

The off-diagonal entries on the ray scale by `1-mu`, hence exactly

\[
M_\pi(\mu)=\mu I+(1-\mu)M_\pi(0)
 =M_\pi(0)[(1-\mu)I+\mu X_\pi(0)].                       \tag{S3}
\]

Because

\[
\operatorname{Sym}M_\pi(0)={I+C\over2}\succeq {I\over2},
\]

`||X_pi(0)||<=2`.  Put
`B_pi=(1-mu)I+mu X_pi(0)`.  Equation (S3) gives
`X_pi(mu)=B_pi^(-1)X_pi(0)`, while

\[
\|B_\pi\|\le1-\mu+2\mu=1+\mu.
\]

Therefore, order by order,

\[
X_\pi(\mu)^T X_\pi(\mu)
\succeq{1\over(1+\mu)^2}X_\pi(0)^TX_\pi(0).             \tag{S4}
\]

Averaging proves the dimension-free ray comparison

\[
\boxed{K(A_\mu)\succeq(1+\mu)^{-2}K(C).}                 \tag{S5}
\]

This is stronger than a continuity statement: it has no spectral-gap,
dimension, or inverse-norm remainder.  The same proof works for every fixed
prefix support/order and hence for each bare prefix matrix `J_t`.

For comparison, the resolvent identity also gives the additive diagnostic

\[
X_\pi(\mu)-X_\pi(0)
=\mu X_\pi(\mu)(I-X_\pi(0)),
\quad
\|K(A_\mu)-K(C)\|\le
{12\mu(2+\mu)\over(1+\mu)^2}\le24\mu.                  \tag{S6}
\]

Unlike (S5), using (S6) inside a block Schur complement introduces avoidable
cross-term losses; (S5) is the useful interpolation statement.

## 3. A tunable low/high spectral projection

Fix `tau>=0`.  Let `P_tau` be the spectral projector of `C` onto eigenvalues
strictly below `tau`, and `Q_tau=I-P_tau`.  Assume the **full shorted**
boundary certificate

\[
K(C)\succeq\kappa P_\tau                              \tag{S7}
\]

for some `kappa>0`.  This is stronger than merely checking
`P_tau K(C) P_tau>=kappa P_tau`; the latter ignores kernel/range Schur
coupling.

By (S5),

\[
K(A_\mu)\succeq bP_\tau,
\qquad b={\kappa\over(1+\mu)^2}.                         \tag{S8}
\]

Independently, the exact two-prefix formula gives the commuting lower bound

\[
K(A_\mu)\succeq J_2(A_\mu)
\succeq F(A_\mu):={2(nI-A_\mu)\over n(n-1)}.             \tag{S9}
\]

Write

\[
d_\tau=\mu+(1-\mu)\tau,
\qquad L=n-(n-1)\mu.                                    \tag{S10}
\]

If `Q_tau!=0`, its eigenvalues of `A_mu` lie in the nonempty interval
`[d_tau,L]` (in particular `d_tau<=L`).  The generalized coefficient supplied
by (S9) is therefore

\[
r_\tau=min_{\lambda\in[d_\tau,L]}
 {2\lambda(n-\lambda)\over n(n-1)\mu}
=\min\left\{
 {2d_\tau(n-d_\tau)\over n(n-1)\mu},
 {2L\over n}
\right\}.                                                \tag{S11}
\]

The equality uses concavity in `lambda` and `n-L=(n-1)mu`.
Consequently `F(A_mu)>=r_tau mu A_mu^(-1)Q_tau`.

If `Q_tau=0`, define `r_tau=+infinity`; there is no high-space constraint and
(S8) alone gives the coefficient `b`.  This convention also makes the
stitching formula below continuous, with
`b r_tau/(b+r_tau):=b`.  It avoids applying the endpoint formula (S11) to an
empty spectral interval.

Both (S8) and (S9) are lower bounds on the same PSD matrix, so every convex
combination is again a lower bound.  Choosing the weight to equalize the low
and high guarantees gives the exact stitching lemma

\[
\boxed{
K(A_\mu)\succeq c_{\rm stitch}\,\mu A_\mu^{-1},
\qquad
c_{\rm stitch}={b r_\tau\over b+r_\tau}.}               \tag{S12}
\]

Indeed, take weight `a=r_tau/(b+r_tau)` on (S8) and `1-a` on
(S9).  On `P_tau`, `mu A_mu^(-1)<=I`, and `ab=c_stitch`.
On `Q_tau`, `(1-a)r_tau=c_stitch`.  All matrices in this argument commute
only where explicitly spectral; no unjustified block deletion is used.

## 4. What boundary statement would close a low/middle band?

Suppose `Q_tau!=0`.  If `mu<=1/2` and

\[
d_\tau\ge n\mu
\quad\Longleftrightarrow\quad
\tau\ge{(n-1)\mu\over1-\mu},                            \tag{S13}
\]

then both endpoint values in (S11) are at least one, so `r_tau>=1`.
Thus any dimension-free `kappa` in (S7) gives the dimension-free coefficient

\[
c_{\rm stitch}\ge {\kappa\over(1+\mu)^2+\kappa}.         \tag{S14}
\]

The exact missing statement is therefore not a vague spectral split.  It is
a **boundary low-spectral-layer shorting inequality**:

```
K(C) >= kappa P_{[0,tau)}(C)
```

with dimension-free `kappa` at the tunable threshold in (S13).  At `tau`
below the first positive eigenvalue this reduces to the open boundary-kernel
inequality.  When positive eigenvalues collapse toward zero, `P_tau` must
grow; using only the exact kernel loses uniformity at lower-rank strata.

There is a precise fixed-ray corollary.  Let `delta_+(C)` be the smallest
positive eigenvalue of `C`, and suppose the full boundary-kernel certificate

```text
K(C)>=kappa P_ker(C)
```

holds for this `C`.  Set `tau=delta_+(C)`; because `P_tau` uses eigenvalues
strictly below `tau`, it is exactly `P_ker(C)`.  Condition (S13) then shows
that the stitch has `r_tau>=1` whenever

```text
mu <= delta_+(C)/[n-1+delta_+(C)]                         (S15)
```

(and `mu<=1/2`; the displayed radius already implies this for `n>=3`).
Consequently

```text
K(mu I+(1-mu)C)
 >= {kappa/[(1+mu)^2+kappa]} mu A_mu^-1.                  (S16)
```

Thus a boundary shorted coefficient gives an explicit `O(delta_+/n)` ray
radius, rather than only an unspecified pointwise neighborhood.  Conversely,
if `delta_+(C)` collapses on the same or a faster scale than `n mu`, a
kernel-only endpoint certificate cannot invoke (S13); the low projector must
absorb the collapsing positive eigenspaces.  This is the exact multiscale
obstruction behind the nonuniform-remainder warning.

## 5. Exact mesoscale obstruction to endpoint-only stitching

The reduction also identifies where it cannot close by itself.  Let

\[
C=J,\qquad \mu=1-{c\over n},\qquad1\ll c\ll n.           \tag{S15}
\]

At the boundary, `K(C)=2P_(1^perp)+I/n`; its range coefficient is only
`1/n`.  The exact two-prefix generalized coefficient on `span(1)` is

\[
r_{2,\parallel}
={L(1+\mu^2)\over n\mu}
\sim {2(1+c)\over n}.                                   \tag{S16}
\]

The near-identity fixed-test coefficient is
`[1+c/sqrt(2)]^(-2)`.  Both (S16) and this coefficient tend to zero if, for
example, `c=sqrt(n)`.  The scalar determinant-tail recurrence has the same
loss.  Nevertheless the exact randomly permuted family has limiting
coefficient one half.

Therefore no convex stitching of only the singular endpoint certificate,
the two-prefix functional bound, and the near-identity norm bound can prove
a universal constant.  The missing information is linear-depth random-order
memory on the high range direction, exactly as exposed by the half-linear
local-inverse and half-prefix analyses.  This is an obstruction to this
certificate set, not to RPCD.
