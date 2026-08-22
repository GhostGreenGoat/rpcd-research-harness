# Independent hostile audit: all-dimensional equal-weight star `W4` slice

Date: 2026-08-22 (Asia/Shanghai)

Verdict: **PASS for the stated equal-magnitude star family**.  This is an
internal E4 proof candidate, not arbitrary stars or universal `W4`; no
Lean/formal or external review exists.

For a `K_(1,p)` star of spectral radius `t`, the center/uniform-leaf sector has
`H=[[0,t],[t,0]]`, `D=diag(t^2,t^2/p)`.  I reconstructed the full-coordinate
diagonal of `F^2` and obtained independently

```text
w=t^2/p+(p-1)t^4/p^2,
S_cc=(d-2)t^2,
S_uu=(d-3)t^2+w,
S_cu=-t^3(p-1)/p.
```

In particular the off-diagonal term follows from
`-2t^3+t^3(1+1/p)`, and the transverse leaf sector has `S=w`; no matching
identity was smuggled in.

The proposed scaled matrix is exactly the target gap multiplied by the
positive scalar `2d(d-1)(d-2)^2`.  Symmetry reduces it to a `2 x 2`
center/uniform block, one repeated transverse scalar, and isolates.  I rebuilt
both block diagonals, its determinant, and the transverse scalar.  Their
denominators are respectively positive forms using `1+2t` or `1+t`, with
`p^2` where stated, and their `t`-Bernstein degrees are `3,5,7,5`.

The exhaustive parameter split is correct:

```text
p=3,d=6+h;  p=4,d=6+h;  p=5+a,d=6+a+h,
a,h>=0.
```

It covers exactly `p>=3,d>=max(6,p+1)`.  An independent Bernstein conversion
found every ordinary power coefficient in `a,h` nonnegative in all four
sectors (up to 200 coefficients in the determinant `p>=5` branch).  Hence
both diagonals and the determinant of the `2 x 2` block, plus the transverse
scalar, are nonnegative.  The sector decomposition proves PSD.  The identity
edge is represented by leading zeros, not divided away.  A fixed exact
control at `p=7,d=12,t=99/100` is strictly positive in all four sectors.

Independent checker and snapshot:

```text
research/iteration6/route_stitch/independent_w4_equal_star_audit.py
research/iteration6/route_stitch/W4_EQUAL_STAR_ALL_D_INDEPENDENT_AUDIT.json
```

The equality of edge magnitudes is essential to the two-sector reduction.
Unequal degree-three stars live on a two-dimensional weight simplex and are
not covered.
