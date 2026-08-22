# Remaining-gradient lemma for the local-inverse state

Status: exact general lemma (E3 proof candidate) plus an exact hostile control
against a tempting scalar without-replacement strengthening.  This lemma does
not close the global half bound.

Fix an order and a row position `k`.  Let `T` contain the current coordinate
and its at most `q` immediate predecessors, and let `O` contain all older
coordinates.  Let `d` be the row of `D_q` supported on `T`, so

```
d M_T=e_k^T.                                               (R1)
```

The unit-diagonal triangular identity `B_T=M_T+M_T^T-I`
implies the exact local energy formula

```
sigma:=d B_T d^T=2-||d||_2^2.                             (R2)
```

Indeed, both `d M_T d^T` and `d M_T^T d^T` equal the current diagonal
coefficient `d_k=1`.  Since `B_T` is positive definite and `||d||^2>=1`,

```
1<=||d||^2<2,       0<sigma<=1.                           (R3)
```

The nonzero old-history part of the defect `D_qM-I` is

```
r=d B_(T,O).                                              (R4)
```

The Schur complement of `B_O` in `B_(O union T)` proves

```
r B_O^-1 r^T <= sigma.                                    (R5)
```

The global spectral floor gives a sharper bound that was not used in the
counterexample below.  Apply the Schur complement to `B-mu I>=0` (first with
any smaller floor and then by continuity).  Since
`(B_O-mu I)^{-1}>=B_O^{-1}`, one obtains

```
B_T-B_TO B_O^{-1}B_OT >= mu I.
```

Testing on `d` and using (R2) yields

```
r B_O^{-1}r^T <=sigma-mu||d||^2
 =2-(1+mu)||d||^2 <=1-mu.                                (R5b)
```

Thus each individual forgotten-history row is uniformly small near the
identity.  This still does not control the operator norm of many aligned
rows when `n(1-mu)` is large; row-frame cancellation remains necessary.

Consequently, for every remaining-gradient vector `h_O`,

```
(r h_O)^2 <= sigma h_O^T B_O h_O.                         (R6)
```

This is a genuine matrix-valued, pathwise residual estimate.  It retains the
conditional covariance geometry lost by the failed scalar child-floor
potential.  It also explains why the local-inverse rows are stable even when
`mu` is small: every such row has Euclidean norm strictly below `sqrt(2)`.

## Why the obvious without-replacement summation still fails

For a uniformly random label subset `O` of size `r`, exact inclusion
probabilities give

```
E[h_O^T B_O h_O]
 =r(r-1)/[n(n-1)] h^T B h
  +r(n-r)/[n(n-1)] ||h||^2.                               (R7)
```

The second term is precisely the near-null-direction obstruction: replacing
it by `mu^-1 h^T B h` reintroduces a condition-number loss, and summing (R6)
over the old-set sizes gives a growing rather than constant coefficient.

One might hope to repair this by strengthening (R5) with an inclusion
fraction, for example

```
r B_O^-1 r^T <= (|O|/n) sigma.                            (R8)
```

This is false exactly.  Take `n=5`, `q=2`, `epsilon=1/100`, and

```
B=epsilon I+(1-epsilon)G,
G_ij=<v_i,v_j>,
v=((0,1),(4/5,3/5),(5/13,12/13),(7/25,24/25),(20/29,21/29)).
```

For the order `(0,4,2,3,1)` and final row, `|O|=2`, while

```
(r B_O^-1 r^T)/sigma
 =96509036395663477402608/104696053844535508536025
 > 9/10 > |O|/n=2/5.                                     (R9)
```

Thus even the exact conditional-variance potential can be almost saturated
by a small old subset.  Any successful average must exploit cancellations or
frame interactions **between different residual rows**, rather than summing
the scalar inequalities (R6) independently.  This is the unresolved generic
step for the linear-memory dual route.

The proof of (R1)--(R7) is quantified for every unit-diagonal SPD `B`, every
order, and every `q`; (R9) is one exact rational obstruction only.  See
`scripts/verify_local_inverse_schur_residual.py`.
