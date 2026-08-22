# Iteration 4 / T080: reverse-paired triangular solves

Date: 2026-08-21 (Asia/Shanghai)

## 0. Status, target, and evidence boundary

Let \(C\succeq0\) be an \(n\times n\) real correlation matrix,
\(C_{ii}=1\), with nonzero nullspace

\[
 \mathcal N:=\ker C,
 \qquad P:=P_{\mathcal N}.
\]

For a total order \(\pi\), let \(M_\pi\) be the unit triangular matrix which contains
\(C_{ij}\) below the diagonal in that order, and put

\[
 B_\pi:=M_\pi^{-1},\qquad
 K_0(C):=\mathbb E_\pi[B_\pi^\top B_\pi].                 \tag{0.1}
\]

T080 asks for a proof or refutation of

\[
 \boxed{K_0(C)\succeq2P}                                  \tag{T080}
\]

for every such \(C\).  Equivalently, after the orthogonal splitting
\(\mathbb R^n=\mathcal N\oplus\mathcal N^\perp\), the full Schur complement of
\(K_0(C)\) on \(\mathcal N\) must be at least \(2I\).  Merely proving
\(PK_0P\succeq2P\) would be insufficient.

This subroute now contains an **exact, independently reconstructed counterexample to (T080)**.
The counterexample was found only after the initially proposed duplicate-child lemma failed.  It
was first reconstructed by two exact enumeration procedures here, then independently rebuilt by a
different run and entered in the main Iteration-4 report.  The combined status is E5 exact
refutation (not a formal Lean proof).  The subroute also gives:

1. exact reverse-pair and dual-frame identities (E3 proof drafts, not independently audited);
2. exact rational counterexamples to two tempting *stronger proof lemmas*;
3. exact all-dimension checks for signed rank-one, orthogonal repeated-vector blocks, and the
   regular-simplex boundary;
4. a complete proof draft of T080 for all singular \(3\times3\) correlation matrices, subsequently
   reconstructed by a separate hostile audit with no blocker (local E4 candidate);
5. an exact \(8\times8\) rational Gram matrix and null vector for which the normalized kernel
   quadratic form is \(1057837/531441<2\), refuting the proposed matrix inequality;
6. a precise description of why pairwise and duplicate-induction repairs fail.

No floating-point search below is promoted to a general statement.  The only numerical sweep is
recorded separately as E1 route guidance, with its seed and command.

## 1. Reverse order is transpose

Fix one order and write \(M=M_\pi\).  Since every off-diagonal entry of \(C\) lies on exactly one
side of the triangular split, while both matrices have diagonal one,

\[
 \boxed{M+M^\top=I+C.}                                    \tag{1.1}
\]

The reverse order \(\bar\pi\) swaps every strict precedence relation, hence

\[
 M_{\bar\pi}=M_\pi^\top,
 \qquad B_{\bar\pi}=B_\pi^\top.                           \tag{1.2}
\]

Consequently the contribution of the unordered reverse pair is

\[
 H_M:=\frac12\left(B^\top B+BB^\top\right),               \tag{1.3}
\]

and uniform averaging over reverse pairs gives exactly \(K_0(C)\).

### Exact harmonic-plus-commutator decomposition

For arbitrary positive-definite matrices \(X,Y\), put \(S=X+Y\) and \(D=X-Y\).  The parallel-sum
identity

\[
 S-DS^{-1}D=4(X^{-1}+Y^{-1})^{-1}                          \tag{1.4}
\]

follows by multiplying out, or from
\(X(X+Y)^{-1}Y=(X^{-1}+Y^{-1})^{-1}\).  Apply this with

\[
 X=B^\top B=(MM^\top)^{-1},
 \qquad Y=BB^\top=(M^\top M)^{-1}.
\]

Then

\[
 \boxed{
 H_M
 =2(MM^\top+M^\top M)^{-1}
 +\frac12(X-Y)(X+Y)^{-1}(X-Y).
 }                                                          \tag{1.5}
\]

The second term is positive semidefinite and vanishes exactly when \(M\) is normal.  Thus a
reverse-pair argument has two distinct sources of coercivity: a harmonic core and a genuinely
noncommutative square remainder.  Dropping the latter will be shown invalid even after averaging
all reverse pairs.

If \(S_\pi:=M-M^\top\), then (1.1) also gives

\[
 MM^\top+M^\top M
 =\frac12\left((I+C)^2-S_\pi^2\right).                    \tag{1.6}
\]

Equations (1.5)--(1.6) are exact; no commutativity is used.

## 2. A single reverse pair is not coercive enough

The strongest naive pairing lemma would assert

\[
 H_M\succeq2P\quad\hbox{for every reverse pair}.           \tag{2.1}
\]

It is false already over the integers.  Take

\[
 C=J_3=\mathbf1\mathbf1^\top,
 \qquad \pi=(1,2,3),
\]

so

\[
 M=\begin{pmatrix}1&0&0\\1&1&0\\1&1&1\end{pmatrix},
 \qquad
 B=M^{-1}=\begin{pmatrix}1&0&0\\-1&1&0\\0&-1&1\end{pmatrix}.
\]

The reverse-pair matrix is

\[
 H_M=
 \begin{pmatrix}
 3/2&-1&0\\
 -1&2&-1\\
 0&-1&3/2
 \end{pmatrix}.                                           \tag{2.2}
\]

For \(u=(1,0,-1)^\top\in\ker C\),

\[
 H_Mu=\frac32u,
 \qquad u^\top H_Mu=3<4=2\lVert u\rVert^2.                \tag{2.3}
\]

Thus (2.1) fails even after restricting the test vector to the kernel; this is not merely a
kernel--range coupling failure.

### Path interpretation for the whole signed rank-one family

After a diagonal sign congruence, every signed rank-one correlation matrix is \(J_n\).  For an
order \(p_1,\ldots,p_n\), the inverse has the exact form

\[
 B=I-\sum_{k=2}^n e_{p_k}e_{p_{k-1}}^\top.                \tag{2.4}
\]

Therefore

\[
 z^\top H_Mz
 =\frac12(z_{p_1}^2+z_{p_n}^2)
   +\sum_{k=2}^n(z_{p_k}-z_{p_{k-1}})^2.                  \tag{2.5}
\]

For this extremal family, a reverse pair is exactly an endpoint-mass plus a path-Laplacian
quadratic form.  A single path has no dimension-free spectral gap on the zero-sum space, which
explains (2.3) and shows that the failure grows, rather than disappears, with dimension.

## 3. Reverse pairing plus cyclic shifts is still insufficient

One possible repair is to group a path with all cyclic choices of its break point, as well as all
reversals.  This also fails exactly.

For \(C=J_n\), fix a cyclic ordering and average (2.5) over its \(n\) broken paths.  Each vertex is
an endpoint for two breaks and each cycle edge occurs in \(n-1\) paths, giving

\[
 \boxed{
 q_{\rm cyc}(z)=\frac1n\lVert z\rVert^2
 +\frac{n-1}{n}\sum_{\{i,j\}\in E(C_n)}(z_i-z_j)^2.
 }                                                          \tag{3.1}
\]

For \(n=4\) and \(u=(1,0,-1,0)^\top\), one has \(\mathbf1^\top u=0\),
\(\lVert u\rVert^2=2\), and the cycle-difference sum is \(4\).  Hence

\[
 q_{\rm cyc}(u)=\frac12+3=\frac72<4=2\lVert u\rVert^2.    \tag{3.2}
\]

Thus no proof can assign the target constant independently to each reverse/cyclic orbit.  It must
mix genuinely different Hamilton paths (or exploit an equivalent global identity).

In fact, a much larger local grouping still fails.  Fix any unordered endpoint set
\(\{a,b\}\) and average all \((n-2)!\) Hamilton paths having those endpoints, with reversal
identified.  For \(C=J_n\) and \(u=e_a-e_b\), every such path has endpoint mass one in (2.5) and
exactly two nonzero edge differences, both of square one.  Hence every member, and therefore the
whole endpoint-conditioned group, satisfies

