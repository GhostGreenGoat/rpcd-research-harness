# Independent hostile audit of the `L3` Schur-compensation proof

Date: 2026-08-22 (Asia/Shanghai)

Audit target:
`research/iteration6/route_l3/schur_compensation_proof.md`.

Outcome: **PASS after independent reconstruction**.  I found no algebraic,
endpoint, or inequality-direction defect.  Subject to the already audited
Iteration-5 premise `C_3>=L_3`, the statement

```text
L_3(A) >= (2 mu/m) A^-1,   m>=3,
```

is eligible to be treated as an internal E4 proof candidate under the
repository evidence ladder.  It is not Lean-verified, externally reviewed,
or a proof of the all-depth RPCD conjecture.

The pivotal steps below were rederived from definitions.  The sibling
verifier was not imported or used as a premise.  My separate exact checker is
`independent_l3_audit.py`, with output
`L3_INDEPENDENT_EXACT_AUDIT.json`.

## 1. Recursive formula really is the explicit Iteration-5 `L3`

Put `H=A-I`, `d=m-1`, and for pivot `i` let
`L_i=[-b_i,I]`, with the child shifted matrix `H_i=C_i-I`.  Direct expansion
gives

```text
U0 := sum_i L_i^T L_i
    = (m-1)I-2H+D,

U1 := sum_i L_i^T H_i L_i
    = (m-2)H-2H^2+2D+E,

S  := sum_i L_i^T H_i^2 L_i,
```

where `D=Diag(diag H^2)` and `E=Diag(diag H^3)`.  The first line follows by
expanding each residual square.  For the second, embed
`L_i` as `P_i-He_i e_i^T`, expand against `H`, and sum the row/column terms.

Since

```text
P_d(C_i)= [3(d-1)I-4H_i+2H_i^2/(d-1)]/[2d(d-1)],
```

substitution in

```text
I/(2m)+(1/m) sum_i L_i^T P_d(C_i)L_i
```

produces exactly

```text
{4(m-1)(m-2)I-10(m-2)H+8H^2+(3m-14)D-4E
 +2S/(m-2)} / [2m(m-1)(m-2)].
```

Thus the proof addresses the actual B5 state, not a larger hidden matrix.

## 2. Child scalar surplus for `d>=3`

For a child eigenvalue `lambda`, define

```text
p_d(lambda)=[3d+1-4lambda+2(lambda-1)^2/(d-1)]/[2d(d-1)],
g=p_d(lambda)-3mu/(2d lambda).
```

Because the child has trace `d` and every eigenvalue is at least `mu`, its
exact feasible interval is

```text
mu <= lambda <= d-(d-1)mu.
```

For `lambda<=1`, independent simplification gives

```text
g_(d,lambda)(lambda)
 =(1-lambda)(2d-lambda-1)/[d(d-1)^2] >=0,

g_(d,mu)-g_(d,lambda)=3(lambda-mu)/(2d lambda).
```

Multiplying the second term by the factor
`(1-mu)/(lambda+1-mu)<=1` proves the claimed lower bound.

For `lambda>=1`, exact division gives

```text
g-3(1-mu)/(2d lambda)
 =(lambda-1)B_d(lambda)/[2d lambda(d-1)^2],

B_d(lambda)=2lambda^2-(4d-2)lambda+3(d-1)^2.
```

The global quadratic minimum is
`B_d(d-1/2)=(2d^2-8d+5)/2>0` for `d>=4`.  Since
`(lambda-mu)/(lambda+1-mu)<=1`, the desired estimate follows.

For `d=3`, I substituted
`mu=1-v`, `lambda=1-v+3vt` and reconstructed the gap directly.  It is

```text
v Q(t,v)/[12(1+3tv)].
```

Converting the monomial coefficients of `Q` independently to tensor
Bernstein form of degree `(3,2)` gives

```text
[4, 9/2, 5]
[6, 15/2, 10]
[8, 6, 0]
[10, 0, 2].
```

All coefficients are nonnegative.  The cases `v=0` (`mu=1`) and interval
endpoints follow directly or by continuity; no division-by-zero endpoint is
being silently used.

## 3. The Schur compensation and its exact `beta/s` factor

Write

```text
A=[[1,b^T],[b,C]],  s=1-b^T C^-1 b,  c=C^-1 b,
beta=3mu/(2d),      G=P_d(C)-beta C^-1.
```

For `mu<1`, positivity of `A-mu I` gives the generalized Schur conditions

```text
b in range(C-mu I),
b^T(C-mu I)^dagger b <=1-mu.
```

In a spectral basis of `C`, `b_lambda=lambda c_lambda`, hence

