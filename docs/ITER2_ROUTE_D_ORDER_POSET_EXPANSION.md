# Iteration 2 route D: order-poset expansion of the triangular inverse

Date: 2026-08-20.

Status: the finite expansions below are **proof candidates (E3)**.  They are algebraic identities,
not a proof of C001.  Their purpose is to replace factorial permutation enumeration by local path and
partial-order combinatorics.

## 1. Random priorities instead of permutations

Give every coordinate an independent continuous priority `r_i`.  Almost surely the priorities are
distinct and induce a uniform random total order.  Write `j <_r i` when `r_j<r_i` and define

\[
(L_r)_{ij}=A_{ij}\mathbf 1\{j<_r i\},
\qquad
M_r=I+L_r. \tag{1}
\]

After sorting coordinates by priority, `L_r` is strictly lower triangular.  Hence it is nilpotent and

\[
M_r^{-1}=\sum_{k=0}^{n-1}(-L_r)^k. \tag{2}
\]

No convergence argument is involved.

## 2. Increasing simple-path formula

For a directed path

\[
C=(i_0,i_1,\ldots,i_k),
\]

put

\[
w(C)=\prod_{q=1}^k A_{i_q i_{q-1}},
\qquad |C|=k.
\]

Call it `r`-increasing if

\[
i_0<_r i_1<_r\cdots<_r i_k.
\]

Every increasing path is automatically vertex-simple.  Expanding (2) gives the exact entry formula

\[
\boxed{
(M_r^{-1})_{ab}
=\mathbf1\{a=b\}
 +\sum_{k=1}^{n-1}(-1)^k
  \sum_{C:b\leadsto a,\ |C|=k}
  w(C)\mathbf1\{C\text{ is }r\text{-increasing}\}.
} \tag{3}
\]

Here the inner sum is over vertex-simple paths with the displayed endpoints.

### Proof

The `(a,b)` entry of `L_r^k` is a sum over sequences
`b=i_0,i_1,...,i_k=a`.  A nonzero term requires every adjacent precedence relation
`i_{q-1}<_r i_q`; strict increase forbids repeated vertices.  Its matrix-entry product is exactly
`w(C)`.  Substitution in (2) proves (3). `square`

## 3. Exact first moment without factorial enumeration

For a fixed simple path on `k+1` vertices, exactly one of their `(k+1)!` relative orders makes the
path increasing.  Therefore

\[
\boxed{
\mathbb E[(M_r^{-1})_{ab}]
=\mathbf1\{a=b\}
 +\sum_{k=1}^{n-1}\frac{(-1)^k}{(k+1)!}
  \sum_{C:b\leadsto a,\ |C|=k}w(C).
} \tag{4}
\]

This is a self-avoiding-path analogue of an exponential generating function.  Replacing the simple
paths by unrestricted powers of `A-I` would be incorrect because a repeated vertex cannot satisfy a
strict total-order chain.

## 4. The inverse Gram matrix as a two-path poset sum

The RPCD energy identity uses

\[
X_r^{-1}=M_r^{-\top}M_r^{-1}.
\]

Its `(a,b)` entry is

\[
(X_r^{-1})_{ab}
=\sum_t(M_r^{-1})_{ta}(M_r^{-1})_{tb}. \tag{5}
\]

Choose a path `C:a leadsto t` and a path `D:b leadsto t`, allowing a zero-length path when an
endpoint already equals `t`.  Their directed edges define a finite relation `P(C,D)` on the union of
their vertices.  If this relation has a directed cycle, no total order can realize both paths.  If it
is acyclic, let `e(P)` be its number of linear extensions and `v(P)` its number of vertices.  A uniform
random total order realizes both paths with probability

\[
\frac{e(P(C,D))}{v(P(C,D))!}. \tag{6}
\]

Expanding (5) and taking expectation proves

\[
\boxed{
\mathbb E[(X_r^{-1})_{ab}]
=\sum_t\sum_{C:a\leadsto t}\sum_{D:b\leadsto t}
(-1)^{|C|+|D|}w(C)w(D)
\frac{e(P(C,D))}{v(P(C,D))!},
} \tag{7}
\]

with cyclic unions assigned coefficient zero.

Equation (7) is exact and contains no inverse, eigenvalue, limiting process, or `n!` permutation sum.
For a fixed total path length, its coefficient depends only on a bounded-size poset.

## 5. Quadratic-form / order-polytope representation

For a vector `z`, (3) also yields

\[
z^\top\mathbb E[X_r^{-1}]z
=\mathbb E_r\sum_t
\left(
\sum_{C:\,\operatorname{end}(C)=t}
(-1)^{|C|}w(C)z_{\operatorname{start}(C)}
\mathbf1\{C\text{ increasing}\}
\right)^2. \tag{8}
\]

This makes positivity manifest before paths are expanded.  Since the priorities are independent
uniform variables, the expectation is equivalently an integral over `[0,1]^n`; each product of path
indicators is the indicator of an order polytope whose volume is (6).

Possible inequalities should preferably operate on (8), where cancellations remain inside a square,
rather than termwise on the alternating sum (7).

## 6. Why this may help C001

Combining (7) with

\[
\mathbb E[T_r^\top A T_r]
=A-A\mathbb E[X_r^{-1}]A \tag{9}
\]

turns a one-epoch RPCD bound into a weighted path/poset lower bound.  Three possible continuations are:

1. **Short-union resummation.** Group all pairs of paths whose union has at most `q` vertices and
   retain their square structure.  This is a combinatorial counterpart of the resolvent-moment
   hierarchy, but its coefficients are exact rational numbers.
2. **Structured extremizers.** Show that, under a fixed spectral floor, the grouped path squares are
   minimized by the signed equicorrelation frame.  This would connect directly to route B.
3. **Recursive order polytopes.** Condition on the minimum-priority vertex.  The order-polytope
   integral then gives the same remaining-set Bellman recursion studied in route A.

## 7. Main barrier

The entrywise expansion (7) has alternating signs, so discarding long paths is not a valid Loewner
lower bound.  A useful truncation must be produced at the square/integral level (8), through an SOS
projection, conditional expectation, or an inverse-polynomial minorant.  Bounding individual path
terms by absolute value destroys the factor-of-two improvement sought in C001.

## 8. Concrete next lemma

Find a finite-dimensional subspace `V_q` of path features in (8) such that orthogonal projection of
the full path sum onto `V_q` is computable from posets on at most `q` vertices.  Bessel's inequality
would then give a rigorous lower bound on `E[X_r^{-1}]` while preserving positivity.  The cases
`q=2,3,4` should reproduce bare Jensen, the two-step correction, and the first resolvent correction in
different coordinates.
