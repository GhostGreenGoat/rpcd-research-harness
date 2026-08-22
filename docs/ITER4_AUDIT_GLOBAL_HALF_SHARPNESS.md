# Iteration 4 audit: the global one-step constant and the bare-Jensen barrier

Date: 2026-08-21.  Status: exact proof reconstruction (E3); the original RPCD
covariance-rate conjecture C001 is not decided here.

## 1. No global one-step constant above one half

Let

\[
A=\mu I+(1-\mu){\bf 1}{\bf 1}^{\mathsf T},\qquad 0<\mu<1,
\]

and let `M_pi` be the unit lower triangular factor in permutation order.  A
forward substitution gives, up to the same permutation,

\[
M_\pi^{-1}{\bf 1}=(1,\mu,\mu^2,\ldots,\mu^{n-1})^{\mathsf T}.
\]

Consequently, for `K=E[M_pi^{-T}M_pi^{-1}]`,

\[
\frac{{\bf 1}^{\mathsf T}K{\bf 1}}{\|{\bf 1}\|^2}
=\frac{1-\mu^{2n}}{n(1-\mu^2)}.
\]

The parallel eigenvalue of `A` is `L=n-(n-1)mu`.  Therefore, with
`gamma=lambda_min(A^(1/2) K A^(1/2))`,

\[
\frac{\gamma}{\mu}
\leq \frac{L(1-\mu^{2n})}{n\mu(1-\mu^2)}.
\]

First sending `n` to infinity at fixed `mu<1`, and then sending `mu` upward to
one, makes the right side tend to `1/2`.  Hence no inequality
`K >= c*mu*A^{-1}` can hold with a dimension-independent `c>1/2`.  The
surviving candidate `c=1/2` is thus sharp for this proof architecture.

For an exact finite witness against `c=1`, take `n=9, mu=9/10`.  The parallel
Rayleigh quotient of `A^(1/2) K A^(1/2)` is

\[
\frac{44731861300157941}{50000000000000000}<\frac9{10}.
\]

The closed-form argument needs no numerical diagonalization and is insensitive
to permutation-product orientation: it is obtained directly by checking the
triangular forward solve.

## 2. Bare Jensen loses every positive uniform constant

Operator Jensen only gives `K >= (A+S)^{-1}`, where

\[
S=\frac13(A-I)^2+\frac16\operatorname{Diag}
  (\operatorname{diag}((A-I)^2)).
\]

On the same family, the parallel eigenvalue of `S` is

\[
s_\parallel=(1-\mu)^2\frac{(n-1)(2n-1)}6.
\]

Thus the ratio certified by bare Jensen is

\[
\frac{L}{\mu(L+s_\parallel)}.
\]

At `n=21, mu=9/20`, this is exactly

\[
\frac{3200}{6401}=\frac12-\frac1{12802},
\]

and the proposed Loewner inequality `mu(A+S) <= 2A` has parallel margin
`-3/800`.  More decisively, at every fixed `0<mu<1` the displayed Jensen ratio
is asymptotic to `3/[n*mu*(1-mu)]` and tends to zero.  Therefore a proof of the
sharp half-constant must retain the inverse-factor variance, the remaining-set
Bellman recursion, or equivalent permutation information.

Exact verifier:
`scripts/iter4_t095_bare_jensen_half_barrier.py`.

## 3. Pairing a word with its reverse is also insufficient

At the rank-one boundary `C=11^T`, the identity-order lower factor is the
cumulative-sum matrix.  Its inverse `D` is the bidiagonal first-difference
matrix.  Pairing this word with its reverse gives the quadratic form

\[
\frac12(D^{\mathsf T}D+DD^{\mathsf T}).
\]

In dimension nine, the kernel vector

\[
z=(-1,-1,-1,-1,0,1,1,1,1)^{\mathsf T}
\]

has exact Rayleigh quotient `3/8`, strictly below `1/2`.  Hence the sharp
global half-constant cannot be proved by a deterministic word/reverse-word
comparison.  This does not threaten the fully averaged conjecture: the other
permutations supply essential positive mass.

Exact verifier:
`scripts/iter4_t095_reverse_pair_half_barrier.py`.

## 4. The half-constant is already a theorem through dimension four

The exact two-update without-replacement decrease matrix for an `n`-dimensional
unit-diagonal SPD matrix is

\[
J_2=\frac{(2n-1)I-2A+\operatorname{Diag}(\operatorname{diag}A^2)}
          {n(n-1)}.
\]

Since the diagonal correction is at least `I`,

\[
J_2\succeq\frac{2(nI-A)}{n(n-1)}.
\]

Every eigenvalue of `A` lies in
`[mu,n-(n-1)mu]`.  Concavity of `lambda(n-lambda)` and evaluation at both
endpoints give `lambda(n-lambda)>=mu(n-1)`.  Functional calculus therefore
proves

\[
K(A)\succeq J_2(A)\succeq\frac{2\mu}{n}A^{-1}.             \tag{1}
\]

For `n<=4`, (1) implies the surviving global conjecture
`K(A)>=(mu/2)A^{-1}` for every admissible `A`.  For arbitrary `n`, it gives the
unconditional finite-time benchmark `O(n^2/mu log(1/epsilon))` coordinate
updates.  Thus the unresolved half-constant problem begins at dimension five.
