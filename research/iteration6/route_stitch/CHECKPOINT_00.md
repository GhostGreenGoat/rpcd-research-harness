# Iteration 6 Route C checkpoint 00

Timestamp: `2026-08-22 16:35:08 +08:00`.

## Target and evidence discipline

For every unit-diagonal SPD `A`, with `mu=lambda_min(A)`, seek a universal
constant `c>0` such that

```
K(A)=E_pi[M_pi(A)^(-T) M_pi(A)^(-1)] >= c mu A^(-1).
```

The sharper half-depth certificate remains open.  This route will not call a
floating-point or finite symbolic check a general proof.

## Inherited facts read before exploration

- The explicit general high-`mu` band follows from the pathwise triangular
  Frobenius bound: `n(1-mu)<=1` gives `K>=(mu/4)A^-1`.
- The complete positive/negative equicorrelation half-prefix curve is proved.
- Every fixed satellite count has an audited boundary-limit lower bound on
  its satellite-transverse sector, but growing counts and other sectors remain
  open.
- Scalar child lifting, determinant-volume-only closure, fixed adjacency,
  reverse pairing, and bare Jensen are exact failed routes.
- Boundary-to-interior perturbation was previously only qualitative on a
  fixed ray; lower-rank two-scale degenerations were the stated obstruction.

## Planned non-numerical avenues

1. Tunable low/high spectral projection with separately allocated PSD
   certificates and an explicit Schur/cross-term audit.
2. Elliptope extremal geometry and Gram-frame decompositions, including an
   exact obstruction to rank-one convex reduction.
3. Exact interpolation `A_mu=mu I+(1-mu)C`, with a uniform triangular-inverse
   modulus and an explicit radius depending on boundary Schur data.

Exact rational/symbolic computations will be used only to reconstruct or
falsify intermediate algebra.
