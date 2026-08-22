# Iteration 5 proof draft: the half-prefix inequality is locally safe at identity

Date: 2026-08-21.  Status: E4 internally hostile-audited first-order theorem
candidate with an independent exact permutation verifier.  The neighborhood
obtained below is fixed-dimensional and is not uniform in `n`.

Let `H` be a nonzero symmetric zero-diagonal matrix and

\[
A_\epsilon=I+\epsilon H,\qquad
t=\lceil n/2\rceil,\quad c=t/n,\quad
d={t(t-1)\over n(n-1)}.
\]

The strict first-order argument below is for `n>=3`.  When `n=2`, one has
`t=1` and `J_1=I/2`, so the target follows directly from
`A\succeq\mu I`; this endpoint does not have the strict jet margin used
below because `d=0`.

For sufficiently small positive `epsilon`, `A_epsilon` is a correlation
matrix and

\[
\mu(A_\epsilon)=1+\epsilon\lambda_{\min}(H).               \tag{L1}
\]

## 1. Exact first jet of the prefix certificate

For a permutation and a position `k<=t`, the triangular solve row has the
expansion

\[
b_{\pi,k}^T=e_{\pi_k}^T
-\epsilon\sum_{j<k}H_{\pi_k\pi_j}e_{\pi_j}^T+O(\epsilon^2).
\]

Since `J_t=E sum_{k<=t} b_{pi,k}b_{pi,k}^T`, a coordinate is in the prefix
with probability `t/n`, while an unordered pair is in it with probability
`t(t-1)/[n(n-1)]`.  Therefore

\[
\boxed{J_t(A_\epsilon)=cI-\epsilon dH+O(\epsilon^2).}       \tag{L2}
\]

This is a full matrix identity, not a scalar-rate expansion.

## 2. Normalized target margin

Using
`A_epsilon^(1/2)=I+(epsilon/2)H+O(epsilon^2)`, (L2) gives

\[
A_\epsilon^{1/2}J_t(A_\epsilon)A_\epsilon^{1/2}
=cI+\epsilon(c-d)H+O(\epsilon^2).                          \tag{L3}
\]

Subtract the desired target `c*mu(A_epsilon)I`.  Its first-order matrix is

\[
(c-d)H-c\lambda_{\min}(H)I.                               \tag{L4}
\]

For `n>=3`, `d>0`.  Because `c-d>0`, the smallest eigenvalue of (L4) occurs at
`lambda_min(H)` and equals

\[
-d\lambda_{\min}(H)>0.                                    \tag{L5}
\]

Here `lambda_min(H)<0` follows from `tr(H)=0` and `H!=0`.  Thus every fixed
nonzero direction away from identity has a strictly positive first-order
half-prefix margin.  Compactness of normalized zero-diagonal directions and
uniformity of the analytic remainder imply that for each fixed `n` there is a
neighborhood of identity in which

\[
J_t(A)\succeq {t\mu(A)\over n}A^{-1}.                     \tag{L6}
\]

The neighborhood may shrink with dimension.  This is essential: the
signed-rank-one sharpness sequence takes `n` to infinity while approaching
identity and has limiting normalized constant one half.

## 3. The complete weighted-prefix hierarchy is locally safe

The same jet identifies the weighted object proposed in Iteration 5.  Put

\[
 C_t:=J_t-\frac12J_{t-1},\qquad J_0=0.
\]

For every `1<=t<=ceil(n/2)`, subtraction in (L2) gives

\[
 C_t(A_\epsilon)
 ={t+1\over2n}I
 -\epsilon{(t-1)(t+2)\over2n(n-1)}H+O(\epsilon^2).     \tag{L7}
\]

Write

\[
 c_t={t+1\over2n},\qquad
 d_t={(t-1)(t+2)\over2n(n-1)}.
\]

After energy normalization and subtraction of `c_t*mu(A_epsilon)I`,
the first-order margin is

\[
 (c_t-d_t)H-c_t\lambda_{\min}(H)I,
\]

whose smallest eigenvalue is `-d_t*lambda_min(H)>0` whenever `t>=2`.
For `t=1`, the desired statement is the global elementary inequality
`J_1=I/n >= (mu/n)A^{-1}`.  Consequently, at every fixed `n>=3` there
is one neighborhood of identity on which all finitely many inequalities

\[
 \boxed{C_t(A)\succeq {t+1\over2n}\mu(A)A^{-1},
 \qquad1\le t\le\lceil n/2\rceil}                     \tag{L8}
\]

hold simultaneously.  This proves the full proposed weighted hierarchy
locally, but the neighborhood is still not uniform in dimension.

## 4. Scope and exact check

- The result is leaf-free and applies to all perturbation directions at each
  fixed dimension.
- It does not give a dimension-uniform spectral neighborhood or settle a
  multiscale approach to identity.
- `scripts/iter5_prefix_identity_jet.py` enumerates all permutations through
  `n=7` with Fraction arithmetic and reconstructs (L2) and (L7) for every
  prefix depth through half, using deterministic frustrated rational
  directions.
