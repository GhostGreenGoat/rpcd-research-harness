# Hostile audit: the dimension-three T080 reduction

**Audited artifact:** Section 9 of `docs/ITER4_T080_REVERSE_PAIR_SUBROUTE.md`.

**Audit status (2026-08-21):** no blocker found.  The result is local to \(n=3\); it does not
resolve T080 in arbitrary dimension.  Exact reconstruction is recorded by
`scripts/iter4_t080_n3_hostile_audit.py` and
`research/evidence/ITER4_T080_N3_HOSTILE_AUDIT_2026_08_21.json`.

## 1. Full-Schur criterion: passed

For rank-two \(C\), write
\(\operatorname{adj}C=\gamma uu^\top\), where \(u\) spans \(\ker C\) and \(\gamma>0\).
Since every triangular factor is invertible, \(K_0\succ0\).  The rank-one downdate criterion gives

\[
 K_0-2{uu^\top\over\|u\|^2}\succeq0
 \quad\Longleftrightarrow\quad
 \|u\|^2-2u^\top K_0^{-1}u\ge0.                            \tag{A1}
\]

Multiplication by \(\gamma\det K_0>0\) changes (A1) into

\[
 \operatorname{tr}(\operatorname{adj}C)\det K_0
 -2\operatorname{tr}(\operatorname{adj}C\operatorname{adj}K_0)\ge0. \tag{A2}
\]

Thus the draft uses the full Loewner/Schur condition, not the weaker kernel compression.

## 2. Six-order algebra and invariant reduction: passed

I independently rebuilt all six \(M_\pi^{-\top}M_\pi^{-1}\) matrices over
\(\mathbb Q(a,b,c)\).  The displayed \(K_{11}\) and \(K_{12}\) formulae agree exactly.  If

\[
 \tau=abc,\qquad q=a^2b^2+a^2c^2+b^2c^2,
\]

and \(E\) denotes the left side of (A2), exact polynomial division verifies

\[
 108E-F(q,\tau)\quad\text{is divisible by}\quad
 \det C=1+2abc-a^2-b^2-c^2.                               \tag{A3}
\]

This is stronger than testing rational points: (A3) proves the claimed identity on the whole
singular algebraic hypersurface.  The checker also independently reproduced both endpoint
factorizations and the degree-seven Bernstein expansion.

## 3. Feasible-set endpoint argument: passed

Set \(x=a^2,y=b^2,z=c^2\).  A rank-two correlation matrix gives

\[
 0\le x,y,z\le1,\qquad x+y+z=1+2\tau,\qquad xyz=\tau^2.   \tag{A4}
\]

For fixed \(\tau\), the feasible set is compact and \(F\) is strictly concave as a function of
\(q=xy+xz+yz\), because its quadratic coefficient is \(-2(4-\tau)<0\).  A concave scalar
function takes its minimum over any compact subset of the real line at the minimum or maximum
feasible \(q\).

At an interior stationary point of \(q\) under the two constraints in (A4), subtracting the
Lagrange equations gives

\[
 (x-y)(1-\lambda z)=(y-z)(1-\lambda x)
 =(z-x)(1-\lambda y)=0
\]

for a multiplier \(\lambda\); hence at least two variables are equal.  The case where the two
constraint gradients are dependent also has \(x=y=z\).  A box-boundary extremum either has a
variable equal to one, or has \(\tau=0\) and is a limit of the unit/equal-variable branches.
Therefore the two branches in the proof draft exhaust both feasible endpoints.

If a variable is one, the other two are \(\tau\), \(0\le\tau\le1\), and the exact factorization is

\[
 F=2(1-\tau)(\tau^2-2\tau+3)(\tau^3+\tau^2+3\tau+9)\ge0. \tag{A5}
\]

If two variables equal \(r\), elimination gives either the preceding branch or

\[
 \tau=r(2r-1),\quad q=r^2+2r(2r-1)^2,\quad0\le r\le1.     \tag{A6}
\]

On (A6), the remaining factors are nonnegative and the last degree-seven polynomial has the
strictly positive Bernstein coefficients

\[
 9,{104\over7},{106\over7},{92\over7},{323\over35},{50\over7},{38\over7},6.
\]

This proves positivity on that branch.  The \(\tau=0\) degeneracies are included at
\((1,0,0)\) and \((1/2,1/2,0)\), up to permutation.

## 4. Rank and boundary coverage: passed

- Rank two is covered by (A1)--(A6), including negative \(\tau\) (the equal-variable branch reaches
  the regular-simplex value \(\tau=-1/8\)).
- Rank one is separately sign-conjugate to \(J_3\), for which
  \(K_0=2P_{\ker C}+I/3\) exactly.
- Rank zero is impossible under \(C_{ii}=1\).

Hence arbitrary nullity/rank is covered for \(n=3\).

## 5. Findings

| Severity | Finding | Disposition |
|---|---|---|
| blocker | none | The checked \(n=3\) proof closes. |
| nonblocker | No Lean/formal proof is present. | Exact symbolic reconstruction exists; formalization remains optional follow-up. |
| nonblocker | The quotient in (A3) is large. | Divisibility is checked exactly; the proof only needs its zero remainder. |
| scope | Nothing here controls \(n\ge4\). | General T080 remains open. |

Under the repository evidence ladder, this supports the label **hostile-audited local theorem
candidate (E4)** for \(n=3\), not a theorem claim for general dimension.
