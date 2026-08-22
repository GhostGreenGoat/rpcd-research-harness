# Iteration 4 synthesis: matrix inequalities for finite-time RPCD

Date: 2026-08-21.  The normalized Hessian is unit diagonal and
`mu=lambda_min(A)`.  The original covariance-map conjecture C001 and the
general `O(n/mu log(1/epsilon))` result remain open.

## Outcome first

The sharp fixed-`A` one-epoch target from Iteration 3 is false, but a weaker and
asymptotically sharp matrix target survives:

\[
K(A)\succeq {\mu\over2}A^{-1}.                              \tag{S1}
\]

Here `K(A)=E[M_pi^{-T}M_pi^{-1}]`.  If (S1) holds, then fresh random
permutations give

\[
\mathbb E\|x_t\|_A^2\le(1-\mu/2)^t\|x_0\|_A^2,
\quad
\mathbb E\|x_t\|_A\le(1-\mu/2)^{t/2}\|x_0\|_A.             \tag{S2}
\]

Thus relative squared `A`-distance uses at most
`(2n/mu)log(1/epsilon)` coordinate updates, while relative expected
`A`-distance uses `(4n/mu)log(1/epsilon)`.  These are the requested asymptotic
order and control expectations of distances, not distances of expected
iterates.

Statement (S1) is proved for every matrix through `n=4` and for the complete
signed-rank-one family in every dimension.  It remains open for a general
matrix starting at `n=5`.

## Exact failure of the stronger target

For

\[
C=\begin{pmatrix}
J_2&\frac23\mathbf1_2\mathbf1_6^T\\
\frac23\mathbf1_6\mathbf1_2^T&\frac23I_6+\frac13J_6
\end{pmatrix},
\]

the spectrum is `0^2,(2/3)^5,14/3`.  On `u=e_1-e_2`,

\[
{u^TK_0(C)u\over\|u\|^2}={1057837\over531441}<2.           \tag{S3}
\]

The value was reconstructed by 56 symmetry classes, all `8!` permutations,
and an independent exact `2^8` Bellman recursion.  Its positive lift at
`mu=1/100` also violates the stronger fixed-`A` M1 rate by an exact rational
margin.  This refutes the sufficient condition C026, not C001.

## Why one half is the right surviving constant

On `A=mu I+(1-mu)11^T`, forward substitution gives

\[
M_\pi^{-1}\mathbf1=(1,\mu,\ldots,\mu^{n-1})
\]

in permutation order.  Hence

\[
{\gamma(A)\over\mu}
\le { [n-(n-1)\mu](1-\mu^{2n})
       \over n\mu(1-\mu^2)}.                               \tag{S4}
\]

Sending `n` to infinity before `mu` tends upward to one makes (S4) tend to
`1/2`; no global one-step constant larger than one half is possible.

Conversely, the determinant-tail certificate at depth `r=ceil(n/2)` satisfies
(S1) on this whole family.  The transverse block follows by counting the two
distinguished coordinates in the random prefix.  The parallel block follows
from `q_k=1+mu^2 q_{k-1}` and a geometric-sum bound.  This proof passed an
independent hostile audit, so the family both validates and makes the constant
sharp.

## General positive results and current blocker

The exact two-update matrix obeys

\[
K(A)\succeq J_2(A)\succeq {2\mu\over n}A^{-1}.              \tag{S5}
\]

Equation (S5) proves (S1) for `n<=4` and gives the unconditional general
benchmark `O(n^2/mu log(1/epsilon))`.

For the determinant-tail Bellman hierarchy, every depth `r=o(n)` is
insufficient on a signed-rank-one low-`mu` family; linear depth is necessary.
At half depth, extensive structured and optimized searches found no violation,
but this is not a proof.  The second Schur-loss moment has an exact ordered-pair
frame and complementary PSD compression.  The remaining obstruction is to
control its third and higher Bellman lifts without scalarizing away the
anisotropy.

## Proof shortcuts ruled out exactly

- Bare inverse Jensen loses every positive dimension-uniform constant.  On an
  equicorrelation family its certified ratio tends to zero; finite rational
  witnesses already fall below one half.
- Pairing each permutation word with its reverse is insufficient.  For
  `C=11^T` in dimension nine, the kernel vector
  `(-1,-1,-1,-1,0,1,1,1,1)` has exact pair quotient `3/8`.
- Fixed shallow determinant tails and childwise scalarization lose factors
  growing with dimension.

The next primary task is T095: prove or refute (S1), preferably through a
half-depth remaining-set inequality or a new full-permutation matrix average
that retains all higher Schur moments.
