# Iteration 5 theorem candidate: half-prefix bound for all equicorrelations

Date: 2026-08-21.  Status: E4 internally hostile-audited family theorem
candidate, with an independent exact finite-permutation reconstruction.

Let

\[
A_n(\rho)=(1-\rho)I+\rho J,
\qquad -{1\over n-1}<\rho<1,
\]

and let `J_s(A)` be the exact expected residual-coordinate energy-decrease
matrix after the first `s` distinct coordinates of a uniform random
permutation.  Fix any `1<=s<=ceil(n/2)` and put

\[
\mu=\min\{1-\rho,1+(n-1)\rho\}.
\]

The claim proved below is the complete leaf-free first-half curve

\[
\boxed{J_s(A_n(\rho))\succeq {s\mu\over n}A_n(\rho)^{-1},
       \qquad1\le s\le\lceil n/2\rceil.}                 \tag{E1}
\]

At `s=ceil(n/2)`, this implies
`J_s(A_n(rho)) >= (mu/2)A_n(rho)^{-1}`.

It covers the full positive and negative equicorrelation interval, not only
the signed-rank-one lift.  It does not cover a general correlation matrix.

## 1. Exact invariant recurrences

Permutation symmetry makes `J_s` scalar on `1^perp` and `span(1)`.  Write its
ordinary eigenvalues as `a_{n,s}` and `p_{n,s}`.  Starting from
`a_{k,0}=p_{k,0}=0`, the Bellman recursion gives

\[
p_{k,t}={1\over k}+{k-1\over k}(1-\rho)^2p_{k-1,t-1},      \tag{E2}
\]

\[
a_{k,t}={1\over k}+{k-2\over k-1}a_{k-1,t-1}
 +{[1+(k-1)\rho]^2\over k(k-1)}p_{k-1,t-1}.               \tag{E3}
\]

For (E3), test on `e_i-e_j`.  If the first pivot is neither special
coordinate, the child vector stays transverse.  If it is special, the child
vector has transverse squared norm `(k-2)/(k-1)` and parallel squared norm
`[1+(k-1)rho]^2/(k-1)`.  Averaging and dividing by
`||e_i-e_j||^2=2` gives (E3).

Putting `q_{k,t}=kp_{k,t}`, (E2) solves after `s` lifts as

\[
q_{n,s}=S_s:=\sum_{j=0}^{s-1}(1-\rho)^{2j},
\qquad p_{n,s}=S_s/n.                                     \tag{E4}

## 2. Nonnegative correlations

Set `alpha=1-rho` and first suppose `rho>=0`.  For the transverse right side
`e_i-e_j`, every special coordinate that appears in the prefix contributes a
solve of magnitude at least one.  The first is exactly `+/-1`; between the two
special coordinates the accumulated solve sum keeps its sign and is multiplied
by `alpha`, so the second has magnitude `1+rho*alpha^ell>=1`.  Hence

\[
a_{n,s}\ge s/n.                                           \tag{E5}
\]

The transverse eigenvalue of `A` is `alpha=mu`, so (E5) proves that block.

For the parallel block, let `delta=rho=1-alpha`.  Since
`n>=2s-1`, its eigenvalue obeys

\[
L_n=1+(n-1)\delta\ge1+2(s-1)\delta=:L_* .                 \tag{E6}
\]

Also

\[
S_s={1-(1-\delta)^{2s}\over\delta(2-\delta)}.              \tag{E7}
\]

At `delta=0`, `A=I`, `S_s=s`, and (E1) is equality, so the
following cancellation is needed only for `delta>0` (equivalently, (E7) may
be read by continuous extension at zero).

The inverse binomial expansion gives

\[
(1-\delta)^{-2s}
\ge1+2s\delta+s(2s+1)\delta^2=:1+X,
\]

and therefore `1-(1-delta)^(2s)>=X/(1+X)`.  After cancelling
`s*delta`, the sufficient inequality
`L_*S_s>=s(1-delta)` reduces to

\[
\begin{aligned}
&[1+2(s-1)\delta][2+(2s+1)\delta]\\
&\quad-(1-\delta)(2-\delta)
 [1+s\delta(2+(2s+1)\delta)]\\
&=\delta[2s+(2s-3)\delta+s(6s+1)\delta^2
              -s(2s+1)\delta^3]\ge0.                    \tag{E8}
\end{aligned}
\]

For `s>=2`, the last two terms combine as
`s*delta^2[(6s+1)-(2s+1)delta]>=4s^2 delta^2`, and all other
coefficients are nonnegative.  The `s=1` case is immediate.  Equations
(E4), (E6)--(E8) give `L_np_{n,s}>=s*mu/n`.

## 3. Negative correlations

Write `rho=-beta`, `alpha=1+beta`, so

\[
\mu=L_n=1-(n-1)\beta,qquad0<\beta<1/(n-1).                \tag{E9}
\]

The parallel recurrence (E4) has `S_s>=s`, hence
`L_np_{n,s}>=s*mu/n`.

For a transverse right side, the first selected special coordinate again
contributes one.  If both are selected and `ell` ordinary coordinates lie
between them, the second solve is `-1+beta*alpha^ell`.  Discarding all later
nonnegative contributions and using

\[
(1-\beta\alpha^\ell)^2
\ge1-2\beta\alpha^{n-2}
\]

gives, from the exact hypergeometric probabilities,

\[
a_{n,s}\ge{s\over n}\left[1-
 \beta\alpha^{n-2}{s-1\over n-1}\right].                 \tag{E10}
\]

Now

\[
{\mu\over\alpha}=1-{n\beta\over\alpha}.
\]

It suffices for (E10) that

\[
\alpha^{n-1}{s-1\over n-1}\le n.                         \tag{E11}
\]

But `alpha<=n/(n-1)`, `(s-1)/(n-1)<=1`, and
`(1+1/(n-1))^(n-1)<e<=n` for `n>=3`; `n=2` is direct.
Thus `(1-rho)a_{n,s}>=s*mu/n`, finishing (E1).

## 4. Scope and verification

- The theorem uses the complete two-isotypic symmetry of an equicorrelation
  matrix.  It is evidence for, not a proof of, the general half-prefix target.
- Unlike the Iteration-4 signed-rank-one proof, no determinant leaf is used.
- `scripts/iter5_equicorrelation_half_prefix.py` independently enumerates all
  permutations through dimension six with rational positive and negative
  correlations, verifies (E2)--(E4), and checks both exact target margins.
  The separate hostile-audit implementation
  `research/iteration5/route_a/scripts/verify_equicorrelation_independent.py`
  checks every `s<=ceil(n/2)` through dimension seven, including positive,
  negative, and zero correlation.
