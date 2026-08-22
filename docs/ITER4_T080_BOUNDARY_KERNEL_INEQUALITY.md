# Iteration 4 / T080: singular-boundary kernel inequality

**Final status of the universal target:** **refuted by an exact rational (n=8)
counterexample** in Checkpoint 5 below.  The earlier checkpoints are retained chronologically so
that the successful local results and the precise failures of the attempted proof routes remain
auditable.  Unless explicitly labelled otherwise, exact algebra below is `E3 proof-draft`;
floating-point experiments are only `E1 numerical evidence`.  The original target was

\[
 K_0(C):={\mathbb E}_{\pi}\,M_\pi(C)^{-\top}M_\pi(C)^{-1}
 \succeq 2P_{\ker C}                                           \tag{T080}
\]

for every singular correlation matrix \(C\succeq0\), \(C_{ii}=1\).  Here the entries of
\(M_\pi\) on and below the order \(\pi\) are those of \(C\).  This is the full-space statement;
it is equivalent to the Schur-complement inequality on \(\ker C\), and is strictly stronger than
merely compressing \(K_0\) to the kernel.

## Checkpoint 1 — 2026-08-21 17:47 +08:00

### 1. Exact signed-rank-one calculation and sharpness

If \(C=ss^\top\), conjugating by \(\operatorname{Diag}(s)\) reduces to \(C={\bf1}{\bf1}^\top\).
In permutation coordinates, \(M_\pi\) is the lower all-ones matrix, and

\[
 \|M_\pi^{-1}z\|^2
 =z_{\pi_1}^2+\sum_{k=2}^n(z_{\pi_k}-z_{\pi_{k-1}})^2.        \tag{1}
\]

Every coordinate is first with probability \(1/n\), while every unordered pair is an adjacent
pair with probability \(2/n\).  Averaging (1) gives

\[
 K_0({\bf1}{\bf1}^\top)=2P_{{\bf1}^\perp}+{1\over n}I.       \tag{2}
\]

Thus (T080) holds for every signed rank-one correlation matrix.  Equation (2) also proves that a
dimension-independent constant larger than \(2\) is impossible: its kernel eigenvalue is
\(2+1/n\downarrow2\).

### 2. Reverse pairing is exact but not by itself coercive enough

For every order, reversing it transposes the triangular factor:

\[
 M_{\operatorname{rev}\pi}=M_\pi^\top .                     \tag{3}
\]

Consequently one reverse pair contributes

\[
 {1\over2}\big(M^{-\top}M^{-1}+M^{-1}M^{-\top}\big).        \tag{4}
\]

The hoped-for pairwise inequality (4) \(\succeq2P_{\ker C}\) is false.  It already fails after
compression to \({\bf1}^{\perp}\) for \(C={\bf1}{\bf1}^\top\), \(n=3\): for the natural order,
the two nonzero compressed eigenvalues of (4) are \(3/2\) and \(19/6\).  (The exact finite witness
and the stronger full-space failure will be recorded in the deterministic checker.)  Fixed cyclic
orbits of orders fail for the same reason.  Hence a proof must use cancellations across more than
one reverse pair.

### 3. Fixed-order variational relaxation loses the required constant

Write \(\mathcal N=\ker C\), \(\mathcal R=\mathcal N^\perp\), and
\(S_\pi=M_\pi-M_\pi^\top\).  Since
\(C=M_\pi+M_\pi^\top-I\),

\[
 P_{\mathcal N}M_\pi={1\over2}P_{\mathcal N}(I+S_\pi).
\]

For a fixed order, minimizing \(\|a\|^2\) subject to
\(P_{\mathcal N}M_\pi a=x\in\mathcal N\) gives the exact value

\[
 4\,x^\top\big[I_{\mathcal N}-P_{\mathcal N}S_\pi^2P_{\mathcal N}
                  \big]^{-1}x.                              \tag{5}
\]

Replacing the common range correction in the Schur complement by an independently optimized
correction for every \(\pi\) yields the average of (5), which is a valid lower relaxation but can be
strictly below \(2\|x\|^2\).  The missing strength is precisely the requirement that all orders use
the same vector \(z=x+y\), \(y\in\mathcal R\).

### 4. Two scalar/global shortcuts that do not close

Operator Jensen gives \(K_0^{-1}\preceq {\mathbb E}[M_\pi M_\pi^\top]\).  The known exact moment
formula reduces on \(\mathcal N\) to

\[
 P_{\mathcal N}{\mathbb E}[M_\pi M_\pi^\top]P_{\mathcal N}
 ={1\over3}P_{\mathcal N}+{1\over6}P_{\mathcal N}DP_{\mathcal N},
 \quad D=\operatorname{Diag}(\operatorname{diag}(C-I)^2).   \tag{6}
\]

The sufficient estimate \(P_{\mathcal N}DP_{\mathcal N}\preceq P_{\mathcal N}\) is false; for
the rank-one family its kernel eigenvalue is \(n-1\).  Also, inserting only child kernel
projections in the remaining-set Bellman recursion loses the directions removed by a deletion and
falls far short of (T080).  Both failures point toward an anisotropic certificate retaining child
range information.

### 5. Active route: determinant tails and basis/circuit averaging

Let \(C=V^\top V\) have rank \(r\).  For every basis \(S\),
\(\det C_S=\det(V_S)^2\), and Cauchy--Binet gives

