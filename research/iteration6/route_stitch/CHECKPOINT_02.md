# Route Stitch checkpoint 02

- Local start: `2026-08-22T16:35:07.9149419+08:00`.
- Checkpoint: approximately one hour into the run.

## New analytic outcome

The exterior prefix certificate has eigenvalue coefficients
`v_i=lambda_i e_(r-1)(lambda_-i)/binom(n,r)`.  The exact pair difference

```text
v_i-v_j=(lambda_i-lambda_j)e_(r-1)(lambda excluding i,j)/binom(n,r)
```

shows that its only spectral bottleneck is the minimum eigenspace.  This
produces the sufficient all-dimensional region

```text
e_(r-1)(lambda_2,...,lambda_n)>=binom(n,r)/2.
```

It contains every rank-two constant-diagonal projector lift
`A=aI-(a-mu)P`, `rank(P)=2`, `diag(P)=2/n`, for all `mu`; a one-line
derivative sign proves this.  For small `mu` this lies strictly outside the
scalar determinant region.  An explicit rational `n=8,mu=1/100` example is
being checked exactly.

## Closed scalar-stitching shortcut

The `J2` polynomial energy coefficient is also weakest at `lambda_min`.
Therefore convex mixing of `J2`, exterior volume, and any sub-target scalar
determinant/near-identity certificate cannot cover any spectrum beyond the
union of the individual regions.  The missing low/high bridge must retain a
noncommuting shorted cross block.

## Independent cross-audit

The sibling `L3` Schur-compensation proof passed a definition-level hostile
audit, including both exceptional Bernstein tables and the negative-sign
high-`mu` branch.  Its exact scope is weighted level three / dimensions at
most six, not half depth in general.
