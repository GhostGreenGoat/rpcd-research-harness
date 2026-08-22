# Hostile audit: weighted two-prefix inequality

Audited source: `research/iteration5/route_c/weighted_prefix_sos.md`, Sections
1--2.

Outcome: **PASS**.  No blocker was found in the all-dimensional statement

```
J_2(A)-J_1(A)/2 >= [3 mu/(2m)]A^{-1},  m>=2.              (W2)
```

The level-three and general hierarchy conjectures were not audited as proved
claims.

## 1. Matrix algebra and zero-diagonal lemma

Substitution of the exact `J_1,J_2` formulae gives

```
C_2=[(3m-1)I-4A+2D]/[2m(m-1)].
```

For `H=A-I`, symmetry and `diag(H)=0` give

```
||Hx||^2
 <=(m-1)sum_i sum_(j!=i) H_ij^2 x_j^2
 =(m-1)x^T Diag(diag(H^2))x.
```

Thus the Loewner direction in the source is correct and
`D>=I+H^2/(m-1)`.

## 2. Scalar feasibility audit

After congruence, the exact scalar remainder is

```
p=lambda[3m+1-4lambda+2(lambda-1)^2/(m-1)]
  -3mu(m-1).
```

It decreases in `mu`.

- If `lambda<=1`, feasibility gives `mu<=lambda`; setting the worst value
  `mu=lambda` produces

  ```
  -2lambda(lambda-1)(2m-lambda-1)/(m-1)>=0.
  ```

- If `lambda>=1`, trace and the floors of the other eigenvalues give
  `mu<=(m-lambda)/(m-1)`.  At that worst value, the remainder is

  ```
  (lambda-1)
  [2lambda^2-(4m-2)lambda+3m(m-1)]/(m-1).
  ```

  The quadratic has its global minimum at `lambda=m-1/2`, with value
  `m^2-m-1/2>0` for every `m>=2`.

These two feasible regions cover the spectral interval, including
`lambda=1`; denominators remain positive at `m=2`.  This independently closes
the proof of (W2).

## 3. Scope

The weighted Bellman identity then combines (W2) with the already audited
`J_2>=2mu/m A^{-1}` as described by Route C.  This audit does not prove its
open `C_3` inequality or the hierarchy at half depth.  Under the repository
ladder, (W2) has internal E4 hostile-audited status, not Lean/E6 validation.
