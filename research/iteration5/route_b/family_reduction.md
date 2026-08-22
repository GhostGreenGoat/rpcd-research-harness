# Route B: exchangeable-group Bellman reduction

Status: exact combinatorial/algebraic reduction at E3 proof-draft level, with
float64 implementation checks.  None of the null searches below proves the
universal half-depth conjecture.

## 1. Why this route differs from Iteration 4

The inherited failures rule out using a fixed shallow prefix, a scalar bound
for every child, a word/reverse-word pair, or a complementary-prefix pathwise
comparison.  The present state instead retains the complete matrix average at
linear depth.  The only imposed structure is invariance under permutations
inside each of `G` coordinate groups.  Thus a dimension-`n` subset state is
replaced by its vector of remaining group counts; all without-replacement
weights and the determinant leaf remain exact.

Let the groups have current counts

\[
 m=(m_1,\ldots,m_G),\qquad |m|=\sum_gm_g.
\]

The correlation matrix has diagonal one, within-group off-diagonal entries
`a_g`, and cross-group entries `b_{gh}=b_{hg}`.  Every Bellman matrix invariant
under the group action is represented by

\[
 (d_g,o_g,c_{gh}),
\]

where `d_g` is a diagonal entry in group `g`, `o_g` a distinct within-group
entry, and `c_gh` a cross-group entry.  This is the full invariant matrix, not
only its compression to a kernel.

## 2. Determinant leaf

In the orthonormal group-indicator basis, the group-constant block of a
principal matrix is

\[
 R_{gg}=1+(m_g-1)a_g,
 \qquad R_{gh}=\sqrt{m_gm_h}\,b_{gh}.                    \tag{1}
\]

The remaining eigenvalues are `1-a_g`, with multiplicity `m_g-1`.  Therefore

\[
 \det A_m=\det R\prod_g(1-a_g)^{m_g-1}.                 \tag{2}
\]

Writing `S=R^{-1}`, the entries of `A_m^{-1}` are

\[
 \begin{aligned}
 (A_m^{-1})_{ii}
   &=\left(1-{1\over m_g}\right){1\over1-a_g}
     +{S_{gg}\over m_g},\\
 (A_m^{-1})_{ij}
   &={S_{gg}-(1-a_g)^{-1}\over m_g}\quad(i\ne j\text{ in }g),\\
 (A_m^{-1})_{ij}
   &={S_{gh}\over\sqrt{m_gm_h}}\quad(i\in g,j\in h).
 \end{aligned}                                           \tag{3}
\]

Multiplying (3) by (2) supplies the exact determinant-tail seed
`det(A_m) A_m^{-1}`.  The implementation evaluates only the `G by G` inverse
and determinant in float64; formulas (1)--(3) themselves are exact.

## 3. One Bellman lift in count coordinates

Suppose the first pivot belongs to group `p`.  The child counts are
`m-e_p`.  Let its invariant certificate be `X^(p)`.  The pivot-to-child
correlation vector is constant on groups:

\[
 \beta_h^{(p)}=a_p\; (h=p),\qquad
 \beta_h^{(p)}=b_{ph}\; (h\ne p).
\]

The vector `y^(p)=X^(p) beta^(p)` is also group-constant, with coordinate
value

\[
 y_h^{(p)}=
 [d_h^{(p)}+(m_h-\mathbf1_{h=p}-1)o_h^{(p)}]\beta_h^{(p)}
 +\sum_{\ell\ne h}(m_\ell-\mathbf1_{\ell=p})
 c_{h\ell}^{(p)}\beta_\ell^{(p)}.                       \tag{4}
\]

Put

\[
 s_p=\sum_h(m_h-\mathbf1_{h=p})\beta_h^{(p)}y_h^{(p)}.
\]

The lifted matrix

\[
 e_pe_p^\top+L_p^\top X^{(p)}L_p
\]

has pivot diagonal `1+s_p`, pivot-to-group-`h` entry `-y_h^(p)`, and equals
the child matrix away from the pivot.  Averaging over the `|m|` possible
labelled pivots gives

