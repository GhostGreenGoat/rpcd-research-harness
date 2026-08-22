# Independent cross-audit of the weighted-adjacency preconditioner

Date: 2026-08-21 (Asia/Shanghai)

Evidence status: **internal E4 proof candidate after this independent hostile
reconstruction (claim C039).**  It has no formal-assistant or external
validation.  This
note does not promote the half-depth RPCD claim.  It audits only (D1)--(D8)
and the logical implication from (D14); (D14) itself is exactly refuted in
Section 5 below.

The audited source is
`research/iteration5/route_a/weighted_adjacency_dual.md`.  The derivation
below was done from the definitions rather than by trusting that source's
verification script.

## 1. Quantifiers and edge cases

Let `B` be a real symmetric positive-definite `n x n` matrix with unit
diagonal, and let

```
mu = lambda_min(B).
```

Then `0 < mu <= 1` because `tr(B)=n`.  The nontrivial proof below assumes
`n>=2`.  For `n=1`, necessarily `B=[1]`, `D_pi=[1]`, and the claimed
inequality is equality.  For `n>=2, mu=1`, all eigenvalues are one, hence
`B=I`, and again equality holds.  It therefore remains to consider
`n>=2, 0<mu<1`.

## 2. Independent count of `E[D_pi^T D_pi]`

Write an oriented consecutive pair as `(j,i)`, meaning that `j` is
immediately before `i` in a uniformly random permutation.  Collapsing the
ordered block `(j,i)` leaves `(n-1)!` permutations, so

```
Pr[(j,i) is consecutive] = (n-1)!/n! = 1/n.              (A1)
```

The first vertex is also uniformly distributed.  Consequently, directly
from the row definition of `D_pi`,

```
E[D_pi^T D_pi]
 = I/n + (1/n) sum_{i != j}
       (e_i-B_ij e_j)(e_i-B_ij e_j)^T.                   (A2)
```

The four pieces in the oriented-pair sum are

```
sum_{i!=j} e_i e_i^T                         = (n-1)I,
sum_{i!=j} B_ij e_i e_j^T                    = B-I,
sum_{i!=j} B_ij e_j e_i^T                    = B-I,
sum_{i!=j} B_ij^2 e_j e_j^T
 = Diag(diag(B^2))-I.
```

Thus, with `Delta=Diag(diag(B^2))`,

```
P_B := E[D_pi^T D_pi] = [(n+1)I-2B+Delta]/n.             (A3)
```

This independently confirms both the probability normalization and the
transpose convention in (D6).  Equation (D7) is simply the quadratic form
of (A2).

## 3. Loewner reduction

For every PSD matrix `Z` and every vector `x`, choose a Gram representation
`Z_ij=<u_i,u_j>`.  Then

```
x^T Z x = ||sum_i x_i u_i||^2
         <= (sum_i |x_i| ||u_i||)^2
         <= n sum_i x_i^2 ||u_i||^2
         = n x^T Diag(diag Z)x.
```

Hence

```
Z <= n Diag(diag Z).                                     (A4)
```

Since `B>=mu I`, functional calculus gives
`Z=B^2-mu^2 I>=0`.  Substitution into (A4), with careful retention of the
direction, yields

```
Delta >= B^2/n + ((n-1)/n) mu^2 I.                       (A5)
```

Combining (A3) and (A5), it suffices to prove

```
[(n+1)I-2B+B^2/n+((n-1)/n)mu^2 I]/n >= mu B^{-1}.        (A6)
```

All matrices in (A6) are functions of `B`, so this is an eigenvalue-wise
claim.  Any eigenvalue `lambda` satisfies

```
mu <= lambda <= L := n-(n-1)mu,                           (A7)
```

because every other eigenvalue is at least `mu` and their sum is `n`.
Multiplying the scalar gap in (A6) by the positive number `n^2 lambda`
gives exactly

```
g(lambda)=lambda[(n-lambda)^2+n+(n-1)mu^2]-n^2 mu.       (A8)
```

No eigenvalue ordering or inversion direction has been lost here.

## 4. Exact positivity of the scalar polynomial

Put `lambda=mu+t(L-mu)`, `0<=t<=1`.  In the standard degree-three
Bernstein basis

```
g = b0(1-t)^3 + 3b1 t(1-t)^2 + 3b2 t^2(1-t) + b3 t^3,
```

direct coefficient conversion gives

```
b0 = n mu(1-mu)^2,
b1 = n(1-mu)[(n-1)mu^2-(4n-3)mu+n^2+n]/3,
b2 = n(1-mu)[-(n-1)mu^2+(2n^2-5n+3)mu+2n]/3,
b3 = n(1-mu)[(n-1)^2 mu^2-(n-1)mu+n].                   (A9)
```

These match (D13), but were recomputed independently.  Each is
nonnegative:

* The bracket in `b1` has derivative
  `2(n-1)mu-(4n-3)<0` on `[0,1]`; its minimum there is
  `(n-1)^2+1`.
