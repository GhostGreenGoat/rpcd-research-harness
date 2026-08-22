# Exact barrier to pathwise multirow tail control

Status: general analytic counterexample family to the **pathwise sufficient
inequality** `Q_pi<=C R_pi`.  It does not refute the permutation-averaged
certificate.

## 1. Bipartite Hilbert family

Let `a>=2`, `N=2a`, `q=a`, and define the rational skew-Hilbert matrix

```
C_ij=0                 if i=j,
C_ij=1/(i-j)           if i!=j.                           (B1)
```

Put `tau=1/4` and

```
A=[[I,tau C^T],[tau C,I]].                                (B2)
```

The classical finite Hilbert inequality gives `||C||<=pi<4`, hence (B2) is
unit-diagonal SPD.  This use of the Hilbert inequality is only to provide an
all-dimensional family; every finite instance can instead be checked exactly
by rational LDL.

Consider the single order placing the first bipartite group before the
second.  Its strict lower triangular part is the shear

```
L=[[0,0],[tau C,0]],   L^2=0,   M=I+L.                    (B3)
```

For the half-window local inverse, a late row `r` remembers early columns
`j>=r` and forgets precisely `j<r`.  If `U=striu(C)` and
`G=stril(C,-1)`, then shear products again vanish and

```
D=I-[[0,0],[tau U,0]],
E=DM=I+[[0,0],[tau G,0]].                                (B4)
```

## 2. Unbounded generalized pathwise covariance

For this order,

```
R=D^TD,
Q=D^T E E^T D.
```

Since `D` is invertible, `Q<=Gamma R` is equivalent by the substitution
`y=Dx` to `EE^T<=Gamma I`.  Test the latter on a vector equal to one on the
late group and zero on the early group.  Since the quadratic form is
`y^T EE^T y=||E^Ty||^2`, the early output has entries (up to reversal)

```
(tau G^T 1)_j=tau H_(a-1-j),
H_k=sum_(j=1)^k 1/j.
```

Therefore the exact generalized Rayleigh quotient is

```
1+(tau^2/a) sum_(r=1)^a H_(r-1)^2.                       (B5)
```

For at least `a/2` indices, `H_(r-1)>=log(a/2)`, so (B5) is at least

```
1+(tau^2/2)log(a/2)^2,                                   (B6)
```

which diverges.  Consequently there is no dimension-free pathwise bound

```
D_pi^T E_pi E_pi^T D_pi <=Gamma D_pi^TD_pi.               (B7)
```

Equivalently, no proof may first control every order's multirow tail norm and
only then average.  Cross-order cancellation is mathematically necessary,
not merely aesthetically preferable.

The bad order has probability `1/binomial(2a,a)` for this labelled bipartite
matrix, so (B5) alone says nothing about the averaged `Q/P` ratio.  It is a
barrier to the pathwise lemma, not to the target `(T)` or RPCD.

`scripts/verify_pathwise_triangular_barrier.py` reconstructs (B3)--(B5) with
exact rationals and checks finite SPD instances.
