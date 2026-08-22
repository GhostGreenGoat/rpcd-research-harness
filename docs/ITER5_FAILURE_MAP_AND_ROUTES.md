# Iteration 5: inherited failure map and route selection

Start: 2026-08-21 19:37:57 +08:00.  Normalization: `diag(A)=I` and
`mu=lambda_min(A)`.  The main target is

\[
H_{\lceil n/2\rceil}(A)\succeq {\mu\over2}A^{-1}.          \tag{I5.1}
\]

If (I5.1) holds, expected `A`-distance has coordinate complexity
`(4n/mu)log(1/epsilon)`.  The target is known for every `n<=4` and for every
signed-rank-one lift; it is open for a general matrix from `n=5` onward.

## 1. Routes that are closed and must not be repeated naively

1. **Sharp one-epoch coefficient two.**  T080 and its positive-`mu` M1 lift
   have exact `n=8` counterexamples.  This does not refute the half target or
   C001.
2. **Bare inverse Jensen/Kadison.**  Equicorrelation families make the
   resulting normalized constant tend to zero with dimension.
3. **Word/reverse-word or complementary-prefix pathwise pairing.**  Exact
   rational kernel directions violate both comparisons.  Full permutation
   mixing is essential.
4. **Fixed shallow determinant/Bessel depth.**  Every `o(n)` determinant-tail
   depth fails on signed rank one.  Consecutive-block Bessel depth two is
   exactly false and depth three has a robust large-dimensional candidate
   counterexample.
5. **Scalar child induction.**  The `n=3,mu=1/5` example makes the cleared
   induction residual `-28/225` although the actual two-prefix target has
   margin `12/25`.  Directional child information is essential.
6. **Compressing all higher Schur loss into the first loss.**  There is no
   finite `R_2<=C R_1`; childwise scalarization loses order `n^3` on the
   simplex boundary; the useful parallel-sum state does not close under the
   next Bellman lift by Jensen.

These are regression controls, not research routes, unless a proposed new
lemma explicitly restores the information each one loses.

## 2. Information that a successful proof must retain

- linear-depth, without-replacement prefix information;
- anisotropy across child Schur complements;
- mixing across genuinely different endpoint sets/orders;
- both low-eigenvalue boundary directions and high-eigenvalue near-identity
  directions, since they impose different sharp constants;
- a matrix/dual certificate, not merely a trace or worst-child scalar.

## 3. Iteration-5 routes

### Route A: direct averaged prefix/potential inequality

First decide whether the stronger statement

\[
J_{\lceil n/2\rceil}(A)\succeq {\mu\over2}A^{-1}           \tag{I5.2}
\]

survives.  Attack it through remaining-gradient potentials, averaged frame
identities, and a Rayleigh/dual formulation.  A counterexample to (I5.2) does
not refute (I5.1), because the determinant leaf may repair it.

### Route B: new large-dimensional hostile families

Use symmetry-reduced subset states for at least three exchangeable groups,
multiscale block couplings, frustrated signs and star/pole mixtures.  The goal
is a counterexample to (I5.1) or an analytically identifiable extremal family,
not another small random-Gram null search.

### Route C: higher Bellman/Schur closure

Retain a matrix-valued adaptive state beyond `R_2`; explore parallel-sum lifts,
exterior/volume-sampling representations, and dual SDP/SOS certificates.  Any
finite basis must pass the simple-null and high-nullity boundary controls.

### Root route: prefix-versus-tail bifurcation and independent audit

Build exact `J_r` and `H_r` comparisons, search for the first dimension where
(I5.2) fails, and identify the missing PSD tail.  In parallel, derive a dual
form in which a universal half bound can be checked by a smaller symmetry or
potential statement.  All subagent claims receive independent reconstruction
before ledger promotion.

## 4. Iteration discipline

Every worker remains active for at least 120 minutes, attempts at least three
distinct avenues, records approximately 30-minute checkpoints, and includes at
least two hostile failures or stress tests.  Automatic harness runs count only
live Codex subprocess time; idle waits and sleep do not count.
