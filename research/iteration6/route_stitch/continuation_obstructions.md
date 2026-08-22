# Exact continuation controls from the boundary to identity

Date: 2026-08-22 (Asia/Shanghai)

Status: **E2 exact route barriers**.  They refute interpolation shortcuts,
not RPCD.

The multiplicative boundary-ray comparison in `spectral_stitching.md`,

```text
K(mu I+(1-mu)C)>=(1+mu)^(-2)K(C),
```

does not follow from a hidden convexity or Loewner monotonicity.  Both simpler
properties already fail in dimension two.

## 1. Exact two-dimensional ray

Let

```text
C=11^T,
A_mu=mu I+(1-mu)C=[[1,q],[q,1]],
q=1-mu.
```

The two chronological inverse factors are transposes of each other.  Direct
averaging gives

```text
K(A_mu)=[[1+q^2/2,-q],[-q,1+q^2/2]].                    (C1)
```

At the endpoints, `K(I)=I` and
`K(C)=[[3/2,-1],[-1,3/2]]`.  The affine endpoint chord is

```text
(1-mu)K(C)+mu K(I).
```

Subtracting it from (C1) gives the exact strict negative gap

```text
K(A_mu)-[(1-mu)K(C)+mu K(I)]
=-mu(1-mu)I/2,        0<mu<1.                            (C2)
```

Thus `K` is not concave along even this simplest boundary ray, and endpoint
lower bounds cannot be linearly interpolated.

## 2. No Loewner monotonicity

Relative to the identity endpoint, the parallel and transverse eigenvalue
changes are

```text
k_parallel(q)-1=-q+q^2/2<0,
k_transverse(q)-1=q+q^2/2>0,     0<q<=1.                 (C3)
```

Hence `K(A_mu)-K(I)` is indefinite.  Moving toward identity improves one
spectral sector and worsens the other; there is no one-sided Loewner
continuation to combine with the high-`mu` band.

## 3. Consequence for the stitching architecture

The viable continuation statement must either compare factors
multiplicatively (as the exact `M_mu=M_0[(1-mu)I+mu X_0]` identity does) or
carry separate spectral/shorted sectors.  A convex endpoint chord, a tangent
minorant based only on endpoint matrices, or a monotonicity argument cannot
serve as the missing bridge.

`verify_continuation_obstructions.py` reconstructs (C1)--(C3) symbolically.
