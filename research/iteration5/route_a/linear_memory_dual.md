# A linear-memory local-inverse dual state

Status: exact algebraic reduction (E2), an asymptotic obstruction to
sublinear bandwidth (E3 proof candidate), and an analytic half-linear
positive-equicorrelation theorem candidate (E3).  No general matrix
inequality is claimed.

## 1. Definition and why it is genuinely new

For an order `pi`, let `M_pi` be the chronological unit-lower factor.  Define
`D_(pi,q)` row by row: invert the triangular problem using only the `q` most
recent coordinates and set all older coefficients to zero.  Equivalently,
each row is the last row of the inverse of its trailing `(q+1)`-coordinate
principal triangular block.  Use the weighted dual feature

```
R_(pi,q)=D_(pi,q)^T D_(pi,q).                              (L1)
```

This interpolates between the refuted fixed adjacency state (`q=1`) and the
complete state (`q=n-1`).  At `q=n-1`, `D=M^-1`, so `P=Q=K` in the dual lemma
and its regression certificate is the exact RPCD inverse moment.  Thus no
information is discarded at the full-memory endpoint.

Unlike fixed shallow depth, the proposed half-prefix state takes
`q=ceil(n/2)`; its memory grows linearly with the target prefix.

## 2. Exact positive-equicorrelation reduction

Let

```
B=(1-rho)I+rho 11^T,  mu=1-rho,  0<rho<1.                 (L2)
```

In a canonical order the local inverse is exactly

```
D_ij = 1                              if i=j,
       -rho mu^(i-j-1)                if 1<=i-j<=q,
       0                              otherwise.           (L3)
```

A direct geometric-series cancellation gives the particularly simple defect

```
E:=DM,
E_ij = 1                              if i=j,
       rho mu^q                       if i-j>q,
       0                              otherwise.           (L4)
```

Thus the discarded history is represented by one explicit residual tail,
not an uncontrolled numerical error.  Averaging conjugates of one canonical
order gives exchangeable `P=E_pi[D^TD]` and
`Q=E_pi[D^T E E^T D]`.  Their exact blocks are

```
p_parallel = ||D 1||^2/n,
p_perp     = (||D||_F^2-p_parallel)/(n-1),
q_parallel = ||E^T D 1||^2/n,
q_perp     = (||D^T E||_F^2-q_parallel)/(n-1).             (L5)
```

The normalized dual-certificate blocks are

```
C_perp     = p_perp^2/q_perp,
C_parallel = [1+(n-1)rho]p_parallel^2/(mu q_parallel).     (L6)
```

Equations (L3)--(L6) are exact rational formulas and are independently
evaluated in `scripts/linear_memory_equicorrelation.py`.

## 3. A sharp bandwidth-scaling obstruction

The near-identity scaling detects whether the memory is truly linear.  Let

```
rho=c/n,   q/n -> alpha,   c>0.                            (L7)
```

Riemann sums in (L5) give

```
s(x)=exp[-c min(x,alpha)],
p(alpha,c)=integral_0^1 s(x)^2 dx,

u(alpha,c;y)=s(y)+c exp(-2c alpha)(1-alpha-y)_+,
q(alpha,c)=integral_0^1 u(alpha,c;y)^2 dy,                 (L8)

C_parallel -> (1+c)p(alpha,c)^2/q(alpha,c),
C_perp -> 1.                                              (L9)
```

In particular, if `q=o(n)`, then `alpha=0`, and

```
p=1,
q=integral_0^1 [1+c(1-y)]^2 dy=1+c+c^2/3,
C_parallel -> (1+c)/(1+c+c^2/3).                          (L10)
```

The last quantity is below `1/2` exactly when

```
c > (3+sqrt(21))/2.                                       (L11)
```

Consequently **no sublinear-bandwidth member of this local-inverse dual
family can prove the sharp half constant uniformly in dimension**.  This is
an analytic explanation of why both fixed-adjacency attempts failed.  For
any proposed universal positive constant, taking the fixed scaling parameter
`c` sufficiently large also makes (L10) smaller than that constant.  Hence
sublinear bandwidth cannot prove even a nonsharp dimension-uniform positive
coefficient over the whole family.  For
fixed `rho` and `q=1`, the failure is even stronger: the formulas in (D18) of
`weighted_adjacency_dual.md` give

```
C_parallel ~ 3/[n rho(1-rho)],                            (L12)
```

so that state cannot prove any dimension-free constant.

## 4. Half-linear bandwidth satisfies the sharp asymptotic inequality

For `alpha=1/2`, (L8) simplifies to

