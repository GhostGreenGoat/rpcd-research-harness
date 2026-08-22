# Iteration 2 main line: analytic identities beyond bare Jensen

Date: 2026-08-20.

Status discipline:

- The algebraic statements below have complete proofs in this document and are labeled
  **proof candidates (E3)** until hostile audit and independent reconstruction are complete.
- The numerical specialization to the C011 matrix is only an E2 check.
- Nothing below proves C001.  The point is to replace the information-destroying bare Jensen step by
  exact variance and without-replacement corrections.

## 1. Setup

Let `A` be unit-diagonal SPD and let `M_pi` be the permuted Gauss--Seidel factor.  Put

\[
X_\pi=M_\pi M_\pi^\top,
\qquad
Y=\mathbb E_\pi X_\pi=A+S,
\qquad
\Delta_\pi=X_\pi-Y.
\]

The epoch matrix is `T_pi=I-M_pi^{-1}A`, and the exact energy identity is

\[
T_\pi^\top A T_\pi=A-A X_\pi^{-1}A. \tag{1}
\]

Thus all loss in the bare matrix-Jensen bound comes from replacing
`E[X_pi^{-1}]` by `Y^{-1}`.

## 2. Exact variance-resolvent identity

### Lemma 2.1 (noncommutative second-order resolvent identity)

For SPD matrices `X,Y` and `Delta=X-Y`,

\[
X^{-1}
=Y^{-1}-Y^{-1}\Delta Y^{-1}
 +Y^{-1}\Delta X^{-1}\Delta Y^{-1}. \tag{2}
\]

#### Proof

Starting from the resolvent identity

\[
X^{-1}-Y^{-1}=-X^{-1}\Delta Y^{-1},
\]

subtract and add `Y^{-1} Delta Y^{-1}`.  The remaining difference is

\[
(Y^{-1}-X^{-1})\Delta Y^{-1}
=Y^{-1}\Delta X^{-1}\Delta Y^{-1},
\]

where `Y^{-1}-X^{-1}=Y^{-1}\Delta X^{-1}` was used in the last equality.  This proves
(2). `square`

Since `E[Delta_pi]=0`, averaging (2) gives the exact formula

\[
\mathbb E X_\pi^{-1}
=Y^{-1}+Y^{-1}
  \mathbb E[\Delta_\pi X_\pi^{-1}\Delta_\pi]
  Y^{-1}. \tag{3}
\]

Consequently

\[
\mathbb E[T_\pi^\top A T_\pi]
=A-AY^{-1}A
-AY^{-1}\mathbb E[\Delta_\pi X_\pi^{-1}\Delta_\pi]Y^{-1}A. \tag{4}
\]

The omitted term in bare Jensen is therefore an explicit PSD variance correction, not an
unstructured error term.

## 3. A monotone polynomial inverse hierarchy

For an integer `r>=1` and `c>0`, define

\[
p_{r,c}(x)
=\frac1c\sum_{k=0}^{2r-1}(1-x/c)^k. \tag{5}
\]

### Lemma 3.1 (global polynomial minorant of inverse)

For every SPD matrix `X`,

\[
p_{r,c}(X)\preceq X^{-1}. \tag{6}
\]

#### Proof

The finite geometric-series identity gives

\[
X^{-1}-p_{r,c}(X)
=X^{-1}(I-X/c)^{2r}. \tag{7}
\]

Both factors on the right are polynomials/functions of `X`, so they commute.  In an eigenbasis of
`X`, every eigenvalue of the right side is
`lambda^{-1}(1-lambda/c)^{2r}>=0`.  Hence (6). `square`

Define the finite moment correction

\[
C_{r,c}
=\mathbb E[\Delta_\pi p_{r,c}(X_\pi)\Delta_\pi]. \tag{8}
\]

Congruence of (6) by `Delta_pi`, followed by (3)--(4), proves:

### Theorem candidate 3.2 (resolvent-moment upper hierarchy)

\[
\boxed{
\mathbb E[T_\pi^\top A T_\pi]
\preceq
U_{r,c}:=
A-AY^{-1}A-AY^{-1}C_{r,c}Y^{-1}A.
} \tag{9}
\]

Equation (9) is a valid upper bound for every `c>0`.  It is a Loewner refinement of bare Jensen when
`X_pi <= 2c I` for every permutation, because this extra spectral condition makes
`p_{r,c}(X_pi)` PSD.  The canonical choice `c=beta` below satisfies the stronger condition
`X_pi <= c I` and gives a monotone hierarchy.  Without such a spectral condition, the polynomial
minorant may be indefinite, so (9) must not be called a refinement merely from (6).

### Lemma 3.3 (canonical scale and monotone convergence)

For every permutation,

\[
\|M_\pi\|_F^2
=n+\sum_{i<j}A_{ij}^2
=\frac{n+\operatorname{tr}(A^2)}2
=:\beta. \tag{10}
\]

Hence `0 \prec X_pi \preceq beta I`.  Moreover, `det(M_pi)=1`, so `det(X_pi)=1` and

\[
\lambda_{\min}(X_\pi)\ge\beta^{-(n-1)}. \tag{11}
\]

Choose `c=beta`.  Then `R_pi=I-X_pi/beta` satisfies

\[
0\preceq R_\pi\preceq(1-\beta^{-n})I. \tag{12}
\]

It follows that