\[
 \sum_{|S|=r}\det C_S=\det(VV^\top).                        \tag{7}
\]

The present question is whether the determinant-tail certificate, averaged over the random last
basis and its fundamental circuits, supplies exactly the kernel directions discarded by projector
induction.  No general inequality has yet been obtained.  The next checkpoint will either state a
closed matrix identity for this average or record the precise obstruction.

## Evidence boundary at checkpoint 1

- (1)--(4), (6), and (7) are exact algebra/combinatorics.
- The rank-one formula (2) is a complete proof for that family only.
- Failures of larger order-group relaxations outside the displayed exact \(n=3\) witness are
  exploratory until entered in a deterministic artifact.
- The general statement (T080) remains open at this checkpoint.

## Checkpoint 2 — 2026-08-21 18:17 +08:00

### 6. Volume-sampled circuit frame, and a hostile-audit correction

The basis/circuit route gives a clean general identity.  Let \(V\in\mathbb R^{r\times n}\) have
full row rank, \(C=V^\top V\), \(F=VV^\top\), and \(P=I-V^\top F^{-1}V=P_{\ker C}\).  For each
basis \(S\subset[n]\), \(|S|=r\), write \(E_S:\mathbb R^r\to\mathbb R^n\) for coordinate
insertion and define

\[
 w_S=\det(V_S)^2,
 \qquad
 G_S=I-E_SV_S^{-1}V.                                      \tag{8}
\]

For every nonsingular basis, \(G_S\) is the oblique projection onto \(\ker V\) along the coordinate
basis \(S\).  Under volume sampling \(\Pr(S)=w_S/\det F\), the first-moment identity is always
valid:

\[
 \boxed{\mathbb E_{\rm vol}G_S=P.}                         \tag{9}
\]

Here is a derivation.  Differentiating Cauchy--Binet
\(\sum_S\det(V_S)^2=\det(VV^\top)\) with respect to \(V\) gives

\[
 {1\over\det F}\sum_Sw_SE_SV_S^{-1}=V^\top F^{-1},
\]

which proves (9).  For the second moment, whiten \(U=F^{-1/2}V\), so
\(UU^\top=I_r\) and \(R:=U^\top U=I-P\) is a rank-\(r\) orthogonal projector.  The only remaining
quadratic term from the **nonsingular** bases is

\[
 Q_{\rm basis}=\sum_{\det U_S\ne0}
 \det(U_S)^2E_SU_S^{-1}U_S^{-\top}E_S^\top.
\]

My initial derivation incorrectly identified this restricted sum with all of \(\nabla e_r(R)\).
A different-run hostile audit found the missing boundary term.  Define

\[
 H_{\rm sing}:=\sum_{\substack{|S|=r\\\det U_S=0}}
 E_S\operatorname{adj}(R_{SS})E_S^\top\succeq0.            \tag{10}
\]

Only subsets of rank \(r-1\) contribute; each contribution is supported in \(\ker U\), so
\(H_{\rm sing}=PH_{\rm sing}P\).  Since
\(\nabla e_r(R)=(I-P)+rP\), the corrected identities are

\[
 \boxed{
 Q_{\rm basis}=(I-P)+rP-H_{\rm sing},\qquad
 \mathbb E_{\rm vol}G_SG_S^\top=(r+1)P-H_{\rm sing}.
 }                                                         \tag{11}
\]

Thus the simpler tight-frame identity holds in general position, when every \(r\)-subset is a
basis.  In general the exact target decomposition is instead

\[
 2P={2\over r+1}
 \left(\mathbb E_{\rm vol}G_SG_S^\top+H_{\rm sing}\right). \tag{12}
\]

The correction is not cosmetic: a zero-volume basis has no random circuit \(G_S\), while its
adjugate can remain nonzero after the two inverse factors cancel the vanishing determinant.  For
example, \(r=1,n=2,U=(1,0)\) has only one positive-weight basis and
\(\mathbb E GG^\top=P\), not \(2P\).  (Correlation columns are nonzero, so this particular toy is
only a diagnostic; repeated/dependent columns give the same issue for \(r\ge2\).)

Equations (9)--(12) remain a useful anisotropic target, but now a proof must also realize or bound
the ghost-circuit correction \(H_{\rm sing}\).  Exact rational general-position instances and the
degenerate unit-column example \(V=((1,1,0),(0,0,1))\) are checked in
`research/evidence/ITER4_T080_EXACT_DIAGNOSTICS_2026_08_21.json`.

### 7. A universal but nonadditive floor

For every (singular or nonsingular) correlation matrix,

\[
 \boxed{K_0(C)\succeq {1\over n}I.}                        \tag{13}
\]

Indeed the first coordinate visited by a permutation satisfies
\((M_\pi^{-1}z)_{\pi_1}=z_{\pi_1}\).  Dropping all other squared components and averaging the
uniform first coordinate proves (11).  Equality on the range direction of \(J_n\) shows that the
constant is sharp.  This residual cannot simply be added to a separate kernel-compression bound;
Loewner lower bounds combine only by convex combination, and the kernel--range Schur coupling is
exactly the part that T080 must retain.

### 8. A second exact all-dimension family

For the regular-simplex correlation

\[
 C={n\over n-1}I-{1\over n-1}J,
 \qquad \ker C=\operatorname{span}\{\mathbf1\},
\]

forward substitution in any order gives

