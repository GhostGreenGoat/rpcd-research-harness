# Dimension-uniform equal-weight star slice of the `W4` shifted inverse

Date: 2026-08-22 (Asia/Shanghai)

Status: **internal E4 proof candidate**.  An independent hostile audit
reconstructed the invariant sectors, scaling, parameter cover, and Bernstein
certificates and passed with no blocking caveat:
`research/iteration6/route_stitch/W4_EQUAL_STAR_ALL_D_HOSTILE_AUDIT.md`.
There is no Lean/formal verification or external review.
This is a structured family, not the universal `W4` theorem.

## Statement

Let `p>=3`, `d>=max(6,p+1)`, and let `C-I` be an equal-magnitude weighted
star `K_(1,p)` plus `d-p-1` isolates.  If the star spectral radius is `t<1`,
then `lambda_min(C)=1-t`, and for every `0<mu<=1-t`,

```text
boxed: L3(C)>=(2/d)[C+(1-mu)I]^-1.                       (S1)
```

Arbitrary edge signs are allowed because a diagonal sign conjugation removes
them on a tree.

## Exact invariant sectors

Use the center and normalized uniform-leaf basis.  There

```text
H=[[0,t],[t,0]],  H^2=t^2I,
D=diag(t^2,t^2/p).
```

Put `w=t^2/p+(p-1)t^4/p^2`.  Directly from the retained-state identity,

```text
S_cc=(d-2)t^2,
S_uu=(d-3)t^2+w,
S_cu=-t^3(p-1)/p.                                       (S2)
```

On each of the `p-1` transverse leaf directions, `H=H^2=0`, `D=t^2/p`,
and `S=w`.  Isolates decouple.

As before, the hardest value is `mu=1-t`.  Multiply the target gap by the
positive scalar `2d(d-1)(d-2)^2`.  Substitution of (S2) gives a `2 x 2`
center/uniform block `M`, one transverse scalar, and the positive isolated
gap.  Their denominators are positive multiples of `p^2(1+2t)` or
`p^2(1+t)`.

The `t`-Bernstein degrees of `M_cc`, `M_uu`, `det(M)`, and the transverse
scalar are respectively `3,5,7,5`.  Their structural leading zeros encode the
identity endpoint.  Every other coefficient is certified nonnegative by the
following exhaustive symbolic split:

```text
p=3:  d=6+h,
p=4:  d=6+h,
p>=5: p=5+a, d=6+a+h,
a,h>=0.                                                  (S3)
```

After each substitution in (S3), every Bernstein coefficient has an ordinary
power-basis expansion in `a,h` with nonnegative integer/rational coefficients.
Thus `M_cc,M_uu,det(M)` and the transverse scalar are nonnegative.  The
`2 x 2` block and all transverse/isolated sectors are PSD, proving (S1).

Exact complete coefficient expressions and sign checks:

```text
scripts/iter6_w4_equal_star_symbolic.py
research/iteration6/route_l3/evidence/W4_EQUAL_STAR_SYMBOLIC.json
```

The script performs no finite `p,d` scan; `a,h` remain symbolic.  Independent
reconstruction artifacts are
`research/iteration6/route_stitch/independent_w4_equal_star_audit.py` and
`research/iteration6/route_stitch/W4_EQUAL_STAR_ALL_D_INDEPENDENT_AUDIT.json`.
