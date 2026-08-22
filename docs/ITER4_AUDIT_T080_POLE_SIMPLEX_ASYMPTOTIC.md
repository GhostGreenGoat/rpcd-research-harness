# Hostile audit: two-pole/simplex asymptotic constant

**Audited claim:** Section 19 of `docs/ITER4_T080_BOUNDARY_KERNEL_INEQUALITY.md`.

**Outcome:** PASS with no conclusion-level blocker.  The statement is an upper bound on any
possible dimension-uniform kernel constant; it does not prove the candidate lower bound `3/2`.

## 1. Gram geometry and spectrum

For two copies of a unit pole and `k` vectors

`w_j=a p+sqrt(1-a^2) r_j`,

where the `r_j` form a centered regular simplex, the distinct ring correlation is exactly

`rho=(k a^2-1)/(k-1)`.

The pole-odd vector is a zero mode.  The ring-standard eigenvalue is `1-rho` with multiplicity
`k-1`.  On the pole-even/ring-constant block, the determinant is zero and the trace is
`2+k a^2`.  This independently reconstructs spectrum (47), including the second zero mode.

## 2. Triangular recurrence and signs

For a positive pole followed by `m` ring symbols, the ring solve values are

`-a, -a q, ..., -a q^(m-1)`, where `q=1-rho`.

The negative pole then has solve value

`-2+(a^2/rho)(1-q^m)`.

The first ring after that pole has value

`a[2-q^m-(a^2/rho)(1-q^m)]`,

and the remaining values form the same geometric progression with ratio `q`.  Squaring and
summing reconstructs every term and sign in (48).  The exact checker compares this closed form
against the unreduced state recurrence word by word.

## 3. Category normalization

A positive-first word is determined by the nonnegative counts `(before,middle,after)` summing to
`k`, hence there are `binom(k+2,2)` such words.  Reversing the pole signs gives the same energy,
so there are twice as many oriented categories.  Averaging their energies and then dividing by
`||e_1-e_2||^2=2` leaves exactly the factor `1/[2 binom(k+2,2)]` in (49).  At `k=6,a=2/3` it
reconstructs `1057837/531441`.

## 4. Interchange of limit and finite average

Fix `a>0` first and take `k>1/a^2`.  Then `0<rho<1`, `q` stays uniformly below one for all
sufficiently large `k`, and `rho` stays uniformly away from zero.  Under the uniform composition
measure,

`E[q^m] <= (k+1)/[(1-q) binom(k+2,2)] = O_a(1/k)`.

The same estimate holds for `q^(2m)`, and symmetry of composition coordinates gives it for the
corresponding powers of the after-count.  Expanding (48) produces only bounded coefficients and
these geometric monomials.  Therefore all nonconstant terms vanish in expectation.  The limiting
word energy is

`2+2/(2-a^2)`,

and division by two gives `1+1/(2-a^2)` as claimed.

Finally, for any `c>3/2`, a positive rational `a` can be chosen so that this fixed-`a` limit is
below `c`, followed by a sufficiently large integer `k`.  The quantifiers are in the required
order.  This proves that no universal Loewner coefficient greater than `3/2` can hold.

## 5. Scope checks

- A low kernel Rayleigh quotient is enough to refute a proposed Loewner lower bound; the pole swap
  additionally makes this line reducing.
- The argument says `inf <= 3/2`, not `inf = 3/2`.
- It does not show the infimum is positive.
- It does not refute the covariance spectral-rate conjecture or the requested big-O complexity.
- The proof is analytic plus exact rational checking, but has no Lean or outside-human validation.

Under the repository evidence policy, this supports promotion of the asymptotic statement from E3
to **E4 hostile-audited proof candidate**.
