# Hostile audit: M1 small-gap Schur reduction and exact boundary certificate

Date: 2026-08-21

Audited artifacts:

- `docs/ITER3_M1_STRONG_ONE_EPOCH_ENERGY.md`, Sections 5.1--5.2;
- `scripts/certify_m1_two_pole_hexagon.py`;
- `research/evidence/M1_TWO_POLE_HEXAGON_EXACT_2026_08_21.json`.

This audit is independent of route M2.  It reconstructs the block perturbation, the complete
kernel/range representation, and the exact quadratic-form computation.  It does not promote the
universal boundary conjecture `S_C >= 2I`, which remains open.

## 1. Verdict

### Conclusion-level blockers

**None found.**  The following claims survive independent reconstruction:

1. the small eigenvalues of
   `A_mu^(1/2) K(A_mu) A_mu^(1/2)` have first-order coefficients equal to the eigenvalues of the
   Schur complement `S_C`;
2. the four coefficient types listed in Section 5.2 cover all five dimensions of `ker(C)` for the
   two-pole/hexagon matrix;
3. the omitted partner in the two-dimensional ring-harmonic block has exactly the same coefficient;
4. the raw-to-orthonormal normalization in the one-dimensional trivial Schur complement is correct;
5. the exact minimum is the pole-difference coefficient and is strictly larger than 2.

### Remaining verifier-completeness blocker

The current exact script is **not self-contained as a block-coverage verifier**.  It assumes, but
does not assert, that its four reported coefficient types exhaust `ker(C)` and that every omitted
off-block coupling is zero.  A hand-coded or future-edited matrix could therefore make the script
print `minimum > 2` while an omitted block or coupling invalidated that conclusion.  This is a P1
artifact-hardening blocker for treating the script alone as a reusable verifier.  It does not
invalidate the current finite-family conclusion because the missing checks were independently
performed exactly in this audit; see Sections 3--5.

No ledger status is changed by this document.

## 2. Independent reconstruction of the Schur perturbation

Let `C` be a singular unit-diagonal PSD matrix and put

\[
 A_\mu=\mu I+(1-\mu)C.
\]

Use the orthogonal decomposition

\[
 \mathbb R^n=\mathcal N\oplus\mathcal R,
 \qquad \mathcal N=\ker C,
 \qquad \mathcal R=\mathcal N^\perp.
\]

Write `C_R` for the positive-definite restriction of `C` to `R`, and

\[
 K_\mu=K(A_\mu),\qquad K_0=K_0(C).
\]

Every permuted triangular factor has diagonal one.  Its inverse is a finite polynomial in its
strictly lower-triangular entries.  Since the off-diagonal entries of `A_mu` depend affinely on
`mu`,

\[
 K_\mu=K_0+O(\mu).                                          \tag{A1}
\]

On `N` and `R`, respectively,

\[
 A_\mu^{1/2}
 =\begin{pmatrix}
   \sqrt\mu I_{\mathcal N}&0\\
   0&C_{\mathcal R}^{1/2}+O(\mu)
  \end{pmatrix}.                                            \tag{A2}
\]

Consequently, for

\[
 H_\mu:=A_\mu^{1/2}K_\mu A_\mu^{1/2},
\]

the block expansion is

\[
 H_\mu=
 \begin{pmatrix}
  \mu(K_0)_{NN}+O(\mu^2)&
  \sqrt\mu(K_0)_{NR}C_R^{1/2}+O(\mu^{3/2})\\
  \sqrt\mu C_R^{1/2}(K_0)_{RN}+O(\mu^{3/2})&
  C_R^{1/2}(K_0)_{RR}C_R^{1/2}+O(\mu)
 \end{pmatrix}.                                             \tag{A3}
\]

The constant-order lower-right block is positive definite: `C_R>0` and `K_0>0`.  For a candidate
small eigenvalue `lambda=O(mu)`, Feshbach/Schur elimination gives the effective null-space matrix

\[
\begin{aligned}
 &\mu(K_0)_{NN}
 -\mu(K_0)_{NR}C_R^{1/2}
 \left[C_R^{1/2}(K_0)_{RR}C_R^{1/2}\right]^{-1}
 C_R^{1/2}(K_0)_{RN}
 +o(\mu)\\
 &\qquad=\mu\left[
 (K_0)_{NN}-(K_0)_{NR}(K_0)_{RR}^{-1}(K_0)_{RN}
 \right]+o(\mu)\\
 &\qquad=\mu S_C+o(\mu).                                   \tag{A4}
\end{aligned}
\]

The dependence of the resolvent on the small eigenvalue changes (A4) only at order `mu^2`.
All remaining eigenvalues stay bounded away from zero.  Hence

\[
 \lambda_{\min}(H_\mu)
 =\mu\lambda_{\min}(S_C)+o(\mu).                            \tag{A5}
\]