\[
p_{r,\beta}(X_\pi)\uparrow X_\pi^{-1},
\quad
C_{r,\beta}\uparrow
\mathbb E[\Delta_\pi X_\pi^{-1}\Delta_\pi],
\quad
U_{r,\beta}\downarrow
\mathbb E[T_\pi^\top A T_\pi]. \tag{13}
\]

The inverse-approximation error obeys

\[
0\preceq X_\pi^{-1}-p_{r,\beta}(X_\pi)
\preceq
\beta^{n-1}(1-\beta^{-n})^{2r}I. \tag{14}
\]

#### Proof

Each strict lower-triangular factor contains the diagonal ones and exactly one copy of every
off-diagonal entry, proving (10).  The spectral bound follows from operator norm being bounded by
Frobenius norm.  The determinant is one because the permuted factor is unit lower triangular.
If the eigenvalues of `X_pi` are `lambda_1,...,lambda_n`, their product is one and each is at most
`beta`; hence each is at least `beta^{-(n-1)}`.  Equations (12)--(14) now follow from the spectral
formula (7).  Monotonicity uses

\[
p_{r+1,\beta}(X)-p_{r,\beta}(X)
=\beta^{-1}R^{2r}(I+R)\succeq0. \quad\square
\]

### Why this is structurally useful

For fixed `r`, `C_{r,beta}` uses only finitely many polynomial moments of `X_pi`.  Entries of
`X_pi` are polynomials in precedence indicators of the random total order.  Expectations of a fixed
number of such indicators reduce to finite partial-order probabilities, rather than an `n!`
enumeration.  Thus (9) creates a possible analytic hierarchy:

```text
permutation precedence combinatorics
    -> finite matrix moments
    -> Loewner certificate U_r <= q A
    -> one-epoch contraction
```

The unresolved step is a uniform symbolic bound on these moments strong enough for the ICML target.

## 4. C011 is closed by the second polynomial level at float64 resolution

For the denominator-1000 rational matrix recorded in
`research/evidence/C011_RATIONAL_CANDIDATE.json`, bare Jensen gives

```text
ICML target             0.8163433709286394
bare Jensen             0.8527799042424034
```

Taking `c=beta=7.662482` gives the following maximum generalized eigenvalue of `U_{r,beta}`:

```text
r=1 (linear p)          0.8200383912374511
r=2 (cubic p)           0.8153270015783769
r=3 (quintic p)         0.8123839916434081
```

Thus the cubic inverse minorant already passes below the ICML target on the route-barrier matrix by
about `0.001016`.  This is only a finite float64 observation, but it shows that the variance hierarchy
recovers precisely the information destroyed by bare Jensen.  T015 should now certify this positive
margin with rational/interval arithmetic instead of certifying only the failure of bare Jensen.

## 5. A universal two-step without-replacement advantage

Move to energy coordinates.  Let unit vectors `v_i` satisfy

\[
\sum_{i=1}^n v_iv_i^\top=A,
\qquad
P_i=v_iv_i^\top,
\qquad
Z_i=I-P_i.
\]

Let `K_WR,2` be the expected squared-norm matrix after two independent uniform projections with
replacement, and `K_WOR,2` the corresponding matrix when two distinct indices are drawn in uniform
order.  Since `Z_i` is a symmetric projection,

\[
K_{\rm WR,2}=\frac1{n^2}\sum_{i,j}Z_iZ_jZ_i,
\qquad
K_{\rm WOR,2}=\frac1{n(n-1)}\sum_{i\ne j}Z_iZ_jZ_i. \tag{15}
\]

Define

\[
W=\sum_i (A^2)_{ii}P_i.
\]

Direct expansion gives

\[
\sum_i Z_iAZ_i=nA-2A^2+W\succeq0. \tag{16}
\]

and hence

\[
K_{\rm WR,2}
=I-\frac2nA+\frac2{n^2}A^2-\frac1{n^2}W, \tag{17}
\]

\[
K_{\rm WOR,2}
=I-\frac{2n-1}{n(n-1)}A
 +\frac2{n(n-1)}A^2
 -\frac1{n(n-1)}W. \tag{18}
\]

Subtracting yields the exact PSD improvement

\[
\boxed{
K_{\rm WR,2}-K_{\rm WOR,2}
=\frac{1}{n^2(n-1)}
 \sum_i Z_iAZ_i
\succeq0.
} \tag{19}
\]

This proves, for every unit-norm frame and every initial vector, that the first two distinct random
coordinates lose at least as much expected energy as two with-replacement coordinates.  It is a
genuine general RPCD-vs-RCD comparison, although only for two steps.

### Limitation

Equation (19) cannot simply be multiplied over disjoint pairs: after a prefix, the current vector and
the remaining coordinate set are correlated.  A successful extension needs a conditional version
whose correction survives this dependence.  This is the main connection to the conditional-Lyapunov
route.

## 6. New proof targets

1. Derive closed precedence-probability formulas for `C_{2,beta}` and bound them uniformly using only
   `n`, `sigma`, and PSD constraints.
2. Prove or refute the stronger one-epoch statement
   `E[T_pi^T A T_pi] <= q(n,sigma) A`.  It is sufficient for C001 but may be strictly stronger.
3. Find a conditional analogue of (19) for a random remaining set and a prefix-dependent PSD test
   matrix.
4. If the stronger one-epoch statement fails, lift the resolvent hierarchy from a single energy matrix
   to the full covariance superoperator or to a multi-epoch Lyapunov metric.
