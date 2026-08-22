# Weighted-adjacency dual certificate

Status: a general dual identity and an algebraic proof candidate for the
preconditioner lemma are E3.  The final inequality `(D14)` is **refuted** by
the exact equicorrelation calculation in Section 5.  This document concerns
the weighted feature `R_pi=D_pi^T D_pi`; it must not be confused with the
separately refuted direct feature `R_pi=D_pi^T` in
`direct_adjacency_regression.md`.

Let `B` be an `n`-dimensional unit-diagonal SPD matrix,
`mu=lambda_min(B)`, and let `M_pi` be its unit lower triangular factor in
permutation order.  Put `X_pi=M_pi^{-1}`.

## 1. A random-test dual lemma

For any square-integrable random matrix `Y_pi`, completing a square gives

```
E[X_pi^T X_pi]
 >= E[X_pi^T Y_pi+Y_pi^T X_pi-Y_pi^T Y_pi].               (D1)
```

Take an arbitrary random matrix `R_pi` and a deterministic matrix `W`, and set
`Y_pi=M_pi^T R_pi W`.  Since `X_pi^T M_pi^T=I`, (D1) becomes

```
K(B) >= P W+W^T P^T-W^T Q W,                              (D2)
P=E[R_pi],
Q=E[R_pi^T M_pi M_pi^T R_pi].
```

When `P=P^T`, `Q` is positive definite, and `R_pi` is symmetric, the choice
`W=Q^{-1}P` proves the exact Bessel/linear-regression certificate

```
K(B) >= P Q^{-1} P.                                       (D3)
```

Bare inverse Jensen is the special case `R_pi=R` fixed.  Formula (D3) instead
permits the test matrix to retain explicit random-order information.

## 2. Weighted adjacency differences

For `pi=(pi_1,...,pi_n)`, define `D_pi` by

```
e_(pi_1)^T D_pi=e_(pi_1)^T,
e_(pi_k)^T D_pi
 =e_(pi_k)^T-B_(pi_k,pi_(k-1)) e_(pi_(k-1))^T,  k>=2,
R_pi=D_pi^T D_pi.                                         (D4)
```

This is not an arbitrary feature.  At the signed-rank-one boundary it is the
exact first-difference triangular inverse.  More generally, the entries below
the diagonal of `D_pi M_pi-I` are conditional-covariance numerators

```
B_(pi_k,j)-B_(pi_k,pi_(k-1)) B_(pi_(k-1),j).              (D5)
```

Thus this state is exact on the high-nullity sharp boundary, exact at the
identity, and its defect measures departure from rank-one conditional
geometry.

Every oriented adjacency has probability `1/n`.  Directly averaging the
path energy gives

```
P_B:=E R_pi
 =[(n+1)I-2B+Diag(diag(B^2))]/n.                          (D6)
```

Equivalently, for every `x`,

```
x^T P_B x
 =||x||^2/n + n^-1 sum_(i!=j)(x_i-B_ij x_j)^2.            (D7)
```

## 3. General preconditioner lemma (proof candidate)

The new averaged path frame obeys

```
P_B >= mu B^{-1}.                                         (D8)
```

Here is a self-contained algebraic proof.  For every `n` by `n` PSD matrix
`Z`, Cauchy--Schwarz gives

```
Z <= n Diag(diag Z).                                      (D9)
```

Apply this to `Z=B^2-mu^2 I>=0`.  With
`Delta=Diag(diag(B^2))`,

```
Delta >= B^2/n +(n-1)mu^2 I/n.                            (D10)
```

Substitution in (D6) reduces (D8), by functional calculus, to

```
g(lambda):=
 lambda[(n-lambda)^2+n+(n-1)mu^2]-n^2 mu >=0              (D11)
```

on

```
mu <= lambda <= L:=n-(n-1)mu.                             (D12)
```

The interval follows from `tr(B)=n`.  Write
`lambda=mu+theta(L-mu)`.  The cubic (D11) in the degree-three
Bernstein basis has control coefficients

```
b0 = n mu(1-mu)^2,
b1 = n(1-mu)[mu^2(n-1)-mu(4n-3)+n^2+n]/3,
b2 = n(1-mu)[-mu^2(n-1)+mu(2n^2-5n+3)+2n]/3,
b3 = n(1-mu)[mu^2(n-1)^2-mu(n-1)+n].                      (D13)
```

All are nonnegative for `n>=2` and `0<mu<=1`:

- the bracket in `b1` decreases on `[0,1]` and ends at
  `(n-1)^2+1`;
