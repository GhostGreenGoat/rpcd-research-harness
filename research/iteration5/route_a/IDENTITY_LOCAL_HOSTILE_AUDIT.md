# Hostile audit: fixed-dimensional identity neighborhood

Audited source: `docs/ITER5_PREFIX_IDENTITY_LOCAL_THEOREM.md`.

Outcome: **PASS for `n>=3`, with `n=2` requiring a separate direct proof**.
The added weighted hierarchy also passes, including its claim of one
simultaneous fixed-dimensional neighborhood.  No radius is uniform in
dimension.

## 1. First jet

For `A=I+epsilon H`, the strict lower part of the triangular factor is
`epsilon H` restricted by the order.  Its inverse is a finite Neumann
polynomial, and the row at prefix position `k` is

```
e_(pi_k)^T-epsilon sum_(j<k)H_(pi_k,pi_j)e_(pi_j)^T
 +O(epsilon^2).
```

A label is selected with probability `t/n`.  An unordered pair is selected
with probability `t(t-1)/[n(n-1)]`, and exactly its later row supplies the
two symmetric first-order cross entries.  Hence

```
J_t=(t/n)I-epsilon*t(t-1)/[n(n-1)] H+O(epsilon^2)
```

with the claimed sign and no missing factor two.  Congruence by the square
root gives (L3).

## 2. Compactness and the uniform remainder

For fixed `n`, normalize zero-diagonal directions by `||H||=1`.  This set is
compact.  Every nonzero symmetric zero-diagonal `H` has trace zero and
`lambda_min(H)<0`; otherwise it would be a nonzero PSD matrix with zero
diagonal, which is impossible.  Continuity therefore gives a
dimension-dependent constant

```
inf_{||H||=1}-lambda_min(H)>0.
```

The prefix matrix is a finite polynomial in the strict triangular entries,
uniformly over finitely many permutations.  The matrix square root is analytic
on a fixed ball about identity.  Their `O(epsilon^2)` remainders are therefore
uniform on the compact normalized direction set.  For `n>=3`, `t>=2` and
`d>0`, so the strict first-order margin dominates this remainder in a single
neighborhood depending on `n`.

This argument does **not** provide a dimension-uniform modulus.  Both the
compactness constant and the analytic remainder bound may deteriorate with
`n`; the source states this limitation correctly.

## 3. The `n=2` endpoint

For `n=2`, `t=1` and `d=0`.  Thus the source statement
`-d lambda_min(H)>0` is false in that dimension, and the strict-jet
compactness argument cannot be used.  The theorem itself remains true, even
globally:

```
J_1=I/2 >= (mu/2)A^{-1}
```

is just `A>=mu I` after congruence.  The corrected statement should say
`n>=3` in the strict first-order section and treat `n=2` separately.

## 4. Weighted-prefix hierarchy

Writing the jet coefficients of `J_t` as

```
c(t)=t/n,
d(t)=t(t-1)/[n(n-1)],
```

direct subtraction gives, with no asymptotic manipulation,

```
c_t=c(t)-c(t-1)/2=(t+1)/(2n),
d_t=d(t)-d(t-1)/2=(t-1)(t+2)/[2n(n-1)].
```

The normalized first-order matrix is

```
(c_t-d_t)H-c_t lambda_min(H) I.
```

The source implicitly uses `c_t-d_t>0`.  It is true throughout the stated
range (indeed for every `t<=n-1`), because

```
2n(n-1)(c_t-d_t)
 =(t+1)(n-1)-(t-1)(t+2)
 >=t(t+1)-(t^2+t-2)=2.
```

Hence its smallest eigenvalue is exactly
`-d_t lambda_min(H)>0` for `t>=2`.  At `t=1`, `d_t=0`, but the required
inequality is globally equivalent to `A>=mu I`, as the source says.

For simultaneous compactness, normalize `H` once.  The continuous quantity
`-lambda_min(H)` has a positive fixed-`n` minimum on that compact sphere.
For each of the finitely many `2<=t<=ceil(n/2)`, the strict linear margin is
at least `d_t` times this minimum; their minimum is still positive.  The
inverse-triangular polynomials and square root have a common uniform
`O(epsilon^2)` remainder on the compact sphere, and `t=1` needs no local
argument.  Therefore a single neighborhood for the entire finite hierarchy
is justified.  The argument supplies no lower bound uniform in `n`.

## 5. Scope

The result establishes local safety in every direction at identity for each
fixed dimension.  It is not a uniform neighborhood theorem, does not control
multiscale sequences in which `n` changes, and does not prove the general
half-prefix statement or C001.  The source exact permutation verifier was run
through `n=7`; no Lean/E6 artifact exists.
