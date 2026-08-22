# Iteration 2, route C: projection algebra and Gram-determinant bounds

Date: 2026-08-20.

## Status discipline

- Statements whose proofs are given below are labelled **THEOREM (E3 proof draft)**.  They have not
  passed a hostile audit or independent reconstruction and are not promoted to theorem candidates in
  the research ledger.
- The norm bound `||P_pi||^2 <= 1-det(A)` is an existing Meany/alternating-projection bound, not a
  novelty claim.  The exact defect factorization below supplies a self-contained proof in the present
  square, unit-vector setting.
- The deduction of a high-`sigma` slice of C001 is a new harness observation whose priority has not
  been audited.
- Nothing in this note proves C001 for every `n` and `sigma`.

## 1. Frame and tensor formulations

Let

\[
A=V^\top V\succ0,
\qquad V=[v_1\ \cdots\ v_n],
\qquad \|v_i\|=1,
\]

where the last property is equivalent to `diag(A)=1`.  Put

\[
Q_i=v_iv_i^\top,\qquad Z_i=I-Q_i.
\]

If `y=Vx`, one coordinate update in coordinate `i` becomes

\[
y^+=V(I-e_ie_i^\top A)x=(I-v_iv_i^\top)y=Z_i y.
\]

For a permutation `pi`, define

\[
P_\pi=Z_{\pi_n}\cdots Z_{\pi_1}.
\]

Then `P_pi=V T_pi V^{-1}`.  Consequently

\[
\mathcal C_A:=\mathbb E_\pi[P_\pi\otimes P_\pi]
=(V\otimes V)\,\mathbb E_\pi[T_\pi\otimes T_\pi]\,
 (V^{-1}\otimes V^{-1}),                                      \tag{1}
\]

so the two covariance matrices have the same spectrum.

It is useful to set

\[
W_i=Z_i\otimes Z_i.
\]

Each `W_i` is itself an orthogonal projection, and

\[
\mathcal C_A={1\over n!}\sum_{\pi\in S_n}
W_{\pi_n}\cdots W_{\pi_1}.                                   \tag{2}
\]

Thus C001 is a special noncommutative, without-replacement product problem for projections on
`R^n tensor R^n`.

## 2. Exact two-step correction on the covariance space

Let

\[
D=\sum_{i=1}^n W_i,\qquad R={D\over n}.
\]

Here `R` is the one-step with-replacement covariance operator in projection coordinates.  Let

\[
C_2={1\over n(n-1)}\sum_{i\ne j}W_jW_i
\]

be the covariance operator after two uniformly ordered distinct indices.

### THEOREM 2.1 (E3 proof draft: exact finite-population correction)

For arbitrary orthogonal projections `W_1,...,W_n`,

\[
\boxed{
C_2={nR^2-R\over n-1},
\qquad
R^2-C_2={R(I-R)\over n-1}\succeq0.
}                                                               \tag{3}
\]

#### Proof

Idempotence gives

\[
\sum_{i\ne j}W_jW_i
=D^2-\sum_iW_i^2=D^2-D.
\]

Substitution of `D=nR` proves the first identity.  Since `R` is an average of orthogonal
projections, `0 <= R <= I`; hence `R(I-R)` is PSD, proving the second identity. `square`

Equation (3) is stronger than a scalar comparison: the without-replacement gain is the exact PSD
operator `R(I-R)/(n-1)`.  It retains a piece of the order information discarded by a first-moment
Jensen bound.  It does not iterate directly through an epoch, because after a prefix the remaining
set and the current state are correlated.

### BARRIER 2.2 (degree three is no longer a polynomial of `R`)

Put

\[
K=\sum_i W_i D W_i.
\]

A direct classification of the equality patterns among three indices gives

\[
\sum_{i,j,k\ \mathrm{distinct}}W_kW_jW_i
=D^3-2D^2+2D-K.                                                 \tag{4}
\]

Indeed, inclusion--exclusion over the events `i=j`, `j=k`, and `i=k` gives

\[
D^3-(D^2+D^2+K)+(D+D+D)-D
=D^3-2D^2+2D-K.
\]

This count is on index triples and does not require the projections to commute.  Relative to the
commuting falling-factorial polynomial, (4) reads

\[
D(D-I)(D-2I)+(D^2-K).                                           \tag{5}
\]

The correction `D^2-K` has no universal Loewner sign for general projections.  For example, take

\[
P=\begin{pmatrix}1&0\\0&0\end{pmatrix},\qquad
Q=\begin{pmatrix}c^2&cs\\cs&s^2\end{pmatrix},
\qquad c,s>0,\quad c^2+s^2=1.
\]

For `D=P+Q` and `K=PDP+QDQ`,