```text
sum_(lambda>mu) lambda^2 c_lambda^2/(lambda-mu)<=1-mu.
```

At `lambda=mu`, the range condition forces `b_lambda=c_lambda=0`, so the
Moore--Penrose endpoint contributes nothing.  This resolves the potentially
dangerous singular endpoint.

The scalar surplus implies

```text
beta/g(lambda)
 <= mu lambda(lambda+1-mu)/[(lambda-mu)(1-mu)]
  = lambda^2/[(lambda-mu)(1-mu)]-lambda.
```

Summation therefore yields

```text
beta c^T G^-1 c
 <=1-c^T Cc=s.
```

For positive definite `G`, the rank-one domination criterion says
`G>=alpha cc^T` iff `alpha c^T G^-1c<=1`.  Consequently the coefficient is
exactly

```text
alpha=beta/s,
```

not `beta`, `beta*s`, or `beta/s^2`.  The block inverse gives, by direct
multiplication,

```text
A^-1-e_i e_i^T-L_i^T C^-1L_i=(1/s)L_i^Tcc^TL_i.
```

It follows termwise that

```text
L_i^T P_d(C_i)L_i >= beta(A^-1-e_i e_i^T).
```

This audit confirms both the multiplier and the orientation of the lift.

## 4. Parent closure for `m>=4`

Averaging the termwise estimate gives

```text
L3 >= beta A^-1 + [1/(2m)-beta/m]I.
```

For `m>=4`, `beta<=1/2`, so the scalar coefficient of `I` is nonnegative.
Using `I>=mu A^-1`, the exact remaining coefficient after subtracting the
target is

```text
beta-2mu/m+mu[1/(2m)-beta/m]
=3mu(1-mu)/[2m(m-1)] >=0.
```

At `mu=1`, unit diagonal and `A>=I` force `A=I`; direct substitution gives
equality.  Thus the separate endpoint is covered.

## 5. Exceptional parent `m=3`

For `d=2`, the same direct reconstruction proves

```text
g_(2,mu)(lambda)
 >=[kappa(mu)/mu]
   (lambda-mu)(1-mu)/[lambda(lambda+1-mu)]
```

on `mu<=lambda<=2-mu`, with

```text
kappa=mu/2                         for mu<=2/3,
kappa=(5mu-2)/4                    for mu>=2/3.
```

For the low branch, `mu=1-v`, `lambda=1-v+2vt`.  After dividing the gap by
the nonnegative endpoint factor `v`, its positive denominator is

```text
2(1+2tv)(1-v+2tv),
```

and the independently reconstructed degree `(4,3)` Bernstein table is

```text
[2,   5/3,  1,     0]
[7/4, 23/12,25/12, 7/4]
[3/2, 11/6, 41/18, 23/6]
[5/4, 17/12,19/12, 1/4]
[1,   2/3,  0,     1].
```

For the high branch, `w=3(1-mu)` places the domain in the unit square.  The
reconstructed degree `(4,4)` table agrees entry-for-entry with the table in
the proof note and is strictly positive; it is stored in the JSON artifact.
All three denominator factors are positive for `0<=w<=1`.

The resulting lift is

```text
L3>=beta A^-1+qI-(beta-kappa)bar(D),
q=(2-3mu)/12.
```

Here `beta-kappa>=0` in both branches.  The exact leverage identity gives
`bar(D)<=(1-mu)A^-1`, so replacing `bar(D)` by its upper bound preserves the
lower-bound direction.

If `mu<=2/3`, then `q>=0`; therefore `I>=mu A^-1` gives
`qI>=qmu A^-1`.  The remaining coefficient is exactly zero.

If `mu>=2/3`, then `q<=0`.  Trace three and the spectral floor imply
`lambda_max(A)<=3-2mu`, hence

```text
I<=(3-2mu)A^-1.
```

Multiplying by the negative `q` reverses the inequality, exactly as needed:

```text
qI>=q(3-2mu)A^-1.
```

The high-branch remaining coefficient is again exactly zero.  Thus the sign
reversal is correct, not an accidental use of the low-branch direction.

## 6. Remaining scope

This proof closes the formerly open explicit Iteration-5 lemma B6 and hence,
using the independently audited `C_3>=L_3`, proves the weighted third-prefix
certificate

```text
C_3(A)>=2mu A^-1/m.
```

It consequently advances the exact finite-prefix result through dimension
six.  It does **not** iterate automatically to depth `ceil(n/2)`: a fourth
Bellman lift produces new conditional Schur-surplus states.  The general
`O(n/mu log(1/epsilon))` RPCD objective remains open.
