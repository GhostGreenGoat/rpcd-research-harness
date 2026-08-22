# T085 finite-time consequences

Status: the transfer from a one-epoch matrix certificate to finite time is rigorous.  The desired
uniform premise `c_r(A)>=c mu` is still conjectural; the weaker two-step premise below is proved in
draft form.

## 1. Exact transfer, with no spectral/Jordan prefactor

Let `A` be unit-diagonal SPD, `mu=lambda_min(A)`, and let `K(A)` be the exact residual-coordinate
one-epoch energy-decrease matrix.  Every determinant-tail level is valid:

`0<=H_r(A)<=K(A)`.

If, for some `gamma in (0,1]`,

`H_r(A)>=gamma A^{-1}`,                                      (1)

then

```
E_pi[T_pi^T A T_pi]
 = A-AK(A)A
 <= A-AH_r(A)A
 <= (1-gamma)A.                                             (2)
```

Fresh independent permutations each epoch and conditional expectation give, for every deterministic
initial point,

```
E ||x_k||_A^2 <= (1-gamma)^k ||x_0||_A^2,                   (3)
E ||x_k||_A   <= (1-gamma)^(k/2) ||x_0||_A.                 (4)
```

Equation (4) is expectation of the distance, obtained by Jensen from the stronger squared-distance
bound (3).  It is not the weaker quantity `||E x_k||_A`.

For a relative squared-distance tolerance `epsilon`, it is sufficient to take

`k >= gamma^{-1} log(1/epsilon)` epochs.

For a relative expected-distance tolerance `epsilon`, it is sufficient to take

`k >= 2 gamma^{-1} log(1/epsilon)` epochs.

Markov applied to (3) also gives

```
P{||x_k||_A >= epsilon ||x_0||_A}
 <= (1-gamma)^k/epsilon^2.
```

Thus failure probability at most `delta` follows from

`k >= gamma^{-1}[2log(1/epsilon)+log(1/delta)]`.

There is also a simultaneous-in-time version with no extra union-bound factor.  For
`0<gamma<1`, the adapted process

`Y_k=||x_k||_A^2/(1-gamma)^k`

is a nonnegative supermartingale by the conditional form of (2).  Ville's inequality therefore
gives

```
P{exists k>=0:
  ||x_k||_A^2 > delta^{-1}(1-gamma)^k||x_0||_A^2} <= delta.  (5a)
```

Thus with probability at least `1-delta` the same geometric envelope holds for every epoch at
once.  This statement uses the fixed `A`-energy Lyapunov function and fresh independent
permutations; it does not follow merely from a spectral-radius asymptotic.

Each epoch uses `n` coordinate updates.  If the missing uniform statement

`gamma=c mu`                                                   (5)

holds for a universal `c>0`, (3) needs

`N <= [n/(c mu)]log(1/epsilon)` coordinate updates, exactly the requested order.

No Jordan-form, spectral-radius, or dimension prefactor enters (2)--(5); they use a one-step
matrix Lyapunov inequality.  Conversion to Euclidean norm can introduce the usual factor
`1/mu`, since `mu||x||_2^2<=||x||_A^2`.

## 2. Unconditional improved two-step certificate

For an `m x m` local problem `B`,

```
J_2(B)=[(2m-1)I-2B+Diag(diag(B^2))]/[m(m-1)].               (6)
```

Because `Diag(diag(B^2))>=I`,

`J_2(B)>=2(mI-B)/[m(m-1)]`.

Every eigenvalue `lambda` of `B` lies in

`[mu,m-(m-1)mu]`: the upper endpoint follows from `tr(B)=m` and the other `m-1` eigenvalues being
at least `mu`.  Concavity of `lambda(m-lambda)` and evaluation at both endpoints give

`lambda(m-lambda)>=mu(m-1)`.

Functional calculus in (6) therefore proves

```
J_2(B) >= (2mu/m)B^{-1}.                                    (7)
```

This improves the previous `2mu/m-mu^2/m^2` coefficient and is sharp at `B=I`.  Since
`K(B)>=J_2(B)`, it gives the unconditional full-epoch bound `gamma=2mu/n`.  Consequently,

```
E ||x_k||_A^2 <= (1-2mu/n)^k ||x_0||_A^2,
N <= [n^2/(2mu)]log(1/epsilon)                              (8)
```

for expected squared `A`-distance.  This is `O(n^2/mu)`, not the desired `O(n/mu)`, because a full
epoch costs `n` coordinate updates.

The exact rational barrier in `bellman_closure.md` shows why (7) may not simply be multiplied or
inducted across dependent coordinate pairs.

## 3. Conditional half-depth corollary

The surviving candidate is

`H_{ceil(n/2)}(A)>=(mu/2)A^{-1}`.                            (9)

If (9) is proved, then (3)--(5) give

```
E ||x_k||_A^2 <= (1-mu/2)^k ||x_0||_A^2,
N <= (2n/mu)log(1/epsilon),
E ||x_k||_A <= (1-mu/2)^(k/2)||x_0||_A.                    (10)
```

At present (9) is an open lemma supported only by the finite search recorded in
`research/evidence/ITER4_T085_HALF_DEPTH_SEARCH.json`.  It is not used as an unconditional result.

The factor `1/2` is now known to be the largest possible universal constant for any certificate of
the form `K(A)>=c mu A^{-1}`.  Indeed, for `A=mu I+(1-mu)11^T`, the parallel triangular solve is
`(1,mu,...,mu^(n-1))`, so

`gamma(A)/mu <= [n-(n-1)mu](1-mu^(2n))/[n mu(1-mu^2)]`.

First sending `n` to infinity and then `mu` to one makes the right side tend to `1/2`.  In
particular, the seemingly natural stronger global guess `gamma>=mu` is already exactly false at
`n=9,mu=9/10`; see `docs/ITER4_T090_CONSTANT_ASSESSMENT.md`.  Thus (9), if true, has the optimal
constant for this entire one-step energy-matrix architecture.

## 4. Exact closure of the historical `n=3, mu=1/5` test

For

`B=(1/5)I+(4/5)11^T`,

the first determinant lift had coefficient `547/1875`, below the strong target
`1-(14/15)^6`.  Retaining the exact second Schur moment makes `H_2=K` in dimension three, and exact
rational arithmetic gives

```
c_2(B)=1237/3125,
c_2(B)-[1-(14/15)^6]=647776/11390625>0.                     (11)
```

Thus the second-level construction genuinely clears the required finite barrier.  Equation (11) is
a single structured finite statement, not an all-dimensional theorem.
