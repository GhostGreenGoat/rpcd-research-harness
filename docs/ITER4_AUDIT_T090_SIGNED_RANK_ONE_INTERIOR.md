# Hostile audit: signed-rank-one interior constant obstruction

**Audited claim:** Section 2 and the finite-time transfer in Section 4 of
`docs/ITER4_T090_CONSTANT_ASSESSMENT.md`.

**Outcome:** PASS, with two presentation qualifications made explicit below: the update count stated
there is for relative **squared** \(A\)-distance.  For the stronger quantity requested by the user,
\(\mathbb E\|x_t\|_A\), Jensen/conditional Cauchy--Schwarz gives the same big-O order but twice
the displayed leading constant.  Also, this direct transfer is in \(A\)-distance; a relative
Euclidean-distance statement incurs a condition-number prefactor unless another argument removes
it.  Neither point affects the algebraic \(1/2\) obstruction.

## 1. Matrix, spectrum, and triangular-factor orientation

Let

\[
 A=\mu I+(1-\mu)J_n,
 \qquad 0<\mu<1.                                         \tag{A1}
\]

It is a unit-diagonal SPD correlation matrix.  Its eigenvalue on
\(\mathbf1^\perp\) is \(\mu\), while on \(\operatorname{span}\{\mathbf1\}\) it is

\[
 \lambda_\parallel=n-(n-1)\mu>\mu.                       \tag{A2}
\]

Thus the parameter called \(\mu\) in (A1) is exactly \(\lambda_{\min}(A)\), not merely a lower
bound.  A signed rank-one matrix \(ss^\top\) is reduced to (A1) by diagonal sign conjugation, which
also conjugates all coordinate factors and preserves the relevant eigenvalues.

For an order \(\pi=(\pi_1,\ldots,\pi_n)\), the convention in the harness is that \(M_\pi\) is
lower **in permutation order**.  Hence \(y=M_\pi^{-1}\mathbf1\) satisfies

\[
 y_{\pi_k}=1-(1-\mu)\sum_{\ell<k}y_{\pi_\ell}.            \tag{A3}
\]

Induction gives

\[
 \boxed{y_{\pi_k}=\mu^{k-1}.}                            \tag{A4}
\]

Indeed the previous sum is \((1-\mu^{k-1})/(1-\mu)\).  This checks both the power direction and
the factor orientation.  Reversing the convention would reverse the displayed vector in labelled
coordinates but would not change its squared norm; (A3) confirms that the document uses the
repository convention rather than relying on that accidental invariance.
The verifier additionally constructs the full labelled matrix at \(n=5,\mu=2/3\), runs all
\(5!=120\) orders through a generic forward solve, and checks both (A4) and
\(M_\pi y=\mathbf1\) coordinate by coordinate.

## 2. The parallel upper bound on \(\gamma(A)\)

Define

\[
 K(A)=\mathbb E_\pi M_\pi^{-\top}M_\pi^{-1},
 \qquad
 \gamma(A)=\lambda_{\min}(A^{1/2}K(A)A^{1/2}).            \tag{A5}
\]

Uniform permutation averaging makes \(K(A)\) permutation invariant, so the parallel line is a
reducing eigenspace.  From (A4), its \(K\)-eigenvalue is

\[
 \kappa_\parallel
 ={1\over n}\sum_{j=0}^{n-1}\mu^{2j}
 ={1-\mu^{2n}\over n(1-\mu^2)}.                          \tag{A6}
\]

Since \(A\) and \(K(A)\) commute on this line, its eigenvalue in (A5) is

\[
 g_{n,\mu}
 =[n-(n-1)\mu],{1-\mu^{2n}\over n(1-\mu^2)}.            \tag{A7}
\]

Therefore \(\gamma(A)\le g_{n,\mu}\).  Equality is not needed for the asymptotic obstruction.
For the displayed finite example \(n=9,\mu=9/10\), an independent exact two-labelled-coordinate
recurrence also reconstructs the transverse eigenvalue and verifies that the parallel eigenvalue
is the actual minimum:

\[
 \gamma(A)=g_{9,9/10}
 ={44731861300157941\over50000000000000000}
 <{9\over10}.                                             \tag{A8}
\]

The exact gap is

\[
 -{268138699842059\over50000000000000000}.
\]

Thus the tempting global statement \(\gamma(A)\ge\mu\) is already exactly refuted at finite
dimension.

## 3. Quantifier order and the constant \(1/2\)

Fix \(0<\mu<1\) first.  Equation (A7) gives

