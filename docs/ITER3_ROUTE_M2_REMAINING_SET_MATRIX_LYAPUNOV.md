# Iteration 3, route M2: remaining-set matrix Lyapunov certificates

Date: 2026-08-21

## Status and objective

This note tries to prove the strong one-epoch energy inequality

\[
 \mathbb E_\pi[T_\pi^\top A T_\pi]\preceq q_{n,\mu}A,
 \qquad
 q_{n,\mu}:=\max\left\{(1-1/n)^n,(1-\mu/n)^{2n}\right\},
 \tag{M2.1}
\]

where `diag(A)=1` and `lambda_min(A)=mu`.  Equivalently, in the residual formulation of
route A, the desired statement is

\[
 K_{[n]}\succeq (1-q_{n,\mu})A^{-1}.                         \tag{M2.2}
\]

The exact identities and certificate hierarchies below are **E3 proof drafts**.  They have not had
an independent reconstruction; they subsequently passed the hostile audit in
`docs/ITER3_AUDIT_M2_BELLMAN.md`.  The two numerical values used to expose a failed
certificate are evaluations of exact rational formulae; they are not evidence for a universal
claim.  This note does not prove (M2.1), C001, or the uniform
`O(n/mu log(1/epsilon))` complexity target.

The positive output is a monotone, direction-preserving Bellman certificate hierarchy.  Its first
nontrivial member has a closed form in `B^{-1}`, its inverse-diagonal leverage scores, and principal
determinants.  The negative output is a precise explanation of why scalar `B^{-1}` induction and a
fixed basis consisting only of `B^{-1}`, `I`, and the first Schur-loss moment do not close.

## 1. Local residual Bellman recursion

Let `B` be an `m` by `m` unit-diagonal SPD principal matrix.  Write

\[
 G:=B^{-1}.
\]

If coordinate `i` is selected first, let `C_i=B_{-i,-i}` and, after moving `i` to the first
position, write

\[
 B=\begin{pmatrix}1&b_i^\top\\b_i&C_i\end{pmatrix},
 \qquad L_i=[-b_i\ \ I].
\]

Thus the residual on the remaining coordinates changes as `h -> L_i h`.  The exact expected
energy-decrease matrix satisfies

\[
 K(B)=\frac1m\sum_{i=1}^m
 \left(e_i e_i^\top+L_i^\top K(C_i)L_i\right),
 \qquad K([1])=[1].                                          \tag{M2.3}
\]

Define the Schur complement and its diagonal matrix by

\[
 s_i:=\frac1{G_{ii}},
 \qquad S_B:=\operatorname{Diag}(s_1,\ldots,s_m).
\]

Route A gives the rank-one order loss

\[
 D_i:=G-e_i e_i^\top-L_i^\top C_i^{-1}L_i\succeq0.          \tag{M2.4}
\]

The following coordinate-free form makes its direction explicit.

### Lemma M2.1 (exact leverage representation of the first Schur loss)

For every `i`,

\[
 \boxed{D_i=s_i(G-I)e_i e_i^\top(G-I).}                      \tag{M2.5}
\]

Consequently, with `bar(D)_B=m^{-1} sum_i D_i`,

\[
 \boxed{
 \overline D_B=\frac1m(G-I)S_B(G-I).
 }                                                            \tag{M2.6}
\]

Moreover, the only nonzero generalized eigenvalue of `(D_i,G)` is `1-s_i`; hence

\[
 D_i\preceq(1-s_i)G\preceq(1-\mu)G.                         \tag{M2.7}
\]

**Proof draft.**  The block inverse formula gives

\[
 G e_i=s_i^{-1}\begin{pmatrix}1\\-C_i^{-1}b_i\end{pmatrix}.
\]

Therefore the vector in the rank-one factorization from route A is
`s_i(G-I)e_i`, which proves (M2.5); summing proves (M2.6).  The generalized-eigenvalue statement is
the rank-one computation already recorded in route A.  Since `B >= mu I`, `s_i>=mu`, proving
(M2.7).  `square`

