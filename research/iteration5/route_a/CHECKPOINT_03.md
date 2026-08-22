# Iteration 5 route A — checkpoint 03

Time: 2026-08-21 21:08 +08:00 (about 90 minutes from observed start).

## Linear memory is necessary for the new dual state

The `q`-step local inverse has now been analyzed exactly on positive
equicorrelations.  It interpolates between the failed adjacency feature at
`q=1` and the exact inverse moment at `q=n-1`.  In the sharp scaling
`rho=c/n`, `q/n->alpha`, its parallel certificate has the explicit continuum
form

```
(1+c)(integral s^2)^2/(integral u^2),
s(x)=exp[-c min(x,alpha)],
u(y)=s(y)+c exp(-2c alpha)(1-alpha-y)_+.
```

For every `q=o(n)`, this becomes
`(1+c)/(1+c+c^2/3)`, which is below one half for
`c>(3+sqrt(21))/2`.  Thus sublinear memory is analytically impossible for
this dual architecture.  At `alpha=1/2`, the remaining exponential
inequality has been proved by an all-positive Taylor coefficient expansion
and independently hostile-audited.

More strongly, a short finite-dimensional argument now proves on every
positive equicorrelation (and signed conjugate) that the half-memory state
gives

```
K(B) >= [25mu/98] B^-1 > (mu/4)B^-1.
```

The proof combines `P>=(mu/2)B^-1` with the pathwise tail norm
`||D_qM||<7/5`.  I independently checked the exact scalar identity,
transverse trace estimate, operator norm, inversion direction, and constant.
This closes the desired update order on the structured family, not in
general.

## Generic remaining-gradient lemma

For an arbitrary unit-diagonal SPD matrix, a local inverse row `d` and its
forgotten-history residual `r` obey

```
sigma=dB_Td^T=2-||d||^2,
r B_O^-1 r^T <= sigma-mu||d||^2 <=1-mu.
```

This follows from the Schur complement of `B-mu I`, using a smaller floor and
continuity if the matrix at the exact floor is singular.  It is the first
generic matrix-valued conditional-tail control for the linear-memory state.

The obvious scalar without-replacement damping is false: an exact rational
`n=5,q=2` example has captured fraction `0.9218...` although `|O|/n=0.4`.
Thus one must exploit cancellation/frame geometry among different residual
rows.  Summing individual Schur estimates cannot close a dimension-free
operator norm.

## Hostile status

- Fixed positional, direct-adjacency, weighted-adjacency, and scalar
  child-floor states are all exactly refuted with separate provenance.
- The equicorrelation theorem passes simultaneously for every prefix depth
  through half.
- The fixed-dimensional identity-local weighted hierarchy passes in one
  simultaneous (nonuniform-in-`n`) neighborhood.
- A float64 exhaustive-order scan of the new half-memory generic certificate
  on 200 hostile matrices through `n=7` found no violation; its smallest
  normalized value was `1.0087996`.  This is E1 only.
