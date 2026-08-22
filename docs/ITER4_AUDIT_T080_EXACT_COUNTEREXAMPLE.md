# Independent hostile audit: exact `n=8` T080 counterexample

**Audited claim:** the `4/5,71/125` construction in
`docs/ITER4_ROOT_PERMUTATION_BLOCK_SOS.md`, independently reconstructed in
`scripts/iter4_root_t080_counterexample_audit.py` by a subset-DP method.

**Provenance warning:** at audit time, `scripts/iter4_t080_exact_counterexample.py` contained a
different `2/3,1/3` construction with coefficient `1057837/531441`.  It is not the source of the
large fraction audited below.  This appears to be concurrent filename/version drift; it does not
affect the exact reconstruction of the explicitly displayed matrix here.

**Audit status:** confirmed by an independent full-permutation rational reconstruction.  The
counterexample refutes T080 and, at the explicit interior point `mu=1/1000`, refutes the stronger
one-epoch `A`-energy matrix bound M1.  It does **not** by itself refute the original RPCD covariance
spectral-radius conjecture C001.

## 1. Matrix definition and exact correlation check

Index the first two coordinates as labelled poles and the other six as ring coordinates.  The
matrix `C` has diagonal one and

```
C_12=1,
C_{pole,ring}=4/5,
C_{ring_i,ring_j}=71/125  (i != j).
```

The invariant subspaces give its spectrum without floating point:

- pole-difference line: `0`;
- ring-standard subspace: `1-71/125=54/125`, multiplicity five;
- the two-dimensional pole/ring-trivial block has trace `146/25` and determinant
  `2(1+5*71/125)-12(4/5)^2=0`.

Hence

`spec(C)={0^2,(54/125)^5,146/25}`.

In particular, `C` is PSD, has unit diagonal, rank six and nullity two.  The vector

`u=(1,-1,0,0,0,0,0,0)`

is exactly in its kernel.

## 2. Triangular-factor orientation

For an order `pi`, the verifier constructs the unit lower Gauss--Seidel factor in that order:

`(M_pi)_{pi_a,pi_b}=C_{pi_a,pi_b}` for `b<=a`, and zero for `b>a`.

It solves `M_pi y=u` by generic forward substitution in the labelled coordinate basis and checks
`M_pi y=u` coordinate by coordinate for every permutation.  It then solves
`M_pi^T z=y` by generic reverse substitution and checks that equation as well.  Therefore

```
||y||^2=u^T M_pi^{-T}M_pi^{-1}u,
z=M_pi^{-T}M_pi^{-1}u,
```

with the same orientation as the definition of `K_0`.

As a separate exact convention check, the audit directly constructs the coordinate-descent update

`U_i=I-e_i e_i^T C`

and multiplies it in chronological order for four representative permutations (identity, reverse,
and two interlaced pole/ring orders).  In all four cases, entry by entry,

`U_{pi_8}...U_{pi_1}=I-M_pi^{-1}C`.

This directly ties the triangular convention used in the `K_0` calculation to the actual RPCD
epoch matrix.  The equality for arbitrary `pi` is the usual forward-substitution identity: the
successive coordinate corrections form the unique solution of `M_pi y=Cx`, so the final iterate
is `x-y=(I-M_pi^{-1}C)x`.

## 3. Full `8!` enumeration and the 56 categories

The independent verifier does not invoke the proposed category recurrence.  It loops over all
`8!=40320` labelled permutations using `fractions.Fraction`.  Grouping the already-computed results
afterward by the ordered positions of the plus and minus poles gives:

- exactly `8*7=56` categories;
- exactly `6!=720` labelled ring permutations in every category;
- exactly one energy value within each category.

Thus the 56-word reduction and its multiplicities are correct, but the reported fraction is also
reconstructed without relying on that reduction.

The exact average is

```
u^T K_0(C)u / ||u||^2
=2296209806050635263939777/1164153218269348144531250
=1.9724292043483962... < 2.                              (A1)
```

The exact gap is

`-32096630488061025122723/1164153218269348144531250`.

## 4. Reducing line and the full Schur condition

Direct full-permutation back substitution also gives exactly

`K_0(C)u=lambda u`,

where `lambda` is (A1); all six ring components of `K_0u` vanish.  This agrees with the conceptual
symmetry proof: swapping the two identical poles preserves `C`, the uniform permutation law and
therefore `K_0`; its odd subspace is the one-dimensional line `span(u)`.

The Rayleigh inequality (A1) alone already refutes the full Loewner statement

`K_0(C)>=2P_{ker C}`,

because `P_{ker C}u=u`.  This is not merely failure of an auxiliary compression.

The reducing property also addresses the boundary Schur complement.  Since `K_0` is positive
definite, its range block is invertible.  The kernel-to-range block annihilates `u`, so

`S_Cu=K_0u=lambda u`.

Therefore `lambda_min(S_C)<=lambda<2`; the exact counterexample reaches the actual T080/M1 boundary
condition, not only `P_NK_0P_N` in a nonreducing direction.

## 5. Strict transfer to a positive-definite finite instance

Set

`A_mu=mu I+(1-mu)C` with `mu=1/1000`.

Then `A_mu` is unit diagonal SPD and has exact smallest eigenvalue `mu` (multiplicity two).  Pole
swap symmetry persists, so `u` remains a common eigenvector:

`A_mu u=mu u`, `K(A_mu)u=kappa_mu u`.

The independent full `8!` rational enumeration gives

```
kappa_mu = 1.97119027872181...,
mu*kappa_mu = 0.00197119027872181....                       (A2)
```

For `n=8`, the active proposed contraction factor is exactly

`q=(1-mu/8)^16>(7/8)^8`,

and

`1-q=0.00199812609330580...`.

The verifier certifies the strict rational gap

```
(1-q)-mu*kappa_mu
=247137176240640644023748165962866652800360729938774131950519498928120138726383589
 /9175040000000000000000000000000000000000000000000000000000000000000000000000000000000
=2.69358145839844e-5 > 0.                                  (A3)
```

The one-epoch energy matrix inequality would require the normalized decrease in every direction to
be at least `1-q`.  Direction `u` has decrease (A2), so (A3) is an exact finite counterexample to
M1.  This direct finite check is stronger than relying only on the asymptotic
`mu lambda_min(S_C)+o(mu)` transfer.

## 6. Scope discipline

What is refuted:

1. T080: `K_0(C)>=2P_{ker C}` for every singular correlation matrix;
2. the stronger one-epoch expected `A`-energy matrix contraction M1 with the conjectured factor,
   already at the displayed rational SPD matrix.

What is **not** refuted by this audit:

- the original conjecture about the spectral radius of the covariance map
  `E[T_pi tensor T_pi]`;
- a weaker finite-time bound with some universal constant below two;
- the separate half-depth T085 candidate.

A one-step Lyapunov operator norm may exceed a proposed factor while the asymptotic covariance-map
spectral radius remains smaller.  No covariance spectrum was computed or claimed here.

## 7. Independent artifact

Run:

```
python scripts/verify_iter4_t080_counterexample_independent.py
```

Output:

`research/evidence/ITER4_T080_EXACT_COUNTEREXAMPLE_INDEPENDENT_AUDIT.json`.

The run uses only Python standard-library exact rational arithmetic, checks every triangular solve,
enumerates all labelled permutations twice (boundary and `mu=1/1000`), and makes no
floating-point sign decision.
