# Iteration 6: analytic-first route selection

Start observation: `2026-08-22 16:34:10 +08:00`.

The normalized parameter is always
`mu=lambda_min(D^{-1/2}QD^{-1/2})`.  The unrestricted target remains a
finite-time `O(n/mu log(1/epsilon))` bound for expectation of distance (or
stronger squared distance), not merely distance of the expected iterate.

## Inherited closed routes

The following are regression controls, not default proof strategies:

1. fixed `A`-energy contraction with the conjectured sharp one-epoch rate;
2. bare inverse Jensen/Kadison and trace-only scalarization;
3. word/reverse-word or complementary-prefix pathwise pairing;
4. fixed or sublinear local-inverse memory;
5. scalar child induction, determinant/volume-only closure, and shallow
   row-Bessel compression;
6. fixed positional/adjacency regression features.

Any reuse must state exactly which missing anisotropic or covariance
information has been restored.

## Active routes

- **Frame route:** prove a dimension-free multirow covariance inequality for
  the half-window local inverse.
- **Bellman route:** prove or refute the explicit degree-four
  `L_3 >= (2mu/n)A^{-1}` inequality while retaining the anisotropic residual.
- **Stitching route:** bridge the general near-identity theorem to low-`mu`
  boundary geometry by spectral splitting, extremal decomposition, or
  quantified continuation.
- **Operator route (root):** seek a covariance-superoperator Lyapunov or
  comparison argument that does not force the already-refuted choice of the
  `A`-energy metric.

Each worker must remain active for at least 120 minutes, try at least three
analytic avenues, record exact failures, and use numerical work only to
falsify or verify a derived identity.