\[
 \lim_{n\to\infty}{g_{n,\mu}\over\mu}
 ={1\over\mu(1+\mu)}.                                    \tag{A9}
\]

Only after this dimension limit do we take \(\mu\uparrow1\), obtaining \(1/2\).  The order is
essential: at \(\mu=1\) exactly, \(A=I\), \(K=I\), and \(\gamma/\mu=1\).

The logically quantified conclusion is as follows.  Given any \(c>1/2\), first choose a fixed
\(\mu<1\) sufficiently close to one that
\(1/[\mu(1+\mu)]<c\); then choose a sufficiently large integer \(n\) so that
\(g_{n,\mu}/\mu<c\).  Since \(\gamma/\mu\le g_{n,\mu}/\mu\), this produces an SPD correlation
matrix violating

\[
 K(A)\succeq c\mu A^{-1}.                                \tag{A10}
\]

Thus no dimension-uniform constant greater than \(1/2\) is possible for this particular global
one-epoch fixed-energy matrix inequality.  The audit found no claim that \(c=1/2\) itself is
proved; it remains a sharp compatible candidate.

## 4. Finite-time transfer, including expectation of distance

Suppose, hypothetically, that (A10) is proved for some universal \(c>0\).  The exact epoch identity

\[
 A-\mathbb E_\pi(T_\pi^\top A T_\pi)=AK(A)A             \tag{A11}
\]

then implies, conditionally on the current iterate and with a fresh independent permutation,

\[
 \mathbb E[\|x_{t+1}\|_A^2\mid x_t]
 \le(1-c\mu)\|x_t\|_A^2.                                \tag{A12}
\]

Iteration gives the strong second-moment statement

\[
 \mathbb E\|x_t\|_A^2
 \le(1-c\mu)^t\|x_0\|_A^2.                              \tag{A13}
\]

For the user-requested expectation of distance, rather than the weaker distance of the expected
iterate, conditional Cauchy--Schwarz yields

\[
 \mathbb E[\|x_{t+1}\|_A\mid x_t]
 \le\sqrt{1-c\mu}\,\|x_t\|_A,
\]

and hence

\[
 \boxed{
 \mathbb E\|x_t\|_A
 \le(1-c\mu)^{t/2}\|x_0\|_A.}                           \tag{A14}
\]

This is genuinely \(\mathbb E\|x_t\|_A\), not
\(\|\mathbb E x_t\|_A\).  Therefore relative expected distance \(\varepsilon\) requires at most

\[
 t\ge {2\over c\mu}\log{1\over\varepsilon}              \tag{A15}
\]

epochs (rounding upward), or
\(O((n/\mu)\log(1/\varepsilon))\) coordinate updates.  For squared distance/objective, the factor
two in (A15) is absent.  If the sharp compatible candidate \(c=1/2\) were proved, the respective
leading update counts from this argument would be \(4n/\mu\) and \(2n/\mu\), up to the logarithm.

If “distance” is required to mean Euclidean distance, (A14) alone gives only

\[
 \mathbb E\|x_t\|_2
 \le \sqrt{{\lambda_{\max}(A)\over\mu}}
 (1-c\mu)^{t/2}\|x_0\|_2.                               \tag{A16}
\]

Thus a relative Euclidean target introduces an additive
\(\tfrac12\log(\lambda_{\max}/\mu)\) inside the iteration logarithm.  With unit diagonal,
\(\lambda_{\max}\le n\).  Removing this condition-number prefactor, if the requested theorem
forbids it, needs a separate Euclidean/covariance argument; it must not be silently inferred from
the fixed \(A\)-energy certificate.

## 5. Scope and independent artifact

- The signed-rank-one interior family bounds only a global **one-epoch fixed \(A\)-energy**
  certificate.  It does not refute the covariance-map spectral-radius conjecture or the desired
  big-O complexity.
- Its \(1/2\) obstruction is a high-eigenvalue parallel-direction effect and is logically distinct
  from the pole--simplex boundary upper bound \(3/2\).
- The finite exact reconstruction, including the transverse comparison at \(n=9\), is implemented
  independently in `scripts/verify_iter4_t090_signed_rank_one_interior.py` and recorded in
  `research/evidence/ITER4_T090_SIGNED_RANK_ONE_INTERIOR_AUDIT_2026_08_21.json`.
- No Lean/formal certificate or outside-human review exists.  Under the internal ladder this is an
  E4 hostile audit with no mathematical blocker and one finite-time presentation clarification.
