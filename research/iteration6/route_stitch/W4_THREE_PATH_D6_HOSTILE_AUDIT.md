# Independent hostile audit: the `d=6` three-path `W4` slice

Date: 2026-08-22 (Asia/Shanghai)

Verdict: **PASS for the stated sparse `d=6` family**.  The seven principal
minors were independently reconstructed, so this slice is an internal E4
proof candidate.  It is not dimension-uniform, not general `W4`, and has no
Lean/formal or external review.

Audited source:
`research/iteration6/route_l3/w4_three_path_d6_slice.md`.  The source checker
was not used as a premise.

## Scope and hardest parameter

For

```text
C_path=[[1,r,0],[r,1,s],[0,s,1]],
t=sqrt(r^2+s^2)<1,
```

the characteristic polynomial of `C_path-I` is
`z(z-t)(z+t)`, so `lambda_min(C)=1-t`.  The derivative

```text
d/dmu [(1/3)(C+(1-mu)I)^-1]
 =(1/3)(C+(1-mu)I)^-2 >=0
```

confirms that the largest admissible `mu=1-t` is the hardest value.  Because
the support is a tree, a diagonal sign conjugation independently absorbs the
signs of `r` and `s`.  For `t>0`, setting

```text
q=r^2/t^2,  r=t sqrt(q),  s=t sqrt(1-q)
```

covers the full family with `q in [0,1]`; at `t=0` all choices of `q` reduce
to the identity.  Thus the square certificate has no missing sign, ratio, or
endpoint case.

## Seven-principal-minor reconstruction

I rebuilt `D,E,F,S` and the closed `L3` matrix from the exact retained-state
formula, formed

```text
G(q,t)=L3(C)_path-(1/3)(C_path+tI)^-1,
```

and independently expanded all `3+3+1=7` nonempty principal minors.  Their
denominators are positive multiples of `(1+t)(1+2t)` (the middle diagonal
minor needs only `1+2t`).  Converting each numerator from the power basis to
the tensor Bernstein basis produced respectively

```text
21, 4, 21, 36, 55, 36, 65
```

coefficients, all nonnegative.  The zero coefficients occur only on the
expected `t=0` identity edge.  A symmetric `3 x 3` matrix is PSD iff all of
its principal minors are nonnegative, so this exhausts the active block; it
is not merely a leading-minor test.  The three isolated coordinates have the
exact gap `t/[3(1+t)]>=0`.

An additional exact interior control used
`t=2/3,q=9/25`, so `(r,s)=(2/5,8/15)`; all seven rational principal minors
were positive.

## Evidence and boundary of the claim

Independent checker:

```text
research/iteration6/route_stitch/independent_w4_three_path_audit.py
```

Evidence snapshot:

```text
research/iteration6/route_stitch/W4_THREE_PATH_D6_INDEPENDENT_AUDIT.json
```

The proof establishes the uniform shifted-inverse condition only for one
three-vertex path plus three isolated coordinates.  It does not cover
`d>6`, overlapping paths, cycles, stars, or dense supports.  Those are the
remaining structural tests before any general fourth-level claim.
