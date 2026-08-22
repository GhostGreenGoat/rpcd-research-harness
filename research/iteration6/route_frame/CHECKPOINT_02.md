# Checkpoint 02

Recorded: 2026-08-22 17:32:00 +08:00 (about 57 minutes after observed
start).

## Cross-route hostile audit completed

The remaining-frame inverse Bellman candidate was first independently
checked against the root's six rank-one family.  A rational ambient
realization gives an original Bellman-gap eigenvalue `-7/576`, confirming
that the transformed `-1/81` gap is not an equivalence/sign artifact.

More importantly, the candidate also fails for the intended **structured
RPCD covariance lift**.  For `n=9`, `A=(I+J)/2`, `mu=1/2`, an exact
`S_9/S_8/S_7` symmetry reduction produces rank-nine lift projections and a
rational test matrix with

```
<X,Delta X>_F=-2422114/12155<0.
```

The seven-dimensional leave-one-out inverses were checked by substituting
their solutions back into the full ambient matrix equations.  This closes
that inverse Bellman potential, not the desired RPCD rate.

## Route A state

- Pathwise and reversal-paired covariance controls are analytically false.
- Full random internal-rank averaging has the exact frozen identity
  `E GG^T=E HH^T+CC^T/m`.
- The actual half-window state remains outside that lemma because its row
  features are adapted to the moving window.
- The operator Schur/parallel-sum avenue has now supplied a sharp negative
  result for the proposed inverse potential; the next useful target must be
  a weaker constant potential or a direct adapted-frame inequality.

No general frame inequality or RPCD theorem is claimed.