\[
D^2-K=cs^2
\begin{pmatrix}c&s\\s&-c\end{pmatrix},                       \tag{6}
\]

whose eigenvalues are `+cs^2` and `-cs^2`.  Therefore the two-step PSD correction cannot be
continued by simply asserting the same sign at degree three.  The special tensor form
`W_i=Z_i tensor Z_i` might impose further constraints, but those constraints still need a proof.
If a three-element family is desired for (4), append the zero orthogonal projection; the same
indefinite block remains.  This example is a barrier for generic projection algebra, not a
counterexample within the more restrictive RPCD tensor family.

## 3. Exact Gram-defect determinant

For a fixed permutation define prefix products

\[
P_0=I,\qquad P_k=Z_{\pi_k}\cdots Z_{\pi_1},
\]

and vectors

\[
w_k=P_{k-1}^\top v_{\pi_k}
=Z_{\pi_1}\cdots Z_{\pi_{k-1}}v_{\pi_k}.
\]

### THEOREM 3.1 (E3 proof draft: exact defect determinant)

For every permutation,

\[
I-P_\pi^\top P_\pi=\sum_{k=1}^n w_kw_k^\top,                  \tag{7}
\]

and

\[
\boxed{\det(I-P_\pi^\top P_\pi)=\det A.}                     \tag{8}
\]

Consequently,

\[
\boxed{\|P_\pi\|_2^2\le 1-\det A}                            \tag{9}
\]

for every order `pi`.

#### Proof

Because `Z_i` is a symmetric projection,

\[
P_{k-1}^\top P_{k-1}-P_k^\top P_k
=P_{k-1}^\top Q_{\pi_k}P_{k-1}=w_kw_k^\top.
\]

Summing over `k` proves (7).  Each `w_k` equals `v_{pi_k}` plus a linear combination of
`v_{pi_1},...,v_{pi_{k-1}}`.  Therefore, if `mathsf W_pi=[w_1 ... w_n]` and
`V_pi=[v_{pi_1} ... v_{pi_n}]`, then

\[
\mathsf W_\pi=V_\pi R_\pi
\]

for an upper-triangular `R_pi` with unit diagonal.  Hence

\[
\det(\mathsf W_\pi\mathsf W_\pi^\top)
=\det(V_\pi V_\pi^\top)=\det(V^\top V)=\det A,
\]

which proves (8).  If `s_1=||P_pi||_2` is the largest singular value, the eigenvalues of the defect
are `1-s_j^2` and all lie in `(0,1]`.  Thus

\[
\det A=\prod_j(1-s_j^2)\le 1-s_1^2,
\]

which gives (9). `square`

### Source and priority