\[
 u^\top H_{\{a,b\}}u=3<4=2\lVert u\rVert^2.               \tag{3.3}
\]

Thus even a factorial-size reverse-closed group can miss the target.  Mixing across *different
endpoint sets* is essential in this sharp family.

## 4. Full permutation mixing repairs the rank-one obstruction exactly

For \(C=J_n\), average (2.5) over every uniform random path.  A vertex is an endpoint with
probability \(2/n\), and an unordered pair is adjacent with probability \(2/n\).  Therefore

\[
 z^\top K_0(J_n)z
 =\frac1n\lVert z\rVert^2
  +\frac2n\sum_{i<j}(z_i-z_j)^2.                           \tag{4.1}
\]

Using
\(\sum_{i<j}(z_i-z_j)^2=n\lVert z\rVert^2-(\mathbf1^\top z)^2\),

\[
 \boxed{
 K_0(J_n)=\left(2+\frac1n\right)I-\frac2nJ,
 \qquad
 K_0(J_n)-2P_{\ker J_n}=\frac1nI.
 }                                                          \tag{4.2}
\]

This is an exact all-dimension verification of (T080) for signed rank-one matrices.  It also shows
that the constant \(2\), if universally true, is asymptotically sharp: the Loewner margin is only
\(1/n\).

The same computation extends without change to an orthogonal repeated-vector block family.  Up to
permutation and diagonal signs, let

\[
 C=\operatorname{diag}(J_{m_1},\ldots,J_{m_r}).             \tag{4.3}
\]

Every triangular solve is block diagonal; the order induced inside each block is uniform.  Thus

\[
 K_0(C)-2P_{\ker C}
 =\operatorname{diag}(m_1^{-1}I_{m_1},\ldots,m_r^{-1}I_{m_r})\succ0. \tag{4.4}
\]

This special case permits arbitrary rank \(r\) and nullity \(n-r\), but it does not cover general
Gram configurations.

## 5. The full-Schur dual-frame formulation

Because \(K_0\succ0\), Schur complementation in
\(\mathcal N\oplus\mathcal N^\perp\) gives the exact equivalence

\[
 K_0\succeq2P
 \quad\Longleftrightarrow\quad
 P K_0^{-1}P\preceq\frac12P.                              \tag{5.1}
\]

For \(u\in\mathcal N\), introduce one vector \(g_\pi\in\mathbb R^n\) for every order.  A standard
least-norm calculation gives

\[
 \boxed{
 u^\top K_0^{-1}u
 =\min_{\mathbb E[B_\pi^\top g_\pi]=u}
   \mathbb E\lVert g_\pi\rVert^2.
 }                                                          \tag{5.2}
\]

Indeed, \(g_\pi=B_\pi K_0^{-1}u\) is feasible and attains the displayed value; completing a square
proves minimality.  Consequently (T080) is equivalent to constructing, for every \(u\in\ker C\),
a dual family satisfying

\[
 \mathbb E[B_\pi^\top g_\pi]=u,
 \qquad
 \mathbb E\lVert g_\pi\rVert^2\le\frac12\lVert u\rVert^2. \tag{5.3}
\]

Unlike a bound on \(PK_0P\), (5.2) retains all kernel--range coupling.

There is a particularly simple but generally too-expensive feasible dual.  Write
\(M=I+L\), with \(L\) strictly lower in the random order.  For \(u\in\ker C\),

\[
 (I+L+L^\top)u=0
 \quad\Longrightarrow\quad
 M^\top u=-Lu.
\]

Thus \(g_\pi=-L_\pi u=M_\pi^\top u\) satisfies
\(B_\pi^\top g_\pi=u\) for every individual order.  Its mean-square cost can be computed exactly.
For fixed coordinate \(i\), use
\(\Pr\{j<_\pi i\}=1/2\),
\(\Pr\{j,k<_\pi i\}=1/3\), and
\(\sum_{j\ne i}C_{ij}u_j=-u_i\).  Summing the resulting second moment gives

\[
 \boxed{
 \mathbb E_\pi\lVert L_\pi u\rVert^2
 =\frac13\lVert u\rVert^2
  +\frac16\sum_j\bigl((C^2)_{jj}-1\bigr)u_j^2.
 }                                                          \tag{5.3a}
\]

This would certify (T080) only under the additional leverage condition that the right side is at
most \(\lVert u\rVert^2/2\).  For \(C=J_n\) it equals
\((n+1)\lVert u\rVert^2/6\), so it already fails for \(n\ge3\), even though the exact target has
the positive margin (4.2).  Formula (5.3a) precisely identifies why the order-by-order null
dependency certificate is too costly: high column leverage must be removed by control variates
across orders.

### What reverse pairing does to the dual problem

For one pair, let its allocated dual load be \(u_M\).  The constraint is

\[
 \frac12(B^\top g+B\bar g)=u_M.                            \tag{5.4}
\]

For any vector \(t\), the control-variate parameterization

\[
 g=M^\top(u_M+t),
 \qquad
 \bar g=M(u_M-t)                                           \tag{5.5}
\]

satisfies (5.4) identically.  Minimizing its mean-square cost over \(t\) yields

\[
 \min_t\frac12\left(
 \lVert M^\top(u_M+t)\rVert^2+
 \lVert M(u_M-t)\rVert^2\right)
 =u_M^\top H_M^{-1}u_M.                                   \tag{5.6}
\]

The minimizer solves

\[
 (MM^\top+M^\top M)t=(M^\top M-MM^\top)u_M.              \tag{5.7}
\]

Now let the expectation range over unordered reverse pairs.  The global dual problem becomes the
exact infimal convolution

\[
 \boxed{
 u^\top K_0^{-1}u
 =\min_{\mathbb E[u_M]=u}
   \mathbb E[u_M^\top H_M^{-1}u_M].
 }                                                          \tag{5.8}
\]

The optimal allocation is \(u_M=H_MK_0^{-1}u\).  Requiring every pair to carry the same load
\(u_M=u\) is precisely the too-strong lemma refuted in Section 2.  A viable reverse-pair proof must
allow bad pairs to carry less of a given null direction and good pairs to carry more, while keeping
the *average full-space vector* equal to \(u\).  Restricting all \(u_M\) to the nullspace would again
discard the range correction present in the Schur complement.

### Even pair-optimal control with an equal load fails

One might retain the optimal within-pair control (5.6) but impose the same allocation \(u_M=u\) on
every pair.  The signed rank-one family disproves this repair too.  For a canonical path, (2.5)
shows that \(H_M\) is the tridiagonal path Laplacian with an additional endpoint mass \(1/2\).
Permutation averaging of \(H_M^{-1}\) is scalar on the zero-sum space.  Direct inversion of that
tridiagonal matrix gives

\[
 \left.\mathbb E_M[H_M^{-1}]\right|_{\mathbf1^\perp}
 =a_n I,
 \qquad
 a_n=\frac{(n+1)(n+6)}{12(n+3)}.                           \tag{5.9}
\]

For completeness, the two scalar data used to obtain (5.9) are

\[
 \operatorname{tr}(H_M^{-1})
 =\frac{n(n+2)(n+7)}{6(n+3)},
 \qquad
 \frac1n\mathbf1^\top H_M^{-1}\mathbf1
 =\frac{n^2+9n+2}{12}.                                    \tag{5.10}
\]

Subtracting the invariant \(\mathbf1\) direction and dividing by \(n-1\) yields (5.9).  In
particular,

\[
 a_n-\frac12=\frac{(n-3)(n+4)}{12(n+3)},                  \tag{5.11}
\]

which is strictly positive for every \(n\ge4\).  Thus optimizing the control variate \(t\) inside
each pair is still insufficient if all pairs are assigned the same null load.  By contrast, the
globally optimal cost from (4.2) is
\((2+1/n)^{-1}\lVert u\rVert^2<\lVert u\rVert^2/2\).  The missing operation is exactly the
cross-pair allocation in (5.8), not a sharper solution of the individual pair problem.

## 6. The harmonic core alone does not close after averaging

