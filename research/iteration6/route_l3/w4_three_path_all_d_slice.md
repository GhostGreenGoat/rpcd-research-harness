# Dimension-uniform `W4` shifted-inverse theorem for a weighted three-path

Date: 2026-08-22 (Asia/Shanghai)

Status: **internal E4 proof candidate**.  An independent hostile audit
reconstructed the scaling, dimension parameter, valuations, denominators, and
all principal-minor Bernstein tables and passed with no blocking caveat:
`research/iteration6/route_stitch/W4_THREE_PATH_ALL_D_HOSTILE_AUDIT.md`.
There is no Lean/formal verification or external review.
This strengthens `w4_three_path_d6_slice.md` from `d=6` to every `d>=6`.
It remains a sparse structured slice, not a proof of unrestricted `W4`.

## Statement

For any `d>=6`, let

```text
C=[[1,r,0],[r,1,s],[0,s,1]] direct_sum I_(d-3),
t=sqrt(r^2+s^2)<1.
```

Then for every `0<mu<=1-t=lambda_min(C)`,

```text
boxed: L3(C)>=(2/d)[C+(1-mu)I]^-1.                       (U1)
```

Consequently every admissible one-coordinate extension of such a child has
full termwise Schur recovery in the `W4` recursion.

## Exact dimension-parametric certificate

Inverse order makes `mu=1-t` the hardest value.  Absorb the signs of `r,s` by
a diagonal sign conjugation and write

```text
r=t sqrt(q),  s=t sqrt(1-q),  0<=q,t<=1,
k=d-6>=0.                                                (U2)
```

Let `N_d` denote the numerator in the closed `L3` formula, so

```text
L3=N_d/[2d(d-1)(d-2)].
```

On the active three-path block, multiply the target gap by the positive scalar
`2d(d-1)(d-2)^2`.  The resulting symmetric matrix is

```text
M_d=(d-2)N_d-4(d-1)(d-2)^2(C_path+tI)^-1.                (U3)
```

For each of the seven nonempty principal subsets `S`, exact algebra gives

```text
det M_d[S,S]
 ={sum_(j=0)^ell k^j t^a_(S,j) p_(S,j)(q,t)}
   /{(1+t)^epsilon_S(1+2t)},                             (U4)
```

up to a positive constant absorbed into the numerator.  The maximum degree in
`k` is `3` for one-by-one minors, `6` for two-by-two minors, and `8` for the
determinant.  Every tensor-Bernstein coefficient of every
`p_(S,j)` on `[0,1]^2` is a nonnegative rational number.  Since
`k,t>=0` and the denominator is positive, all principal minors are
nonnegative.  The principal-minor characterization proves `M_d>=0`, hence
(U1).  Isolated coordinates decouple and have exact gap

```text
2/d-2/[d(1+t)]=2t/[d(1+t)]>=0.                           (U5)
```

The complete coefficient tables and stripped powers `a_(S,j)` are stored in
the exact artifact below; no interpolation in the dimension and no numerical
parameter grid is used.

## Scope and next obstruction

This closes the first non-matching interaction uniformly in dimension: one
degree-two vertex and its oriented `H^2-D` leaf-to-leaf term.  Therefore the
next minimal unsupported combinatorial state is not an isolated length-two
path.  It is either two overlapping degree-two interactions (a four-vertex
path), a cycle where signs cannot all be removed, or a vertex of degree at
least three.  Those are the smallest families on which the present principal-
minor certificate should next be tested or abstracted.

Exact artifact:

```text
scripts/iter6_w4_three_path_all_d_exact.py
research/iteration6/route_l3/evidence/W4_THREE_PATH_ALL_D_EXACT.json
```

Independent reconstruction artifacts are
`research/iteration6/route_stitch/independent_w4_three_path_all_d_audit.py` and
`research/iteration6/route_stitch/W4_THREE_PATH_ALL_D_INDEPENDENT_AUDIT.json`.
The result has no Lean formalization or external review.
