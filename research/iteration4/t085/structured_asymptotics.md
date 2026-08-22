# Structured asymptotics for the second-moment compression

Status: algebraic proof draft (E3), pending hostile audit.

Write `rate_B(X)=lambda_max(B^{1/2}XB^{1/2})`.  The symbols `R,U,W,P` are those in
`compression_lemma.md`, and all limits below take `mu->0` with fixed `m>=3`.

## 1. Signed rank-one / high-nullity family

Let

`B=mu I+(1-mu)11^T`.

The inverse and leverage are exchangeable.  On `1^perp`, `G` has eigenvalue `1/mu` and

`s_i=1/G_ii ~ m mu/(m-1)`.

Consequently

`rate_B(bar(D)_B) -> 1/(m-1)` on the `(m-1)`-dimensional transverse space, while the parallel
normalized rate vanishes.

Every child is the same family in dimension `d=m-1`.  Its first-loss transverse normalized rate is
`1/(d-1)=1/(m-2)`.  At the parent, averaging the lifted child transverse spaces multiplies the
ordinary transverse coefficient by `(m-2)/(m-1)`.  After the parent `B` normalization this gives

```
rate_B(R) -> 1/(m-1).                                       (1)
```

For the pre-lift bound, `alpha_i->1/(m-2)` and

`rate_B(G-bar(D)-I/m)->(m-2)/(m-1)`,

so

`rate_B(U)->1/(m-1)`: this side is sharp.

For the post-lift bound, the pivot Schur matrix is

`C_i-b_i b_i^T=mu[I+(1-mu)11^T]`.

Its product with the child transverse loss has limiting rate `1/(m-2)`, hence

`rate_B(W)->1/(m-2)`.

Using the exact child spectral rates, taking the parallel sum on the transverse space gives

```
rate_B(P) -> 2/(2m-3).                                      (2)
```

Thus `P/R -> 2(m-1)/(2m-3)`, which tends to one.  Since the normalized spectrum of `R` consists of
`m-1` copies of `1/(m-1)` and one zero, the direct trace-square bound (3) in
`compression_lemma.md` equals `2/m`, with overhead `2(m-1)/m<2`.

For the trace-square-only child version, put `d=m-1`.  Formula (2) applied to the `d-1` equal
nonzero child-loss eigenvalues gives

```
rate_B(U^(2)) -> 2(d-1)/d^2,
rate_B(W^(2)) -> 2/d,
rate_B(P^(2)) -> 4(d-1)/[d(2d-1)].                          (2a)
```

Thus `P^(2)/R -> 4(d-1)/(2d-1)<2`.  The adaptive selector chooses `U^(2)` and has overhead
`2(d-1)/d<2`.

## 2. Regular simplex / simple-null family

Let `C_m` have diagonal one and off-diagonal `-1/(m-1)`, and set

`B=mu I+(1-mu)C_m`.

At `mu=0`, the parent transverse eigenvalue is `m/(m-1)` and the all-ones eigenvalue is zero.  A
child has dimension `d=m-1`, diagonal one and off-diagonal `-1/d`.  Its eigenvalues are

`(d+1)/d` on `1^perp` and `1/d` on `span(1)`.  Its inverse diagonal is `2d/(d+1)`, so its leverage
is `(d+1)/(2d)`.  Direct substitution into

`bar(D)=d^{-1}(G-I)sI(G-I)` gives the child ordinary loss eigenvalues

```
D_trans = 1/[2d^2(d+1)],
D_parallel = (d+1)(d-1)^2/[2d^2].                           (3)
```

For a parent transverse vector, the lifted child vector has zero child-parallel component because
`1+(m-1)(-1/(m-1))=0`.  Its averaged transverse squared norm is `(m-2)/(m-1)`.  Combining this with
(3) and the parent normalization proves

```
r := rate_B(R) -> (m-2)/[2(m-1)^4].                         (4)
```

The child normalized maximum rate is

`alpha=m(m-2)^2/[2(m-1)^3]`.

Meanwhile the lifted inverse average has parent transverse normalized rate `(m-2)/(m-1)`.  Hence

```
rate_B(U) -> m(m-2)^2 r.                                    (5)
```

This is the exact cubic child-scalarization loss.

For the post-lift bound, `E_i^s=C_i-b_i b_i^T` annihilates the dangerous child-parallel mode at
`mu=0`.  Its surviving transverse product with (3) is

```
beta_i -> 1/[2(m-1)^3]=[(m-1)/(m-2)]r.                      (6)
```

Thus the exact-spectral `W` has bounded overhead, and the exact-spectral parallel sum yields

```
rate_B(P)/r
 -> 2m(m-1)(m-2)^2/[m(m-2)^3+(m-1)].                       (7)
```

The expression in (7) is bounded (it tends to two), whereas the pre-lift factor in (5) diverges
like `m^3`.  Finally, `R` again has `m-1` equal nonzero normalized eigenvalues and one zero, so the
direct trace-square scalar bound has overhead `2(m-1)/m<2`.

For the trace-square-only post-lift rate, the surviving spectrum has `d-1` equal eigenvalues and one
zero.  Equation (2) doubles the aggregate parent rate exactly:

```
rate_B(W^(2)) -> 2r.
```

