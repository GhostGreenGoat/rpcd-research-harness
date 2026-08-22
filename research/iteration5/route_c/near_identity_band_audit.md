# Independent audit of the uniform near-identity band

Date: 2026-08-21.  Audited source:
`research/iteration5/route_a/uniform_near_identity_band.md`.

Verdict: no algebraic or quantifier blocker found; this is a valid E3 proof
candidate in the stated restricted regime.

Let `delta=1-mu`.  Since `tr(B)=n`, the eigenvalue deviations
`a_i=lambda_i-1` satisfy `sum a_i=0` and `a_i>=-delta`.  This polytope is
compact (each `a_i<=(n-1)delta`).  Its vertices have `n-1` entries equal to
`-delta` and the remaining entry `(n-1)delta`.  Convexity of
`sum a_i^2` therefore gives exactly

```
sum a_i^2<=n(n-1)delta^2<=n^2delta^2=theta^2.
```

For every permutation, `B_pi-I` remains symmetric with zero diagonal, so
its strict lower triangle contains exactly half the off-diagonal Frobenius
energy.  Hence

```
||M_pi-I||_2<=||B-I||_F/sqrt(2)<=theta/sqrt(2)
```

uniformly and pathwise.  With fixed dual feature `R_pi=I`,
`P=I` and `Q=E[M_piM_pi^T]`; the pathwise norm gives
`Q<=[1+theta/sqrt(2)]^2I`.  Loewner inversion has the stated direction, and
`B>=mu I` is equivalent to `I>=mu B^-1`.  Thus

```
K(B)>=[1+theta/sqrt(2)]^-2 mu B^-1.
```

When `theta<=1`, `1+1/sqrt(2)<2`, yielding the claimed coefficient larger
than `mu/4`.  The `n=1` case is the identity equality; for `n>=2` all steps
apply verbatim.  The result says nothing when `n(1-mu)>1` and does not
repair the global bare-Jensen barriers.

## Prefix corollary (N8)--(N9)

Fix a prefix set and chronological order `S`, `|S|=t`.  Extend that order to
a full permutation.  The strict-lower entries of its `t x t` factor `M_S`
are a subset of the full strict-lower entries, so the same pathwise bound

```
||M_S||_2<=1+theta/sqrt(2)                               (A1)
```

holds without replacing `theta` by a dimension-`t` parameter.  The exact
sequence energy is `||M_S^-1 h_S||^2`; (A1) therefore gives

```
||M_S^-1 h_S||^2
 >=[1+theta/sqrt(2)]^-2||h_S||^2.                        (A2)
```

For a uniform without-replacement prefix, its unordered support is uniform
among size-`t` subsets.  Hence, exactly (with no independence assumption),

```
E||h_S||^2=sum_i Pr[i in S]h_i^2=(t/n)||h||^2.           (A3)
```

Equations (A2)--(A3) prove N8 simultaneously as a family of matrix
inequalities for every integer `1<=t<=n`.  The final comparison with
`mu B^-1` again uses `I>=mu B^-1`.

If `theta<=2-sqrt(2)`, then

```
1+theta/sqrt(2)<=sqrt(2),
```

so the squared inverse factor is at least `1/2`.  For
`t=ceil(n/2)`, also `t/n>=1/2`; thus

```
J_t>=(mu/4)B^-1,
H_t>=J_t.
```

This confirms N9 for both parities and for `n=1`.  It must be distinguished
from N5--N6b: the latter is a full-epoch `K=J_n` fixed-test certificate and
achieves `mu/2` in this band, whereas N8--N9 is a direct prefix estimate and
loses the additional factor `t/n`, giving `mu/4` at half depth.  Neither is
the conjectured sharp `mu/2` half-prefix bound.