The exact energy identity gives

\[
 r_E(A_\mu)=1-\lambda_{\min}(H_\mu),                        \tag{A6}
\]

so Section 5.1's formula

\[
 r_E(A_\mu)=1-\mu\lambda_{\min}(S_C)+o(\mu)
\]

has the correct Schur complement, sign, normalization, and minimum-eigenvalue operation.

Two qualifications are important but nonblocking:

- `K_mu=K_0+O(mu)`, rather than mere convergence, is what makes the displayed remainder immediate;
- `q_(n,mu)=(1-mu/n)^(2n)` is the active maximum only for sufficiently small positive `mu`, which is
  exactly the regime of this perturbation.

## 3. Complete irreducible decomposition for the exact family

Let

\[
 a=\frac4{\sqrt{21}}.
\]

The two pole vectors are both `e_3`; the six ring vectors have latitude `a` and angles
`2 pi j/6`.  The coordinate correlation matrix is invariant under

\[
 G=S_2\times D_6.
\]

Relabeling a uniformly random order by any group element shows

\[
 P_g^\top K_0 P_g=K_0\qquad(g\in G).                        \tag{A7}
\]

Thus `K_0`, its `N/R` blocks, and `S_C` respect the real irreducible decomposition.

An explicit orthogonal decomposition is as follows.  Semicolons separate the two pole coordinates
from the six ring coordinates.

### Kernel, dimension 5

\[
 p_-=(1,-1;0,0,0,0,0,0),                                   \tag{A8}
\]

\[
 h_{2,c}=(0,0;2,-1,-1,2,-1,-1),                            \tag{A9}
\]

\[
 h_{2,s}=(0,0;0,1,-1,0,1,-1),                              \tag{A10}
\]

\[
 h_3=(0,0;1,-1,1,-1,1,-1),                                 \tag{A11}
\]

\[
 n_0=(-3a,-3a;1,1,1,1,1,1).                                \tag{A12}
\]

The pair `(h_2c,h_2s)` is the two-dimensional second ring harmonic.  It is one real irreducible
`D_6` block.  The other three displayed types are one-dimensional inequivalent irreducibles.

### Range, dimension 3

The first ring harmonic contributes a two-dimensional range block, for example

\[
 h_{1,c}=(0,0;2,1,-1,-2,-1,1),                             \tag{A13}
\]

\[
 h_{1,s}=(0,0;0,1,1,0,-1,-1),                              \tag{A14}
\]

and the trivial range direction is

\[
 r_0=(1,1;a,a,a,a,a,a).                                    \tag{A15}
\]

Direct exact multiplication gives

\[
 Cp_-=Ch_{2,c}=Ch_{2,s}=Ch_3=Cn_0=0,                        \tag{A16}
\]

\[
 Ch_{1,c}=\frac57h_{1,c},\qquad
 Ch_{1,s}=\frac57h_{1,s},\qquad
 Cr_0=\frac{46}{7}r_0.                                     \tag{A17}
\]

Therefore `rank(C)=3`, the nonzero eigenvalues are `5/7,5/7,46/7`, and (A8)--(A12) exhaust
`ker(C)`.  There is no missing null block.

By (A7), all inequivalent blocks have zero coupling.  A symmetric operator commuting with the
rotation and reflection on the two-dimensional second-harmonic block is scalar there.  Hence one
representative, `h_2c`, determines both eigenvalues; omission of `h_2s` from the production script
is mathematically harmless once this representation argument is supplied.

Only `n_0` and `r_0` are copies of the same trivial representation, so they may couple.  This is
exactly the coupling eliminated by the script's `trivial_schur` calculation.

## 4. Audit of the Schur normalization in the script

Let

\[
 N_0=\langle n_0,n_0\rangle,
 \qquad R_0=\langle r_0,r_0\rangle,
\]

and define raw exact quadratic forms

\[
 u=\langle n_0,K_0n_0\rangle,
 \quad v=\langle r_0,K_0r_0\rangle,
 \quad w=\langle n_0,K_0r_0\rangle.
\]

In the orthonormal basis `(n_0/sqrt(N_0),r_0/sqrt(R_0))`, the `K_0` block is

\[
 \begin{pmatrix}
  u/N_0&w/\sqrt{N_0R_0}\\
  w/\sqrt{N_0R_0}&v/R_0
 \end{pmatrix}.                                             \tag{A18}
\]

Its null-space Schur coefficient is

\[
 \frac{u}{N_0}
 -\frac{w^2}{N_0R_0\,(v/R_0)}.                              \tag{A19}
\]

The script computes exactly (A19): `null_value=u/N_0`, `range_value=v/R_0`, and its subtraction is
`cross_squared/(N_0 R_0 range_value)`.  There is no missing norm, extra norm, or square-root factor.

