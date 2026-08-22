# Iteration 6 root checkpoint 01

Observed time: 2026-08-22 17:25 +08:00.

## Analytic progress

1. The covariance dynamics admit an exact lift to a fully symmetrized product
   of orthogonal projection superoperators.  Its lifted frame satisfies the
   sharp spectral floor `sum Q_i >= mu I`.
2. The tempting remaining-frame inverse Bellman potential is exact for one
   and two projections, but is now **closed in general** by a six-vector
   rational equicorrelation counterexample.  The transformed gap has exact
   parallel eigenvalue `-1/81`; an independent reconstruction in the original
   Bellman coordinates also passed.
3. The stronger restriction to the RPCD covariance-lift family is also
   exactly refuted at positive equicorrelation `n=9,rho=1/2`.  An independent
   rational symmetry reduction gives a negative quadratic gap
   `-2422114/12155`, with full ambient inverse residuals checked exactly.
4. The explicit third Bellman level `L3 >= (2mu/n)A^-1` has passed an
   independent hostile audit.  It proves `C3 >=2mu A^-1/n` in every dimension,
   the target-order finite-time bound for `n<=6`, and the all-dimensional
   three-prefix benchmark `J3>=3mu A^-1/n`.

## Methodological consequences

- Abstract projection-frame information alone is insufficient for the simple
  inverse potential; any projection-superoperator proof must retain more than
  the frame sum.
- The successful `L3` proof works for the opposite reason: it retains a
  direction-specific Schur defect and pays for it with the exact child
  anisotropic surplus.
- The first unresolved hierarchy step is now explicit `W4`: prove a
  termwise Schur-recovery inequality in child dimension at least six, or its
  weaker averaged defect allowance.  Dropping the anisotropic remainder is
  already exactly known to fail.

No unrestricted `O(n/mu)` theorem is claimed at this checkpoint.