\[
 M_\pi^{-1}\mathbf1=(1,q,q^2,\ldots,q^{n-1})^\top,
 \qquad q={n\over n-1}.
\]

Permutation symmetry removes the Schur coupling, and the kernel eigenvalue is

\[
 \beta_n={1\over n}\sum_{k=0}^{n-1}q^{2k}>2.              \tag{14}
\]

The strict inequality follows by retaining the first two binomial terms: their average is exactly
\(2\), while a positive second-order term remains.  In contrast to signed rank one,
\(\beta_n\to(e^2-1)/2\), so this family is not asymptotically sharp.

### 9. Independently audited local closure at \(n=3\)

A separate reverse-pair subroute reduced every rank-two \(3\times3\) correlation to two signed
permutation invariants and proved nonnegativity by concavity plus endpoint factorizations.  I
independently reconstructed its six-order algebra, verified exact divisibility on the singular
hypersurface, and audited the feasible-set endpoint classification.  No blocker was found.  The
details are in `docs/ITER4_T080_N3_HOSTILE_AUDIT.md`; the exact checker is
`scripts/iter4_t080_n3_hostile_audit.py`.

The proper status is **E4 hostile-audited local proof candidate:** T080 holds for every singular
\(3\times3\) correlation matrix, including rank one and rank two.  This does not cover \(n\ge4\).

### 10. Hostile test of the fixed length-three Bessel certificate

Let \(\mathcal V_q\) be the scalar feature space on permutations spanned by the constant and all
oriented consecutive blocks of lengths \(2,\ldots,q\).  If \(\Pi_q\) is the orthogonal projection
onto \(\mathcal V_q\) and \(\mathcal Bz=(M_\pi^{-1}z)_\pi\), then

\[
 K_q=\mathcal B^\ast\Pi_q\mathcal B,
 \qquad 0\preceq K_2\preceq K_3\preceq\cdots\preceq K_n=K_0. \tag{15}
\]

Thus \(K_3\succeq2P\) would prove T080.  My first attack at \(n=9\), where full permutation
enumeration is still possible, used high-nullity block matrices and low-rank Gram matrices.  The
smallest float64 projected margin was

\[
 \lambda_{\min}(K_3-2P)\approx0.0167880
\]

for the two-pole ring at latitude \(0.88\); its exact-\(K_0\) margin was about \(0.0426797\).
Block families \(J_5\oplus J_4\), \(J_7\oplus J_2\), and
\(J_3\oplus J_3\oplus J_3\) also remained positive.  These E1 results are stored in
`research/evidence/ITER4_T080_Q3_ATTACK_N9_2026_08_21.json`.

A subsequent \(n=10\) cross-fit search from the root route found the two-pole ring at latitude
\(0.78\) below zero in two independent runs:

\[
 -0.00812527\quad(400{,}000\text{ orders}),\qquad
 -0.00828123\quad(600{,}000\text{ orders}),                \tag{16}
\]

while the sampled exact-\(K_0\) margins were about \(+0.0582\).  The artifacts are
`ITER4_BLOCK3_BESSEL_N10_CROSSFIT_400K_A.json` and
`ITER4_BLOCK3_BESSEL_N10_CROSSFIT_600K_B.json`.  Equation (16) is strong replicated E1 evidence,
not an exact counterexample; nevertheless fixed \(q=3\) is no longer a viable universal proof
candidate unless an exact reconstruction overturns the estimator.

## Evidence boundary at checkpoint 2

- (8)--(13) now include the hostile-audit correction for singular bases.  The original unqualified
  second-moment claim was blocked and has been withdrawn; the corrected identity has a derivation
  and a finite exact degenerate-correlation check.
- The \(n=3\) result has a different-run proof and hostile audit, but no Lean/formal certificate.
- The positive \(q=3\), \(n=9\) results and negative replicated \(n=10\) cross-fit candidate are E1
  only.  They point away from any universal fixed-\(q=3\) certificate.
- General T080, arbitrary rank/nullity/dimension, remains open.

## Checkpoint 3 — 2026-08-21 18:30 +08:00

### 11. The sharp \(n=3\) constant is \(7/3\) (E4 local candidate)

The audited \(n=3\) invariant argument can be strengthened all the way to the rank-one value.  For
rank-two \(C\), let \(A_C=\operatorname{adj}C=\gamma uu^\top\), and for a proposed constant
\(\alpha\) define the full-Schur rank-one-downdate numerator

\[
 E_\alpha:=\operatorname{tr}(A_C)\det K_0
 -\alpha\operatorname{tr}(A_C\operatorname{adj}K_0).       \tag{17}
\]

Because \(\gamma\det K_0>0\), \(E_\alpha\ge0\) is equivalent to
\(K_0\succeq\alpha P_{\ker C}\); this is again the full Schur condition.

Put \(\tau=abc\) and \(q=a^2b^2+a^2c^2+b^2c^2\).  An independent six-order exact reduction gives,
on \(\det C=0\),

\[
 324E_{7/3}=3G(q,\tau),                                   \tag{18}
\]

where

\[
\begin{aligned}
G={}&(2\tau-9)q^2
 +(-2\tau^4+5\tau^3+37\tau+51)q\\
 &+\tau^5-15\tau^4-13\tau^3-51\tau^2-150\tau+18.
\end{aligned}                                              \tag{19}
\]

Since \(\tau\le1\), the coefficient \(2\tau-9\) is strictly negative.  Therefore the same compact
feasible-set classification used in the audited \(\alpha=2\) proof reduces the minimum to its two
endpoint branches.