The triangular solve is also in the correct order.  For each chronological order it solves the
unit lower-triangular system

\[
 M_\pi z=P_\pi^\top v
\]

and accumulates dot products of the solutions.  Thus it computes

\[
 v^\top\mathbb E[(M_\pi M_\pi^\top)^{-1}]w
\]

rather than an inverse with the multiplication order reversed.

The quadratic-field representation
`(u,v) = u+v sqrt(21)` is correct, as is its multiplication rule.  In particular,
`(0,4/21)` equals `4/sqrt(21)`, and the ring correlation is

\[
 \frac{16}{21}+\frac5{21}\cos(2\pi(j-k)/6).
\]

All final diagonal and Schur coefficients are rational, so the comparison with the integer 2 is an
exact `Fraction` comparison; no floating-point sign decision occurs.

## 5. Independent exact reproduction

The production verifier was run with

```text
<bundled-python> scripts/certify_m1_two_pole_hexagon.py
```

with no seed and no tolerance.  It completed successfully and reproduced all four fractions in the
document and evidence JSON.  The minimum was

\[
 \frac{54099374095982388041}{26363285800809721344}
 =2+\frac{1372802494362945353}{26363285800809721344}.        \tag{A20}
\]

An independent augmented exact enumeration used the same `8!` orders but added the missing
`h_2s` vector and the two first-harmonic range probes from (A13)--(A14).  Again there was no seed or
tolerance.  It found:

```text
only nonzero off-diagonal K0 block:
  <n0,K0 r0> = (1934590183380900055/52726571601619442688) sqrt(21)

normalized h2c coefficient:
  11509555074695071519/5021578247773280256
normalized h2s coefficient:
  11509555074695071519/5021578247773280256
<h2c,K0 h2s> = 0
```

All exact kernel/range actions in (A16)--(A17) passed.  Thus the cross-block zeros assumed by the
production script are true for the current hard-coded family, and the two-dimensional block has
the claimed repeated eigenvalue.

## 6. Blocker and nonblocker table

| Item | Audit result | Classification |
|---|---|---|
| `K_mu -> K_0` and the first-order block scales | Correct; polynomial dependence actually gives `K_mu=K_0+O(mu)` | Nonblocker |
| Use of the Schur complement of `K_0`, rather than of `C_R^(1/2)K_RR C_R^(1/2)` | Correct; the two `C_R^(1/2)` factors cancel as in (A4) | Nonblocker |
| Claim that the minimum first-order coefficient is `lambda_min(S_C)` | Correct; range eigenvalues remain uniformly positive and all null eigenvalues are `mu eig(S_C)+o(mu)` | Nonblocker |
| Kernel dimension and listed irreducibles | Complete: multiplicities `1+2+1+1=5` | Nonblocker |
| Omitted sine partner of the second harmonic | Same exact coefficient; block is scalar by `D_6` symmetry | Nonblocker mathematically; missing script assertion |
| Coupling of nontrivial null irreps to range | Exactly zero; independently recomputed | Nonblocker mathematically; missing script assertion |
| Trivial Schur normalization | Correct, including both raw vector norms | Nonblocker |
| Quadratic-field arithmetic and comparison with 2 | Correct and exact | Nonblocker |
| Evidence JSON fractions versus verifier output | Exact match | Nonblocker |
| Script verifies `rank(C)=3`, kernel coverage, and all ignored cross terms | It does not | **P1 verifier-completeness blocker** |
| Script writes or compares the evidence JSON itself | It only prints; the JSON can drift after future edits | P2 reproducibility hardening, not a current conclusion blocker |
| Generic check `value not in [trivial_cross]` for irrational components | Key-insensitive equality could accidentally exempt another entry equal to the cross value | P2 defensive-code issue; inactive on the current exact data |

## 7. Required hardening before treating the script as a standalone verifier

The script should be extended to perform these exact assertions itself:

1. include the full five-vector null basis and three-vector range basis in Section 3;
2. assert (A16)--(A17), orthogonality, and total dimension eight;
3. accumulate all block cross terms and assert that only the `n_0/r_0` term is nonzero;
4. assert equality of the normalized `h_2c` and `h_2s` coefficients and their zero cross term;
5. assert positivity of every norm and of the trivial range diagonal before division;
6. select the allowed irrational entry by its dictionary key, not by tuple-value equality;
7. generate the evidence JSON or compare every stored rational string with freshly computed output.

Until those checks are added, the correct status is:

- the current two-pole/hexagon finite coefficient: independently reproduced exact certificate with
  no conclusion-level blocker found;
- `S_C >= 2I` for all singular correlation matrices: still an open proof target;
- the production script by itself: exact arithmetic is sound, but block coverage is not yet
  self-verifying.
