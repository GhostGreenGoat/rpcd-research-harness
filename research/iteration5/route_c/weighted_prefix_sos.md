# Weighted prefix SOS hierarchy

Status: the all-dimensional level-two result has internal E4 status after an
independent hostile audit (`research/iteration5/route_a/ROUTE_C_W2_HOSTILE_AUDIT.md`);
it has no formal-assistant or external validation.  The level-three and
general statements remain conjectures under hostile attack.

Let `J_t(A)` be the exact decrease matrix after a uniform ordered prefix of
`t` distinct coordinates, for a unit-diagonal `m x m` SPD matrix `A` with
`mu=lambda_min(A)`.  Put

```text
C_t(A) := J_t(A) - (1/2) J_{t-1}(A).
```

The proposed weighted hierarchy is

```text
C_t(A) >= [(t+1)mu/(2m)] A^{-1},       1 <= t <= ceil(m/2). (W_t)
```

If `(W_t)` and `J_{t-1}>=[(t-1)mu/m]A^{-1}` hold, then

```text
J_t = C_t + J_{t-1}/2 >= (t mu/m) A^{-1}.
```

Thus the hierarchy is calibrated so that every level is sharp at `A=I` and,
if closed through half depth, proves the desired half certificate.  It does
not assert `(W_t)` after half depth; a global extension would contradict the
known signed-rank-one obstruction to coefficient one.

## 1. A zero-diagonal row-square lemma

If `H=H^T` is `m x m` with zero diagonal, then

```text
H^2 <= (m-1) Diag(diag(H^2)).                              (1)
```

Indeed, for every vector `x`,

```text
||Hx||^2
 = sum_i (sum_{j != i} H_ij x_j)^2
 <= (m-1) sum_i sum_{j != i} H_ij^2 x_j^2
 = (m-1) sum_j (H^2)_jj x_j^2.
```

Symmetry is used in the last equality.  This simple inequality is stronger
than the generic PSD estimate `X<=m Diag(diag X)` because a zero diagonal
removes one term from every row.

## 2. Exact proof draft of the weighted level two

The known exact formulae are

```text
J_1=I/m,
J_2=[(2m-1)I-2A+D]/[m(m-1)],
D=Diag(diag(A^2)).
```

Consequently

```text
C_2 = [(3m-1)I-4A+2D]/[2m(m-1)].                          (2)
```

Set `H=A-I`.  Since `diag(H)=0`,

```text
D=I+Diag(diag(H^2)) >= I+H^2/(m-1).                       (3)
```

It remains to check a scalar polynomial.  If `lambda` is an eigenvalue of
`A`, then `mu<=lambda<=m-(m-1)mu`.  Congruence by `A^(1/2)` and (2)--(3)
reduce `(W_2)` to

```text
p(lambda,mu)
 := lambda[3m+1-4lambda+2(lambda-1)^2/(m-1)]
    -3mu(m-1) >= 0.                                       (4)
```

For `lambda<=1`, feasibility gives `mu<=lambda`; (4) decreases in `mu`, and

```text
p(lambda,lambda)
 = -2lambda(lambda-1)(2m-lambda-1)/(m-1) >= 0.            (5)
```

For `lambda>=1`, the trace constraint and the lower floor on the other
eigenvalues give `mu<=(m-lambda)/(m-1)`.  At that upper value,

```text
p = (lambda-1)
    [2lambda^2-(4m-2)lambda+3m(m-1)]/(m-1).               (6)
```

The quadratic in (6) is convex.  Its vertex is `m-1/2`, where its value is
`m^2-m-1/2>0` for `m>=2`.  Equations (5)--(6) prove, for every `m>=2`,

```text
boxed: J_2-(1/2)J_1 >= (3mu/(2m)) A^{-1}.                 (7)
```

This is an all-dimensional weighted two-prefix theorem candidate with
internal E4 hostile-audited status.  It is not Lean/formally verified and
has not received external mathematical review.

## 3. Exact third-prefix state

Write `D_q=Diag(diag(A^q))` and define the PSD ordered-pair frame

```text
T(A)=sum_{i != j} [(A^2)_jj-A_ij^2]
     (e_j-A_ij e_i)(e_j-A_ij e_i)^T.                      (8)
```

Lifting the exact child `J_2` formula gives

```text
J_3 = I/m + { (2m-3)[mI-2A+D_2]
              -2[mA-2A^2+D_3] + T(A) }
             /[m(m-1)(m-2)].                              (9)
```

Formula (9) was checked against the subset Bellman recursion.  It retains
the anisotropy that the exact direct-sum barrier in `CHECKPOINT_01.md` shows
cannot be scalarized.

The next falsifiable statement is

```text
boxed conjecture: C_3=J_3-J_2/2 >= (2mu/m) A^{-1}.         (10)
```

Together with the already proved `J_2>=(2mu/m)A^{-1}`, (10) would yield
`J_3>=(3mu/m)A^{-1}`.  It would prove the desired half certificate for every
matrix through dimension six, rather than only through dimension four.

The E1 hostile search in `evidence/J3_SOS_HOSTILE_SEARCH.json` evaluated
12,800 random-rank, signed-rank-one, and simplex cases for `3<=m<=12`.
There was no violation; every dimension approached equality only near
`A=I`.  This is route-selection evidence, not a proof.

## 4. Exact compound-correlation subfamily at level three

For `A=(1-a)I+a 11^T`, `-1/(m-1)<a<1`, both `A` and (9) have only parallel
and transverse eigenvalues.  Direct substitution gives

```text
c_perp = [2a^4(m-1)-4a^3m+8a^3+5a^2m-13a^2+10a+4m-4]
         /[2m(m-1)],
c_parallel = [2a^4-8a^3+13a^2-10a+4]/(2m),               (11)
```

where `c` denotes the ordinary eigenvalue of `C_3`.

For `a>=0`, `mu=1-a`.  The transverse target gap factors as

```text
-a(a-1)(2a^2-4a+5)(a(m-1)+2)/[2m(m-1)] >= 0.             (12)
```

The parallel gap is `a P_m(a)/(2m)`.  On writing `b=1-a` and `r=m-3`, the
degree-four Bernstein coefficients of `P_m(1-b)` on `[0,1]` are

```text
r+3, (4r+9)/4, (7r+9)/6, (6r+1)/4, 2(2r+1),              (13)
```

so it is nonnegative.

For `a<0`, put `a=-c/(m-1)`, `0<c<1`.  The parallel gap factors as

```text
a(a-2)(2a^2-4a+5)(1+a(m-1))/[2m] >= 0.                   (14)
```

The transverse gap is `-a Q_m(a)/[2m(m-1)]`.  After the same `r=m-3`
substitution, all five degree-four Bernstein coefficients of the numerator
`Q_m(-c/(m-1))` have polynomials with strictly positive coefficients in
`r`; the explicit expressions are generated by the exact verifier.  Thus
(10) holds on the complete positive and negative compound-correlation
family.  This structured result is E3 pending independent reconstruction.

## 5. Precise remaining obstacle

The Bellman identity

```text
C_t(B)=I/(2m)+(1/m) sum_i L_i^T C_{t-1}(C_i)L_i           (15)
```

is linear, but inserting only the scalar conclusion of (7) recreates the
same anisotropy loss seen in Iteration 4.  A proof of (10) must use the
explicit surplus in (1), lifted through the codimension-two frame (8), or an
equivalent dual SOS.  The new hierarchy changes the state from a nonlinear
parallel sum to a linear weighted Bellman object, but it has not yet closed
at level three.
