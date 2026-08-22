# Hostile audit: finite positive-equicorrelation dual constant

Audited source: Section 5 of `linear_memory_dual.md`.

Outcome: **PASS** for every finite positive equicorrelation matrix and its
diagonal-sign conjugates.  The constant is nonsharp and the proof does not
extend by itself to a general correlation matrix.

## 1. Preconditioner block

The exact row sums of `D_q` are `mu^min(q,i)`.  Hence

```
p_parallel=[S_q+(n-q)mu^(2q)]/n >=S_q/n.
```

With `z=mu^(2q)` and `ell=n-(n-1)mu`, direct use of
`(1-mu)S_q=(1-z)/(1+mu)` gives the equality in (L17).  Since `q/n>=1/2`,
the last term of `S_q` gives `S_q/n>=z/(2mu^2)`.  The remaining scalar bound

```
z/(2mu^2)+(1-z)/[mu(1+mu)]>=1/2
```

is valid: after multiplication by `2mu^2(1+mu)`, the gap is
`(1-mu)[2mu+z(1-mu)]`.

For the transverse block, `tr(P)=||D||_F^2>=n` and the positive row sums are
at most one, so `p_parallel<=1` and `p_perp>=1`.  These two eigenvalue checks
indeed imply `P>=(mu/2)B^-1`; no direction is omitted.

## 2. Tail norm and dual inversion

The exact defect is `DM=I+rho mu^q U_q`.  Both maximum row and column sums of
`U_q` are `n-q-1<=q`, so its spectral norm is at most `q`.  The elementary
bounds `(1-rho)^q<=exp(-q rho)` and `y exp(-y)<=1/e` give (L19).

Pathwise,

```
D^T(DM)(DM)^TD <=(1+1/e)^2D^TD,
```

so averaging gives `Q<=c^2P`.  Order reversal under inversion then yields
`P Q^-1 P>=c^-2P`; combining with the audited preconditioner inequality gives
exactly `mu/[2(1+1/e)^2]>25mu/98`.  The Loewner directions and the factor two
are correct.

Diagonal-sign conjugation preserves `M,D,P,Q` up to the same orthogonal
conjugation, so the stated signed extension is also valid.

## 3. Scope

This proves an explicit dimension-free full-epoch certificate only on the
positive-equicorrelation orbit.  The architectural generic gaps remain a
lower bound for the averaged local-inverse frame `P` and a dimension-free
operator bound on the aligned conditional-tail rows.  It does not prove the
general `H_ceil(n/2)` target.
