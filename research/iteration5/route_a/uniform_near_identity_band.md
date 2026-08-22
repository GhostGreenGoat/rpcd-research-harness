# A dimension-scaled near-identity theorem candidate

Status: E4 internally hostile-audited proof candidate for a general
unit-diagonal SPD matrix.  This is a restricted spectral regime, not the
global conjecture.

Let `B` be `n` by `n`, unit diagonal and SPD, with
`mu=lambda_min(B)`.  Put

```
theta=n(1-mu).                                            (N1)
```

## 1. A trace-to-Frobenius bound

Write the eigenvalue deviations as `a_i=lambda_i(B)-1`.  They sum to zero
and obey `a_i>=-(1-mu)`.  The convex function `sum a_i^2` is maximized on
this simplex when `n-1` deviations equal `-(1-mu)` and the remaining one
equals `(n-1)(1-mu)`.  Hence

```
||B-I||_F^2=sum_i a_i^2
 <=n(n-1)(1-mu)^2 <=theta^2.                              (N2)
```

For every permutation, its chronological triangular factor is

```
M_pi=I+tril(B_pi-I,-1).
```

Because `B-I` is symmetric with zero diagonal, exactly half its off-diagonal
Frobenius energy lies strictly below the diagonal.  Therefore

```
||M_pi-I||_2 <=||M_pi-I||_F
 =||B-I||_F/sqrt(2) <=theta/sqrt(2),                      (N3)

||M_pi||_2 <=1+theta/sqrt(2).                             (N4)
```

These bounds are pathwise and uniform over all orders.

## 2. Fixed-test dual certificate

Use the general dual lemma with the fixed random feature `R_pi=I`.  Then

```
P=I,
Q=E[M_pi M_pi^T]
 <=(1+theta/sqrt(2))^2 I,

K(B)>=Q^-1
 >=[1+theta/sqrt(2)]^-2 I
 >=[1+theta/sqrt(2)]^-2 mu B^-1.                          (N5)
```

The last step is just `B>=mu I`.  In particular, the **sharp half constant**
already holds in the smaller explicit band

```
n(1-mu)<=2-sqrt(2),                                      (N6a)
```

because `1+(2-sqrt(2))/sqrt(2)=sqrt(2)`.  Thus

```
K(B)>=(mu/2)B^-1                                         (N6b)
```

throughout (N6a).  More generally, if

```
n(1-mu)<=1,                                               (N6)
```

then `1+1/sqrt(2)<2`, and

```
boxed: K(B) >= (mu/4)B^-1.                               (N7)
```

Thus the conjectured `O(n/mu log(1/epsilon))` update order already holds,
with an explicit universal constant, throughout the dimension-scaled band
`mu>=1-1/n` for **every** unit-diagonal SPD matrix.  This is stronger and
more quantitative than a compactness-only neighborhood at each fixed `n`.

## 3. A simultaneous direct-prefix corollary

The same norm estimate applies before the end of an epoch.  For a fixed
prefix set/order `S` of size `t`, let `M_S` be its chronological triangular
factor.  The exact prefix energy is `||M_S^-1 h_S||^2`, and (N3) holds for
`M_S` because its strict-lower entries form a subset of those of `M_pi`.
Therefore

```
||M_S^-1 h_S||^2
 >=[1+theta/sqrt(2)]^-2 ||h_S||^2.
```

A uniform without-replacement prefix satisfies
`E||h_S||^2=(t/n)||h||^2`.  Consequently, simultaneously for every
`1<=t<=n`,

```
J_t(B)>=(t/n)[1+theta/sqrt(2)]^-2 I
       >=(t/n)[1+theta/sqrt(2)]^-2 mu B^-1.                (N8)
```

In particular, when `theta<=2-sqrt(2)` and `t=ceil(n/2)`,

```
H_t(B)>=J_t(B)>=(mu/4)B^-1.                               (N9)
```

This is a dimension-uniform positive half-prefix constant on a genuinely
all-matrix spectral band.  It is not the conjectured sharp one-half prefix
constant, but it already suffices for the requested complexity order in this
regime.

## 4. Scope and relation to failed Jensen routes

This use of the fixed test is deliberately local in spectral geometry.
Outside a bounded `theta` band, (N4) loses a dimension-free constant; the
existing exact bare-Jensen barriers remain untouched.  The result does not
cover near-identity sharp scalings `rho=c/n` for arbitrary unbounded `c`, nor
matrices with `n(1-mu)>1`.  Linear-memory conditional-tail control is still
needed for those regimes.

The earlier Iteration-4 Bellman analysis also supplies an explicit scalar
determinant-leaf high-`mu` region.  The result here is a separate leaf-free
certificate for `K` and `J_t`; it is not claimed to be the first high-`mu`
result or to contain that earlier region.

No numerical search is used in (N1)--(N9).  The convex extremum in (N2), the
triangular Frobenius factor in (N3), and the Loewner inversion in (N5) were
independently reconstructed in
`research/iteration5/route_c/near_identity_band_audit.md`.
