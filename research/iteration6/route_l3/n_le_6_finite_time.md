# Finite-time RPCD consequences of weighted level three

Date: 2026-08-22

Status: exact transfer from the internal E4 weighted level-two and level-three
theorem candidates.  There is no Lean verification or external review.

## 1. Prefix constants

Let `J_t(A)` be the exact expected decrease matrix after a uniform ordered
prefix of `t` distinct coordinates, and let

```text
C_t=J_t-(1/2)J_(t-1).
```

For a unit-diagonal SPD `n x n` matrix with `A>=mu I`, the audited statements
are

```text
J_1=I/n >=(mu/n)A^-1,                                    (1.1)

C_2 >=(3mu/(2n))A^-1,                                    (1.2)

C_3 >=L3 >=(2mu/n)A^-1.                                  (1.3)
```

Consequently,

```text
J_2=C_2+J_1/2 >=(2mu/n)A^-1,                             (1.4)

J_3=C_3+J_2/2 >=(3mu/n)A^-1.                             (1.5)
```

For every `n>=3`, the full epoch dominates its first three positions, so

```text
K(A)>=J_3(A)>=(3mu/n)A^-1.                               (1.5a)
```

This gives an all-dimensional strong-expectation benchmark before using the
sharper half-prefix constants available through dimension six.

Since the full one-permutation decrease matrix `K=J_n` dominates every
prefix, choose `q=ceil(n/2)`.  Equations (1.1), (1.4), and (1.5) prove, for
every `1<=n<=6`,

```text
K(A)>=J_q(A)>=(qmu/n)A^-1>=(mu/2)A^-1.                   (1.6)
```

The dimension-specific coefficient `rho_n=q/n` is

```text
n:       1    2    3    4    5    6
rho_n:   1   1/2  2/3  1/2  3/5  1/2.                   (1.7)
```

For `n=1`, unit diagonal forces `A=[1]` and one update is exact.

## 2. All-dimensional three-prefix benchmark

For one fresh uniform permutation, the exact identity

```text
E_pi[T_pi^T A T_pi]=A-AK(A)A
```

and (1.5a) give, for every `n>=3`,

```text
E[||x_(k+1)||_A^2 | x_k]
 <=(1-3mu/n)||x_k||_A^2.                                 (A1)
```

Fresh independent epochs, tower property, and Jensen imply

```text
E||x_k||_A^2 <=(1-3mu/n)^k||x_0||_A^2,                  (A2)

E||x_k||_A <=(1-3mu/n)^(k/2)||x_0||_A.                  (A3)
```

Thus relative expected `A`-distance `epsilon` is achieved after

```text
k_all=ceil{2log(1/epsilon)/[-log(1-3mu/n)]}
 <=ceil{(2n/(3mu))log(1/epsilon)}                         (A4)
```

epochs, or

```text
N_all<=n ceil{(2n/(3mu))log(1/epsilon)}                  (A5)
```

coordinate updates.  This is a rigorous all-dimensional
`O(n^2/mu log(1/epsilon))` benchmark for expectation of the distance itself,
not distance of the expected iterate.  It remains one factor `n` weaker than
the conjectured target.

If `n=3,mu=1`, unit diagonal and `A>=I` force `A=I`; one epoch is exact.  Thus
the logarithmic display (A4) is read only when `3mu/n<1`, with this zero-
contraction endpoint handled separately.

For `n=2`, use `K=J_2>=mu A^-1` separately:

```text
E||x_k||_A <=(1-mu)^(k/2)||x_0||_A,
N_2<=2 ceil{(2/mu)log(1/epsilon)}.                        (A6)
```

The scalar case `n=1` terminates in one coordinate update.

## 3. Sharper constants through dimension six

For one fresh uniform permutation, the exact energy identity is

```text
E_pi[T_pi^T A T_pi]=A-AK(A)A.                            (2.1)
```

Combining (1.6) with (2.1), and conditioning on the current iterate at each
fresh epoch, gives

```text
E[||x_(k+1)||_A^2 | x_k]
 <=(1-rho_n mu)||x_k||_A^2.                              (2.2)
```

Tower property and Jensen therefore give the stronger iterate-distance
statements requested in the problem:

```text
E||x_k||_A^2
 <=(1-rho_n mu)^k ||x_0||_A^2,                           (2.3)

E||x_k||_A
 <=(1-rho_n mu)^(k/2)||x_0||_A.                          (2.4)
```

These are expectations of the (squared) distance itself, not the weaker
distance of the expected iterate.

To ensure `E||x_k||_A<=epsilon||x_0||_A`, it is enough to take

```text
k >=ceil{ 2 log(1/epsilon)/[-log(1-rho_n mu)] }
  <=ceil{ 2 log(1/epsilon)/(rho_n mu) }.                  (2.5)
```

Every complete RPCD epoch uses `n` coordinate updates, so

```text
N <=n ceil{2 log(1/epsilon)/(rho_n mu)}
  <=n ceil{4 log(1/epsilon)/mu}.                          (2.6)
```

Thus the conjectured-order `O(n/mu log(1/epsilon))` finite-time complexity is
proved internally for every `n<=6`.  The first inequality in (2.6) keeps the
better odd-dimensional constants `rho_3=2/3` and `rho_5=3/5`.

## 4. Simultaneous high-probability version

Define

```text
Z_k=||x_k||_A^2/(1-rho_n mu)^k.                           (3.1)
```

Equation (2.2) makes `(Z_k)` a nonnegative supermartingale.  Ville's
inequality yields, with probability at least `1-delta`, simultaneously for
every epoch `k>=0`,

```text
||x_k||_A
 <=delta^(-1/2)(1-rho_n mu)^(k/2)||x_0||_A.              (3.2)
```

Hence it suffices that

```text
k >=[2log(1/epsilon)+log(1/delta)]
     /[-log(1-rho_n mu)]                                 (3.3)
```

and a simpler sufficient bound is

```text
k >=[2log(1/epsilon)+log(1/delta)]/(rho_n mu).            (3.4)
```

There is no union-bound `log k` penalty.

As above, when `rho_n mu=1`, unit diagonal forces the identity case and one
epoch is exact; (3.1)--(3.4) apply to `rho_n mu<1`.

## 5. Evidence boundary

- Weighted level two: internal E4, independently hostile-audited in Iteration
  5.
- Explicit `L3` and weighted level three: internal E4 after
  `research/iteration6/route_stitch/L3_HOSTILE_AUDIT.md`.
- The transfers (1.4)--(A6) and (2.1)--(3.4) are exact
  conditional-expectation algebra.
- The all-dimensional conclusion is the benchmark (A5), not the conjectured
  `O(n/mu)` update bound.  Closing the remaining factor starts with the open
  `W4` Schur-recovery condition in `general_t_schur_recursion.md`.