If one squared correlation is one, \(q=\tau^2+2\tau\), \(0\le\tau\le1\), and

\[
 324E_{7/3}
 =6(1-\tau)^3(\tau^3+\tau^2+3\tau+9)\ge0.                \tag{20}
\]

If two squared correlations equal \(r\), use
\(\tau=r(2r-1)\), \(q=r^2+2r(2r-1)^2\), \(0\le r\le1\).  Then

\[
 324E_{7/3}
 =6(1-r)^3(4r^3+5r^2+2r+3)P_5(r),                       \tag{21}
\]

with

\[
 P_5(r)=32r^5-40r^4+20r^3-30r^2+49r+3.
\]

Its degree-five Bernstein coefficients on \([0,1]\) are

\[
 3,{64\over5},{98\over5},{127\over5},{121\over5},34,
\]

all strictly positive.  Thus (20)--(21) are nonnegative.  They vanish only at the rank-one endpoint
\(r=\tau=1\).  Rank-one matrices are sign-conjugate to \(J_3\), for which (2) gives the exact
kernel eigenvalue \(7/3\).  Consequently the proof draft establishes

\[
 \boxed{K_0(C)\succeq{7\over3}P_{\ker C}
 \quad\text{for every singular }3\times3\text{ correlation }C,} \tag{22}
\]

and \(7/3\) is sharp.  The symbolic generator and exact artifact are
`scripts/iter4_t080_n3_sharp_invariants.py` and
`research/evidence/ITER4_T080_N3_SHARP_7_OVER_3_2026_08_21.json`.

A different run subsequently hostile-audited the new scaling, full-Schur downdate, invariant
substitution, endpoint exhaustion (including \(\tau\le0\)), both factorizations, and the Bernstein
reconstruction.  It found no blocker.  Thus (22) is an **E4 hostile-audited local sharp theorem
candidate**.  It has not been formalized or independently promoted for general \(n\).

### 12. Fixed-ray low-\(\mu\) consequence, and its quantifier limit

For every fixed singular \(3\times3\) correlation \(C\), the audited block perturbation formula
gives

\[
 r_E(\mu I+(1-\mu)C)
 =1-\mu\lambda_{\min}(S_C)+o_C(\mu).                      \tag{23}
\]

Equation (22) gives \(\lambda_{\min}(S_C)\ge7/3\), whereas the conjectured low-gap rate is
\((1-\mu/3)^6=1-2\mu+O(\mu^2)\).  The strict \(1/3\) first-order margin implies: for each fixed
boundary ray \(C\), there exists \(\mu_0(C)>0\) such that the strong one-epoch energy inequality
holds for \(0<\mu<\mu_0(C)\).  Along that ray this yields the desired
\(O(\mu^{-1}\log(1/\varepsilon))\) epoch scale (and \(n=3\) is fixed).

This is not yet a uniform compact-neighborhood theorem.  A sequence \(C_k\) can approach a lower
rank stratum on the same scale as \(\mu_k\), and (23) has not been proved with a remainder uniform
over that two-scale degeneration.  No global finite-\(\mu\), all-\(C\) claim is made here.

## Evidence boundary at checkpoint 3

- The \(7/3\) statement is an exact E4 hostile-audited local sharp proof candidate with an E2
  symbolic artifact; it has no Lean/formal certificate.
- The fixed-ray corollary uses the already audited perturbation reduction, but its radius depends on
  \(C\).
- General dimension T080 and the uniform finite-time RPCD bound remain open.

## Checkpoint 4 — 2026-08-21 18:50 +08:00

### 13. An \(n=4\) nullity-one symmetric family closes

Suppose a rank-three \(4\times4\) correlation matrix has two identical Gram columns \(p,q\).
Then \(u=e_p-e_q\) spans its kernel.  The transposition \(p\leftrightarrow q\) fixes \(C\), hence
also fixes the permutation average \(K_0(C)\); its odd line \(\operatorname{span}\{u\}\) is therefore
a reducing subspace.  It is enough to prove

\[
 u^\top K_0(C)u\ge4=2\|u\|^2.                             \tag{24}
\]

The remaining-set Bellman recursion gives an exact induction.  If an ordinary coordinate is first,
the child retains the duplicate null vector.  If \(p\) or \(q\) is first, the immediate cost is one
and the child right side is, up to sign,

\[
 z=(I+B)e_i,                                               \tag{25}
\]

where \(B\) is the child correlation and \(i\) is the remaining copy.  Thus the induction closes
whenever

\[
 z^\top K_0(B)z\ge3.                                      \tag{26}
\]

A separate run proved (26) for child sizes at most three.  I independently reconstructed the
certificate: for size two the value is
\(4-r^2+r^4/2\ge7/2\); for size three, completing the square in the third correlation leaves a
bicubic on \([0,1]^2\) whose sixteen Bernstein coefficients are all nonnegative.  The exact audit is
`scripts/iter4_t080_duplicate_child_audit.py`.

Consequently (24), and hence T080, holds for every rank-three \(n=4\) correlation with an identical
pair.  An antipodal pair reduces to this case by a diagonal sign conjugation.  This is a local
nullity-one symmetric-family result, not all of \(n=4\).

### 14. The tempting all-dimension duplicate induction is exactly false

The child lemma (26) does not extend to arbitrary size.  Let

