# A matching-block slice of the uniform `W4` shifted-inverse lemma

Date: 2026-08-22 (Asia/Shanghai)

Status: **internal E4 proof candidate**.  An independent hostile audit passed
with no blocking caveat:
`research/iteration6/route_stitch/W4_MATCHING_BLOCK_HOSTILE_AUDIT.md`.
There is no Lean/formal verification or external review.
This proves one structured slice of the still-open universal inequality (2.15)
in `general_t_schur_recursion.md`; it is not a proof of general `W4`.

## Statement

Let `d>=6`, and let `C` be a unit-diagonal SPD matrix whose support graph is a
matching: after a simultaneous permutation,

```text
C=direct_sum_j [[1,r_j],[r_j,1]] direct_sum I_q,
```

where the `r_j` may have different magnitudes and either sign.  If
`0<mu<=lambda_min(C)`, then

```text
boxed: L3(C)>=(2/d)[C+(1-mu)I]^-1.                       (M1)
```

Consequently the full termwise Schur recovery condition for the `W4` Bellman
step holds uniformly over every admissible one-coordinate extension of this
child `C`.

## Exact block reduction

Put `H=C-I` and `D=Diag(diag H^2)`.  Every row of `H` has at most one nonzero
entry, hence

```text
H^2=D,  F=H+H^2-D=H,  E=Diag(diag H^3)=0.
```

In the exact retained state,

```text
S=(d-3)H^2-2H^3+HD+DH+Diag(diag F^2)=(d-2)D.            (M2)
```

Substitution into the closed formula for `L3` gives

```text
L3(C)={4(d-1)(d-2)I-10(d-2)H+(3d-4)D}
       /[2d(d-1)(d-2)].                                  (M3)
```

Thus `L3(C)` and `C` are simultaneously block diagonal.  On a singleton,
the left eigenvalue is `2/d`, while the right side of (M1) is
`2/[d(2-mu)]<=2/d`.

Consider a two-coordinate block and put `t=|r_j|`.  Its two `H` eigenvalues
are `h=+t,-t`, and `t<=1-mu`.  On such an eigenline, after multiplying by
positive denominators, (M1) is equivalent to

```text
N_h:=4(d-1)(d-2)(1-mu+h)
     +(3d-4)t^2(2-mu+h)
     -10(d-2)h(2-mu+h) >=0.                              (M4)
```

Let `a=1-mu` and `t=au`, so `0<=a,u<=1`.

For `h=-t`, all three terms in

```text
N_- =4(d-1)(d-2)(a-t)
     +(3d-4)t^2(1+a-t)
     +10(d-2)t(1+a-t)                                   (M5)
```

are nonnegative.

For `h=+t`, write `k=d-6>=0`.  Exact expansion in the dimension gives

```text
N_+(d)=N_+(6)+k partial_d N_+(6)+4a(1+u)k^2,             (M6)

N_+(6)=2a[40+20u-20au-13au^2+7a^2u^2+7a^2u^3],         (M7)

partial_d N_+(6)
 =a[36+26u-10au-7au^2+3a^2u^2+3a^2u^3].                (M8)
```

The first bracket is at least

```text
40+20u(1-a)-13au^2 >=27,
```

and the second is at least

```text
36+u(26-10a-7au)>=36+9u>0.
```

Every term in (M6) is therefore nonnegative.  This proves both eigenline
comparisons and hence (M1), with no restriction that the blocks share a
common correlation magnitude or sign.

## Scope and evidence

The result includes arbitrary direct sums of hostile near-singular positive
blocks, negative blocks, and isolated coordinates.  It strictly broadens the
single isolated-coupling slice and is not a two-eigenvalue/equicorrelation
argument.  It still relies crucially on the matching identity `H^2=D`; graphs
with a vertex of degree two create nonzero off-diagonal `H^2-D` and are not
covered.

Independent symbolic reconstruction artifact:

```text
scripts/iter6_w4_matching_block_exact.py
research/iteration6/route_l3/evidence/W4_MATCHING_BLOCK_EXACT.json
```

The script verifies (M2)--(M8) as polynomial identities.  The universal signs
above are analytic; the script is regression evidence rather than their
source.  Independent reconstruction artifacts are
`research/iteration6/route_stitch/independent_w4_matching_audit.py` and
`research/iteration6/route_stitch/W4_MATCHING_BLOCK_INDEPENDENT_AUDIT.json`.