Since the second term of (1.5) is PSD, it is tempting to average only

\[
 G_{\rm harm}:=\mathbb E_{\{\pi,\bar\pi\}}
   [2(MM^\top+M^\top M)^{-1}].                            \tag{6.1}
\]

This lower bound is not sufficient in general, even on a one-parameter rational rank-two family.
Let

\[
 C(t)=\begin{pmatrix}
 1&-1&t\\
 -1&1&-t\\
 t&-t&1
 \end{pmatrix},
 \qquad |t|<1.                                             \tag{6.2}
\]

It is the Gram matrix of \(v,-v,w\) with \(v^\top w=t\), and
\(\ker C(t)=\operatorname{span}\{u\}\), \(u=(1,1,0)^\top\).  Exact averaging over the three
reverse pairs gives

\[
 \frac{u^\top G_{\rm harm}u}{\lVert u\rVert^2}
 =\frac{4(4t^6+7t^4+11t^2+15)}
 {3(t^2+1)(3t^4-t^2+10)},                                 \tag{6.3}
\]

and hence

\[
 \frac{u^\top G_{\rm harm}u}{\lVert u\rVert^2}-2
 =-\frac{2t^2(t^4-8t^2+5)}
 {3(t^2+1)(3t^4-t^2+10)}.                                 \tag{6.4}
\]

The denominator is positive, so the harmonic core is strictly below \(2\) whenever

\[
 0<|t|<\sqrt{4-\sqrt{11}}.                                 \tag{6.5}
\]

In contrast, retaining the commutator-square remainder gives the exact full coefficient

\[
 \frac{u^\top K_0(C(t))u}{\lVert u\rVert^2}
 =\frac{t^4-2t^2+15}{6},                                  \tag{6.6}
\]

whose gap above two is

\[
 \frac{t^4-2t^2+3}{6}
 =\frac{(t^2-1)^2+2}{6}>0.                                \tag{6.7}
\]

The signed permutation which swaps the antipodal pair and flips the sign of coordinate three fixes
\(C(t)\), acts as \(+I\) on \(\mathcal N\), and as \(-I\) on \(\mathcal N^\perp\).  Equivariance
therefore makes \(\mathcal N\) a reducing subspace of \(K_0\).  Thus (6.7), together with positivity
on \(\mathcal N^\perp\), proves (T080) for this special family.
Equations (6.3)--(6.7) also give an exact obstruction: the noncommutative remainder in (1.5) is not
optional.

## 7. A deterministic example with nonzero Schur coupling

Let

\[
 V=\begin{pmatrix}1&0\\0&1\\3/5&4/5\end{pmatrix},
 \qquad C=VV^\top,
 \qquad u=(-3/5,-4/5,1)^\top.                              \tag{7.1}
\]

Then \(C\) is a rational rank-two correlation matrix, \(Cu=0\), and exact enumeration of its six
orders gives

\[
 K_0=
 \begin{pmatrix}
 1523/1250&8/25&-83/125\\
 8/25&849/625&-106/125\\
 -83/125&-106/125&3/2
 \end{pmatrix}.                                            \tag{7.2}
\]

Here the kernel compression and the true Schur coefficient are different:

\[
 \frac{u^\top K_0u}{\lVert u\rVert^2}=\frac{3293}{1250},
 \qquad
 \frac{\lVert u\rVert^2}{u^\top K_0^{-1}u}
 =\frac{3157}{1202},                                      \tag{7.3}
\]

with coupling loss

\[
 \frac{3293}{1250}-\frac{3157}{1202}
 =\frac{2984}{375625}>0.                                  \tag{7.4}
\]

Indeed,

\[
 (I-P)K_0u=\frac1{625}(-44,-12,-36)^\top\ne0.             \tag{7.5}
\]

The true coefficient is still above two; this is not a counterexample.  It is an exact warning
that a proof of only the kernel compression would not establish T080.

## 8. A second all-dimension boundary check: regular simplex

Consider the regular-simplex correlation matrix

\[
 C=\frac{n}{n-1}I-\frac1{n-1}J,
 \qquad \ker C=\operatorname{span}\{\mathbf1\}.            \tag{8.1}
\]

For a fixed order, the triangular factor has constant strict-lower entry
\(t=-1/(n-1)\).  If \(r=1-t=n/(n-1)\), direct forward substitution gives

\[
 B_\pi\mathbf1=(1,r,r^2,\ldots,r^{n-1})^\top              \tag{8.2}
\]

in the ordered coordinates.  Full permutation invariance makes \(\mathbf1\) a reducing direction
of \(K_0\), with eigenvalue

\[
 \lambda_{\mathcal N}
 =\frac1n\sum_{k=0}^{n-1}\left(\frac n{n-1}\right)^{2k}.  \tag{8.3}
\]

Bernoulli's inequality gives

\[
 \left(1+\frac1{n-1}\right)^{2k}
 \ge1+\frac{2k}{n-1},
\]

so the sum in (8.3) is at least \(2n\).  Therefore
\(\lambda_{\mathcal N}\ge2\); positivity and the reducing decomposition prove (T080) for this
simple-nullity family.  Unlike signed rank one, it is not asymptotically sharp: (8.3) tends to
\((e^2-1)/2\).

### A duplicate-direction induction reduced to one child inequality

The numerically dangerous two-pole constructions contain duplicate Gram vectors.  There is an
exact reduction for such a null direction.  Suppose \(C\) has two identical Gram rows/columns
\(p,q\), and let \(u=e_p-e_q\).  In the Bellman recursion, selecting a coordinate outside
\(\{p,q\}\) first leaves the same duplicate null vector in the child.  Selecting \(p\) or \(q\)
first contributes one immediately, and the child residual is, up to sign,

\[
 z=(I+B)e_i,                                               \tag{8.4}
\]

where \(B\) is the correlation matrix after deleting the selected copy and \(i\) labels the
remaining copy.  Consequently, induction over the number of other coordinates would prove
\(u^\top K_0(C)u\ge4\) if the following child lemma were available:

\[
 \boxed{
 ((I+B)e_i)^\top K_0(B)((I+B)e_i)\ge3
 \quad\text{for every correlation }B\text{ and every }i.
 }                                                          \tag{8.5}
\]

Indeed, with \(n-2\) ordinary coordinates, the Bellman average would be at least

\[
 \frac1n\bigl((n-2)\,4+2(1+3)\bigr)=4.                    \tag{8.6}
\]

This is presently an **E0 sublemma**, not a proved fact.  It is sharp in order: for \(B=J_m\),
(4.2) gives the exact value

\[
 ((I+J_m)e_i)^\top K_0(J_m)((I+J_m)e_i)=3+\frac1m.         \tag{8.7}
\]

A seed-`20260821` float64 guidance check on 50 row-normalized Gaussian Gram matrices per
\(m=1,\ldots,8\), with every coordinate tested and `K_0` evaluated by subset DP, found minima from
`4.0` down to about `3.04`, but this null search does not prove (8.5).  Pairwise reverse order is not
enough: individual pair averages below three occur from \(m=3\) onward.  Thus (8.5), if true, again
requires global order mixing.

There is a useful exact projection-word form of the remaining gap.  Let
\(B_{jk}=v_j^\top v_k\), distinguish \(v=v_i\), put
\(Z_j=I-v_jv_j^\top\), fix an order \(q_1,\ldots,q_{m-1}\) of the other vectors, and insert \(i\)
after its first \(k\) entries.  Define

\[
 e_k=Z_{q_k}\cdots Z_{q_1}v,
 \qquad a_k=v^\top e_k,
 \qquad S_k=Z_{q_{m-1}}\cdots Z_{q_{k+1}}.                 \tag{8.8}
\]

Forward substitution, together with the Pythagorean energy identity for orthogonal projections,
gives

\[
 \boxed{
 \lVert M_\pi^{-1}(I+B)e_i\rVert^2
 =3+2a_k-
 \left\lVert S_k\bigl(e_k-(1+a_k)v\bigr)\right\rVert^2.
 }                                                          \tag{8.9}
\]

