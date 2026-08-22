# Hostile audit: half-depth certificate on the signed-rank-one interior family

**Audited source:** `research/iteration4/t085/structured_asymptotics.md`, Section 4.

**Claim:** for \(n\ge2\),
\(A_n(\mu)=\mu I+(1-\mu)J_n\), \(0<\mu\le1\), and
\(r=\lceil n/2\rceil\),

\[
 H_r(A_n)\succeq {\mu\over2}A_n^{-1}.                    \tag{H1}
\]

Here \(H_r\) is the determinant-tail Bellman hierarchy: reveal \(r\) exact triangular-solve
coordinates, then apply \(\det(B)B^{-1}\) to the remaining principal problem.

**Outcome:** PASS for this family only.  The prefix/leaf interpretation, both invariant blocks,
and every normalization factor reconstruct exactly.  No extension to general matrices follows.

## 1. Transverse block

Take \(u=e_i-e_j\), \(\|u\|^2=2\).  Before either special coordinate appears in a prefix, all
solves are zero.  The first special solve is \(\pm1\).  If \(\ell\) ordinary coordinates occur
before the second special coordinate, the accumulated sum is \(\pm\mu^\ell\), so the second solve
is

\[
 \mp[1+(1-\mu)\mu^\ell],
\]

whose squared magnitude is at least one.  The determinant leaf is PSD.  Thus each path contributes
at least the number of special coordinates selected in the prefix.  A uniform \(r\)-prefix selects
an expected \(2r/n\) specials, hence the transverse eigenvalue of \(H_r\) obeys

\[
 h_\perp\ge {2r/n\over2}={r\over n}\ge{1\over2}.          \tag{H2}
\]

Since the transverse eigenvalue of \(A_n\) is \(\mu\), (H2) is exactly (H1) on
\(\mathbf1^\perp\).  The solve sign and the factor \(\|u\|^2=2\) are both essential and were
checked explicitly.

## 2. Parallel block and Bellman normalization

At a local size \(k\), let \(p_k\) be the parallel eigenvalue and put \(q_k=kp_k\).  For the
parallel right side, the first solve is one and the child right side is \(\mu\mathbf1_{k-1}\).
The Bellman average therefore gives exactly

\[
 p_k={1\over k}+{(k-1)\mu^2\over k}p_{k-1},
 \qquad q_k=1+\mu^2q_{k-1}.                              \tag{H3}
\]

The factor \((k-1)/k\) in the first form is the child parallel norm divided by the parent norm;
it is not an extra probability.  At the leaf size \(d=n-r\),
\(\det(A_d)A_d^{-1}\) has parallel eigenvalue \(\mu^{d-1}\), so

\[
 q_d=d\mu^{d-1}\ge0,
 \qquad q_n=S_r+\mu^{2r}q_d\ge S_r,
 \quad S_r=\sum_{j=0}^{r-1}\mu^{2j}.                     \tag{H4}
\]

Let \(L=n-(n-1)\mu\) be the parallel eigenvalue of \(A_n\), and \(z=\mu^{2r}\).  Then

\[
 {L\over n\mu}S_r={S_r\over n}+{1-z\over\mu(1+\mu)}.
\]

Because \(r/n\ge1/2\) and
\(S_r\ge r\mu^{2r-2}\),

\[
 {L\over n\mu}S_r
 \ge {1\over\mu(1+\mu)}
 +{z(1-\mu)\over2\mu^2(1+\mu)}
 \ge{1\over2}.                                          \tag{H5}
\]

At \(\mu=1\) the same conclusion follows by continuity (indeed \(S_r=r\)).  Since
\(p_n=q_n/n\), (H4)--(H5) give \(Lp_n\ge\mu/2\), which is (H1) on the parallel line.

## 3. Loewner conclusion and scope

Permutation invariance makes \(H_r(A_n)\) scalar on the two orthogonal irreducible spaces
\(\mathbf1^\perp\) and \(\operatorname{span}\{\mathbf1\}\).  Sections 1--2 cover both, so the
Loewner inequality (H1) follows.

- This is an exact all-\(n\), all-\(\mu\) result for the signed-rank-one interior family.
- The omitted \(n=1\) case is immediate from \(A=H=K=[1]\).
- It is consistent with, and asymptotically sharp against, the separate result that no global
  one-epoch constant greater than \(1/2\) is possible.
- It does not prove the half-depth inequality for a general correlation matrix or even a general
  exchangeable block union.
- The source proof and this different-run reconstruction support E4 hostile-audited family status;
  there is no Lean/E6 certificate.