\[
 d_h={1+s_h+(m_h-1)d_h^{(h)}+
              \sum_{p\ne h}m_p d_h^{(p)}\over |m|},     \tag{5}
\]

\[
 o_h={-2y_h^{(h)}+(m_h-2)o_h^{(h)}+
              \sum_{p\ne h}m_p o_h^{(p)}\over |m|},     \tag{6}
\]

and, for `h != ell`,

\[
 c_{h\ell}={-y_\ell^{(h)}-y_h^{(\ell)}
 +(m_h-1)c_{h\ell}^{(h)}+(m_\ell-1)c_{h\ell}^{(\ell)}
 +\sum_{p\notin\{h,\ell\}}m_p c_{h\ell}^{(p)}\over |m|}. \tag{7}
\]

Terms with zero multiplicity are omitted.  Equations (2)--(7), iterated
`r=ceil(n/2)` times, compute the complete `H_r`.  The number of states is the
number of reachable count vectors rather than `2^n`; for the tested
`(8,13,21,34)` instance it is `49,876` at `n=76`.

## 4. Full generalized minimum

For every group with `m_g>1`, the group-transverse generalized eigenvalue is

\[
 (1-a_g)(d_g-o_g).                                      \tag{8}
\]

On the group-constant subspace, form `R` from (1) and

\[
 Q_{gg}=d_g+(m_g-1)o_g,\qquad
 Q_{gh}=\sqrt{m_gm_h}\,c_{gh}.                          \tag{9}
\]

The remaining generalized eigenvalues are those of
`R^(1/2) Q R^(1/2)`.  The reported coefficient is the minimum of (8) and the
full spectrum of (9).  Hence the search never substitutes a kernel Rayleigh
quotient for the Loewner target.

## 5. PSD family parameterization and spectral scales

To guarantee admissibility, choose vectors `w_g` and let
`W=(w_g^T)_g`.  Declare the boundary group-constant block to be
`C_red=WW^T`; then

\[
 \rho_g={\|w_g\|^2-1\over k_g-1},\qquad
 \rho_{gh}={w_g^Tw_h\over\sqrt{k_gk_h}}.                \tag{10}
\]

Provided `0 <= ||w_g||^2 <= k_g`, this is a PSD correlation matrix: its
transverse eigenvalues are `1-rho_g`, and its constant block is `WW^T`.
Using fewer latent dimensions than groups makes it singular.  The positive
lift

\[
 A=\mu I+(1-\mu)C                                      \tag{11}
\]

then has exact spectral floor `mu`.  Nearly rank-deficient `W` creates
additional eigenvalue scales between `mu` and order one, so (10)--(11) cover
the requested multiscale degenerations rather than only a single isotropic
boundary ray.

## 6. Finite controls

The reproducer performs the following hostile controls.

1. On a three-group `n=6` matrix, (2)--(7) agree entrywise with an unrelated
   generic `2^n` subset recursion; the recorded maximum absolute discrepancy
   is `2.22e-16`.
2. Flipping arbitrary signs on whole groups leaves the generalized minimum
   invariant; the recorded gap is zero.
3. The identity matrix returns coefficient exactly one.
4. A signed-rank-one `n=1000, mu=0.98` control approaches the known sharp
   half constant from above.
5. For the leading `n=76` candidate, building the complete `76 by 76`
   matrices from (8)--(9) reproduces the reduced coefficient within
   `6.11e-16`.  An independent 3,000-order Monte Carlo evaluation of the
   pathwise prefix-plus-leaf quadratic form differs from the DP prediction by
   `-1.39` standard errors.

Controls 1--5 test the implementation and conventions; they do not certify a
general inequality.

## 7. Current search boundary

The three principal hostile avenues are:

- three rank-two groups with frustrated prototype signs (`n=60`);
- four uneven groups with rank-three, potentially multiscale couplings
  (`n=39` through `116`);
- a duplicate-pole group coupled to three simplex-arranged leaf groups
  (`n=56`).

A separate five/six-group one-factor search tests heterogeneous block
loadings.  The smallest value so far is above `1/2`; consequently no rational
reconstruction or counterexample claim is triggered.  All such null results
remain E1.