\[
B=\begin{pmatrix}
1&1&4/5&4/5&4/5\\
1&1&4/5&4/5&4/5\\
4/5&4/5&1&23/50&23/50\\
4/5&4/5&23/50&1&23/50\\
4/5&4/5&23/50&23/50&1
\end{pmatrix},
\qquad z=(I+B)e_1=(2,1,4/5,4/5,4/5)^\top.                \tag{27}
\]

This is the Gram matrix of two repeated poles and a latitude-\(4/5\) triangle.  Its eigenvalues are

\[
 98/25,\quad27/50,\quad27/50,\quad0,\quad0,
\]

so it is a valid singular correlation matrix.  Two independent exact enumerations of all
\(5!=120\) orders give

\[
 z^\top K_0(B)z
 ={7204453277\over2441406250}
 =3-{119765473\over2441406250}
 \approx2.9509440623<3.                                  \tag{28}
\]

Thus (26) is refuted as a general lemma, not merely numerically suspect.  This kills the proposed
all-dimension duplicate-vector induction.  It does **not** refute T080, and it does not affect the
proved child-size-\(\le3\) argument for the \(n=4\) family.  The exact matrix, characteristic
polynomial, and rational gap are stored in
`research/evidence/ITER4_T080_DUPLICATE_CHILD_M3_AUDIT_2026_08_21.json`.

## Evidence boundary at checkpoint 4

- The \(n=4\) duplicate/antipodal nullity-one family is supported by a different-run proof and an
  independent exact reconstruction of its child lemma through size three.
- The general duplicate child lemma is exactly refuted by (27)--(28).
- Neither result decides T080 for generic \(n=4\) or for arbitrary dimension.

## Checkpoint 5 — 2026-08-21 18:49 +08:00

### 15. A second surviving \(n=4\) corank-one family

One additional local calculation survives the general counterexample below.  Let the first three
coordinates be exchangeable with common correlation

\[
 a={3b^2-1\over2},
\]

and let their common correlation with coordinate four be \(b\), where \(|b|<1\).  The first-three
difference space has eigenvalue \(3(1-b^2)/2\) (multiplicity two), while the group-constant
two-dimensional block has eigenvalues zero and \(1+3b^2\).  Hence this is a rank-three correlation
matrix with null vector

\[
 u_b=(1,1,1,-3b)^\top .                                  \tag{29}
\]

The exact 24-order average gives the full-Schur coefficient

\[
 s_b={\|u_b\|^2\over u_b^\top K_0(C)^{-1}u_b}.
\]

After putting \(s=b^2\), the numerator and denominator of \(s_b-2\) have strictly positive
Bernstein coefficients on \([0,1]\).  Thus \(s_b>2\) for \(|b|<1\); the endpoint values are
\(s_0=133/48\) and \(s_b\to9/4\) as \(|b|\to1\).  A different run checked the PSD decomposition,
the lower-in-order convention, the full-Schur orientation, both endpoint values, and both
Bernstein reconstructions without finding a blocker.  The exact artifact is
`research/evidence/ITER4_T080_N4_S3_CORANK_ONE_2026_08_21.json`.  This is an E4 local-family
candidate only.

### 16. Exact \(n=8\) counterexample: T080 is false

Let \(C\in\mathbb Q^{8\times8}\) have two pole coordinates and six ring coordinates:

\[
 \boxed{
 C=\begin{pmatrix}
 J_2 & \frac23\mathbf1_2\mathbf1_6^\top\\[2mm]
 \frac23\mathbf1_6\mathbf1_2^\top &
 \frac23 I_6+\frac13J_6
 \end{pmatrix}.}                                         \tag{30}
\]

Thus the two poles are identical, every pole--ring correlation is \(2/3\), and every distinct
ring--ring correlation is \(1/3\).  This is a correlation matrix.  For example, take a unit vector
\(p\), six regular-simplex vertices \(r_j\in p^\perp\),
\(r_j^\top r_k=-1/5\) for \(j\ne k\), and Gram vectors

\[
 p,\ p,\quad w_j={2\over3}p+{\sqrt5\over3}r_j .           \tag{31}
\]

The invariant-subspace decomposition gives the exact spectrum

\[
 \operatorname{spec}(C)
 =\{0^{(2)},(2/3)^{(5)},14/3\},                           \tag{32}
\]

and an orthogonal basis of its kernel is

\[
 u=(1,-1,0,0,0,0,0,0)^\top,
 \qquad
 v=(-2,-2,1,1,1,1,1,1)^\top.                            \tag{33}
\]

For clarity about orientation, if \(\pi=(\pi_1,\ldots,\pi_8)\), then \(M_\pi\) is the
unit-diagonal lower-in-order factor and \(y=M_\pi^{-1}u\) is computed by

\[
 y_{\pi_k}=u_{\pi_k}
 -\sum_{\ell<k}C_{\pi_k\pi_\ell}y_{\pi_\ell}.            \tag{34}
\]

Consequently \(\sum_k y_{\pi_k}^2=u^\top M_\pi^{-\top}M_\pi^{-1}u\), with no transpose
ambiguity.  The six ring labels are exchangeable.  It is therefore enough to enumerate the
ordered positions of the labelled positive and negative poles: there are

\[
 8\cdot7=56
\]

category words, each representing exactly \(6!=720\) labelled orders, and
\(56\cdot720=8!\).  Maintaining the sums \(s_p,s_r\) of previously solved pole and ring values
gives the exact updates

