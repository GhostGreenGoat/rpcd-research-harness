# Failed lemmas and unresolved objections

Date: 2026-08-22 (Asia/Shanghai)

Every item below is a limitation of an auxiliary proof route unless explicitly
stated otherwise.  None is an RPCD counterexample.

## F1. Low-space compression is not a Loewner shorted certificate

For the exact rank-two extreme correlation matrix in
`extremal_geometry.md`, the null-space compression coefficient is
`3293/1250`, while the largest full Loewner coefficient is only
`3157/1202`; their gap is `2984/375625>0`.  Therefore
`P K P>=kappa P` cannot be substituted for `K>=kappa P`.  Any spectral
stitch must retain the low/high cross block or a Schur complement.

Evidence: E2 exact rational counterexample to the shortcut.

## F2. Endpoint interpolation and Loewner monotonicity fail

On the exact two-coordinate boundary ray,

```text
K(A_mu)-[(1-mu)K(C)+mu K(I)]=-mu(1-mu)I/2,
```

and `K(A_mu)-K(I)` has one positive and one negative eigenvalue.  Thus neither
concavity of the endpoint chord nor one-sided Loewner monotonicity supplies a
boundary-to-identity bridge.

Evidence: E2 exact symbolic obstruction.

## F3. Elliptope reduction to signed rank one is false

The Gram correlation of `(1,0),(0,1),(3/5,4/5)` is an exact rank-two extreme
elliptope point.  In general an extreme Gram rank need only satisfy
`r(r+1)/2<=n`, so its nullity can be `n-O(sqrt(n))`.  Extreme-point reduction
does not turn the problem into a one-dimensional low spectral layer.

Evidence: E2 exact extremality certificate and dimension count.

## F4. Scalar spectral mixing gives no new region

The `J2` polynomial-energy coefficient and exterior coefficient are both
weakest on the minimum eigenspace.  If both are below the target there, every
convex combination is below it in the same direction.  Adding a scalar
determinant or near-identity certificate cannot repair that shared bottleneck.

Evidence: exact analytic no-gain lemma; this excludes only scalar convex
mixing, not noncommuting shorted stitching.

## F5. Exterior volume stops at multi-low geometry

- Isotropic rank three is covered for every dimension and `mu`.
- Isotropic rank four already has boundary ratio `729/1750<1/2` at `n=9`.
- The nonsymmetric three-low spectrum `(0,0,0,1,1,1,1,4)` has ratio `2/5`.
  Its positive block lift has cleared gap
  `(1-mu)(3mu^2+19mu-7)`, negative for
  `0<mu<(sqrt(445)-19)/6`.

These are exact failures of the exterior sufficient certificate, not of the
RPCD target.

## F6. Boundary-ray norm continuation has an `O(delta_+/n)` radius

The exact multiplicative identity gives a genuine local bridge, but combining
it with `J2` controls a fixed singular ray only when roughly
`mu<=delta_+/(n-1+delta_+)`.  Signed rank-one families in the mesoscale
`mu=1-c/n`, `1<<c<<n`, show that this endpoint/norm architecture can vanish
while the exact half-depth quantity stays near `1/2`.  Linear-depth order
memory is still missing.

## F7. General `W4` remains open

Independent audits now pass the uniform shifted-inverse lemma for matching
support, one weighted three-vertex path plus isolates in every `d>=6`, and
equal-magnitude stars.  These do not cover overlapping paths, cycles,
unequal-weight degree-three stars, or dense support.  The identity `H^2=D` is
specific to matchings; the path and equal-star proofs instead rely on
family-specific invariant-sector/Bernstein certificates.  A dimension-uniform
abstraction for general support has not been found.

## F8. The unrestricted half-depth target remains open

The new regions force any counterexample to have `n>=7`, at least three
subunit eigenvalues, failure of the determinant-tail scalar coefficient, and
failure of the exterior elementary-symmetric condition.  They do not exclude
that remaining multiscale, multi-low-mode region.
