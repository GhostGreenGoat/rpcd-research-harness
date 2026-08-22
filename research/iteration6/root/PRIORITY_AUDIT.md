# Iteration 6 directional priority audit

Date checked: 2026-08-22.

Scope: targeted primary-source search for randomly permuted coordinate
descent, without-replacement projection products, prefix/elementary-symmetric
certificates, and finite-time distance bounds.  This is not a systematic
bibliographic review and does not establish novelty.

## Primary sources checked

- Kim, Lee, Yun, *Provable Benefit of Random Permutations over Uniform
  Sampling in Stochastic Coordinate Descent*, ICML 2025:
  <https://proceedings.mlr.press/v267/kim25x.html>.
- Sun, Luo, Ye, *On the Efficiency of Random Permutation for ADMM and
  Coordinate Descent*: <https://arxiv.org/abs/1503.06387>.
- Gurbuzbalaban, Ozdaglar, Vanli, Wright, *Randomness and Permutations in
  Coordinate Descent Methods*: <https://arxiv.org/abs/1803.08200>.
- Recht, Re, *Beneath the Valley of the Noncommutative
  Arithmetic-Geometric Mean Inequality*: <https://arxiv.org/abs/1202.4184>.
- Lai, Lim, *Recht-Re Noncommutative Arithmetic-Geometric Mean Conjecture is
  False*: <https://arxiv.org/abs/2006.01510>.
- Han, Xie, *A Simple Linear Convergence Analysis of the Randomized
  Reshuffling Kaczmarz Method*: <https://arxiv.org/abs/2410.01140>.

The targeted searches did not locate the weighted third-prefix `L3` Schur
certificate, the exterior condition based on
`e_(ceil(n/2)-1)(lambda_2,...,lambda_n)`, or the conditional dual-regression
filtration in these sources.  The 2025 RPCD paper still states the general
unit-diagonal result as a conjecture; the reshuffling-Kaczmarz paper uses an
instance-specific product norm rather than an explicit normalized spectral
floor.

## Evidence consequence

This search is too narrow to satisfy the repository's full priority gate.
Claims C043, C045, C047, and C048 therefore remain `proof_candidate` even
where their internal hostile audits pass.  They must not be described as
published-new theorems or as externally validated results.