- the bracket in `b2` is at least `2n-(n-1)>0` after dropping
  its nonnegative middle term;
- the last bracket is `a^2-a+n` for `a=mu(n-1)` and is
  positive;
- the remaining factors are manifestly nonnegative.

A polynomial is a convex combination of its Bernstein control coefficients,
so (D11) follows.  At `mu=1`, `B=I` and (D8) is equality.  This completes the
proof candidate.

## 4. The proposed closure inequality

Put

```
Q_B=E[R_pi M_pi M_pi^T R_pi].
```

By (D3), the sharp half-constant would follow from the concrete matrix
inequality

```
Q_B <= (2/mu) P_B B P_B.                                  (D14)
```

Indeed, inversion and congruence turn (D14) into
`P_B Q_B^{-1}P_B >= (mu/2)B^{-1}`.  Unlike bare Jensen,
`Q_B` retains adjacency-conditioned order variance and is exact on the
rank-one boundary.  It is also a finite polynomial permutation moment; no
triangular inverse appears in its definition.

Equation (D14) is **false**.  The original exhaustive float64 enumeration
over all orders for random lifted Gram matrices through `n=7` found no
violation, but that small-dimensional null search was only E1 and missed the
exact dimension-50 obstruction below.

## 5. Exact weighted-feature obstruction

Take the positive equicorrelation matrix

```
B=(1-rho)I+rho 11^T,   n=50,   rho=1/10,   mu=9/10.       (D15)
```

Fix the identity order.  Let `S` be the subdiagonal shift and `L` the strict
lower all-ones matrix.  Then

```
M=I+rho L,  D=I-rho S,  R=D^T D,  F=RM,
Q_order=F F^T.                                           (D16)
```

Permutation averaging makes `P` and `Q` exchangeable.  Put
`d=1+(n-1)rho^2` and `ell=1+(n-1)rho`.  Their transverse and parallel
eigenvalues are

```
p_perp = [n+1-2(1-rho)+d]/n,
p_par  = [n+1-2 ell+d]/n,                                 (D17)

T = tr(Q_order)
  = n+(n-1)rho^2
    +(n-2)rho^2 mu^2(1+rho^2)
    +(n-2)(n-3)rho^2 mu^4/2,

S0 = 1^T Q_order 1
   = [1+(n-2)rho mu^2]^2 +(n-1)mu^2
     +(n-3)(n-2)rho mu^3
     +(n-3)(n-2)(2n-5)rho^2 mu^4/6,

q_par=S0/n,       q_perp=(T-q_par)/(n-1).                 (D18)
```

For clarity, (D18) follows by writing the rows of `F=RM`.  The first row is
`e_1^T-rho e_2^T`; an interior row `i` has entries
`rho mu^2` in columns `j<=i-2`, `-rho^2 mu` in column `i-1`,
`1` in column `i`, and `-rho` in column `i+1`; the last row has
`rho mu` in columns `j<=n-2` and `1` in column `n`.

The normalized eigenvalues of the dual certificate
`B^(1/2)P Q^-1 P B^(1/2)/mu` are exactly

```
c_perp = p_perp^2/q_perp
       = 1259043289/1225885468 > 1/2,

c_par  = ell p_par^2/(mu q_par)
       = 75142223/160062876
       = 1/2 - 4889215/160062876 < 1/2.                   (D19)
```

Thus both the certificate and the sufficient inequality (D14) fail in the
parallel direction.  This refutes only this particular `R=D^T D` state; it
does not refute the general dual lemma (D2), the preconditioner lemma (D8),
the actual RPCD half-prefix inequality, or C001.  See
`scripts/weighted_adjacency_equicorrelation_barrier.py` and its JSON output.

For provenance, the different direct feature `R=D^T` already fails at
`n=20,rho=mu=1/2`, with normalized parallel value
`9261/18985=1/2-463/37970`; see `direct_adjacency_regression.md`.

## 6. Hostile controls and scope

- Restricting `R_pi` to diagonal weights depending only on permutation
  position fails exactly at the signed-rank-one boundary in dimension 20;
  see `evidence/dual_and_potential_controls.json`.
- The exact obstruction (D19) shows that even optimal deterministic matrix
  regression for this one-step weighted state loses the half constant.
- Neither (D8) nor any search here proves the half-depth `H_r` target, the
  global half-constant, or C001.  A successful dual state must retain a number
  of order/path scales growing with `n`; the fixed-adjacency state is closed.