```
p = [1+(c-1)e^(-c)]/(2c),

q = (1-e^(-c))/(2c) + 3e^(-c)/2
    -2e^(-c)[1-e^(-c/2)]/c + c^2 e^(-2c)/24.              (L13)
```

The desired equicorrelation certificate is the scalar exponential inequality

```
2(1+c)p^2 >= q.                                           (L14)
```

The scalar inequality (L14) has a direct positive-coefficient proof.  Put
`x=exp(-c)` and `F=2(1+c)p^2-q`.  Exact simplification gives

```
24c^2 exp(2c) F = H(c),

H(c)=12exp(2c)+(-12c^2+60c-24)exp(c)-48c exp(c/2)
     -c^4+12c^3-12c^2-12c+12.                            (L15)
```

The first Taylor coefficients of `H` are

```
[c^0]H=[c^1]H=0,  [c^2]H=24,  [c^3]H=36,  [c^4]H=9.
```

For every `k>=5`, the coefficient is

```
[c^k]H = (12/k!)
  [2^k-k^2+6k-2-k/2^(k-3)].                              (L16)
```

Now `2^k>=k^2` for `k>=4` (induction), while
`6k-2>k/2^(k-3)` for `k>=5`.  Hence every coefficient in (L15) is
nonnegative and at least one is positive.  Therefore `F>0` for `c>0`,
proving (L14).  It follows from (L9) that the half-linear local-inverse dual
certificate has limiting parallel constant at least one half throughout the
sharp scaling (L7); the transverse limit is one.  The constant tends to one
half from above as `c->infinity`.

An exact finite rational reconstruction for selected dimensions and a dense
logarithmic scan remain useful regression controls, but are no longer the
basis for the sign conclusion.

This proof covers only the positive-equicorrelation control family and only
the scaling limit (L7).  The generic next lemma must compare the conditional tail
`D_(pi,q)M_pi-I` with the averaged frame `E[D_(pi,q)^TD_(pi,q)]` for
`q=ceil(n/2)` without reducing it to a scalar child floor.

## 5. A finite-dimensional universal-constant certificate on the family

The same half-linear state gives a nonasymptotic constant, by a shorter norm
argument.  Set `q=ceil(n/2)`, `z=mu^(2q)`, and

```
S_q=sum_(j=0)^(q-1) mu^(2j).
```

The parallel eigenvalue in (L5) is at least `S_q/n`.  With
`ell=n-(n-1)mu`, the exact identity

```
ell S_q/(n mu)
 =S_q/n+(1-z)/[mu(1+mu)]
 >=z/(2mu^2)+(1-z)/[mu(1+mu)] >=1/2                  (L17)
```

uses `q/n>=1/2` and the last term of `S_q`; the final scalar inequality is
elementary.  Moreover, `tr(P)=||D_q||_F^2>=n`, while every row sum of `D_q`
is `mu^min(q,i)<=1`.  Hence `p_parallel<=1` and
`p_perp=(tr(P)-p_parallel)/(n-1)>=1`.  Since the transverse eigenvalue of
`B` is `mu`, these two estimates prove

```
P >= (mu/2) B^{-1}.                                      (L18)
```

By (L4), `D_qM=I+rho mu^q U_q`, where `U_q` is the zero-one matrix below
the `q`-th subdiagonal.  Its maximum row and column sums are at most
`n-q-1<=q`; therefore

```
||D_qM|| <=1+rho q mu^q
          <=1+(q rho)exp(-q rho) <=1+1/e <7/5.            (L19)
```

Here `y exp(-y)<=1/e`, while `e>1+1+1/2=5/2` gives
`1/e<2/5`; thus the last comparison can be kept entirely rational.

Consequently, order by order and then after permutation averaging,

```
Q=E[D_q^T(D_qM)(D_qM)^TD_q]
 <=(1+1/e)^2 P <(49/25)P.                                 (L20)
```

The dual regression certificate (D3) now gives the genuine finite statement

```
K(B) >= P Q^{-1}P
     >= mu/[2(1+1/e)^2] B^{-1}
     >  (25mu/98)B^{-1} > (mu/4)B^{-1}.                   (L21)
```

Thus half-linear memory proves the requested `O(n/mu)` update order on every
positive equicorrelation matrix, and on every diagonal-sign conjugate of
that family, with an explicit nonsharp constant.  The
stronger direct prefix theorem already gives one half on this family; the
value of (L21) is architectural: it isolates two generic lemmas that would
extend the dual route beyond the family, namely a preconditioner lower bound
like (L18) and a bounded conditional-tail norm like (L19).