Hence (8.5) is equivalent to the global word inequality

\[
 \mathbb E_{q,k}\left[
 2a_k-\left\lVert S_k(e_k-(1+a_k)v)\right\rVert^2
 \right]\ge0.                                             \tag{8.10}
\]

This formulation is potentially amenable to a martingale or path-SOS argument.  It also exposes
another no-go: seed-`20260821` float64 tests found fixed projection words with a negative sum over
all insertion gaps from word length three onward, and even pairing a word with its reversal did not
restore nonnegativity.  Thus any proof of (8.10) must average genuinely different orders of the
other projections, consistently with the rank-one obstructions in Sections 2--5.

The child lemma can nevertheless be proved exactly through size three.  For size one its left side
is four.  For

\[
 B=\begin{pmatrix}1&r\\r&1\end{pmatrix}
\]

directly averaging the two orders gives

\[
 ((I+B)e_1)^\top K_0(B)((I+B)e_1)
 =4-r^2+\frac12r^4\ge\frac72.                              \tag{8.11}
\]

For size three, write

\[
 B=\begin{pmatrix}1&a&b\\a&1&c\\b&c&1\end{pmatrix},
 \qquad z=(I+B)e_1=(2,a,b)^\top.
\]

The same six-order matrix (9.1), without imposing \(\det B=0\), gives

\[
 z^\top K_0(B)z-3=\frac16N(a,b,c),                         \tag{8.12}
\]

where \(N\) is quadratic in \(c\), with leading coefficient
\(2a^2b^2+3a^2+3b^2\).  If \((a,b)\ne(0,0)\), minimize over **all real** \(c\), which is a
relaxation of the correlation-matrix feasible interval.  With \(x=a^2,y=b^2\), exact completion of
the square gives

\[
 \min_{c\in\mathbb R}N(a,b,c)
 =\frac{P(x,y)}{2xy+3x+3y},                               \tag{8.13}
\]

\[
\begin{aligned}
P(x,y)={}&2x^3y^2+9x^3+2x^2y^3-12x^2y^2+9x^2y-18x^2\\
&+9xy^2-28xy+18x+9y^3-18y^2+18y.
\end{aligned}                                              \tag{8.14}
\]

On \([0,1]^2\), the bicubic Bernstein coefficient matrix of \(P\), with rows and columns indexed
from zero to three, is

\[
 \begin{pmatrix}
 0&6&6&9\\
 6&80/9&61/9&26/3\\
 6&61/9&20/9&2\\
 9&26/3&2&0
 \end{pmatrix}.                                           \tag{8.15}
\]

Every coefficient is nonnegative, so \(P\ge0\) on the square.  When \(a=b=0\), direct substitution
gives \(N=6\).  Hence (8.5) holds for every correlation matrix of size at most three.  This is an
E3 finite-dimensional proof draft.

#### The child lemma is false in size five

The qualifier in the preceding paragraph is essential.  Consider the rational correlation matrix

\[
 B=\begin{pmatrix}
 1&1&4/5&4/5&4/5\\
 1&1&4/5&4/5&4/5\\
 4/5&4/5&1&23/50&23/50\\
 4/5&4/5&23/50&1&23/50\\
 4/5&4/5&23/50&23/50&1
 \end{pmatrix},
 \qquad
 z=(I+B)e_1=(2,1,4/5,4/5,4/5)^\top.                    \tag{8.16}
\]

It is PSD: its characteristic polynomial is

\[
 \det(\lambda I-B)
 =\frac{\lambda^2(25\lambda-98)(50\lambda-27)^2}{62500}.
                                                                    \tag{8.17}
\]

Exact enumeration of all \(120\) triangular solves gives

\[
 z^\top K_0(B)z
 =\frac{7204453277}{2441406250}
 =2.9509440622592\ldots<3,                               \tag{8.18}
\]

with exact gap

\[
 z^\top K_0(B)z-3
 =-\frac{119765473}{2441406250}.                          \tag{8.19}
\]

This was independently recomputed inside the present run from the \(120\) permutation recurrences,
and the supplied fraction was matched exactly.  Geometrically, the last three Gram vectors are
\(w_j=(4/5)p+(3/5)r_j\), where the \(r_j\) form an equilateral triple in \(p^\perp\); this explains
the otherwise nonobvious entry \(23/50\).  Thus (8.5) is **false**, although the size-at-most-three
result above remains valid.  In particular, the duplicate-direction induction (8.6) cannot be the
general proof of T080.

#### The same geometry gives an exact \(n=8\) counterexample to T080

The failure is not confined to the stronger child lemma.  Let \(C\in\mathbb Q^{8\times8}\) have
two pole coordinates \(1,2\) and six ring coordinates \(R=\{3,\ldots,8\}\), with

\[
 C_{12}=1,
 \qquad C_{ij}=\frac23\quad(i\in\{1,2\},\ j\in R),
 \qquad C_{jk}=\frac13\quad(j\ne k\in R),                \tag{8.20}
\]

and diagonal entries one.  To see \(C\succeq0\), take a unit vector \(p\), a regular simplex
\(r_1,\ldots,r_6\subset p^\perp\) with
\(r_j^\top r_k=-1/5\) for \(j\ne k\), and use Gram vectors

\[
 p,\ p,\quad
 w_j=\frac23p+\frac{\sqrt5}{3}r_j\quad(1\le j\le6).       \tag{8.21}
\]

Indeed \(w_j^\top w_k=1/3\) for \(j\ne k\).  More explicitly,

\[
 \det(\lambda I-C)
 =\frac{\lambda^2(3\lambda-14)(3\lambda-2)^5}{729},       \tag{8.22}
\]

so \(C\) has rank six and nullity two.  An explicit orthogonal kernel basis is

\[
 u=(1,-1,0,0,0,0,0,0)^\top,\qquad
 v=(-2,-2,1,1,1,1,1,1)^\top.                             \tag{8.22a}
\]

In particular, \(Pu=u\) and \(\lVert u\rVert^2=2\).  Direct exact enumeration of all
\(8!=40320\) orders gives

\[
 \boxed{
 \frac{u^\top K_0(C)u}{\lVert u\rVert^2}
 =\frac{1057837}{531441}
 =1.990506942445\ldots<2.
 }                                                         \tag{8.23}
\]

The exact violation is

\[
 u^\top(K_0(C)-2P)u=-\frac{10090}{531441}<0.             \tag{8.24}
\]

There is a much shorter exact reconstruction of (8.23).  Ring labels are exchangeable, so the
energy of a permutation depends only on the positions and order of the two poles among six ring
symbols.  There are \(2\binom82=56\) such category words, each representing \(6!\) permutations.
During a forward solve keep

\[
 s_p=\sum_{\text{past poles}}y_j,
 \qquad s_r=\sum_{\text{past ring}}y_j.
\]

For the positive pole, negative pole, and a ring coordinate, respectively, the exact updates are

\[
\begin{array}{c|c|c}
\text{symbol}&y&\text{updated state}\\ \hline
+&1-s_p-\frac23s_r&s_p\leftarrow s_p+y\\
-&-1-s_p-\frac23s_r&s_p\leftarrow s_p+y\\
R&-\frac23s_p-\frac13s_r&s_r\leftarrow s_r+y.
\end{array}                                               \tag{8.25}
\]

For an additional hand-check, take the positive pole first and let \(m\) and \(\ell\) be the
numbers of ring symbols between and after the two poles.  (The rings before the first pole produce
zero.)  With \(q=2/3\), the energy of that word is

\[
\begin{aligned}
 E_{m,\ell}={}&1+\frac45(1-q^{2m})
 +\frac49(1+2q^m)^2\\
 &+\frac4{45}(2+q^m)^2(1-q^{2\ell}).                     \tag{8.25a}
\end{aligned}
\]

The negative-first orientation has the same energy.  Therefore summing \(\sum y^2\) over the
\(56\) words reduces to the finite rational sum

\[
 u^\top K_0(C)u
 =\frac1{28}\sum_{m=0}^6\sum_{\ell=0}^{6-m}E_{m,\ell}
 =\frac{2115674}{531441}.                                 \tag{8.26}
\]

