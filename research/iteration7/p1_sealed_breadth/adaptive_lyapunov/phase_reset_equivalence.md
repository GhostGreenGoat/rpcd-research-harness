# Bounded-horizon block contraction and phase-reset Lyapunov equivalence

## Status and scope

This is a same-run proof draft, capped at E3.  It repairs the first bad edge of the
phase-dependent cone route without assuming C051.  It does not prove the universal
bounded-horizon premise, so C050 remains open.  The immutable route card has SHA-256
`6f6c32dc47396bd06e660d29895af2df800f8e2ae9103809b8a8fe1918e5c2e0` and is not
modified.

Let

```
M*(P)=E_pi[T_pi^T P T_pi]
```

for a fresh uniform RPCD epoch.  All matrices below are real, unit-diagonal SPD,
`mu=lambda_min(A)`, and all statements concern every deterministic initial point.

## 1. Phase-reset lemma

Fix one admissible `A`.  Suppose that for some integer `m>=1` and `q in (0,1)`,

```
(M*)^m(A) <= q^m A.                                    (PR1)
```

Define `m` phase facets

```
P_j=q^(-j)(M*)^j(A),        j=0,...,m-1.                (PR2)
```

Exact coordinate descent decreases `A`-energy pathwise.  Hence

```
(M*)^j(A)<=A                                                   (PR3)
```

for every `j>=0`.  Consequently

```
P_0=A,
0<=P_j<=q^(-(m-1))A<=q^(-m)A,                           (PR4)
M*(P_j)=qP_(j+1)                for j<m-1,
M*(P_(m-1))<=qP_0.                                      (PR5)
```

Thus the deterministic routing is the cycle

```
0 -> 1 -> ... -> m-1 -> 0.
```

On PSD covariance states set

```
V(X)=max_(0<=j<m) tr(P_j X).                             (PR6)
```

Equations (PR4)--(PR5) give

```
tr(AX)<=V(X)<=q^(-(m-1))tr(AX),
V(M(X))<=qV(X).                                         (PR7)
```

Therefore, for every deterministic `x_0` and every epoch count `k`,

```
E||x_k||_A^2 <= q^(-(m-1))q^k||x_0||_A^2,
E||x_k||_A   <= q^(-(m-1)/2)q^(k/2)||x_0||_A.           (PR8)
```

The second inequality is Jensen applied to the squared random distance.  It is not a
bound on the distance of the expected iterate.  This construction is phase-dependent,
controls the full non-normal transient through `q^(-m)`, and is not a common one-step
`A`-metric inequality.

## 2. Quantitative equivalence with C050

Consider the bounded-horizon statement:

> There are universal `theta in (0,1)` and `B>0` such that, for every admissible
> `A`, some integer `m` satisfies `1<=m<=B/mu` and
> `(M*)^m(A)<=theta A`.                                      (BH)

### (BH) implies C050

Put `q=theta^(1/m)`.  Then (PR1) holds and
`q^(-(m-1))<=q^(-m)=theta^(-1)`.  Since
`m<=B/mu`,

```
q^(k/2)=exp((log theta)k/(2m))
       <=exp(-[-log(theta)]mu k/(2B)).                   (BH1)
```

Equation (PR8) therefore proves C050 with the explicit universal constants

```
C=theta^(-1/2),       c=-log(theta)/(2B).                (BH2)
```

One epoch uses `n` coordinate updates, so the bound has the required
`O((n/mu)log(1/epsilon))` update order.

### C050 implies (BH)

Assume C050 with universal `C,c>0`.  The `k=0` case forces `C>=1`.  Pathwise
monotonicity gives `Z_k=||x_k||_A<=Z_0`, and hence

```
E Z_k^2 <= Z_0 E Z_k <= C exp(-c mu k)Z_0^2.
```

Because this holds for every deterministic `x_0`,

```
(M*)^k(A)<=C exp(-c mu k)A.                              (BH3)
```

Fix, for example, `theta=1/2` and choose

```
m=ceil(log(2C)/(c mu)).                                  (BH4)
```

Then (BH3) gives `(M*)^m(A)<=theta A`.  Also `mu<=1`, because `A` has trace
`n`, so

```
m <= [log(2C)/c+1]/mu.                                  (BH5)
```

Thus (BH) holds with `B=log(2C)/c+1`.  This proves a quantitative equivalence,
subject to the same-run E3 ceiling.

## 3. Exact finite-dimensional dual obstruction

For fixed rational `A`, horizon `m`, and rational `theta`, define

```
G_m=theta A-(M*)^m(A).                                  (D1)
```

The block condition is exactly `G_m>=0`.  By self-duality of the PSD cone it
fails iff there is a PSD matrix `X` with

