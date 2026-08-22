# Independent subset-DP/Schur audit: simple `2/3,1/3` T080 example

**Status:** exact reconstruction passed.  This note concerns only the simpler matrix with
pole--ring correlation `2/3` and ring off-diagonal `1/3`; it is separate from the later
`4/5,71/125` example.

## 1. Exact matrix check

Let `C` have two identical poles and six exchangeable ring coordinates, with unit diagonal and

```
C_{12}=1,       C_{pole,ring}=2/3,       C_{ring_i,ring_j}=1/3  (i != j).
```

Two exact kernel vectors are

```
u=(1,-1,0,0,0,0,0,0),
v=(-2,-2,1,1,1,1,1,1).
```

The ring-standard eigenvalue is `2/3`, with multiplicity five.  On the pole/ring-trivial block,
the determinant is zero and the trace is `14/3`.  Hence

`spec(C)={0^2,(2/3)^5,14/3}`,

which proves exactly that `C` is a unit-diagonal PSD correlation matrix of nullity two.

## 2. Independent `2^8` Bellman calculation

The verifier does not use pole-position classes or enumerate permutations.  For a nonempty index
set `B`, condition on the first pivot `i` and let `D=B\{i}`.  In `(i,D)` block order,

```
M_pi^{-1} = [ 1             0       ]
             [-M_D^{-1} b   M_D^{-1}],
```

where `b=C_{D,i}`.  Thus, if `K_D=E[M_D^{-T}M_D^{-1}]`, the conditional inverse Gram is

```
[1+b^T K_D b   -b^T K_D]
[-K_D b              K_D].
```

Averaging this block over the `|B|` possible first pivots gives a closed `2^8` subset recursion.
The implementation uses only `fractions.Fraction` and reconstructs the full `8 by 8` matrix `K_0`.

It obtains

```
u^T K_0(C)u / ||u||^2 = 1057837/531441
                       = 1.990506... < 2,
```

with exact gap `-5045/531441`.

## 3. Actual Schur condition, not only a compression

The full subset-DP matrix satisfies exactly

`K_0(C)u=(1057837/531441)u`.

Conceptually, pole swap fixes `C` and the uniform permutation law, so it commutes with `K_0`; the
swap-odd subspace is precisely `span(u)`.  Therefore this line is reducing.  Moreover `K_0` is
positive definite because every `M_pi^{-T}M_pi^{-1}` is positive definite, so its restriction to
`range(C)` is invertible.  The kernel/range Schur complement consequently has

`S_Cu=(1057837/531441)u`.

In particular, this is a failure of the actual T080 Schur condition and, already from its
Rayleigh quotient, of the full Loewner inequality `K_0(C)>=2P_{ker C}`.  It is not merely failure
of a nonreducing kernel compression.

## 4. Exact positive-definite M1 counterexample

Set

`A_mu=mu I+(1-mu)C`, with `mu=1/100`.

Its eigenvalues are exactly `1/100` (multiplicity two), `67/100` (multiplicity five), and
`463/100`; it is unit diagonal SPD and `lambda_min(A_mu)=mu`.  The same independent subset DP gives

```
kappa_mu=u^T K(A_mu)u/||u||^2
        =277091954946975183681661134197
         /140000000000000000000000000000.
```

Because `A_mu u=mu u`, the one-epoch energy identity

`A_mu-E[T_pi^T A_mu T_pi]=A_mu K(A_mu)A_mu`

makes the normalized expected final energy along `u` equal to `1-mu*kappa_mu`.  Here the active M1
factor is `q=(1-mu/8)^16>(7/8)^8`, and exact subtraction gives

```
(1-mu*kappa_mu)-q
=4198136398771974389711477950466919707327993
 /197032483697459200000000000000000000000000000000
>0.
```

Thus M1 fails at an explicit rational positive-definite matrix; no limiting argument is needed.

## 5. Scope

This exact certificate refutes T080 and the stronger one-epoch `A`-energy contraction M1.  It does
**not** refute the original covariance-map spectral-radius conjecture C001, because a one-step
operator-norm bound can fail while a multi-step spectral-radius bound still holds.

Reproduce with:

```
python scripts/verify_iter4_t080_simple_subset_dp.py
```

Evidence is written to
`research/evidence/ITER4_T080_SIMPLE_SUBSET_DP_INDEPENDENT_AUDIT.json`.