Equivalently, the unnormalized double sum is
\(59238872/531441\).  Thus
the displayed average is exactly twice (8.23).  A second implementation enumerating all \(40320\) labelled
permutations with rational arithmetic returned the same fraction.  Its convention was explicit:
for a labelled order \(\pi\), it recursively computed

\[
 y_{\pi_k}=u_{\pi_k}-\sum_{\ell<k}C_{\pi_k\pi_\ell}y_{\pi_\ell},
                                                                    \tag{8.27}
\]

which is exactly the solution of \(M_\pi y=u\) for the lower-in-order triangular factor used in
(0.1), and accumulated \(\sum_k y_{\pi_k}^2=u^\top B_\pi^\top B_\pi u\).

Finally, swapping the two pole coordinates leaves \(C\), the uniform order distribution, and hence
\(K_0(C)\) invariant.  Its \(-1\) eigenspace is the one-dimensional span of \(u\), so \(u\) is a
reducing eigenvector of \(K_0(C)\).  Thus (8.23) is also the exact full-Schur coefficient in this
direction; there is no hidden kernel--range coupling that could repair the violation.

An exact remaining-set recursion gives a fuller symmetry audit.  If \(A,B,c,d,e\) denote,
respectively, the pole diagonal, pole off-diagonal, pole--ring, ring diagonal, and distinct
ring--ring entries of \(K_0(C)\), it returns

\[
\begin{aligned}
A&=\frac{6151142}{3720087},&
B&=-\frac{1253717}{3720087},&
c&=-\frac{5802943}{19131876},\\
d&=\frac{6031064}{4782969},&
e&=-\frac{730865}{33480783}.                              \tag{8.27a}
\end{aligned}
\]

Besides \(u\), the kernel direction is
\(v=(-2,-2,1,1,1,1,1,1)^\top\).  The full Schur coefficient in the latter direction is

\[
 s_v=\frac{\lVert v\rVert^2}{v^\top K_0(C)^{-1}v}
 =\frac{616286806298099}{272688930830412}
 =2.260036\ldots>2.                                      \tag{8.27b}
\]

The pole-swap and ring-permutation representations separate \(u\), \(v\), the one-dimensional
range-trivial direction, and the ring-standard range space.  Hence the two eigenvalues of the
full kernel Schur complement are exactly \(1057837/531441\) and \(s_v\); the first is genuinely
the least one.

Consequently (8.20)--(8.27) form an E5 exact, independently reconstructed refutation.  The
independent checker is scripts/iter4_t080_exact_counterexample.py, with exact record
research/evidence/ITER4_T080_EXACT_COUNTEREXAMPLE_N8_2026_08_21.json; the main report records the
cross-run audit and evidence promotion.  These equations refute the proposed auxiliary inequality
T080 itself, not
the original RPCD complexity conjecture; the logical implications for the broader harness must be
reassessed separately.

The counterexample also gives a direct post-mortem of reverse pairing.  Pair the category with pole
positions \((i,j)\) with \((7-i,7-j)\), and divide the paired energy by
\(\lVert u\rVert^2=2\).  Among the resulting \(28\) reverse pairs, exactly \(15\) have coefficient
below two and \(13\) above two.  The exact extremes are

\[
 \min_{\{\pi,\bar\pi\}}
 \frac{u^\top H_\pi u}{\lVert u\rVert^2}
 =\frac{11517649}{9565938}=1.204027\ldots,
 \qquad
 \max_{\{\pi,\bar\pi\}}
 \frac{u^\top H_\pi u}{\lVert u\rVert^2}
 =\frac{4177}{1458}=2.864883\ldots.                       \tag{8.27c}
\]

Their exact mean is \(1057837/531441\), as it must be.  Thus the final violation is a genuinely
cross-pair imbalance: reverse symmetrization removes orientation but does not provide enough
coercivity even after all reverse pairs are averaged.

#### An asymptotic pole--simplex family: no universal constant above \(3/2\)

The \(n=8\) example is one member of an exact family.  Fix \(k\ge2\) and \(0<a<1\).  Take two
copies of \(p\) and \(k\) vectors

\[
 w_j=a p+\sqrt{1-a^2}\,r_j,
 \qquad r_j^\top r_\ell=-\frac1{k-1}\quad(j\ne\ell),       \tag{8.28}
\]

where the \(r_j\) are a regular \(k\)-point simplex in \(p^\perp\).  Then the pole--ring
correlation is \(a\), while the ring off-diagonal correlation is

\[
 \rho=\frac{ka^2-1}{k-1}.                                 \tag{8.29}
\]

The Gram spectrum is

\[
 0\ \text{(multiplicity 2)},\qquad
 \frac{k(1-a^2)}{k-1}\ \text{(multiplicity \(k-1\))},
 \qquad 2+ka^2\ \text{(multiplicity 1)}.                  \tag{8.30}
\]

Thus this is a correlation matrix of rank \(k\), and \(u=e_1-e_2\) is again a reducing null
direction.  The category-word calculation also has a closed finite form.  Put
\(q=1-\rho\), \(D=1-q^2=\rho(2-\rho)\), and let \(m,\ell\) count ring symbols between and after
the poles.  For \(\rho\ne0\), the word energy is

\[
\begin{aligned}
 E_{m,\ell}(a,k)={}&1+\frac{a^2(1-q^{2m})}{D}
 +\left[-2+\frac{a^2}{\rho}(1-q^m)\right]^2\\
 &+\frac{a^2}{D}
 \left[2-q^m-\frac{a^2}{\rho}(1-q^m)\right]^2
 (1-q^{2\ell}),                                           \tag{8.31}
\end{aligned}
\]

and the normalized kernel eigenvalue is exactly

\[
 \lambda_{k,a}
 :=\frac{u^\top K_0(C)u}{\lVert u\rVert^2}
 =\frac1{2\binom{k+2}{2}}
 \sum_{m=0}^k\sum_{\ell=0}^{k-m}E_{m,\ell}(a,k).           \tag{8.32}
\]

Equation (8.31) follows by summing the geometric sequence of triangular-solve coefficients in
each ring run; (8.32) is uniform averaging over the compositions of \(k\) ring symbols around the
two poles.  For fixed \(a\in(0,1)\), as \(k\to\infty\),
\(\rho\to a^2\), \(q\to1-a^2\), and the fraction of compositions with either \(m\) or \(\ell\)
bounded tends to zero.  Dominated finite-sum convergence in (8.32) therefore gives

\[
 \boxed{\lim_{k\to\infty}\lambda_{k,a}
 =1+\frac1{2-a^2}.}                                      \tag{8.33}
\]

Letting positive rational \(a\downarrow0\) after this limit yields

\[
 \inf_{n,C}\ \inf_{\substack{u\in\ker C\\u\ne0}}
 \frac{u^\top K_0(C)u}{\lVert u\rVert^2}
 \le\frac32.                                              \tag{8.34}
\]

Thus even a repaired universal inequality \(K_0(C)\succeq cP_{\ker C}\) cannot have
\(c>3/2\).  Equation (8.34) is only an upper bound on the best possible universal constant; no
matching \(3/2\) lower bound is proved here.  The order of limits matters: at \(a=0\) exactly the
pole block decouples and has a larger coefficient, so (8.34) uses small positive \(a\) followed by
large \(k\).

There is a cleaner polynomial form which is useful for attacking the possible matching lower
bound.  Put \(t=a^2\),

\[
 q=\frac{k(1-t)}{k-1},\qquad
 S_m=\sum_{r=0}^{m-1}q^r,\qquad
 T_m=\sum_{r=0}^{m-1}q^{2r}.
\]

Then (8.31), including its removable \(\rho=0\) case, is exactly

\[
 \boxed{
 E_{m,\ell}
 =1+tT_m+(tS_m-2)^2
 +t\left(1-\frac qkS_m\right)^2T_\ell.
 }                                                         \tag{8.35}
\]