If all children are replaced by a scalar certificate `K(C_i) >= c C_i^{-1}`, (M2.3)--(M2.4)
give the exact lifted lower bound

\[
 K(B)\succeq
 cG+\frac{1-c}{m}I-c\overline D_B.                           \tag{M2.8}
\]

This is the cleanest form of the scalar-induction bottleneck: all useful directional information
is in `bar(D)_B`.

## 2. A monotone determinant-tail Bellman hierarchy

The Gram-defect result from route C gives, for every local principal problem,

\[
 K(B)\succeq \det(B)B^{-1}.                                  \tag{M2.9}
\]

Instead of applying (M2.9) only at the full matrix, apply it to the random remaining principal
problem after revealing a prefix.

Define `H_0(B)` and its Bellman lifts recursively by

\[
 H_0(B):=\det(B)B^{-1},                                      \tag{M2.10}
\]

\[
 H_{r+1}(B):=\frac1m\sum_{i=1}^m
 \left(e_i e_i^\top+L_i^\top H_r(C_i)L_i\right).            \tag{M2.11}
\]

For a one-dimensional matrix, all `H_r([1])` are set equal to `[1]`.

### Theorem candidate M2.2 (monotone determinant-tail certificates)

For every unit-diagonal SPD `B` of size `m` and every `r>=0`,

\[
 \boxed{
 \det(B)B^{-1}=H_0(B)
 \preceq H_1(B)\preceq\cdots\preceq H_{m-1}(B)=K(B).
 }                                                            \tag{M2.12}
\]

In particular, every `H_r(B)` is a certified lower bound on the total energy decrease, and the
hierarchy becomes exact after at most `m-1` Bellman lifts.

**Proof draft.**  Validity of `H_0<=K` is (M2.9), and (M2.3) preserves Loewner lower bounds.
It remains to establish the first monotonic step.  Put

\[
 d=\det B,\qquad \delta_i=\det C_i.
\]

Schur factorization gives `d=s_i delta_i`; Hadamard's inequality gives `0<delta_i<=1`.  For each
possible first coordinate,

\[
\begin{aligned}
 &e_i e_i^\top+\delta_iL_i^\top C_i^{-1}L_i-dG\\
 &\quad=\delta_i\bigl((1-s_i)G-D_i\bigr)
       +(1-\delta_i)e_i e_i^\top\succeq0,                   \tag{M2.13}
\end{aligned}
\]

where the last step uses (M2.7) with its sharp coefficient `1-s_i`.  Averaging proves
`H_1>=H_0`.  Inductively, `H_r(C_i)<=H_{r+1}(C_i)` for every child, and (M2.11) proves the next
monotonic step.  Once `r>=m-1`, all leaves of the recursion are one-dimensional exact problems, so
(M2.3) gives `H_r(B)=K(B)`.  `square`

The probabilistic interpretation is useful: reveal `r` coordinates and account for their exact
decrease; on the remaining principal problem use the pathwise Gram-determinant certificate.  An
extra reveal cannot weaken the certificate, which is the content of (M2.13).

### Lemma M2.3 (closed form of the first lift)

Let `d=det(B)` and `G=B^{-1}`.  Then

\[
 \boxed{
 H_1(B)=\frac1m\left[
 d\,\operatorname{tr}(G)G-d(G-I)^2
 +I-d\operatorname{Diag}(\operatorname{diag}G)
 \right].
 }                                                            \tag{M2.14}
\]

**Proof draft.**  Since `delta_i=d/s_i=dG_ii`, (M2.4) gives

\[
\begin{aligned}
H_1(B)
 &=\frac1m\sum_i
 \left[\delta_iG-\delta_iD_i+(1-\delta_i)e_ie_i^\top\right].
\end{aligned}
\]

Now

\[
 \sum_i\delta_i=d\operatorname{tr}G,
 \qquad
 \sum_i\delta_iD_i=d(G-I)^2,
\]

where the second identity is the exact cancellation of the Schur leverage `s_i` in (M2.5).
The diagonal term is `I-d Diag(diag G)`, proving (M2.14).  `square`

This cancellation is the main positive M2 result.  It replaces a sum of differently oriented
rank-one Schur losses by one explicit matrix polynomial plus a diagonal leverage correction.

