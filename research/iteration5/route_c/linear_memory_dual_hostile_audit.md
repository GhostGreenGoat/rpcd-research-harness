# Hostile audit of the positive-equicorrelation linear-memory dual state

Date: 2026-08-21 (Asia/Shanghai)

Audited source:
`research/iteration5/route_a/linear_memory_dual.md`, especially Sections 4
and 5.  Status: **independent E3 reconstruction on the stated
positive-equicorrelation family.**  No conclusion below applies to a
general correlation matrix.

## 1. Exact finite state and indexing

Let

```
B=(1-rho)I+rho 11^T,  mu=1-rho,  0<rho<1,
q=ceil(n/2),  n>=2.
```

In chronological order, direct triangular multiplication verifies

```
D_ij=1                                      (i=j),
D_ij=-rho mu^(i-j-1)                       (1<=i-j<=q),
D_ij=0                                      (i-j>q),
```

and

```
DM=I+rho mu^q U_q,
(U_q)_ij=1 iff i-j>q.                                      (H1)
```

For `i-j<=q`, (H1) is the finite geometric cancellation
`1-rho sum_{k=0}^{i-j-1}mu^k=mu^(i-j)`; for `i-j>q`, the
truncated row leaves `rho mu^q`.  This confirms the exponent and the strict
inequality in the tail definition.  The case `n=2,q=1` has `U_q=0`; the
formulas remain valid.  Dimension one should be separated as the trivial
identity case because the requested memory exceeds `n-1` there.

Permutation averaging conjugates the canonical matrices.  Since the
all-ones vector is invariant, the parallel eigenvalues are exactly

```
p_parallel=||D1||^2/n,
q_parallel=||(DM)^T D1||^2/n,                             (H2)
```

and trace subtraction gives the transverse values in (L5).  Thus no
normalization factor is missing.

## 2. Independent reconstruction of the half-scaling limit

Take `rho=c/n`, `q/n->alpha`, with fixed `c>0`.  The row sum of row `i` of
`D` is

```
r_i=mu^min(q,i-1).
```

Consequently, with `i/n->x`,

```
r_i -> s(x)=exp[-c min(x,alpha)].                          (H3)
```

Moreover, from (H1), for `j/n->y`,

```
[(DM)^T D1]_j
 =r_j+rho mu^q sum_{i>j+q}r_i
 ->s(y)+c exp(-2c alpha)(1-alpha-y)_+.                    (H4)
```

The second exponential in (H4) is correct: every index in the tail already
has row sum `mu^q`, supplying one factor in addition to the factor in
`DM-I`.  Riemann sums now give (L8).  The off-diagonal Frobenius mass per
dimension tends to zero in the transverse trace subtraction, giving
`C_perp->1`.

At `alpha=1/2`, splitting the integrals at `1/2` gives

```
p=(1-e^-c)/(2c)+e^-c/2
 =[1+(c-1)e^-c]/(2c),

q=(1-e^-c)/(2c)+3e^-c/2
  -2e^-c(1-e^(-c/2))/c+c^2e^(-2c)/24.                   (H5)
```

This independently confirms (L13), including the sign of its cross term.

## 3. Audit of the Taylor certificate

Let `F=2(1+c)p^2-q`.  Substitution of (H5), without invoking the source
verifier, gives

```
24c^2e^(2c)F
 =12e^(2c)+(-12c^2+60c-24)e^c-48ce^(c/2)
  -c^4+12c^3-12c^2-12c+12=:H(c).                         (H6)
```

The coefficients through degree four are `0,0,24,36,9`.  For `k>=5`, the
polynomial tail in (H6) contributes nothing, and multiplying the remaining
coefficient by `k!/12` gives

```
2^k-k(k-1)+5k-2-4k/2^(k-1)
 =2^k-k^2+6k-2-k/2^(k-3).                                (H7)
```

For `k>=5`, `2^k>=k^2` and
`6k-2>k/2^(k-3)`, so every coefficient in (H7) is positive.  Since the
coefficient of `c^2` is already positive, `H(c)>0` for every `c>0`.
The multiplier in (H6) is positive, proving (L14).  Hence the limiting
parallel certificate is at least one half for every fixed `c>0`; the audit
found no interchange-of-limit claim beyond the stated order of limits.

## 4. Finite-dimensional preconditioner bound

Put

```
z=mu^(2q),  S_q=sum_{j=0}^{q-1}mu^(2j).
```

Equation (H2) actually gives

```
p_parallel=[S_q+(n-q)z]/n >=S_q/n.                       (H8)
```

The exact algebra in (L17) is

```
ell S_q/(n mu)
 =S_q/n+S_q(1-mu)/mu
 =S_q/n+(1-z)/[mu(1+mu)].                                (H9)
```

Since all `q` terms of `S_q` are at least its last term
`z/mu^2`, and `q/n>=1/2` for both even and odd `n`,

```
S_q/n >= z/(2mu^2).                                      (H10)
```

Finally `1/(2mu^2)>=1/[mu(1+mu)]>=1/2` for `0<mu<=1`, so
the affine expression in `z` in (L17) is at least one half.  Thus
`p_parallel>=mu/(2ell)`.

Every row sum `r_i` lies in `(0,1]`, so `p_parallel<=1`.  Also
`tr(P)=||D||_F^2>=n` because the diagonal of `D` is one.  Therefore

```
p_perp=[tr(P)-p_parallel]/(n-1)>=1.                       (H11)
```

The eigenvalues of `(mu/2)B^-1` are `mu/(2ell)` in the
parallel direction and `1/2` transversely.  Equations (H8)--(H11) prove
`P>=(mu/2)B^-1`, including `n=2`; no odd/even gap was found.

## 5. Tail norm and regression direction

The maximum row and column sums of `U_q` are both `n-q-1`.  For
`q=ceil(n/2)`, this is at most `q` in both parity cases.  Hence

```
||U_q||_2<=sqrt(||U_q||_1||U_q||_infinity)<=q.
```

Using `(1-rho)^q<=e^(-q rho)` and
`y e^-y<=1/e`, (H1) gives

```
||DM||_2<=1+rho q mu^q<=1+1/e.                           (H12)
```

For every order and vector `x`,

```
x^T D^T(DM)(DM)^T D x
 =||(DM)^T Dx||^2
 <=(1+1/e)^2 ||Dx||^2.
```

Averaging preserves the direction, so `Q<=(1+1/e)^2P`.  Inverting and
congruencing (all matrices are positive definite) yields

```
P Q^-1 P >=P/(1+1/e)^2
           >=mu B^-1/[2(1+1/e)^2]>mu B^-1/4.             (H13)
```

The rational comparison uses `1/e<2/5`, so
`1/[2(1+1/e)^2]>25/98>1/4` exactly as claimed.

## 6. Verdict and scope

No error was found in the exponential Taylor certificate, the scaling
normalization, the finite `S_q` identity, the even/odd memory bounds, the
`n=2` endpoint, the operator-norm direction, or the inverse Loewner step.
Sections 4--5 of the source are valid E3 proof candidates for positive
equicorrelation matrices.  They do **not** establish either generic lemma
`P>=(mu/2)B^-1` or `||D_qM||=O(1)` for arbitrary unit-diagonal SPD `B`;
those are the remaining general-matrix obstacles.