This gives a complete proof of the candidate lower bound \(E_{m,\ell}\ge3\) in the
negative-ring-correlation regime \(0\le t\le1/k\).  Indeed then
\(q=1+x/(k-1)\) and \(t=(1-x)/k\) for some \(x\in[0,1]\).  Since

\[
 tS_m\le tS_k
 \le(1-x)\left(1+\frac{x}{k-1}\right)^{k-1}
 \le(1-x)e^x\le1,
\]

and \(T_m\ge S_m\), setting \(X=tS_m\in[0,1]\) in (8.35) gives

\[
 E_{m,\ell}\ge1+X+(2-X)^2
 =3+(1-X)(2-X)\ge3.                                      \tag{8.36}
\]

Thus \(\lambda_{k,a}\ge3/2\) is rigorously proved for \(a^2\le1/k\), even pointwise in the two
gap lengths.  The remaining regime \(a^2>1/k\), where \(0\le q<1\), genuinely requires averaging:
the \(n=8\) example has individual and reverse-paired word energies below three.
A different run independently rederived
\(2-q^m-tS_m=1-(q/k)S_m\) and checked every inequality in (8.35)--(8.36), reporting no blocker.
This low-latitude subfamily result is therefore E4 hostile-audited.

Exact and deterministic searches support a stronger statement in the remaining regime:

\[
 \lambda_{k,a}\ \stackrel{?}{\ge}\ 1+\frac1{2-a^2}
 \quad\text{for every finite }k.                          \tag{8.37}
\]

For each \(k=2,\ldots,12\), exact symbolic expansion found that
\(\lambda_{k,a}-3/2\), as a degree-\(2k\) polynomial in \(t=a^2\), has only nonnegative natural
Bernstein coefficients.  More sharply, for \(k=2,\ldots,22\), the degree-\(2k+1\) polynomial

\[
 R_k(t):=(2-t)(\lambda_{k,\sqrt t}-1)-1                  \tag{8.38}
\]

has strictly positive, monotonically decreasing Bernstein coefficients; its last coefficient is
\(1/(k+2)\).  Finally, for \(k=2,\ldots,12\), every natural Bernstein coefficient of the
degree-\(2k+2\) polynomial
\(\lambda_{k,\sqrt t}-\lambda_{k+1,\sqrt t}\) is nonnegative (only the \(t=0\) endpoint
coefficient vanishes).  The \(t=1\) difference is exactly
\(1/((k+2)(k+3))\).

The last three coefficients in the first pattern are not merely experimental.  Directly
differentiating the finite category sum (8.32) at \(t=1\) gives

\[
 \lambda_{k,1}=2+\frac1{k+2},\qquad
 \left.\frac{d}{dt}\lambda_{k,\sqrt t}\right|_{t=1}=\frac{k}{k+2},\qquad
 \left.\frac{d^2}{dt^2}\lambda_{k,\sqrt t}\right|_{t=1}
 =\frac{2k(k+1)}{(k-1)(k+2)}.
                                                               \tag{8.38a}
\]

