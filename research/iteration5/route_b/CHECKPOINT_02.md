# Route B checkpoint 02

- Interval covered: `2026-08-21 20:08:57--20:38:10 +08:00`.
- All reported searches are E1 unless an exact rational finite statement is
  explicitly identified.

## A cleaner near-extremal family

Three equal duplicate groups placed at the vertices of a regular planar
simplex give a non-signed-rank-one family with spectrum

\[
 \mu^{\,3(k-1)+1},\qquad
 \left[\mu+(1-\mu){3k\over2}\right]^2.
\]

At `k=100`, `n=300`, `mu=0.94`, the half-depth ratio is
`0.5184132838`.  It remains above the signed-rank-one baseline at the same
`n,mu`, namely `0.5167275158`; therefore it is a second near-sharp family, not
a better extremizer in that comparison.  Searches with four through six
simplex groups were less hostile at the accessible sizes.

## Exact failure of a tempting family proof

The signed-rank-one proof counts every selected distinguished coordinate as
at least one unit of squared solve energy.  This does not transfer pathwise to
the replicated simplex.  For three groups, `mu=1/5`, after the first positive
special in group zero, take ordinary pivot groups

`(1,0,0,2)`

before the negative special.  Exact `Fraction` arithmetic gives the latter
solve as

\[
 -{2889\over3125},
\]

whose magnitude is below one by `236/3125`.  The finite certificate is
`pathwise_shortcut_counterexample.json`.  This kills the pathwise extension,
not the averaged half-depth claim.

## Signed-rank-one is not a pointwise finite extremizer

Optimizing the excess over the signed-rank-one value at identical `n,mu`
found a three-prototype example at `n=90` with

```
structured ratio       = 0.5949344773962826
signed-rank-one ratio  = 0.5963145593837560
excess                 = -0.0013800819874734
```

The margin to the actual half target is still positive by `0.09493`.  Under
proportional dimension scaling the negative excess rapidly shrinks, so this
is a finite extremizer warning rather than evidence of an asymptotic
violation.

## Large-n satellite attack

The preceding geometry was compressed to two duplicate groups: a large group
of copies of `p` and a small satellite group of copies of `q`.  This keeps a
full two-count Bellman state and allows thousands of tests at `n=300`.  Among
1,200 seeded samples, the smallest ratio was

\[
 0.5153289714491474>1/2
\]

at counts `(297,3)`, `mu=0.9505106068`, and prototype angle
`1.9477232226`.  It is `0.00036647` below signed rank one at the same `n,mu`.
At fixed parameters it decreases to `0.51277482` at `n=1000`, still positive
by `0.01277`; the signed-rank-one excess shrinks in magnitude.

## Next attacks

1. Re-optimize the satellite angle, multiplicity and `mu` directly at
   `n=1000`, where the half margin is small.
2. Run high-precision/full-matrix reconstruction if any margin becomes
   negative; no present value triggers that gate.
3. Test whether keeping two eigenvalue scales simultaneously small can make
   the negative signed-rank-one excess comparable to its shrinking half-gap.
4. Convert the clean replicated-simplex and satellite scans into a single
   portable evidence record with explicit seeds, state counts and controls.
