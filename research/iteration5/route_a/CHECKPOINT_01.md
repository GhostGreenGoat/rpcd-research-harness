# Iteration 5 route A — checkpoint 01

Time: 2026-08-21 20:07 +08:00 (about 30 minutes from observed start).

## Avenue A: remaining-gradient potential

In energy coordinates, put `v_i=B^(1/2)e_i`.  The `v_i` are unit vectors,
their frame operator is `sum_i v_i v_i^T=B`, and a coordinate update is the
orthogonal projection

```
z -> (I-v_i v_i^T)z.
```

Thus `J_t` is exactly the expected energy removed by `t` random
without-replacement projections.  For residual coordinates `h`, one deletion
has the exact decomposition

```
h^T B^-1 h = h_i^2 + (L_i h)^T C_i^-1(L_i h) + h^T D_i h.
```

The last order-loss term is why a potential containing only selected energy
and the scalar remaining optimum does not close.

I tested the strongest natural repair of that scalar induction: use the
*actual* child floors `mu_i=lambda_min(C_i)` instead of replacing them by the
global `mu`.  It would require

```
I/m + m^-1 sum_i (mu_i/2)L_i^T C_i^-1 L_i >= (mu/2)B^-1.   (P)
```

This is false exactly.  Let `epsilon=1/100` and lift the rank-two rational Gram
matrix with rows

```
(0,1), (4/5,3/5), (5/13,12/13), (7/25,24/25).
```

The parent and all three-coordinate children have spectral floor exactly
`epsilon`.  On `v=(1,1,-1,-1)`, the left side of (P) minus the right side has
the strictly negative rational quadratic form recorded in
`evidence/dual_and_potential_controls.json`.  This is an obstruction to the
potential, not to `H_ceil(m/2)`.

## Avenue B: a new dual/random-order certificate

Let `X_pi=M_pi^-1`.  For **any** random symmetric matrix `R_pi`, completing a
square with `Y_pi=M_pi^T R_pi` gives the exact general lemma

```
K=E[X_pi^T X_pi]
 >= E[2R_pi-R_pi M_pi M_pi^T R_pi].                        (D)
```

The usual bare Jensen certificate is only the special case of a fixed `R`.
Therefore (D) offers a precise way to retain order variance: let `R_pi` depend
on the revealed positions or adjacency graph.

For the first subclass, take `R_pi` diagonal, with weight `r_p` at permutation
position `p`.  Five scalar moments of `(r_p)` give a closed formula for the
right side of (D).  At the signed-rank-one boundary, its transverse value is

```
2 b^T r-r^T Q_n r,
b=(1/n)1,
(Q_n)_ii=(i+1)/n,
(Q_n)_ij=-(1+min(i,j))/[n(n-1)].
```

`Q_n` is positive definite, so the best possible positional-diagonal value is
`b^T Q_n^-1 b`.  At `n=20`, exact rational LDL reconstruction gives

```
26221995579032758253469900984813715376999179
------------------------------------------------ < 1/2.
57727556009634555508186582715359351326391580
```

Consequently position weights alone cannot prove the half constant.  The
general lemma (D) survives; its next nontrivial state must contain adjacency
or path information, consistent with the signed-rank-one first-difference
inverse.

## Avenue C: structured hostile audit

The new equicorrelation half-prefix draft was independently reconstructed.
The transverse Bellman coefficient in (E3), the inverse-binomial polynomial
in (E8), and the negative-correlation hypergeometric penalty in (E10) all
check.  One presentation gap was reported immediately: the positive proof
divides by `delta=rho`, so `rho=0` must be handled separately by `A=I` (where
the claimed equality is immediate).  A complete audit and alternate exact
verifier are in progress.

## Current route choice

The generic proof should not continue with a scalar remaining-energy state.
The two live directions are:

1. enrich the dual test `R_pi` with random path/adjacency matrices; or
2. find a matrix-valued remaining-gradient potential that retains the
   rotated Schur-loss directions rather than replacing every child by its
   minimum generalized eigenvalue.