\[
 \begin{array}{c|c}
 +&1-s_p-\frac23s_r\\
 -&-1-s_p-\frac23s_r\\
 R&-\frac23s_p-\frac13s_r.
 \end{array}                                               \tag{35}
\]

Fraction arithmetic over these 56 states gives

\[
 {u^\top K_0(C)u\over\|u\|^2}
 ={1057837\over531441}
 =1.990506942445\ldots
 =2-{5045\over531441}.                                   \tag{36}
\]

An independent generic forward solve over all \(40320\) labelled permutations gives exactly the
same fraction and checks \(M_\pi y=u\) coordinate by coordinate.  A second closed finite check is
also available: if \(m\) and \(\ell\) are the numbers of rings between and after the two poles,
then with \(q=2/3\)

\[
 E_{m,\ell}=1+{4\over5}(1-q^{2m})
 +{4\over9}(1+2q^m)^2
 +{4\over45}(2+q^m)^2(1-q^{2\ell}),                      \tag{37}
\]

and

\[
 {1\over28}\sum_{m=0}^6\sum_{\ell=0}^{6-m}E_{m,\ell}
 ={2115674\over531441}=u^\top K_0(C)u.                   \tag{38}
\]

Since \(Pu=u\) and \(\|u\|^2=2\), (36) yields the exact strict violation

\[
 \boxed{
 u^\top(K_0(C)-2P_{\ker C})u
 =-{10090\over531441}<0.}                                \tag{39}
\]

Swapping the two poles fixes \(C\) and the uniform permutation average.  The odd subspace of that
swap is exactly \(\operatorname{span}\{u\}\), so \(u\) is a reducing eigenvector of \(K_0(C)\).
Thus its kernel compression is also its full-Schur coefficient: the violation cannot be repaired
by hidden kernel--range coupling.

The deterministic checker
`scripts/iter4_t080_exact_counterexample.py` implements both the 56-class recurrence and the
generic \(8!\) enumeration in exact `Fraction` arithmetic.  Its record is
`research/evidence/ITER4_T080_EXACT_COUNTEREXAMPLE_N8_2026_08_21.json`.  A different run first
derived (30)--(38), and the displayed reconstruction independently recovered the same matrix,
spectrum, convention, multiplicities, and rational gap.  A third verifier,
`scripts/verify_iter4_t080_simple_subset_dp.py`, avoids both category classes and permutation
enumeration: it reconstructs the full \(8\times8\) matrix \(K_0\) by an exact \(2^8\) first-pivot
Bellman recursion and checks
\(K_0u=(1057837/531441)u\).  Its audit and record are
`docs/ITER4_AUDIT_T080_SIMPLE_SUBSET_DP.md` and
`research/evidence/ITER4_T080_SIMPLE_SUBSET_DP_INDEPENDENT_AUDIT.json`.  This therefore meets the
internal gate for an exact independently reconstructed refutation of T080; it is not merely a
floating-point counterexample candidate.

### 17. Exact positive-definite lift refutes the strong one-epoch M1 certificate

The boundary failure persists at an explicit positive gap.  Set

\[
 \mu={1\over100},\qquad A_\mu=\mu I+(1-\mu)C.             \tag{40}
\]

Its off-diagonal pole--pole, pole--ring, and distinct ring entries are respectively
\(99/100,33/50,33/100\), and

\[
 \operatorname{spec}(A_\mu)
 =\{(1/100)^{(2)},(67/100)^{(5)},463/100\},               \tag{41}
\]

so it is an exact rational positive-definite correlation matrix with
\(\lambda_{\min}(A_\mu)=\mu\).

Pole-swap symmetry still makes \(u\) a reducing vector and \(A_\mu u=\mu u\).  The same two exact
enumerations give

\[
 \kappa_\mu:={u^\top K(A_\mu)u\over\|u\|^2}
 ={277091954946975183681661134197
   \over140000000000000000000000000000}
 =1.979228249621\ldots .                                  \tag{42}
\]

The one-epoch energy identity

\[
 A-\mathbb E(T_\pi^\top A T_\pi)=A K(A)A                \tag{43}
\]

therefore gives the witnessed expected \(A\)-energy ratio exactly as
\(1-\mu\kappa_\mu\).  For \(n=8\), the active proposed M1 target is

\[
 q_\mu=(1-\mu/8)^{16}=(799/800)^{16}>(7/8)^8.
\]

Exact integer comparison gives

\[
 (1-\mu\kappa_\mu)-q_\mu
 ={4198136398771974389711477950466919707327993
 \over197032483697459200000000000000000000000000000000}
 >0,                                                       \tag{44}
\]

approximately \(2.13068\times10^{-5}\).  Hence the strong fixed-\(A\), one-epoch energy bound M1
with this exact \(q_\mu\) is false, not just its singular limiting lemma.  The exact checker and
record are `scripts/iter4_t080_positive_mu_lift.py` and
`research/evidence/ITER4_T080_POSITIVE_MU_EXACT_LIFT_2026_08_21.json`.

### 18. What this does and does not settle

The exact counterexample settles the logical status of the Iteration-4 route:

- universal T080 is **refuted**;
- the proposed strong one-epoch fixed \(A\)-energy certificate M1, with the displayed sharp target
  \(q_\mu\), is also **refuted**;
