# Covariance as a symmetrized product of projection superoperators

Status: analytic reduction and exact identities; the final symmetrized-product
gap is open.

Let `A` be unit diagonal SPD, `v_i=A^(1/2)e_i`,
`R_i=v_iv_i^T`, and `Z_i=I-R_i`.  Work on the real symmetric matrices with
the Frobenius inner product.  Define

```
Pi_i(X)=Z_i X Z_i,       Q_i=I-Pi_i.
```

## 1. Orthogonal projection lift

Because `Z_i` is a symmetric orthogonal projection, `Pi_i` is itself a
self-adjoint orthogonal projection on the symmetric-matrix Hilbert space.
If `P_pi=Z_(pi_n)...Z_(pi_1)` is one energy-coordinate RPCD epoch, then

```
P_pi^T X P_pi
 =Pi_(pi_1) Pi_(pi_2)...Pi_(pi_n)(X).
```

Consequently the RPCD covariance operator is exactly the fully symmetrized
noncommutative product

```
C_A = (1/n!) sum_pi Pi_(pi_1)...Pi_(pi_n).                (P1)
```

This is not the false fixed-`A`-energy statement: it lifts the entire
covariance dynamics to a larger projection problem.

## 2. The lifted frame has spectral floor `mu`

For symmetric `X`, direct block decomposition along the unit vector `v_i`
gives

```
<X,Q_iX> = 2||Xv_i||^2-(v_i^T X v_i)^2.                  (P2)
```

Hence, for `S=sum_i Q_i`,

```
<X,SX>
 =2 tr(X^2 A)-sum_i(v_i^T Xv_i)^2.                       (P3)
```

Since `(v_i^T Xv_i)^2<=||Xv_i||^2`, summing yields

```
<X,SX> >= tr(X^2A) >=mu||X||_F^2.                        (P4)
```

Thus the lifted projection family has no common nonzero fixed vector and

```
sum_i(I-Pi_i) >=mu I_Sym.                                (P5)
```

The constant is sharp as a statement based only on the frame floor: at
`A=I`, diagonal matrix directions have lifted frame eigenvalue one, equal to
`mu`.

## 3. A precise sufficient projection-AGM lemma

The unrestricted target order would follow from the following statement for
this structured lifted family: there is a numerical `c>0` such that

```
rho[(1/n!) sum_pi Pi_(pi_1)...Pi_(pi_n)]
 <=1-c lambda_min(sum_i(I-Pi_i)).                         (P6)
```

Indeed (P4) would give `rho(C_A)<=1-cmu`, and self-adjointness would then
give finite-time expected squared `A`-distance with a `sqrt(n)` prefactor;
the update complexity remains `O(n/mu log(1/epsilon))`.

There is no scale contradiction in this special family: testing the lifted
frame on `X=I` gives Rayleigh quotient one, so its minimum eigenvalue is at
most one.  An all-orthogonal-projection version would need the capped form
`1-c min{lambda_min(sum_i(I-Pi_i)),1}`; without the cap, coincident
complementary projections give an immediate false right-hand side.

The stronger noncommutative arithmetic-geometric-mean comparison with
`[(1/n)sum_i Pi_i]^n` would also suffice, but is not assumed here.  The
research question is whether the much weaker linear spectral-gap form (P6)
can be proved using the special congruence structure `Pi_i=Z_i(·)Z_i`.

## 4. Immediate warning

Applying independent with-replacement projections would give the desired
gap from (P5), but replacing the without-replacement symmetrized product by
that power is a noncommutative comparison and cannot be inserted without a
proof.  This note is a reduction, not a solution.

The full Recht--Re norm AGM comparison is known to be false from product
length five onward (Lai--Lim, arXiv:2006.01510), so (P6) must be attacked as
a strictly weaker gap inequality and preferably use the congruence structure.
Han--Xie's reshuffling-Kaczmarz linear convergence theorem
(arXiv:2410.01140) uses the instance-dependent constant
`max_pi ||T_pi A^dagger A||<1`; it does not quantify that constant by the
frame floor and therefore does not supply (P6).

Primary references checked:

- https://arxiv.org/abs/2006.01510
- https://arxiv.org/abs/2410.01140
