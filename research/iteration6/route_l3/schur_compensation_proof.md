# Schur compensation proof candidate for the explicit `L3` inequality

Date: 2026-08-22 (Asia/Shanghai)

Status: **internal E4 proof candidate**.  The argument below is exact, has
portable symbolic regression checks, and passed an independent hostile
reconstruction in
`research/iteration6/route_stitch/L3_HOSTILE_AUDIT.md`.  There is no
Lean/formal-assistant proof or external review.

## 1. Statement

Let `A` be a real symmetric unit-diagonal SPD matrix of size `m>=3`, and let
`0<mu<=lambda_min(A)`.  Write `H=A-I`,

```text
D=Diag(diag H^2),   E=Diag(diag H^3),
F=H+H^2-D,
S=sum_i L_i^T(C_i-I)^2 L_i,
```

where `C_i=A_(-i,-i)` and `L_i=[-b_i I]` is the residual lift after moving
coordinate `i` first.  Define the Iteration-5 sufficient state

```text
L3={4(m-1)(m-2)I-10(m-2)H+8H^2+(3m-14)D-4E
    +2S/(m-2)} / [2m(m-1)(m-2)].                 (1.1)
```

Equivalently, with `d=m-1`,

```text
P_d(C)=[(3d+1)I-4C+2(C-I)^2/(d-1)]/[2d(d-1)],
L3=I/(2m)+(1/m) sum_i L_i^T P_d(C_i)L_i.          (1.2)
```

The candidate theorem is

```text
boxed:  L3(A) >= (2mu/m) A^-1,   m>=3.            (1.3)
```

In particular, taking `mu=lambda_min(A)` proves the explicit open lemma B6
from Iteration 5.  Together with the already established exact comparison
`C3>=L3`, it proves the weighted third-prefix inequality
`C3>=2mu A^-1/m`.  This does not by itself prove the unrestricted all-depth
RPCD conjecture.

## 2. The discarded anisotropic state has an exact pair-difference SOS

This identity is not needed to scalarize the proof; it explains exactly which
state the proof must preserve.  Put

```text
R=(m-2)H-H^2+D=(m-1)H-F.
```

For `W_i=H-E_iH-FE_i`, the `j`th row is zero when `i=j`, while for `i!=j`,

```text
e_j^T W_i=e_j^T H-F_ji e_i^T.                       (2.1)
```

Therefore rowwise variance gives the exact identity

```text
S-R^2/(m-1)
 =Diag(diag F^2)-F^2/(m-1)                            (2.2)
 =1/(m-1) sum_j sum_{i<k; i,k!=j}
   (F_ji e_i-F_jk e_k)(F_ji e_i-F_jk e_k)^T >=0.      (2.3)
```

Thus the missing term after the failed repeated row-Bessel compression is a
coordinate-pair/exterior two-form Gram matrix.  It is not an uncontrolled
fourth moment.  It also shows why keeping only `R^2` loses the transverse
variance on the positive rank-one boundary.

## 3. A scalar child-surplus lemma for `d>=3`

Let

```text
p_d(lambda)=[3d+1-4lambda+2(lambda-1)^2/(d-1)]
             /[2d(d-1)],
g_(d,mu)(lambda)=p_d(lambda)-3mu/(2d lambda).          (3.1)
```

If `d>=3` and

```text
mu <= lambda <= d-(d-1)mu,                              (3.2)
```

then

```text
g_(d,mu)(lambda)
 >= 3(lambda-mu)(1-mu)
    /[2d lambda(lambda+1-mu)].                           (3.3)
```

Here (3.2) is exactly the feasible spectral interval for a unit-diagonal
`d x d` principal child whose eigenvalues are all at least `mu`.

### 3.1 Low spectral regime

For `lambda<=1`, direct factorization gives

```text
g_(d,lambda)(lambda)
 =(1-lambda)(2d-lambda-1)/[d(d-1)^2] >=0,               (3.4)

g_(d,mu)(lambda)-g_(d,lambda)(lambda)
 =3(lambda-mu)/(2d lambda).                              (3.5)
```

The right side of (3.3) is the quantity in (3.5) multiplied by
`(1-mu)/(lambda+1-mu)<=1`, proving this regime.

### 3.2 High spectral regime for `d>=4`

For `lambda>=1`, the stronger comparison

```text
g_(d,mu)(lambda)-3(1-mu)/(2d lambda)
 =(lambda-1) B_d(lambda)/[2d lambda(d-1)^2],             (3.6)

B_d(lambda)=2lambda^2-(4d-2)lambda+3(d-1)^2             (3.7)
```

holds exactly.  The convex quadratic has its vertex at `d-1/2` and minimum

```text
B_d(d-1/2)=(2d^2-8d+5)/2>0,   d>=4.                     (3.8)
```

Since `(lambda-mu)/(lambda+1-mu)<=1`, (3.6) implies (3.3).

### 3.3 Exceptional child dimension `d=3`

Put

