# Analytic regime map after spectral stitching and `L3`

Date: 2026-08-22 (Asia/Shanghai)

This note collects only proved/proof-candidate sufficient conditions and
logical necessary conditions for a counterexample.  It does not claim the
remaining region is hostile.

Let `r=ceil(n/2)` and target

```text
H_r(A)>=(mu/2)A^-1.                                      (R1)
```

## 1. Regions now covered

1. **Small dimension:** the independently reconstructed `L3` theorem closes
   (R1) for every `n<=6`.
2. **High-`mu` determinant tail:** the inherited exact scalar Bellman
   coefficient

   ```text
   a_(n,r)(mu)=
    {mu(1-mu^r)/(1-mu)+mu^r d delta_d(mu)}/n,
   d=n-r,
   delta_d(mu)=mu^(d-1)[d-(d-1)mu]
   ```

   proves (R1) whenever `a_(n,r)(mu)>=mu/2`.
3. **Sparse negative inertia:** the exterior certificate proves (R1) whenever
   `A-I` has at most two negative eigenvalues, equivalently at most two
   eigenvalues of `A` lie below one.
4. **Isotropic three-dimensional low space:** (R1) holds for
   `A=aI-(a-mu)P`, with `rank(P)=3`, `diag(P)=3/n`, for all `mu` and `n>=4`.
5. **General exterior region:** more broadly, (R1) follows whenever

   ```text
   e_(r-1)(lambda_2,...,lambda_n)>=binom(n,r)/2.
   ```

These last three statements are leaf-free: they prove the stronger
`J_r>=(mu/2)A^-1`.

## 2. Exact high-`mu` scaling boundary of the scalar tail

Put `mu=1-c/n`, with fixed `c>=0`, and let `n` tend to infinity.  Directly
from the exact coefficient above,

```text
a_(n,r)(mu)/mu ->
D(c):=(1-e^(-c/2))/c +(1/2)e^(-c)(1+c/2).                (R2)
```

The first term is `integral_0^(1/2) e^(-cs) ds`, hence strictly decreasing;
the second has derivative `-e^(-c)(1+c)/4`.  Thus `D` decreases strictly
from one to zero.  There is a unique `c_*` with `D(c_*)=1/2`; a scalar
evaluation gives

```text
c_*=1.7298443299...                                      (R3)
```

(the decimal is a reproducible diagnostic, while the defining equation is
the exact statement).  Therefore every fixed `c<c_*` is eventually covered
by the determinant-tail half certificate.  Endpoint/norm stitching is not
needed in that band.

## 3. What an unresolved hostile sequence must look like

Combining the independent certificates, a counterexample must satisfy

```text
n>=7,
negative_inertia(A-I)>=3,
a_(n,r)(mu)<mu/2,
e_(r-1)(lambda_2,...,lambda_n)<binom(n,r)/2.              (R4)
```

In the near-identity scaling `mu=1-c/n`, it must additionally have
`c>=c_*+o(1)` if it is to escape the determinant scalar tail.

The `J2` localization bound in `spectral_geometry_region.md` says any
violating energy-coordinate witness must concentrate quantitatively on the
joint low spectral layer.  The exact continuation result in
`spectral_stitching.md` says a fixed boundary kernel certificate controls a
ray only out to radius `O(delta_+/n)`, where `delta_+` is the first positive
boundary eigenvalue.  Consequently the genuinely unresolved geometry is a
multi-low-mode, multiscale degeneration, not an arbitrary point of the
elliptope.

## 4. Proof-route boundaries

- `J2` and exterior volume are both weakest on the minimum eigenspace, so
  convex spectral mixing gives no region beyond their union.
- Rank-three *isotropic* low space is covered, but the spectrum
  `(0,0,0,1,1,1,1,4)` has exterior ratio `2/5`; arbitrary three-low-mode
  geometry needs more than volume.
- Rank-four isotropic low space already has exterior ratio `729/1750<1/2`
  at `n=9` in the boundary limit.
- Boundary-to-identity affine interpolation and Loewner monotonicity fail
  exactly in dimension two.

All four are barriers to auxiliary certificates, not RPCD counterexamples.
