# Independent hostile audit: all-`d` weighted three-path `W4` slice

Date: 2026-08-22 (Asia/Shanghai)

Verdict: **PASS for every integer `d>=6` in the stated
`P_3 direct_sum I_(d-3)` family**.  This is an internal E4 proof candidate,
not unrestricted `W4`; there is no Lean/formal or external review.

Audited source:
`research/iteration6/route_l3/w4_three_path_all_d_slice.md`.  I rebuilt the
dimension-parametric matrix and all coefficient certificates without using
the source checker as a premise.

## 1. Positive scaling and quantifiers

Writing the closed state as

```text
L3=N_d/[2d(d-1)(d-2)]
```

and `R=(C_path+tI)^-1`, the target gap is `L3-(2/d)R`.  Multiplication by
the strictly positive scalar `2d(d-1)(d-2)^2` gives exactly

```text
M_d=(d-2)N_d-4(d-1)(d-2)^2 R.                           (A1)
```

Thus no inequality direction is changed in (U3).  Put `k=d-6`.  The proof
uses only `k>=0`, so it covers every required integer dimension (indeed the
polynomial sign argument is valid for real `k>=0`).  The previous audit of
the `d=6` slice already checked that `mu=1-t` is hardest, diagonal sign
conjugation is exhaustive on a path, and `q=r^2/t^2 in [0,1]` covers all
relative edge weights.

## 2. Denominators, `t` valuations, and Bernstein signs

I independently expanded the seven nonempty principal minors of `M_d`.
Each denominator is a positive rational constant times `(1+2t)`, with an
additional `(1+t)` except for the middle one-by-one minor.  Hence all
denominators are positive on `0<=t<=1`.

As polynomials in `k`, the three one-by-one minors have degree 3, the three
two-by-two minors degree 6, and the determinant degree 8.  Every coefficient
is divisible exactly by `t`, `t^2`, or `t^3`, respectively.  After exact
polynomial division by that power, independent power-to-tensor-Bernstein
conversion on `(q,t) in [0,1]^2` found every coefficient nonnegative.  The
only zero Bernstein entries occur in the `k^6` coefficients for subsets
`01` and `12`; nonnegativity, rather than strict positivity, is all that is
needed.

Consequently every coefficient of every principal-minor numerator is
nonnegative for `k>=0`; all seven principal minors are nonnegative.  The
symmetric principal-minor criterion yields `M_d>=0`.  At `t=0` the extracted
factors correctly give equality rather than an illicit division.  Isolated
coordinates separately have gap `2t/[d(1+t)]>=0`.

An exact hostile interior control at `d=11`, `t=2/3`, `q=9/25` had all seven
principal minors strictly positive.

## 3. Evidence and scope boundary

Independent checker:

```text
research/iteration6/route_stitch/independent_w4_three_path_all_d_audit.py
```

Evidence snapshot:

```text
research/iteration6/route_stitch/W4_THREE_PATH_ALL_D_INDEPENDENT_AUDIT.json
```

This proves the shifted-inverse/outer-Schur recovery lemma for one weighted
length-two path plus isolates in all `d>=6`.  It still does not cover a
four-vertex path, overlapping degree-two interactions, cycles, degree-three
vertices, or dense children.  No general fourth-depth or RPCD conclusion is
being asserted.
