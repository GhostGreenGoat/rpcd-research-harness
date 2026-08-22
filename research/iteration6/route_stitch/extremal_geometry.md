# Convex/extremal correlation geometry: exact obstructions

Date: 2026-08-22 (Asia/Shanghai)

Status: **E2 exact finite diagnostics and negative structural results**.  No
general RPCD bound is claimed here.

## 1. Why rank-one boundary matrices cannot be the only extreme tests

Consider the three unit Gram vectors

```text
v1=(1,0),  v2=(0,1),  v3=(3/5,4/5)
```

and their correlation matrix

```text
C=[[1,0,3/5],[0,1,4/5],[3/5,4/5,1]].
```

It has exact spectrum `{0,1,2}`.  The standard elliptope extremality
criterion asks whether the rank-one forms `v_i v_i^T` span `Sym_2`.  In the
coordinates `(h11,h12,h22)`, the three equations `v_i^T H v_i=0` have
coefficient matrix

```text
[[1,0,0], [0,0,1], [9/25,24/25,16/25]],
```

whose determinant is `-24/25`.  Hence `H=0`, so `C` is an extreme point of
the elliptope.  It is rank two, not a signed rank-one matrix.  Therefore a
convex-geometric proof cannot reduce all boundary correlations to signed
rank-one endpoints.

This is already an obstruction in dimension three; it is not an asymptotic
pathology.

There is also an opposite large-dimensional lesson.  If an elliptope extreme
point has Gram rank `r`, the same extremality criterion requires the `n`
forms `v_i v_i^T` to span the `r(r+1)/2`-dimensional space `Sym_r`.  Hence

```text
r(r+1)/2 <= n,
r <=(sqrt(8n+1)-1)/2.                                    (E1)
```

Thus a nontrivial extreme boundary correlation has nullity at least

```text
n-(sqrt(8n+1)-1)/2 = n-O(sqrt(n)).                        (E2)
```

After the positive lift `A_mu=mu I+(1-mu)C`, all those kernel directions
become eigenvalues `mu<1`.  Therefore an extremal-decomposition strategy in
large dimension leads precisely to a **high-dimensional low spectral
layer**, not to the at-most-two-subunit region proved in
`spectral_geometry_region.md`.  Even a valid convex reduction would still
need the full shorted/multirow mechanism on that layer.

## 2. Compression is weaker than the full low-space certificate

Enumerating all six orders exactly gives

```text
K(C)=[[1523/1250, 8/25,   -83/125],
      [8/25,      849/625,-106/125],
      [-83/125,  -106/125, 3/2]].
```

For the null vector `z=(-3,-4,5)`, the compressed Rayleigh coefficient is

```text
z^T K z / ||z||^2 = 3293/1250.
```

But the largest coefficient in the **full Loewner** bound
`K >= alpha P_span(z)` is, by the rank-one domination criterion,

```text
alpha_short = ||z||^2/(z^T K^-1 z) = 3157/1202.
```

Their exact difference is `2984/375625>0`.  Thus even for an actual RPCD
boundary covariance, checking `P K P >= alpha P` does not establish
`K>=alpha P`: cross blocks consume a strictly positive Schur-complement
budget.  This directly constrains the low/high spectral stitching route.

## 3. Orbit averaging has no available concavity principle

The Iteration-2 exact example in
`docs/ITER2_ROUTE_B_SYMMETRY_EXTREMAL.md` gives a correlation orbit pair
whose permutation average has a *smaller* exact RPCD covariance rate:

```text
R(A)=(4521+3 sqrt(2321049))/31250 > R((A+P^TAP)/2)=153/625.
```

Both matrices have the same spectral floor `2/5`.  Hence the covariance-rate
functional required by the conjecture is not concave along this orbit
segment.  Symmetrizing a hostile matrix before proving the inequality is not
justified by convexity.

## 4. Consequence for a viable geometry route

A successful extremal proof must handle all of the following simultaneously:

1. higher-rank extreme elliptope points;
2. the full shorted operator on a low spectral subspace, not merely its
   compression;
3. a nonlinear/random-order argument that does not assume concavity under
   orbit averaging.

One remaining plausible language is a frame decomposition that keeps the
coordinate leverage profile and the low/high cross block as explicit state.
The present diagnostics show that a scalar convex mixture of normalized low
and high Gram frames loses precisely the data needed for Loewner stitching.

## 5. Reproduction

Run:

```powershell
python research/iteration6/route_stitch/verify_extremal_geometry.py
```

The script uses exact rational SymPy arithmetic and writes
`EXTREMAL_GEOMETRY_EXACT.json`.  It is an exact check of this one finite
example, not evidence for universal quantifiers.
