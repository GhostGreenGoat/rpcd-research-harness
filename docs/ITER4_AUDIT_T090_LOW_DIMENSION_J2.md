# Hostile audit: the two-prefix corollary in dimensions at most four

**Claim audited:** for every unit-diagonal SPD correlation matrix
\(A\in\mathbb S_{++}^n\), \(\lambda_{\min}(A)=\mu\), the global one-epoch candidate

\[
 K(A)\succeq {\mu\over2}A^{-1}                           \tag{L1}
\]

holds when \(n\le4\).

**Outcome:** PASS.  The proof is exact and dimension-uniform through \(n=4\); no numerical search
is used.  It controls expected \(A\)-distance/objective as described below, not automatically a
condition-number-free relative Euclidean distance.

## 1. Exact two-prefix matrix and first Loewner step

For \(n\ge2\), the exact distinct-coordinate prefix hierarchy satisfies
\(0\preceq J_2(A)\preceq K(A)\), with

\[
 J_2(A)=
 {(2n-1)I-2A+\operatorname{Diag}(\operatorname{diag}A^2)
  \over n(n-1)}.                                         \tag{L2}
\]

Because \(A_{ii}=1\),

\[
 (A^2)_{ii}=\sum_j A_{ij}^2\ge1.
\]

Consequently

\[
 J_2(A)-{2(nI-A)\over n(n-1)}
 ={\operatorname{Diag}(\operatorname{diag}A^2)-I\over n(n-1)}
 \succeq0.                                                \tag{L3}
\]

This verifies the first Loewner direction.  Equality in (L3) occurs for diagonal \(A\), so the
diagonal correction cannot be assigned the opposite sign.

## 2. Spectral endpoint audit

Since \(A\) has trace \(n\) and every eigenvalue is at least \(\mu\), each eigenvalue \(\lambda\)
lies in

\[
 \mu\le\lambda\le n-(n-1)\mu.                            \tag{L4}
\]

The desired second step

\[
 {2(nI-A)\over n(n-1)}\succeq {2\mu\over n}A^{-1}       \tag{L5}
\]

is equivalent, after congruence by \(A^{1/2}\), to

\[
 \lambda(n-\lambda)\ge\mu(n-1).                          \tag{L6}
\]

The left side is concave in \(\lambda\), so its minimum on (L4) is at an endpoint.  At the lower
endpoint,

\[
 \mu(n-\mu)\ge\mu(n-1)
\]

because \(\mu\le1\).  At the upper endpoint, putting
\(d=n-(n-1)\mu\ge1\) gives

\[
 d(n-d)=d(n-1)\mu\ge\mu(n-1).                            \tag{L7}
\]

Thus (L5) has the stated direction, including \(\mu=1\), where both endpoint checks meet at
equality.

Combining (L2)--(L5) proves for every \(n\ge2\)

\[
 K(A)\succeq J_2(A)\succeq {2\mu\over n}A^{-1}.          \tag{L8}
\]

If \(n\le4\), then \(2/n\ge1/2\), so (L1) follows.  The \(n=1\) case is separate and trivial:
\(A=K(A)=[1]\).  Therefore (L1) is proved for every \(n\le4\).  Formula (L8) alone does not prove
(L1) for \(n\ge5\); no such extrapolation is made.

## 3. Finite-time meaning

With fresh independent permutations, the epoch energy identity and (L1) give

\[
 \mathbb E[\|x_{t+1}\|_A^2\mid x_t]
 \le(1-\mu/2)\|x_t\|_A^2.                               \tag{L9}
\]

Hence

\[
 \mathbb E\|x_t\|_A^2\le(1-\mu/2)^t\|x_0\|_A^2,
 \qquad
 \mathbb E\|x_t\|_A\le(1-\mu/2)^{t/2}\|x_0\|_A.       \tag{L10}
\]

The second inequality is expectation of distance, not distance of the expected iterate.  It gives
at most \((4n/\mu)\log(1/\varepsilon)\) coordinate updates for relative expected
\(A\)-distance, and \((2n/\mu)\log(1/\varepsilon)\) for relative squared distance/objective, up to
integer rounding.  Thus the requested \(O((n/\mu)\log(1/\varepsilon))\) order is established in
\(A\)-distance for \(n\le4\).

For relative Euclidean distance, norm conversion adds the factor
\(\sqrt{\lambda_{\max}(A)/\mu}\) before the geometric term; removing the resulting additive
condition-number logarithm needs a separate argument.

For completeness, (L10) also gives a high-probability \(A\)-distance statement without any new
matrix estimate.  Markov's inequality implies

\[
 \Pr\!\left(\|x_t\|_A\ge\varepsilon\|x_0\|_A\right)
 \le {e^{-\mu t/2}\over\varepsilon^2}.
\]

Thus failure probability at most \(\delta\) follows from
\(t\ge(2/\mu)(2\log(1/\varepsilon)+\log(1/\delta))\) epochs.

## 4. Evidence status

- The prefix monotonicity and formula (L2) were already independently reconstructed in
  `docs/ITER3_AUDIT_M2_BELLMAN.md`.
- This audit independently checks the new diagonal comparison, spectral interval, concave endpoint
  reduction, scaling at \(n=4\), and finite-time norm semantics.
- No Lean artifact exists.  Under the repository ladder, (L1) for \(n\le4\) is an E4
  hostile-audited theorem candidate, not a formalized E6 theorem.