- the sharp \(n=3\) result, the two \(n=4\) symmetric-family results, and the exact rank-one and
  regular-simplex calculations remain valid local results;
- none of this refutes the original covariance second-moment spectral conjecture C001, nor the
  desired finite-time complexity \(O((n/\mu)\log(1/\varepsilon))\).  M1/T080 was a sufficient
  certificate route, not a proved necessary condition.  Adapted Lyapunov metrics, covariance-map
  cancellations across epochs, or a weaker boundary constant could still yield the target
  asymptotic complexity.

In particular, replacing the coefficient \(2\) in (T080) by the witnessed
\(1057837/531441\) would not change a big-\(O\) complexity by itself.  The new obstruction is to
find a positive **dimension-uniform** lower coefficient, or to bypass this fixed-energy boundary
inequality entirely.

### 19. Stronger post-mortem: no universal constant above \(3/2\)

The same geometry yields an exact all-dimensional family.  Fix \(k\ge2\) and \(0<a<1\), take two
copies of a pole \(p\), and take \(k\) ring vectors

\[
 w_j=ap+\sqrt{1-a^2}\,r_j,
 \qquad r_j^\top r_\ell=-{1\over k-1}\quad(j\ne\ell),     \tag{45}
\]

where the \(r_j\) form a regular \(k\)-point simplex in \(p^\perp\).  The ring off-diagonal
correlation is

\[
 \rho={ka^2-1\over k-1}.                                  \tag{46}
\]

This Gram construction is valid for every such \(a,k\), including negative \(\rho\).  Its exact
spectrum is

\[
 0^{(2)},\qquad
 \left({k(1-a^2)\over k-1}\right)^{(k-1)},
 \qquad 2+ka^2.                                           \tag{47}
\]

The pole difference \(u=e_1-e_2\) is again a reducing null direction.  Put \(q=1-\rho\),
\(D=1-q^2=\rho(2-\rho)\).  If \(m,\ell\) are the ring counts between and after the two poles, the
same triangular recurrence sums exactly to

\[
\begin{aligned}
 E_{m,\ell}(a,k)={}&1+{a^2(1-q^{2m})\over D}
 +\left[-2+{a^2\over\rho}(1-q^m)\right]^2\\
 &+{a^2\over D}
 \left[2-q^m-{a^2\over\rho}(1-q^m)\right]^2
 (1-q^{2\ell}),                                           \tag{48}
\end{aligned}
\]

with the removable \(\rho=0\) case understood by continuity.  There are
\(2\binom{k+2}{2}\) category words, so

\[
 \lambda_{k,a}:={u^\top K_0(C)u\over\|u\|^2}
 ={1\over2\binom{k+2}{2}}
 \sum_{m=0}^k\sum_{\ell=0}^{k-m}E_{m,\ell}(a,k).          \tag{49}
\]

For fixed \(a>0\), take \(k>1/a^2\), so \(0<\rho<1\).  Then
\(\rho\to a^2\), \(q\to1-a^2\), and a uniformly sampled composition of \(k\) has both
\(m,\ell\to\infty\) in probability.  This last assertion has an explicit quantitative bound:
for every fixed \(L\),

\[
 \Pr(m<L)\le {L(k+1)\over\binom{k+2}{2}}=O_a(k^{-1}),
 \qquad
 \Pr(\ell<L)=O_a(k^{-1}).                                \tag{50}
\]

Equivalently, the exact weighted geometric sums obey

\[
 {\sum_{m=0}^k(k-m+1)q^m\over\binom{k+2}{2}}
 \le {k+1\over(1-q)\binom{k+2}{2}}=O_a(k^{-1}),          \tag{51}
\]

and likewise for \(q^{2m},q^\ell,q^{2\ell}\).  All coefficients in (48) are bounded for fixed
\(a\) and sufficiently large \(k\), so (51) justifies passage through the finite average rather
than merely asserting pointwise convergence.  Setting the vanishing geometric terms to zero gives

\[
 \boxed{
 \lim_{k\to\infty}\lambda_{k,a}
 =1+{1\over2-a^2}.}                                      \tag{52}
\]

Now let \(c>3/2\).  Choose a positive **rational** \(a\) small enough that
\(1+1/(2-a^2)<c\), and only then choose a sufficiently large integer \(k\).  Equations
(46), (49), and (52) produce a rational correlation matrix with
\(\lambda_{k,a}<c\).  Therefore

\[
 \boxed{
 \inf_{n,C}\inf_{0\ne u\in\ker C}
 {u^\top K_0(C)u\over\|u\|^2}\le{3\over2},}             \tag{53}
\]

and no repaired universal inequality \(K_0(C)\succeq cP_{\ker C}\) can have \(c>3/2\).
The quantifier order is essential: first \(k\to\infty\) at fixed \(a>0\), then \(a\downarrow0\).
At \(a=0\) exactly, the pole block decouples and the two limits do not commute.

The exact checker `scripts/iter4_t080_pole_simplex_family.py` compares (48) word by word with the
direct state recurrence in `Fraction` arithmetic, recovers (36) at \(k=6,a=2/3\), and records
rational fixed-\(a\) limits.  Its artifact is
`research/evidence/ITER4_T080_POLE_SIMPLEX_ASYMPTOTIC_2026_08_21.json`.  This is an E3 asymptotic
proof draft.  A different run subsequently reconstructed the spectrum, the last-run sign in
(48), the factor two in (49), the composition weights, the geometric-moment bound, fixed-\(a\)
domination, and the iterated quantifiers.  Its audit
`docs/ITER4_AUDIT_T080_POLE_SIMPLEX_ASYMPTOTIC.md` reports no blocker, so (53) is now an **E4
hostile-audited asymptotic candidate**.  It proves only an upper bound on the best possible
constant: **no \(3/2\) lower bound has been proved**.