## 3. The corresponding subset-dependent Lyapunov matrices

Let `R` be the actual remaining coordinate set, `B=A_RR`, and
`h=(Ax)_R=A_{R,:}x`.  Define

\[
 W_R^{(r)}
 :=A-A_{:,R}H_r(B)A_{R,:}.                                  \tag{M2.15}
\]

Use the terminal convention `W_empty^(r)=A`.  Consecutive depths satisfy the exact certificate
Bellman relation

\[
 W_R^{(r+1)}={1\over|R|}\sum_{i\in R}
 U_i^\top W_{R\setminus\{i\}}^{(r)}U_i.                    \tag{M2.15a}
\]

Since `H_r(B)<=K(B)`, the exact remaining-sweep expectation obeys

\[
 \mathbb E[x_{\rm end}^\top A x_{\rm end}\mid x,R]
 \le x^\top W_R^{(r)}x.                                     \tag{M2.16}
\]

Equation (M2.11) is precisely the residual-coordinate version of a Bellman lift of these matrices:
at depth `r+1`, average the depth-`r` child certificate after the first update.  Thus
`W_R^(r)` is an explicit remaining-set matrix Lyapunov upper certificate, not a scalar estimate
that forgets `R`.

At a full epoch, put

\[
 c_r(A):=\lambda_{\min}\!\left(A^{1/2}H_r(A)A^{1/2}\right).
                                                                    \tag{M2.17}
\]

Since `0<H_r(A)<=K(A)` and the exact terminal-energy matrix is PSD, one has
`0<c_r(A)<=1`.

Then

\[
 \mathbb E[T_\pi^\top A T_\pi]
 \preceq(1-c_r(A))A.                                        \tag{M2.18}
\]

Fresh independent epochs therefore give the genuine finite-time bounds

\[
 \mathbb E\|x_k\|_A^2
 \le(1-c_r(A))^k\|x_0\|_A^2,                               \tag{M2.19}
\]

\[
 \mathbb E\|x_k\|_A
 \le(1-c_r(A))^{k/2}\|x_0\|_A.                             \tag{M2.20}
\]

This controls expectation of the distance (and, more strongly, expectation of squared distance),
not merely the distance of the expected iterate.  It yields a coordinate-update bound

\[
 N=O\!\left(\frac{n}{c_r(A)}\log\frac1\varepsilon\right)
                                                                    \tag{M2.21}
\]

for squared `A`-distance, with a factor two in the logarithmic exponent for expected `A`-distance.
By (M2.12), `c_r(A)>=det(A)`, so every level recovers or improves the previous determinant bound.
At depth `n-1`, `c_r` is the exact one-epoch `A`-energy contraction coefficient.  What is not known
is a dimension-uniform proof that some tractable level satisfies

\[
 c_r(A)\ge1-q_{n,\mu}\quad\text{or even}\quad c_r(A)\ge c\mu
                                                                    \tag{M2.22}
\]

with a universal `c>0` before the hierarchy has effectively reconstructed the full problem.

## 4. How the two-step without-replacement correction enters

There is a second direction-preserving hierarchy that accounts only for a revealed prefix.  For
`0<=t<=m`, set

\[
 J_0(B)=0,
 \qquad
 J_{t+1}(B)=\frac1m\sum_i
 \left(e_i e_i^\top+L_i^\top J_t(C_i)L_i\right).            \tag{M2.23}
\]

with `J_0(empty)=0`.

Then `J_t(B)` is the exact expected energy-decrease matrix after the first `t` distinct coordinates,

\[
 0=J_0(B)\preceq J_1(B)\preceq\cdots\preceq J_m(B)=K(B).
                                                                    \tag{M2.24}
\]

The first two members have closed forms

\[
 J_1(B)=\frac1m I,                                           \tag{M2.25}
\]

\[
 \boxed{
 J_2(B)=\frac{(2m-1)I-2B+
 \operatorname{Diag}(\operatorname{diag}B^2)}{m(m-1)}.
 }                                                            \tag{M2.26}
\]