```
<X,G_m><0.                                               (D2)
```

If `G_m` is not PSD, `X=zz^T` can be chosen rank one from a negative direction
`z`.  For rational data, a rational negative direction gives a zero-tolerance
certificate.  To refute a proposed finite bound `m<=M`, one must provide such a
separator for every `m=1,...,M`.  A null finite search is not a proof; to refute
the universal (BH) statement one would need a quantified admissible family that
does this for arbitrary proposed `B` at fixed `theta`.

This is the exact dual attack interface for the next edge.  It retains every
block power up to the horizon and therefore cannot hide a non-normal prefactor.

## 4. Exact noncommuting reset stress

For

```
A=[[1,3/10,0],[3/10,1,2/5],[0,2/5,1]],
mu=1/2,       q=3/20,
```

the adjacent update commutator norm-squares are exactly `1053/5000` and
`241/625`.  The exact generator proves

```
det(q^m A-(M*)^m(A))<0,          m=1,...,8,              (N1)
q^9 A-(M*)^9(A)>0.                                      (N2)
```

All principal minors in (N2) are stored in `exact_phase_reset_output.json`.
Moreover the nine facets (PR2) all satisfy `P_j<(6/5)A`.  Hence they close as
the exact cycle `0->1->...->8->0`.  This is a finite canonical-reset depth
result, not a lower bound against arbitrary facets and not an all-dimensional
claim.  In particular, the earlier five-facet self-loop closes sooner; reset
routing and self-loop routing are distinct sufficient architectures.

## 5. Symbolic near-singular two-epoch repair

Let

```
A_rho=[[1,rho],[rho,1]],       99/100<=rho<1,
mu=1-rho,                      q=1-(21/8)mu.
```

Exact averaging gives

```
M*(A_rho)=rho^2(1-rho^2)I/2,
(M*)^2(A_rho)=rho^4(1-rho^4)I/4.                        (S1)
```

The minimum-eigenvector `(1,-1)` of `A_rho` gives the one-epoch fixed-metric
gap

```
q(1-rho)-rho^2(1-rho^2)/2
=(rho-1)^2(4rho^2+8rho-13)/8<0.                         (S2)
```

Thus the forbidden single fixed-`A` route fails throughout this near-singular
interval.  In contrast, the smaller eigenvalue of the two-epoch reset gap is

```
q^2(1-rho)-rho^4(1-rho^4)/4
=(rho-1)^2 p(rho)/64,                                   (S3)
```

where

```
p(rho)=16rho^6+32rho^5+48rho^4+64rho^3+64rho^2-377rho+169.
```

With `t=100(1-rho) in [0,1]`, the exact Bernstein coefficients of `p(1-t/100)`
are

```
16,
9209/600,
551401/37500,
8791897/625000,
104979019/7812500,
6006946949/468750000,
762469279201/62500000000.
```

They are all strictly positive, proving (S3) is positive for `rho<1` in the
stated interval.  The two facets `P_0=A`, `P_1=q^(-1)M*(A)` therefore close as
`0->1->0`.  Since `q>=779/800`, (PR8) gives the explicit structured bound

```
E||x_k||_A
 <=sqrt(800/779) exp(-(21/16)mu k)||x_0||_A.             (S4)
```

This is a symbolic near-singular proof draft for `n=2`, not C050.  It shows that
the phase-reset repair can succeed exactly where a one-epoch fixed-`A` LMI fails.

## 6. Adaptive-state growth and corrected first bad edge

The literal phase list stores

```
m*n(n+1)/2 = O(B n^2/mu)                                (G1)
```

scalar entries under (BH).  This is polynomial in `n` and linear in `1/mu`,
instead of the factorial permutation-history parameterization.  It is a
representation cost, not a coordinate-update cost or a state lower bound.

Most importantly, C050 does **not** require a dimension-uniform number of facets.
The quantitative equivalence proves that `m=O(1/mu)` phases and a universal
metric comparison are sufficient and are forced by C050 up to constants.  The
previous demand for a uniformly bounded facet count was therefore an
over-strong proof-engineering condition, not the correct target-transfer edge.

The corrected first bad edge is exactly (BH): prove a universal fixed-factor
block contraction by some horizon `B/mu`, or construct a quantified exact dual
family that defeats every such proposed `B,theta`.  This edge targets C050
directly and neither assumes C051 nor treats C051 as equivalent.

## 7. Reproduction

Run

```
{python} ./exact_phase_reset.py \
  --output ./exact_phase_reset_output.json
```

The script uses exact SymPy rational arithmetic and symbolic factorization,
with tolerance zero and no random seed.