### 20. First attack on the possible \(3/2\) replacement

Within the pole--simplex family, set \(b=a^2\).  For each fixed \(k\), cancellation of the
removable \(\rho=0\) factors in (49) makes
\(\lambda_{k,a}-3/2\) a polynomial in \(b\) of degree at most \(2k\).  Exact symbolic conversion
to the degree-\(2k\) Bernstein basis proves

\[
 \lambda_{k,a}>{3\over2}
 \quad(0\le a\le1)                                       \tag{54}
\]

for every \(2\le k\le15\): every Bernstein coefficient is strictly positive.  This is an E2
finite family certificate through ambient dimension \(n=17\), not an induction in \(k\).

The exact energy formula also closes one all-\(k\) parameter regime.  With \(t=a^2\),
\(q=k(1-t)/(k-1)\), \(S_m=\sum_{r<m}q^r\), and
\(T_m=\sum_{r<m}q^{2r}\), (48) is equivalently

\[
 E_{m,\ell}=1+tT_m+(tS_m-2)^2
 +t\left(1-{q\over k}S_m\right)^2T_\ell.                \tag{55}
\]

If \(0\le t\le1/k\), write \(q=1+x/(k-1)\), \(t=(1-x)/k\).  Then
\(tS_m\le(1-x)(1+x/(k-1))^{k-1}\le(1-x)e^x\le1\) and
\(T_m\ge S_m\).  Setting \(X=tS_m\) in (55) gives, word by word,

\[
 E_{m,\ell}\ge1+X+(2-X)^2
 =3+(1-X)(2-X)\ge3.                                     \tag{56}
\]

Thus \(\lambda_{k,a}\ge3/2\) is proved for the entire negative-ring-correlation regime
\(a^2\le1/k\), in every dimension.  This subcase was independently algebra-audited without a
blocker; the positive-ring regime still requires averaging.

Two stronger finite patterns were also certified exactly.  For \(2\le k\le15\), all natural
Bernstein coefficients of

\[
 (2-t)(\lambda_{k,\sqrt t}-1)-1
\]

are strictly positive, proving \(\lambda_{k,a}\ge1+1/(2-a^2)\) in those dimensions.  For
\(2\le k\le12\), the Bernstein coefficients of
\(\lambda_{k,a}-\lambda_{k+1,a}\) are nonnegative, proving finite dimension-monotonicity there.
These patterns would close the full pole--simplex \(3/2\) lower bound if extended uniformly in
\(k\), but no general coefficient formula or coupling has been proved.

A tempting route to all \(k\) is false.  One might cyclically rotate the three ring-gap counts
(before, between, after) and hope that the three word energies average at least three.  At
\(k=52\), \(a=2/5\), and gaps \((17,17,18)\), exact rational arithmetic gives a cyclic average
strictly below three (gap approximately \(-0.00123636\)).  Thus no proof may replace the global
composition average by that pointwise three-cycle inequality.

Both the positive finite certificates and the exact failed-route witness are recorded by
`scripts/iter4_t080_pole_simplex_three_halves_scout.py` in
`research/evidence/ITER4_T080_POLE_SIMPLEX_THREE_HALVES_SCOUT_2026_08_21.json`.  The all-\(k\)
pole--simplex lower bound, and still more the universal inequality
\(K_0(C)\succeq(3/2)P_{\ker C}\), remain open.

## Final evidence boundary

- Equations (30)--(44) use only finite exact rational arithmetic except for the printed decimal
  approximations.  The PSD/SPD claims follow from the exact spectra.
- The counterexample was checked by two structurally different finite computations (56 symmetry
  classes and all \(8!\) labelled orders) and independently reconstructed by a different run.
- No Lean certificate or outside human validation exists; this is an internal E5 exact refutation,
  not an E6 formalized result.
- The broad RPCD finite-time problem remains open.  The next iteration should retire T080/M1 as a
  universal target and record any replacement claim with its exact norm, sampling, and dimension
  dependence.
- The stronger \(3/2\) upper bound in (53) has an exact finite formula, an analytic limiting
  argument, and a different-run hostile audit (E4).  Its status remains lower than the finite
  independently reconstructed \(n=8\) refutation.
- The Bernstein calculation (54) is certified only for \(2\le k\le15\); the accompanying exact
  cyclic-orbit counterexample blocks one local proof strategy but does not refute a \(3/2\) lower
  bound.
- Equations (55)--(56) are an analytic all-\(k\) proof only for \(a^2\le1/k\).  The stronger
  Bernstein and dimension-monotonic patterns in the complementary regime remain finite-\(k\)
  evidence.

## Wall-clock record

- Root-observed active start: **2026-08-21 17:31:54 +08:00**.
- Actual final checkpoint read from `Get-Date`: **2026-08-21 19:32:15 +08:00**.
- Observed active interval: **2:00:21** (120.351 minutes), exceeding the required 120 minutes.
- The first task-specific main artifact was created at 17:47:18; this is recorded separately and
  is not substituted for the root-observed start time.
