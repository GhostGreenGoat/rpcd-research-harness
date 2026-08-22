# Iteration 6 Route Frame — checkpoint 00

Observed local start: `2026-08-22 16:34:50 +08:00`.  This worker will remain
actively researching through at least `18:34:50 +08:00`.

## Quantified target

Let `A` be any `n x n` unit-diagonal SPD matrix,
`mu=lambda_min(A)`, `q=ceil(n/2)`, and for a uniform permutation `pi` let
`M_pi` be the chronological unit-lower factor.  Let `D_pi` invert, in each
row, only the current coordinate and its `q` most recent predecessors.  Put

```
E_pi=D_pi M_pi,
R_pi=D_pi^T D_pi,
P=E_pi[R_pi],
Q=E_pi[R_pi M_pi M_pi^T R_pi]
 =E_pi[D_pi^T E_pi E_pi^T D_pi].
```

The open goal is to prove, for some numerical `c>0` independent of `n,A,mu`,

```
P Q^-1 P >= c mu A^-1.                                  (T)
```

By the exact dual regression lemma, `(T)` implies
`K(A)>=c mu A^-1` and hence the desired `O(n/mu log(1/epsilon))` update order.
A refutation must identify whether the feature fails or merely a proposed
sufficient comparison fails.

## Inherited exact controls

- Fixed or sublinear memory is closed; on `rho=c/n` equicorrelation its
  normalized certificate tends to `(1+c)/(1+c+c^2/3)`.
- Every forgotten row `r` satisfies the pathwise Schur estimate
  `r A_O^-1 r^T<=sigma-mu||d||^2<=1-mu`, but exact cardinality damping is
  false.
- `P_q=J_q+(n-q)(J_(q+1)-J_q)` exactly; lower-bounding it by the desired
  prefix conjecture is circular.
- Half-linear memory passes the sharp equicorrelation asymptotic and gives a
  finite `25/98` family constant.

## Three analytic avenues

1. Conditional matrix Bessel/Gram: retain cross-row Gram matrices instead of
   summing single-row Schur inequalities.
2. Complement/random-window coupling: pair forgotten halves, or expose the
   permutation through a martingale/Efron--Stein decomposition.
3. Operator Schur/parallel-sum and dual variation: eliminate the old block at
   matrix level and optimize a deterministic/random test before scalarizing.

Bare Jensen, fixed adjacency, fixed `q`, and scalar row summation are used
only as exact hostile controls.
