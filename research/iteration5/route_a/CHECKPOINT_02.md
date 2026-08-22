# Iteration 5 route A — checkpoint 02

Time: 2026-08-21 20:42 +08:00 (about 64 minutes from observed start).

## Fixed-adjacency dual states are now closed

The two superficially similar features have been separated and independently
refuted:

1. **Direct adjacency**, `R_pi=D_pi^T`, fails exactly for positive
   equicorrelation at `n=20,rho=mu=1/2`; its normalized parallel certificate
   is `9261/18985=1/2-463/37970`.
2. **Weighted adjacency**, `R_pi=D_pi^T D_pi`, fails exactly at
   `n=50,rho=1/10,mu=9/10`; its normalized parallel certificate is
   `75142223/160062876=1/2-4889215/160062876`.

The latter was missed by the earlier exhaustive random scan through dimension
7.  The exact exchangeable block formulas and an independent dense rational
reconstruction are now in `weighted_adjacency_dual.md` and
`scripts/weighted_adjacency_equicorrelation_barrier.py`.  The E3 lemma
`E[D^T D] >= mu B^-1` survives, but its proposed covariance closure D14 does
not.  Neither failure is a counterexample to the actual RPCD inequality.

This is a concrete scaling lesson: a state that remembers only one random
edge has fixed memory, while the sharp equicorrelation triangular inverse has
a geometric tail over all earlier positions.  The next state must have
bandwidth or a mixture of path lengths growing linearly with the half-prefix.

## Independent hostile audits completed

- The equicorrelation half-prefix proof was independently reconstructed.  The
  Bellman recurrence, positive inverse-binomial identity, and negative
  pathwise estimate pass, after handling `rho=0` directly rather than through
  a divided expression.
- The identity-local theorem is valid for each fixed `n`; its advertised
  strict first-order margin needs `n>=3`.  At `n=2`, the first derivative
  coefficient vanishes, although the theorem follows directly because the
  prefix has length one.
- Route C's weighted two-step SOS lemma was reconstructed without its verifier.
  The zero-diagonal square lemma, coefficient collection, and endpoint scalar
  check pass.  This is a hostile E4 audit of an internal E3 candidate, not yet
  a theorem about the full half-prefix target.

## Remaining work

I am pivoting from the failed fixed-edge features to a falsifiable
linear-memory dual state.  The clean control family is positive
equicorrelation, where `M^-1` has coefficients
`-rho(1-rho)^(distance-1)`.  This permits exact comparison of a bandwidth-`q`
truncation with `q` fixed versus `q` proportional to `n`, before attempting a
generic matrix inequality.