To obtain (M2.26), move to energy coordinates, insert the exact two-step WOR residual matrix from
route C, and congruence-transform the two-step energy drop back by `B^{-1/2}`.  The diagonal term
comes from
`B^{-1/2} [sum_i (B^2)_ii P_i] B^{-1/2}=Diag(diag(B^2))`.

The two-step PSD advantage over sampling with replacement implies

\[
 J_2(B)\succeq
 \left[1-(1-\mu/m)^2\right]B^{-1}.                           \tag{M2.27}
\]

Every local principal matrix still satisfies `B>=mu I` by Cauchy interlacing; this is the spectral
floor used in (M2.27).

This is a useful non-isotropic child seed for (M2.11), but its scalar consequence alone gives only
`c=2mu/m-mu^2/m^2`.  Hence it yields
`O(n^2/mu log(1/epsilon))` coordinate updates at the full dimension, not the desired
`O(n/mu log(1/epsilon))`.  Equations (M2.23)--(M2.24) are the correct conditional continuation;
simply multiplying the two-step factor over disjoint pairs is invalid because the state and the
remaining set are correlated.

## 5. Why the natural low-dimensional matrix basis does not close

The leverage identity suggests an ansatz using

\[
 G,\qquad I,\qquad \overline D_B.
\]

Suppose a child certificate contains

\[
 aC_i^{-1}+bI-c\overline D_{C_i}.
\]

The three Bellman images are

\[
 \frac1m\sum_iL_i^\top C_i^{-1}L_i
 =G-\overline D_B-\frac1mI,                                 \tag{M2.28}
\]

\[
 \frac1m\sum_iL_i^\top L_i
 =:\mathcal J_B
 =\frac{mI-2B+\operatorname{Diag}(\operatorname{diag}B^2)}m,\tag{M2.29}
\]

and

\[
 \mathcal R_B
 :=\frac1m\sum_iL_i^\top\overline D_{C_i}L_i.               \tag{M2.30}
\]

Thus the parent lower bound becomes

\[
 aG+\frac{1-a}{m}I-a\overline D_B+b\mathcal J_B-c\mathcal R_B.
                                                                    \tag{M2.31}
\]

The `I` term already creates the new directions `B` and `Diag(diag B^2)`.  More seriously,
`R_B` contains inverse-diagonal Schur weights of every codimension-one child and hence codimension-two
principal-minor data.  It is not reduced by (M2.5)--(M2.6).  Iterating creates the successive
Schur-loss moments along the deletion chain.  Therefore the proposed fixed basis is not Bellman
closed without an additional, presently missing inequality that compresses `R_B` back to earlier
moments.  The determinant-tail hierarchy retains these new moments instead of discarding them.

This is an algebraic closure obstruction, not a proof that no clever finite basis exists.

## 6. A sharp directional obstruction to averaging the `D_i`

One might hope that the average in (M2.6) always gains a factor `1/m`, for example

\[
 \overline D_B\preceq \frac{C}{m}G
\]

with a universal constant `C`.  This is false.

Let `C` be a unit-diagonal PSD correlation matrix with a simple zero eigenvalue, unit null vector
`u`, and `u_i != 0` for every coordinate.  Set

\[
 B_\mu=\mu I+(1-\mu)C.
\]

As `mu` decreases to zero, for fixed `C,m` and with every `O(1)` understood in operator norm,

\[
 G_\mu=B_\mu^{-1}=\mu^{-1}uu^\top+O(1),
 \qquad
 s_i=\frac{\mu}{u_i^2}+O(\mu^2).
\]

Using (M2.5),

\[
 D_i
 =s_i(G_\mu-I)e_i e_i^\top(G_\mu-I)
 =\mu^{-1}uu^\top+O(1)
 =G_\mu+O(1).                                                \tag{M2.32}
\]

Every first-step Schur loss therefore aligns with the same nearly singular direction, and

\[
 \lambda_{\max}\!\left(
 B_\mu^{1/2}\overline D_{B_\mu}B_\mu^{1/2}
 \right)\longrightarrow1.                                  \tag{M2.33}
\]