The pre-lift two-moment rate is exact here because its largest eigenvalue is the exceptional
one and all remaining eigenvalues are equal.  Therefore, with `A_m=m(m-2)^2`,

```
rate_B(P^(2))/r -> 4A_m/(A_m+2)<4.                           (7a)
```

The adaptive selector chooses `W^(2)` and has overhead exactly two.  This distinguishes the smooth
parallel certificate used in the main float stress test from the sharper exact-spectral and
adaptive variants.

## 3. Meaning of the two tests

- High nullity needs the leverage-weighted anisotropy in `U`.
- A simple null needs the pivot Schur matrix in `W` to suppress the child direction that disappears
  upon lifting to the parent.
- The parallel sum is a rigorous PSD mechanism for selecting the complementary information without
  deciding which geometry holds.

These calculations prove that the compression itself passes both required limiting tests.  They do
not bound its third and higher Bellman lifts, which remains the blocker documented in
`bellman_closure.md`.

## 4. A larger exactly analyzable half-depth class

Before the boundary block-union calculation, the one-block signed-rank-one family admits an
all-`mu` half-depth proof.  Let `r=ceil(n/2)`, `d=n-r`, and write the ordinary determinant-tail
eigenvalues on `1^perp` and `span(1)` as `h_perp,h_parallel`.

For a transverse right side `e_i-e_j`, every distinguished coordinate that appears in the random
prefix contributes squared solve magnitude at least one: the first contributes exactly one, and
before the second appears the accumulated solve sum retains the first sign while decaying by
factors of `mu`.  Hence the prefix energy is at least the number of distinguished coordinates
selected.  Its expectation is `2r/n`, and normalization by `||e_i-e_j||^2=2` gives

`h_perp>=r/n>=1/2`.                                        (8a)

On the parallel line, let `p_k` be the ordinary parallel eigenvalue at local size `k` and put
`q_k=k p_k`.  One Bellman lift obeys

`q_k=1+mu^2 q_{k-1}`.

Indeed, the first pivot solve equals one and leaves the constant child right side `mu 1`; its
child energy is therefore multiplied by `mu^2`.

The determinant leaf is nonnegative, so after `r` lifts

`q_n>=S_r:=sum_{j=0}^{r-1}mu^(2j)`.

With `L=n-(n-1)mu` and `z=mu^(2r)`, the generalized parallel coefficient divided by `mu` is at
least

```
L S_r/(n mu)
 =S_r/n+(1-z)/[mu(1+mu)]
 >=z/(2mu^2)+(1-z)/[mu(1+mu)]
 =1/[mu(1+mu)]+z(1-mu)/[2mu^2(1+mu)]
 >=1/2.                                                     (8b)
```

Here `S_r/n>=(r/n)mu^(2r-2)>=z/(2mu^2)`.  The endpoint `mu=1` follows by continuity.  Equations
(8a)--(8b) cover the whole space because uniform prefix averaging makes `H_r` permutation
invariant, with exactly the transverse and parallel eigenspaces.  They prove, for every `n>=2` and
`0<mu<=1`,

`H_{ceil(n/2)}(mu I+(1-mu)11^T)>=(mu/2)A^{-1}`.            (8c)

Diagonal sign conjugation gives the same result for every signed-rank-one block considered alone.
This is an exact structured theorem candidate; it is not the universal half-depth statement.

Let `n=k_1+...+k_b` and consider the block-diagonal family

`A_mu=diag(B_{k_1}(mu),...,B_{k_b}(mu))`,

where each nontrivial block is signed-rank-one (independent diagonal sign conjugacies are harmless).
Let a global random prefix contain `r` coordinates, and fix a block of size `k>=2`.  The number `S`
of selected coordinates from this block is hypergeometric, with

```
E S=rk/n,
P(S=0)=binom(n-k,r)/binom(n,r)                               (8)
```

under the convention that the numerator is zero if `n-k<r`.

The local rank-one prefix formula, proved by the same transverse/parallel recursion as the shallow
determinant-tail formula, is

```
lim_{mu->0} c_s^prefix(B_k(mu))/mu
 = (2s-1-1/k)/(k-1),       1<=s<=k.                         (9)
```

The local parallel generalized coefficient is order one as soon as `s>=1`, so after division by
`mu` it cannot be the limiting minimum.  Averaging (9) over `S` gives the exact transverse limit

```
g(n,r,k)
 =[2rk/n-(1+1/k)(1-P(S=0))]/(k-1).                         (10)
```

For `r=ceil(n/2)`, use `2r/n>=1` and `P(S>=1)<=1` to obtain

```
g(n,ceil(n/2),k)
 >= 1-1/[k(k-1)] >= 1/2.                                   (11)
```

The expected prefix matrix remains block diagonal, so its generalized minimum is the minimum over
the block values.  Since `H_r>=J_r`, (11) proves

```
liminf_{mu->0} c_{ceil(n/2)}(A_mu)/mu >= 1/2                (12)
```

for every finite disjoint union of signed-rank-one blocks.  This strictly enlarges the one-block
sharpness analysis and explains why the two-block counterexample searches bottomed out above
`0.8` in small dimensions.  Statement (12) is still a structured-boundary result, not the universal
half-depth conjecture.