Indeed, at \(q=0\), \(S_m=T_m=\mathbf1_{\{m>0\}}\), while
\(S'_m=-k/(k-1)\) for \(m\ge2\), \(S'_1=0\), and \(T'_m=0\).  Summing the
resulting category derivatives gives \(k(k+1)\), before division by
\(2\binom{k+2}{2}=(k+1)(k+2)\).  Consequently, if \(d=2k+1\), then

\[
 R_k(1)=\frac1{k+2},\qquad R_k'(1)=-\frac3{k+2},\qquad
 R_k''(1)=\frac{4k}{(k-1)(k+2)},
\]
\[
 b_d=\frac1{k+2},\qquad b_{d-1}=\frac2{2k+1},\qquad
 b_{d-2}=\frac{2k^2+5k-5}{(k-1)(k+2)(2k+1)}.             \tag{8.38b}
\]

where \(b_j\) are the degree-\(d\) Bernstein coefficients.  Thus only the earlier
coefficients remain to be controlled in a uniform proof.  Notice also that
\[
 b_{d-2}-b_{d-1}
 =\frac{3k-1}{(k-1)(k+2)(2k+1)}>0,
\]
so the final strict decrease is uniform.  The identities (8.38a)--(8.38b)
are exact algebraic consequences of (8.32), not numerical evidence.

The endpoint-jet calculation continues two steps further.  Exact Taylor truncation of
(8.32) at \(t=1\) gives, for every integer \(k\ge3\),
\[
\begin{aligned}
 b_{d-3}-b_{d-2}
 &=
 \frac{12k^5-14k^4+13k^2-36k+1}
 {2(k-1)^3(k+1)(k+2)(2k-1)(2k+1)},\\
 b_{d-4}-b_{d-3}
 &=
 \frac{3(4k^7-10k^6+12k^5-k^4-30k^3-2k^2-24k+11)}
 {2(k-1)^5(k+1)(k+2)(2k-1)(2k+1)}.                    \tag{8.38c}
\end{aligned}
\]
Both numerators are manifestly positive for \(k\ge3\): after setting \(r=k-3\), their
descending coefficient lists are respectively
\[
 (12,166,912,2497,3390,1792),\qquad
 (4,74,588,2609,6978,11176,9738,3404).
\]
For reconstruction, put \(h=1-t\), truncate \(S_m,T_m\) through \(h^4\),
and group each gap as \(0,1,2,3,4,\ge5\).  When \(k\ge10\), the high--high category
has exactly \((k-9)(k-8)/2\) compositions and the mixed categories have
\(k-i-4\) compositions.  Exact symbolic summation and Bernstein conversion produce
(8.38c); direct rational evaluation covers \(k=3,\ldots,9\).  This is an E3 algebraic
proof draft pending hostile reconstruction.  It proves that the final five Bernstein
coefficients are positive and strictly decreasing in the required direction.  Even a
proof of every fixed-width endpoint jet would not by itself control the middle
\(\Theta(k)\) coefficients.

These are E2 finite-\(k\) certificates generated with exact SymPy rational arithmetic, not a
general proof.  A deterministic float64 check on
\(k=2,\ldots,999\) and the grid \(t=j/100\), \(0\le j\le100\), found no violation of
\(\lambda_{k,a}\ge\lambda_{k+1,a}\) at tolerance \(10^{-10}\).  Separate dense-grid/golden-section
searches through \(k=2000\), including \(t<1/k\), found minima above \(3/2\) approaching it from
above.  There was no random seed.

The precise analytic breakpoint is now clear: proving the Bernstein coefficient pattern or the
dimension monotonicity for symbolic \(k\) would establish (8.37) by the limit (8.33), and hence a
sharp \(3/2\) lower bound **inside this pole--simplex family**.  No coefficient formula or coupling
proof uniform in \(k\) was obtained, so neither (8.37) nor a universal \(3/2\) inequality outside
this family is promoted.

A coarse attempt to avoid the exact tail average also fails.  Replacing
\(T_\ell\) by the valid lower bound \(\mathbf1_{\{\ell>0\}}\) reduces (8.35) to a tractable
one-sum expression, but a deterministic float64 scan reaches only \(1.33666\) after normalization
at \(k=500,t\approx0.06853\).  This is a failure of that lower bound, not a counterexample to
\(\lambda\ge3/2\); the discarded geometric tail energy is quantitatively essential.

One tempting symbolic closure was also ruled out precisely.  Performing the two triangular
geometric sums in (8.32) writes the gap in (8.37) as

\[
 \lambda_{k,a}-1-\frac1{2-t}
 =\frac{A_0(q,k)+A_1(q,k)q^k+A_2(q,k)q^{2k}}
 {2k^3(k+1)(k+2)(q-1)^5(q+1)^3(kq+k-q)},                \tag{8.39}
\]

with removable limits at \(q=1\).  The middle coefficient factors exactly as

\[
 A_1=4q^2(q+1)^3
 (kq-k-1)(kq-k-q)(kq-k+q)(kq+k-q).                      \tag{8.40}
\]

On \(0\le q<1\), its sign changes at \(q=k/(k+1)\).  The other two coefficients also do not have
a uniform sign pattern sufficient for (8.39).  Thus treating \(q^k\) as an independent
nonnegative symbol and proving coefficientwise positivity cannot close the argument; a valid
proof must use the nonlinear relation \(q^k\) itself, the Bernstein/dimension-monotonic structure,
or a probabilistic coupling.

For fixed \(t\in(0,1)\), setting the exponentially small \(q^k\)-terms aside and expanding the
closed sum at \(k=\infty\) gives the exact first correction

\[
 \lambda_{k,\sqrt t}
 =1+\frac1{2-t}
 +\frac{2-t^2}{t(2-t)}\,\frac1k
 +O_t(k^{-2})+O_t(q^k).                                  \tag{8.41}
\]

Its \(1/k\) coefficient is positive.  Combining the small-\(t\) expansions
\(1+1/(2-t)-3/2\sim t/4\) and
\((2-t^2)/(t(2-t)k)\sim1/(tk)\) predicts the observed near-minimizer
\(t\sim2/\sqrt{k}\).  A direct two-scale expansion makes this precise: for every fixed \(c>0\),
putting \(t=c/\sqrt{k}\) gives

\[
 \lambda_{k,\sqrt t}
 =\frac32+\frac{c^2+4}{4c\sqrt{k}}
 +\frac{c^4+4c^2+10}{8c^2k}
 +O_c(k^{-3/2})+O_c(e^{-c\sqrt{k}}).                     \tag{8.42}
\]

The leading coefficient \(c/4+1/c\) is minimized at \(c=2\), where it equals one.  Thus this
family has an explicit near-extremal sequence with
\(a^2\sim2/\sqrt{k}\) and
\(\lambda=3/2+1/\sqrt{k}+O(1/k)\).  Equations (8.41)--(8.42) are symbolic asymptotic
consequences of the exact finite sum, not floating-point fits.  They remain E3 algebraic proof
drafts pending an independent symbolic reconstruction.

## 9. Complete dimension-three reduction (subsequently hostile-audited)

Reverse-pair enumeration admits a complete symbolic reduction when \(n=3\).  This section is a
self-contained proof draft of T080 for every singular \(3\times3\) correlation matrix.  After it
was written, a different run independently rebuilt its algebra and feasible-set argument in
`docs/ITER4_T080_N3_HOSTILE_AUDIT.md`, with an exact checker at
`scripts/iter4_t080_n3_hostile_audit.py`; that audit reported no blocker.  Thus this is now a local
E4 candidate, still not a general-dimensional theorem.

Write

\[
 C=\begin{pmatrix}1&a&b\\a&1&c\\b&c&1\end{pmatrix}.
\]

If \(\operatorname{rank}C=1\), diagonal signs reduce it to \(J_3\), already covered by (4.2).
Assume henceforth that \(\operatorname{rank}C=2\).  Exact enumeration of the six triangular solves
gives

\[
\begin{aligned}
 K_{11}&=1+\frac{a^2+b^2}{3}
 +\frac{(a-bc)^2+(ac-b)^2}{6},\\
 K_{12}&=-a-\frac{a(b^2+c^2)}6+\frac{2bc}3,
\end{aligned}                                              \tag{9.1}
\]

with the other entries obtained by simultaneous permutation of \((1,2,3)\) and \((a,b,c)\).

Put \(A_C=\operatorname{adj}C\).  Since \(C\succeq0\) has rank two,
\(A_C=\gamma uu^\top\) for a nonzero null vector \(u\) and some \(\gamma>0\).  The rank-one update
criterion gives

\[
 K_0-2P_{\ker C}\succeq0
 \quad\Longleftrightarrow\quad
 E:=\operatorname{tr}(A_C)\det K_0
 -2\operatorname{tr}(A_C\operatorname{adj}K_0)\ge0.        \tag{9.2}
\]

Indeed, after division by \(\gamma\det K_0>0\), (9.2) is exactly
\(\lVert u\rVert^2-2u^\top K_0^{-1}u\ge0\).  Thus (9.2) is the full Schur condition, not merely a
kernel compression.

Define the signed-permutation invariants

\[
 \tau:=abc,
 \qquad q:=a^2b^2+a^2c^2+b^2c^2.                          \tag{9.3}
\]

The singularity equation is

\[
 a^2+b^2+c^2=1+2\tau.                                    \tag{9.4}
\]

Substituting (9.1) into (9.2), separating monomials with all-even and all-odd parity, expressing
the two symmetric polynomials through
\(a^2+b^2+c^2,q,a^2b^2c^2\), and then using (9.4) gives the exact identity

\[
 E=\frac1{108}F(q,\tau),                                  \tag{9.5}
\]

where

\[
\begin{aligned}
F(q,\tau)={}&-2(4-\tau)q^2
 +(-2\tau^4+5\tau^3-\tau^2+37\tau+39)q\\
&+\tau^5-19\tau^4-15\tau^3-51\tau^2-150\tau+54.
\end{aligned}                                              \tag{9.6}
\]

Because \(|a|,|b|,|c|\le1\), one has \(\tau\le1\).  Therefore (9.6) is strictly concave in
\(q\) for fixed \(\tau\), and its minimum over the compact feasible \(q\)-interval occurs at an
endpoint.

To classify the endpoints, set \(x=a^2,y=b^2,z=c^2\).  For fixed \(\tau\), these variables lie in
\([0,1]\) and obey

\[
 x+y+z=1+2\tau,
 \qquad xyz=\tau^2.                                       \tag{9.7}
\]

An interior extremum of \(q=xy+xz+yz\) under (9.7) has two variables equal, by subtracting the
Lagrange multiplier equations.  A boundary extremum either has one variable equal to one, or (when
\(\tau=0\)) is a continuous limit of the same cases.

If one variable is one, (9.7) forces the other two to equal \(\tau\), with
\(0\le\tau\le1\), and \(q=\tau^2+2\tau\).  Direct factorization gives

\[
 F(\tau^2+2\tau,\tau)
 =2(1-\tau)(\tau^2-2\tau+3)(\tau^3+\tau^2+3\tau+9)\ge0.   \tag{9.8}
\]

If two variables equal \(r\), then (9.7) factors as

\[
 (r-\tau)(2r^2-r-\tau)=0.                                 \tag{9.9}
\]

The first factor is the preceding unit-variable case.  The second gives the parameterization

\[
 \tau=r(2r-1),
 \qquad q=r^2+2r(2r-1)^2,
 \qquad 0\le r\le1.                                      \tag{9.10}
\]

On this curve,

\[
 F=2(1-r)(4r^3+5r^2+2r+3)P_7(r),                          \tag{9.11}
\]

where

\[
 P_7(r)=32r^7-104r^6+132r^5-102r^4+115r^3-117r^2+41r+9.
\]

In the degree-seven Bernstein basis on \([0,1]\), the coefficients of \(P_7\) are

\[
 9,\quad\frac{104}7,\quad\frac{106}7,\quad\frac{92}7,
 \quad\frac{323}{35},\quad\frac{50}7,\quad\frac{38}7,\quad6. \tag{9.12}
\]

They are all positive, so \(P_7(r)>0\) on \([0,1]\).  Equations (9.8) and (9.11)--(9.12), together
with concavity in \(q\), prove \(F\ge0\) throughout the feasible rank-two set.  Therefore (9.2)
holds.  Combining with the separately treated rank-one case proves the following internal result:

> **Hostile-audited local candidate (E4).**  T080 holds for every singular \(3\times3\)
> unit-diagonal PSD correlation matrix, with arbitrary rank and nullity.

The independent audit checked the symbolic divisibility behind (9.5), the full-Schur criterion,
negative and zero \(\tau\), endpoint exhaustion, and Bernstein positivity.  No independent
reconstruction beyond that hostile audit or formal proof is claimed here.

### Sharp local upgrade to \(7/3\)

A subsequent exact invariant calculation replaces the coefficient two by the sharp coefficient
\(7/3\) in dimension three.  For the rank-two case, the rank-one-downdate numerator

\[
 \mathcal E_{7/3}
 :=\operatorname{tr}(\operatorname{adj}C)\det K_0
 -\frac73\operatorname{tr}(\operatorname{adj}C\operatorname{adj}K_0)
\]

satisfies \(324\mathcal E_{7/3}=3G(q,\tau)\), where

\[
\begin{aligned}
G(q,\tau)={}&(2\tau-9)q^2
+(-2\tau^4+5\tau^3+37\tau+51)q\\
&+\tau^5-15\tau^4-13\tau^3-51\tau^2-150\tau+18.
\end{aligned}                                             \tag{9.13}
\]

It is again concave in \(q\).  At the unit-variable endpoint,

\[
 3G=6(1-\tau)^3(\tau^3+\tau^2+3\tau+9),
\]

and at the equal-variable endpoint \(\tau=r(2r-1)\),

\[
 3G=6(1-r)^3(4r^3+5r^2+2r+3)P_5(r),
\]

where

\[
 P_5(r)=32r^5-40r^4+20r^3-30r^2+49r+3
\]

has degree-five Bernstein coefficients
\(3,64/5,98/5,127/5,121/5,34\).  The same feasible-endpoint classification therefore proves the
rank-two case.  Signed \(J_3\) has null eigenvalue exactly \(7/3\), so the constant is sharp.
I independently checked the \(324\) scaling, Sherman--Morrison orientation, parity/invariant
substitution, negative-\(\tau\) endpoint coverage, and both factorizations without finding a
blocker.  This is an E4 sharp \(n=3\) local candidate and has no conflict with the \(n=8\)
counterexample.

## 10. Checkpoints, computations, and unresolved objections

### Wall-clock checkpoints

- **17:28--17:47 +08:00:** 17:28 was a local clock sample in this run (not used for the
  conservative duration certificate below).  Established
  (1.1)--(1.3), found the exact \(J_3\) reverse-pair obstruction, the \(J_4\) cyclic-orbit
  obstruction, and the exact full-average repair (4.2).  Reported the checkpoint at 17:47.
- **17:47--18:22 +08:00:** derived the full-Schur dual-frame infimal convolution, exact
  harmonic-core counterexample, regular-simplex calculation, and the child lemma through size
  three.  Closed the complete \(n=3\) invariant proof and received a different-run hostile audit
  with no blocker.  Reported the second checkpoint at 18:22.
- **18:22--18:44 +08:00:** hostile-checked the volume-circuit boundary term,
  the sharp \(n=3\) constant \(7/3\), and an \(n=4\) symmetric family.  Independently verified the
  exact size-five child counterexample, then amplified its pole--simplex geometry to the exact
  \(n=8\) T080 counterexample (8.20)--(8.26).
- **18:44--19:32:02 +08:00:** completed the full \(n=8\) kernel Schur calculation and
  reverse-pair postmortem; developed the all-dimensional pole--simplex formula, its sharp
  asymptotic obstruction at \(3/2\), the hostile-audited \(a^2\le1/k\) subfamily, and the
  fixed-\(t\)/two-scale asymptotics.  Extended exact Bernstein certificates through \(k=22\)
  and derived the exact final-five-coefficient endpoint jet (8.38a)--(8.38c).
  The root process independently observed this agent active at **17:31:54 +08:00**; the final
  clock sample was **19:32:02 +08:00**, so the conservative observed active interval was
  **2 hours and 8 seconds**.  This—not the earlier local sample—is the duration certificate.

### Deterministic and E1 checks used only for route selection

The verification command is portable:

```text
python scripts/iter4_t080_pole_simplex_three_halves_scout.py
```

The deterministic scripts enumerated permutations in lexicographic order.  Exact formulae in
Sections 2--8 were reconstructed with integer/rational arithmetic; SymPy 1.14.0 was installed only
under the task-specific temporary directory `%TEMP%\rpcd_t080_sympy` for symbolic factoring.  No
repository dependency or credential file was changed.

The assigned subroute was constrained to edit only this document, so the pole--simplex finite-\(k\)
Bernstein and asymptotic generators were run from standard input and no separate script/evidence
file was created here.  The independently reconstructed \(n=8\) counterexample does have portable
artifacts at scripts/iter4_t080_exact_counterexample.py and
research/evidence/ITER4_T080_EXACT_COUNTEREXAMPLE_N8_2026_08_21.json.  Equations
(8.35)--(8.42), together with their exact \(k\)-ranges and float grids, specify what a follow-up
portable checker must reproduce.

An E1 search used seed `20260821`, ranks chosen uniformly from `1,...,n-1`, row-normalized Gaussian
Gram vectors, and full permutation enumeration for `n<=6`.  It found:

- individual reverse-pair defects below zero (expected after Section 2);
- reverse/cyclic-orbit defects below zero from `n=4` onward (already exactly certified by Section 3);
- no full-average T080 counterexample in that finite sample.

The nullspace threshold was `1e-8` and eigensolvers were float64.  The null result is not evidence
for the universal conjecture.

The null E1 result above also illustrates why generic Gaussian sampling missed the structured
repeated-pole/simplex counterexample in (8.20).  That counterexample was checked with exact rational
arithmetic in two ways:

1. all \(40320\) labelled permutations in lexicographic order;
2. the \(56\) exchangeability classes and the state recurrence (8.25).

Both returned \(1057837/531441\) for the normalized energy.  There was no floating-point tolerance
in either equality.  Float64 was used only afterward to print the decimal expansion.

### Cross-route hostile-audit note: zero-volume circuits

A requested check of the volume-circuit identity uncovered a separate exact boundary obstruction.
If \(U\) has orthonormal rows and \(P=I-U^\top U\), zero-volume \(r\)-subsets cannot simply be
included in the gradient of \(e_r(U^\top U)\), because their adjugates need not vanish.  With

\[
 H_{\rm sing}
 =\sum_{\det U_S=0}E_S\operatorname{adj}((U^\top U)_{SS})E_S^\top,
\]

the corrected second moment is

\[
 \mathbb E_{\rm vol}G_SG_S^\top=(r+1)P-H_{\rm sing},
\]

not \((r+1)P\) in general.  The exact diagnostic \(r=1,U=(1,0)\) gives
\(\mathbb E GG^\top=P\), not \(2P\).  The simpler identity is correct in general position.  This
correction was reported to and incorporated by the parent route.

### Precise remaining obstruction

Before (8.23) was found, the exact repair (5.8) would have required a noncircular allocation
\(u_M\), computable from the order and Gram dependencies, for which

\[
 \mathbb E[u_M]=u,
 \qquad
 \mathbb E[u_M^\top H_M^{-1}u_M]\le\frac12\lVert u\rVert^2. \tag{10.1}
\]

For (8.20) such an allocation cannot exist, because (5.8) is an equality and its optimum exceeds
\(\lVert u\rVert^2/2\).  Thus the obstruction is now logical rather than merely technical:
reverse pairing cannot prove the false universal target.  Using the same load for each pair,
averaging only cyclic shifts, dropping the commutator remainder, and the duplicate-child induction
all fail at explicitly recorded levels.

The remaining work is to determine which earlier RPCD reductions used T080, separate sufficient
from necessary implications, and replace T080 by a weaker valid inequality or an additional
structural hypothesis.  No conclusion about the original conjectured RPCD complexity follows from
the failure of this auxiliary matrix inequality alone.

The parent route also lifted the same
matrix to the exact SPD correlation
\(A_\mu=\mu I+(1-\mu)C\) at \(\mu=1/100\) and, by two rational enumerations, refuted the proposed
strong one-epoch fixed-\(A\) energy certificate M1.  See
scripts/iter4_t080_positive_mu_lift.py and
research/evidence/ITER4_T080_POSITIVE_MU_EXACT_LIFT_2026_08_21.json.  This finite lift still does
not refute the covariance-superoperator spectral conjecture C001: compensation across epochs and
covariance directions remains possible.  Moreover, any positive dimension-uniform replacement
constant would still be compatible with the desired big-\(O\) scaling; (8.34) only shows that such
a constant cannot exceed \(3/2\) within this proof template.