The lower limit follows by testing the near-null vector.  The matching upper limit uses
`bar(D)_(B_mu)<=G_mu`, hence
`B_mu^(1/2) bar(D)_(B_mu) B_mu^(1/2)<=I`; these two bounds give the stated squeeze.

The regular-simplex correlation matrix, with all off-diagonal entries `-1/(m-1)`, is an explicit
example.  Thus direction averaging is not uniformly available at the first deletion.

The opposite geometry also matters.  For the signed rank-one structured family

\[
 B_\mu=\mu I+(1-\mu)\mathbf1\mathbf1^\top,
\]

the minimum eigenspace has dimension `m-1`, `S_B` is scalar, and the normalized eigenvalue of
`bar(D)_B` on that eigenspace tends to `1/(m-1)`.  Here the first-step losses do disperse, but every
principal child remains badly conditioned.  A scalar child certificate applies its worst rate in
all directions and throws away precisely this anisotropy.  A successful universal induction must
handle both geometries simultaneously:

1. simple near-null mode: losses align, but deleting a coordinate improves the child spectrum;
2. high-multiplicity near-null mode: losses disperse, but the children remain ill-conditioned.

Using the worst scalar fact from each geometry at the same time reproduces the crude failed
recurrence from route A.

## 7. Exact rational barrier for the first determinant lift

The closed certificate (M2.14) can be substantially stronger than `det(B)B^{-1}`, but one lift is
not enough for the target, even on the known signed rank-one structured family.

Take `m=3`, `mu=1/5`, and

\[
 B=\frac15 I+\frac45\mathbf1\mathbf1^\top.
\]

Its eigenvalues are `1/5,1/5,13/5`, and `det(B)=13/125`.  Since `H_1(B)` commutes with `B`, (M2.14)
can be evaluated on the two eigenspaces.  Its smallest generalized eigenvalue relative to `B^{-1}`
is

\[
 c_1(B)=\lambda_{\min}(B^{1/2}H_1(B)B^{1/2})
 =\frac{547}{1875}\approx0.291733.                           \tag{M2.34}
\]

The strong target requires

\[
 1-q_{3,1/5}
 =1-\left(\frac{14}{15}\right)^6
 =\frac{3861089}{11390625}
 \approx0.338971.                                            \tag{M2.35}
\]

The exact gap is

\[
 (1-q_{3,1/5})-c_1(B)
 =\frac{538064}{11390625}>0.                                 \tag{M2.36}
\]

This does not refute (M2.1): the exact structured-family sweep is already known to satisfy the
target.  It proves only that `H_1` cannot be the final uniform certificate.  The missing gain is in
the anisotropic child matrices retained by deeper levels of (M2.11).

## 8. Outcome and next falsifiable lemma

The M2 attempt produced the following reusable objects:

1. the exact leverage representation (M2.5)--(M2.6);
2. the monotone determinant-tail Lyapunov hierarchy (M2.10)--(M2.12), exact after `m-1` lifts;
3. the closed first lift (M2.14), whose Schur weights cancel exactly;
4. the prefix/two-step direction-preserving hierarchy (M2.23)--(M2.27);
5. the finite-time per-instance bound (M2.19)--(M2.21).

The full `O(n/mu log(1/epsilon))` conclusion remains open because no uniform estimate of the form
`c_r(A)>=c mu` has been proved without expanding essentially the whole deletion hierarchy.

A concrete next lemma, stronger than scalar induction but weaker than evaluating all subsets, is:

> Find a PSD compression of the second Schur-loss moment `R_B` in (M2.30), with coefficients that
> depend on the actual leverage vector `(s_i)` and the child spectral floors, such that the class
> generated by `G`, `I`, `bar(D)_B`, and the compression is Bellman stable and yields
> `c_{n-1}(A)>=1-q_{n,mu}` (or at least `>=c mu`).

Any proposed compression must be checked against both asymptotic geometries in Section 6 and the
exact structured barrier (M2.34)--(M2.36).  A bound that replaces every `s_i` by `mu`, or every
`D_i` by `(1-mu)G`, has already discarded the information needed to pass these tests.