* In the bracket in `b2`, the linear coefficient
  `(2n-3)(n-1)` is nonnegative.  Dropping that term and using
  `mu^2<=1` leaves `2n-(n-1)=n+1>0`.
* The bracket in `b3` is `a^2-a+n`, with `a=(n-1)mu`; its unrestricted
  minimum is `n-1/4>0`.
* The remaining factors are nonnegative.

Bernstein basis functions are nonnegative on `[0,1]`, so `g>=0`.  Together
with the two equality edge cases, this establishes the audited proof
candidate

```
P_B >= mu B^{-1}                                           (A10)
```

for every dimension and every unit-diagonal SPD `B`.

## 5. Audit of the dual algebra and the refuted closure step

Let `M_pi` be invertible, `X_pi=M_pi^{-1}`, and let `Y_pi` be any
square-integrable test matrix.  Pointwise,

```
(X_pi-Y_pi)^T(X_pi-Y_pi)>=0,
```

so taking expectations proves (D1).  For
`Y_pi=M_pi^T R_pi W`, with symmetric `R_pi`, one obtains

```
E[X_pi^T Y_pi] = E[R_pi]W = P W,
E[Y_pi^T Y_pi] = W^T Q W,
Q=E[R_pi M_pi M_pi^T R_pi].                               (A11)
```

Here `D_pi` is invertible in permutation coordinates, hence
`R_pi=D_pi^T D_pi` is positive definite.  Therefore every integrand in
`Q` is positive definite and `Q>0`.  Since `P=P^T`, choosing
`W=Q^{-1}P` gives exactly `K(B)>=P Q^{-1}P`.

Finally, if the (now exactly refuted) inequality

```
Q <= (2/mu) P B P                                         (A12)
```

were available, both sides would be positive definite, so inversion and
congruence would give

```
P Q^{-1}P >= (mu/2)B^{-1}.                               (A13)
```

Thus the implication from (D14) is algebraically valid.  However, (A12) is
false.  The exact artifact
`research/iteration5/route_a/evidence/weighted_adjacency_exact_barrier.json`
gives the positive equicorrelation matrix with

```
n=50, rho=1/10, mu=9/10.
```

On its parallel eigenspace, the optimal regression certificate associated
with `R_pi=D_pi^T D_pi` has normalized coefficient

```
75142223/160062876
 = 1/2 - 4889215/160062876 < 1/2.                         (A14)
```

Equivalently, (A12) has a strict rational negative parallel gap.  The
artifact also records an exact dense-formula reconstruction.  This refutes
the proposed closure (D14), not (A10) and not the RPCD half-prefix
conjecture.  The audited surviving result is only the preconditioner lemma
and the dual identity.

## 6. Audit verdict

No algebraic, probability-normalization, Loewner-direction, or quantifier
error was found in (D1)--(D8).  The `n=1` case should be stated separately,
but is a trivial equality and does not affect the result.  The general
preconditioner lemma has internal E4 proof-candidate status: the originating
derivation and this hostile independent reconstruction agree.  It is not a
formal or externally reviewed theorem.  In contrast, (D14) is not merely
open: the exact barrier (A14) disproves it for this feature.

## 7. Stronger obstruction: no dimension-uniform closure constant

The failure is not confined to the sharp constant two.  Fix any
`0<rho<1`, set `mu=1-rho`, and let
`B=(1-rho)I+rho 11^T`.  Independently multiplying the identity-order
matrices

```
M=I+rho L,  D=I-rho S,  R=D^T D,  F=RM
```

reproduces the parallel moments

```
ell = 1+(n-1)rho,
p_parallel = [1+(n-1)mu^2]/n,
q_parallel = S0/n,
```

where

```
S0=[1+(n-2)rho mu^2]^2+(n-1)mu^2
   +(n-3)(n-2)rho mu^3
   +(n-3)(n-2)(2n-5)rho^2 mu^4/6.                       (A15)
```

The normalized parallel regression coefficient is

```
c_n = ell p_parallel^2/(mu q_parallel).
```

All terms here are exact rational functions.  Their leading coefficients
give

```
ell/n -> rho,
p_parallel -> mu^2,
q_parallel/n^2 -> rho^2 mu^4/3,
lim_{n->infinity} n c_n = 3/(rho mu).                    (A16)
```

Therefore `c_n->0`.  In particular, there is no finite dimension-uniform
`C` for which

```
Q <= (C/mu) PBP
```

holds for this fixed-adjacency state: such an inequality would force
`c_n>=1/C`.  For the concrete rational choice `rho=1/10`, `mu=9/10`, the
exact value at `n=500` is

```
c_500=835670784749/13025285081505 < 1/8.                 (A17)
```

Thus enlarging the proposed constant from two to four or eight cannot save
the feature.  A successful dual state needs memory/order scales growing
with dimension.  The independent dense checks and (A17) are recorded by
`scripts/verify_iter5_route_c_fixed_adjacency_asymptotic.py`.