```text
v=1-mu,    t=(lambda-mu)/[3(1-mu)].                     (3.9)
```

The trace upper bound makes `(t,v)` range over `[0,1]^2`.  The gap in (3.3)
is exactly

```text
v Q(t,v)/[12(1+3tv)],                                    (3.10)
```

where the tensor Bernstein coefficients of `Q`, of degrees `(3,2)` in
`(t,v)`, are

```text
[4, 9/2, 5]
[6, 15/2, 10]
[8, 6, 0]
[10, 0, 2].                                               (3.11)
```

Every coefficient is nonnegative, completing the exact proof of (3.3).

## 4. Directional Schur compensation for `d>=3`

Fix a coordinate and write the parent block as

```text
A=[[1,b^T],[b,C]],
s=1-b^T C^-1 b,
c=C^-1 b,
beta=3mu/(2d).                                            (4.1)
```

Set

```text
G=P_d(C)-beta C^-1.                                       (4.2)
```

The eigenvalues of `G` are `g_(d,mu)(lambda)`.  For `mu<1`, `G` is positive
definite.  The PSD block `A-mu I` implies

```text
b in range(C-mu I),
b^T(C-mu I)^dagger b <=1-mu.                             (4.3)
```

In a spectral basis of `C`, (4.3) becomes

```text
sum_(lambda>mu) lambda^2 c_lambda^2/(lambda-mu)<=1-mu.   (4.4)
```

The scalar lemma implies

```text
beta/g_(d,mu)(lambda)
 <=mu lambda(lambda+1-mu)/[(lambda-mu)(1-mu)].            (4.5)
```

The right side in (4.5) is exactly

```text
lambda^2/[(lambda-mu)(1-mu)]-lambda.                     (4.6)
```

Coordinates with `lambda=mu` have `b_lambda=c_lambda=0` by (4.3).  Summing
(4.5)--(4.6) and using (4.4) yields

```text
beta c^T G^-1 c <=1-c^T Cc=s.                            (4.7)
```

The standard rank-one domination criterion now gives the directional matrix
inequality

```text
boxed: G >=(beta/s) c c^T.                               (4.8)
```

This is the missing anisotropic multiplier: it pays specifically in the
Schur-defect direction instead of replacing the child surplus by a scalar.

The block inverse identity is

```text
D_i:=A^-1-e_i e_i^T-L_i^T C^-1L_i
   =(1/s)L_i^T c c^T L_i.                                (4.9)
```

Combining (4.2), (4.8), and (4.9) gives the termwise lift

```text
L_i^T P_d(C_i)L_i
 >=beta(A^-1-e_i e_i^T).                                 (4.10)
```

No averaging or Jensen step occurs in (4.10).

For later use, define the actual child Schur-envelope remainder

```text
M_i=G_i-(beta/s_i)c_i c_i^T >=0.                          (4.11)
```

Then (4.10) has the stronger exact form

```text
L_i^T P_d(C_i)L_i
 =beta(A^-1-e_i e_i^T)+L_i^T M_iL_i.                     (4.12)
```

## 5. Parent closure for `m>=4`

Average (4.10) in (1.2).  Since `d=m-1`,

```text
L3 >=beta A^-1+[1/(2m)-beta/m]I.                         (5.1)
```

For `m>=4`, the coefficient of `I` is nonnegative.  From `A>=mu I`,
`I>=mu A^-1`.  Hence the difference between (5.1) and the target is at least

```text
{ beta-2mu/m+mu[1/(2m)-beta/m] }A^-1
 =3mu(1-mu)/[2m(m-1)] A^-1 >=0.                          (5.2)
```

This proves (1.3) for every `m>=4`, conditional only on the exact lemmas
already proved above.

In fact this is an explicit PSD multiplier certificate.  Put

```text
q=1/(2m)-beta/m=(m-1-3mu)/[2m(m-1)] >=0.                 (5.3)
```

Using (4.12), the target gap is exactly

```text
L3-(2mu/m)A^-1
 =(1/m)sum_i L_i^TM_iL_i
  +q(I-mu A^-1)
  +[3mu(1-mu)/(2m(m-1))]A^-1.                            (5.4)
```

Every term is PSD.  Thus the proof keeps the full anisotropic child state and
assigns it a nonzero matrix-valued Schur multiplier; it is not the failed
`S -> R^2/(m-1)` compression in disguise.

## 6. The parent dimension `m=3`

For `m=3`, the child dimension is `d=2` and full `beta=3mu/4`
compensation is false.  A smaller piecewise compensator is sufficient:

```text
kappa(mu)=mu/2,                    0<mu<=2/3,
kappa(mu)=(5mu-2)/4,               2/3<=mu<=1.            (6.1)
```

For either branch, the exact scalar statement is

```text
g_(2,mu)(lambda)
 >=[kappa(mu)/mu]
   (lambda-mu)(1-mu)/[lambda(lambda+1-mu)],               (6.2)
```