Inequality (9) is the classical Meany/Gram-determinant estimate for cyclic alternating projections.
Galantai, *On the rate of convergence of the alternating projection method in finite dimensional
spaces*, JMAA 310 (2005), 30--44, gives the alternating-projection estimate
([DOI 10.1016/j.jmaa.2004.12.050](https://doi.org/10.1016/j.jmaa.2004.12.050)).
Dai and Schon explicitly restate the square, normalized-row Kaczmarz form
`rho^2 <= 1-product_i singular_value_i(B)^2`
([arXiv:1411.4017, Section III-A](https://arxiv.org/abs/1411.4017)).  For the present square frame,
that product is `det(V^T V)=det A`.  Therefore (9) must not be presented as new.  The factorization
(7)--(8) records a self-contained proof under exactly the assumptions used here: `n` linearly
independent unit vectors in `R^n` and unrelaxed orthogonal hyperplane projections.

## 4. Consequences for C001

All norms below are induced Euclidean norms on the vectorized covariance space, equivalently induced
operator norms for the Frobenius norm on matrices.  Similarity in (1) is used only to preserve the
spectrum.  In projection coordinates, the full permutation average is self-adjoint by pairing each
word with its reversed permutation, although the argument only needs the general inequality
`rho(C) <= ||C||_2`.  By (1), subadditivity of operator norm, and (9),

\[
\rho(\mathcal M_A)=\rho(\mathcal C_A)
\le\|\mathcal C_A\|_2
\le\mathbb E_\pi\|P_\pi\otimes P_\pi\|_2
=\mathbb E_\pi\|P_\pi\|_2^2
\le1-\det A.                                                   \tag{10}
\]

This is deterministic in the order and therefore does not yet exploit the random-permutation
average.

Let the eigenvalues of `A` be `lambda_i`.  They obey

\[
\lambda_i\ge\sigma,\qquad \sum_i\lambda_i=\operatorname{tr}A=n.
\]

The product is minimized on this simplex when `n-1` eigenvalues equal `sigma`.  To see this, take any
two eigenvalues `sigma<a<=b` and transfer `delta in (0,a-sigma]` from `a` to `b`.  Their product
changes by

\[
(a-\delta)(b+\delta)-ab
=\delta(a-b)-\delta^2\le0.
\]

Repeating this operation leaves at most one eigenvalue above `sigma`; the trace constraint fixes it as
`n-(n-1)sigma`.  Therefore

\[
\det A\ge d_n(\sigma)
:=\sigma^{n-1}\bigl(n-(n-1)\sigma\bigr).                       \tag{11}
\]

This eigenvalue bound is sharp even with unit diagonal: equality is attained by

\[
A_\sigma=\sigma I+(1-\sigma)\mathbf1\mathbf1^\top.
\]

Combining (10)--(11) gives the general analytic estimate

\[
\boxed{\rho(\mathcal M_A)\le1-d_n(\sigma).}                    \tag{12}
\]

### THEOREM 4.1 (E3 proof draft: C001 for `n=2`)

For `n=2`, (12) proves C001 for every `sigma in (0,1]`.

Indeed,

\[
1-d_2(\sigma)=(1-\sigma)^2
\le(1-\sigma/2)^4,
\]

because `1-sigma <= (1-sigma/2)^2`.  The latter quantity is one of the two terms in the C001
maximum.

### THEOREM 4.2 (E3 proof draft: a general high-`sigma` slice)

For `n>=2`, let `tau_n in (0,1)` be the unique solution of

\[
\tau_n^{n-1}\bigl(n-(n-1)\tau_n\bigr)
=1-\left(1-{1\over n}\right)^n.                               \tag{13}
\]

Then C001 holds for every unit-diagonal SPD `A` with
`lambda_min(A)=sigma >= tau_n`.

To see uniqueness, note that

\[
d_n'(\sigma)=n(n-1)\sigma^{n-2}(1-\sigma)>0
\]

on `(0,1)`, while `d_n(0)=0` and `d_n(1)=1`.  If `sigma>=tau_n`, (12)--(13) give

\[
\rho(\mathcal M_A)
\le1-d_n(\sigma)
\le\left(1-{1\over n}\right)^n
\le\max\left\{
\left(1-{1\over n}\right)^n,
\left(1-{\sigma\over n}\right)^{2n}
\right\}.
\]

This is a genuine partial result for arbitrary frames, but it only covers the near-orthogonal/high
minimum-eigenvalue regime.  Since (11) is sharp and (9) ignores the permutation average, extending
this particular scalar determinant argument alone cannot be expected to settle the difficult
small-`sigma` region.

## 5. Relation to noncommutative AM--GM

Kim--Lee--Yun already identify the projection representation and a matrix AM--GM route in Appendix
E.2 of their ICML paper
([PMLR paper and PDF](https://proceedings.mlr.press/v267/kim25x.html)).  The general Recht--Re
noncommutative AGM conjecture is false from degree five onward; Lai--Lim prove this via a
noncommutative Positivstellensatz
([arXiv:2006.01510](https://arxiv.org/abs/2006.01510)).  Their paper also stresses that the upper
Loewner half may survive, so their counterexample must not be claimed to refute the special RPCD
projection inequality.

### BARRIER 5.1

Even a perfect black-box comparison

\[
\left\|{1\over n!}\sum_\pi W_{\pi_n}\cdots W_{\pi_1}\right\|
\le\left\|{1\over n}\sum_iW_i\right\|^n
\]

would generally be too weak to prove the ICML target: the right side is the with-replacement RCD
covariance rate, and the ICML paper proves that this rate is strictly larger than its RPCD target on
the structured class.  A useful AM--GM refinement must retain the finite-population deflation in
(3), rather than end at the norm of the one-step average.

At degree three, (4)--(6) show exactly where a simple scalar/falling-factorial continuation breaks:
the new pinching moment `K=sum_i W_i D W_i` is unavoidable and its correction has no generic sign.
The next viable analytic target is therefore a bound on this pinching term using the special
rank-one-frame form of the `Z_i`, not another bare Jensen or generic matrix-AM--GM application.

## 6. What this route accomplished

1. **THEOREM / E3:** an exact covariance-level two-step without-replacement correction,
   `R^2-C_2=R(I-R)/(n-1)`.
2. **BARRIER:** degree three introduces a genuinely noncommutative, generally indefinite correction.
3. **EXTERNAL THEOREM + self-contained specialization:** the Meany/Gram determinant bound
   `||P_pi||^2 <= 1-det A` under the precise square unit-frame assumptions.
4. **THEOREM / E3:** C001 follows for all `n=2` instances and for every `n` in the analytic
   high-`sigma` region (13).
5. **UNRESOLVED:** the remaining parameter region needs a permutation-sensitive bound on higher
   pinching/word moments; the determinant scalar and bare noncommutative AM--GM bounds discard too
   much information.
