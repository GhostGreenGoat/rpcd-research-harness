# The first non-matching `W4` slice: a three-vertex path at `d=6`

Date: 2026-08-22 (Asia/Shanghai)

Status: **internal E4 proof candidate**.  An independent hostile audit
reconstructed all seven principal minors and passed with no blocking caveat:
`research/iteration6/route_stitch/W4_THREE_PATH_D6_HOSTILE_AUDIT.md`.
There is no Lean/formal verification or external review.
It proves the uniform shifted-inverse lemma only for the smallest relevant
child dimension and one sparse support family, not for general `W4`.

## Statement

Let

```text
C=[[1,r,0],[r,1,s],[0,s,1]] direct_sum I_3,
t=sqrt(r^2+s^2)<1.
```

Then `lambda_min(C)=1-t`.  For every `0<mu<=1-t`,

```text
boxed: L3(C)>=(1/3)[C+(1-mu)I]^-1.                       (P1)
```

Since `2/d=1/3` at `d=6`, this is exactly the uniform-extension condition
(2.15).  It therefore proves full termwise `W4` recovery for every admissible
parent extension of this child.

## Reduction to a compact exact certificate

The right side of (P1) is increasing in `mu` in Loewner order, so it suffices
to use the hardest value `mu=1-t`.  Diagonal sign conjugation absorbs arbitrary
signs of `r,s`.  Write

```text
r=t sqrt(q),  s=t sqrt(1-q),  0<=q,t<=1.                 (P2)
```

All matrices in the exact `L3` formula remain block diagonal between the path
and the three isolated coordinates.  On an isolated coordinate the gap is

```text
1/3-1/[3(1+t)]=t/[3(1+t)]>=0.                            (P3)
```

It remains to check the symmetric `3 x 3` active gap

```text
G(q,t)=L3(C)_path-(1/3)(C_path+tI)^-1.                   (P4)
```

For every nonempty subset `S` of the three path coordinates, exact expansion
has the form

```text
det G[S,S]=p_S(q,t)/d_S(t),                              (P5)
```

where the denominators are positive multiples of `(1+t)(1+2t)` (with one
factor sometimes absent).  Converting every numerator to its tensor Bernstein
basis on `[0,1]^2` gives only nonnegative rational coefficients.  The seven
tables, including zeros at the identity edge `t=0`, are stored in the exact
JSON artifact below.  Hence every principal minor is nonnegative.  The
principal-minor characterization of symmetric PSD matrices gives `G>=0` and
proves (P1).

## Interpretation and boundary

This is the first support graph not covered by the matching identity
`H^2=D`: its middle vertex has degree two and `H^2-D` creates an oriented
leaf-to-leaf interaction.  Thus that interaction alone is not a barrier at
the first relevant dimension.  What remains open is a dimension-uniform
certificate for this path family, followed by overlapping paths/cycles where
several such interactions share coordinates.

Exact independent-reconstruction artifact:

```text
scripts/iter6_w4_three_path_d6_exact.py
research/iteration6/route_l3/evidence/W4_THREE_PATH_D6_EXACT.json
```

The proof uses exact Bernstein coefficients, not a parameter grid.  Independent
reconstruction artifacts are the checker and JSON alongside the hostile-audit
report in `research/iteration6/route_stitch`.