on `mu<=lambda<=2-mu`.  It implies, by the same Schur calculation as Section
4,

```text
P_2(C)-beta C^-1 >=(kappa/s)cc^T.                         (6.3)
```

### 6.1 Exact positivity of the two scalar branches

For the low branch put `v=1-mu` and
`t=(lambda-mu)/[2(1-mu)]`.  After removing a manifest positive denominator,
the numerator has tensor Bernstein coefficients of degrees `(4,3)`:

```text
[2, 5/3, 1, 0]
[7/4, 23/12, 25/12, 7/4]
[3/2, 11/6, 41/18, 23/6]
[5/4, 17/12, 19/12, 1/4]
[1, 2/3, 0, 1].                                           (6.4)
```

They are nonnegative on the larger square `0<=v,t<=1`, so in particular on
the required low-`mu` strip.

For the high branch put `w=3(1-mu)` and the same feasible `t`; now
`0<=w,t<=1`.  The gap is

```text
w Q_hi(t,w)/
 [18(3-w)(3+2tw)(3-w+2tw)],                               (6.5)
```

and the degree `(4,4)` Bernstein coefficients of `Q_hi` are

```text
[162, 567/4, 243/2, 102, 84]
[567/4, 1053/8, 975/8, 897/8, 205/2]
[243/2, 459/4, 437/4, 211/2, 103]
[405/4, 729/8, 669/8, 621/8, 147/2]
[81, 243/4, 45, 36, 34].                                  (6.6)
```

Every denominator factor and every coefficient is positive.

### 6.2 Closing the parent estimate

Let

```text
bar(D)=(1/3)sum_i D_i.
```

The exact leverage bound gives

```text
bar(D)<=(1-mu)A^-1.                                       (6.7)
```

Lifting (6.3) gives

```text
L3>=beta A^-1+qI-(beta-kappa)bar(D),
q=(2-3mu)/12.                                             (6.8)
```

If `mu<=2/3`, then `q>=0` and `I>=mu A^-1`.  Subtracting the target, the
remaining coefficient of `A^-1` is exactly

```text
beta-2mu/3-(beta-kappa)(1-mu)+qmu=0.                      (6.9)
```

If `mu>=2/3`, then `q<=0`.  The unit trace and the spectral floor give
`lambda_max(A)<=3-2mu`, hence

```text
I<=(3-2mu)A^-1,
qI>=q(3-2mu)A^-1.                                         (6.10)
```

With the high-branch value of `kappa`, the remaining coefficient is again
exactly zero:

```text
beta-2mu/3-(beta-kappa)(1-mu)+q(3-2mu)=0.                (6.11)
```

At `mu=1`, unit diagonal and `A>=I` force `A=I`, where (1.3) is equality.
This completes the proof candidate for `m=3`.

There is again an exact PSD decomposition.  Define

```text
M_i=G_i-(kappa/s_i)c_i c_i^T >=0,
E_D=(1-mu)A^-1-bar(D) >=0.                                (6.12)
```

For the low branch (`q>=0`), the cancellation (6.9) gives

```text
L3-(2mu/3)A^-1
 =(1/3)sum_i L_i^TM_iL_i
  +(beta-kappa)E_D+q(I-mu A^-1).                          (6.13)
```

For the high branch let `L=3-2mu`; then `LA^-1-I>=0`, and (6.11) gives

```text
L3-(2mu/3)A^-1
 =(1/3)sum_i L_i^TM_iL_i
  +(beta-kappa)E_D+(-q)(LA^-1-I).                         (6.14)
```

Equations (5.4), (6.13), and (6.14) are the promised matrix SOS/multiplier
certificate, modulo the scalar Bernstein certificates establishing `M_i>=0`.

## 7. Evidence, scope, and audit record

Portable exact checker:

```powershell
python scripts/iter6_l3_schur_compensation.py
```

It checks every displayed scalar factorization, reconstructs all Bernstein
tables exactly, checks the block inverse identity, and runs a fixed (not
random) set of rational Gram regressions in parent dimensions three through
five.  Output:
`evidence/SCHUR_COMPENSATION_EXACT.json`.

The independent hostile audit reconstructed, without trusting this script:

1. the coefficient `beta/s` in the rank-one domination (4.8);
2. the Moore--Penrose boundary `lambda=mu` in (4.3)--(4.7);
3. the sign reversal in the high-`mu` use of (6.10);
4. both parent coefficient cancellations (5.2), (6.9), and (6.11);
5. that (1.2) is exactly the Iteration-5 `L3`, rather than the larger exact
   `C3`.

It reports PASS with no blocking caveat.  Independent artifacts:

```text
research/iteration6/route_stitch/L3_HOSTILE_AUDIT.md
research/iteration6/route_stitch/independent_l3_audit.py
research/iteration6/route_stitch/L3_INDEPENDENT_EXACT_AUDIT.json
```

The result closes only the explicit third-level Bellman lemma.  Extending the
compensation mechanism to growing depth is a separate open problem.
