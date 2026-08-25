# Exact transfer from the locked block lemma to C050

Assume only the route-local block statement

```
(L_A^*)^L(A) <= A/2,          L=ceil(16/mu),             (T1)
```

for every real unit-diagonal SPD `A`, where every epoch uses a fresh
independent uniform permutation.  This section does not assume C051.

Let `H_j=(L_A^*)^j(A)`.  Every coordinate update is nonexpansive in
`A`-energy, hence `0<=H_(j+1)<=H_j`.  Positivity of `L_A^*` and (T1) give
inductively

```
H_(qL) <=2^(-q)A.                                      (T2)
```

For an arbitrary epoch count write `k=qL+r`, `0<=r<L`.  The incomplete final
block is handled without throwing away sampling semantics:

```
H_k<=H_(qL)<=2^(-q)A.                                  (T3)
```

For every deterministic initial point `x_0`, independence of fresh epoch
permutations and the covariance identity yield

```
E||x_k||_A^2=x_0^T H_k x_0<=2^(-q)||x_0||_A^2.         (T4)
```

This is expectation of squared distance for every initial point, not squared
distance of the expected iterate.  Jensen/Cauchy--Schwarz then gives

```
E||x_k||_A <=2^(-q/2)||x_0||_A.                        (T5)
```

Since unit diagonal implies `0<mu<=1`,

```
L=ceil(16/mu)<=17/mu,
q=floor(k/L)>=k/L-1>=mu k/17-1.
```

Substitution in (T5) proves

```
E||x_k||_A
 <=sqrt(2) exp[-(log 2)mu k/34] ||x_0||_A.             (T6)
```

Thus the locked lemma implies canonical claim C050 with universal
`C=sqrt(2)` and `c=(log 2)/34`.  One epoch contains `n` coordinate updates,
so relative expected `A`-distance `epsilon` costs
`O((n/mu)log(1/epsilon))` coordinate updates.  The proof covers `k=0`, every
incomplete final block, and every initial point.

The proposed warm-start repair

```
(L_A^*)^2(A)<=(1-mu)(L_A^*)(A)                         (T7)
```

would imply (T1) by positivity, but (T7) remains open for general `A`.  It is
equivalently the polar-cone assertion

```
D-mu I in cone{C(yy^T):y in R^n}^*,       D=I-C(I),    (T8)
```

by self-adjointness of `C`.  This tests only covariances reachable after one
fresh epoch; it does not assume the stronger full-PSD inequality `D>=mu I`.
The continuation proves (T7) only on two additional analytic slices and does
not assert it as C050 or C051.

If (T7) is exactly refuted, the same transfer remains available from a longer
reachable observability window: any universal `gamma>0` and `m<=b/mu`
satisfying

```
sum_(j=1)^m C^j(D) >= gamma C(I)                       (T9)
```

give `H_(m+1)<=(1-gamma)H_1<=(1-gamma)I`; iteration in
blocks of `m+1` then yields C050 with universal constants, and the same
incomplete-block monotonicity and Jensen steps (T3)--(T6) apply.  Statement
(T9) is only a route-local fallback idea, not a proved lemma.

Pass-4 exact certificates add two further analytic families satisfying (T7):
the generic unequal signed rank-two boundary and a rank-four sign-frustrated
five-cycle.  They do not change any quantifier in this transfer.  In
particular, familywise validity of (T7) is not substituted for its universal
premise, and the 252-matrix subset-DP null search through `n=12` remains E1.
