# Independent hostile audit: matching-support `W4` slice

Date: 2026-08-22 (Asia/Shanghai)

Verdict: **PASS for the stated matching-support scope**.  This upgrades that
slice to an internal E4 proof candidate under the repository protocol.  It is
not the universal `W4` lemma, has no Lean/formal proof, and has no external
review.

Audited source:
`research/iteration6/route_l3/w4_matching_block_slice.md`.  I reconstructed
the pivotal identities below without treating
`scripts/iter6_w4_matching_block_exact.py` as a premise.

## 1. Scope and retained state

Let `d>=6`, `0<mu<=lambda_min(C)`, and, after a simultaneous permutation,

```text
C = direct_sum_j [[1,r_j],[r_j,1]] direct_sum I_q.
```

Put `H=C-I`, `t_j=|r_j|`, and `D=Diag(diag H^2)`.  Within each two-coordinate
block, `H^2=t_j^2 I_2`; singleton rows vanish.  Thus globally

```text
H^2=D,  H^3=HD=DH,  F=H+H^2-D=H,
E=Diag(diag H^3)=0,  Diag(diag F^2)=D.
```

Independent substitution in the exact retained-state identity gives

```text
S=(d-3)H^2-2H^3+HD+DH+Diag(diag F^2)=(d-2)D.
```

Substituting these relations in the already audited closed formula for `L3`
gives exactly

```text
L3(C)=[4(d-1)(d-2)I-10(d-2)H+(3d-4)D]
       /[2d(d-1)(d-2)].                                  (A1)
```

No equality of the different `|r_j|`, and no common sign, was used.

## 2. Both block eigenlines

The block eigenvalues of `H` are `h=+t,-t`.  Since `C>=mu I`,
`0<=t<=a:=1-mu`; hence every denominator below is positive.  Comparing (A1)
with `2/[d(2-mu+h)]` and clearing the positive denominator gives

```text
N_h=4(d-1)(d-2)(a+h)+(3d-4)t^2(1+a+h)
    -10(d-2)h(1+a+h).                                    (A2)
```

For `h=-t`, all three summands in

```text
N_-=4(d-1)(d-2)(a-t)+(3d-4)t^2(1+a-t)
    +10(d-2)t(1+a-t)
```

are nonnegative.

For `h=+t`, set `t=au` and `d=6+k`, with `a,u in [0,1]` and `k>=0`.  Direct
coefficient reconstruction gives

```text
N_+(6+k)=2a B_0+k a B_1+4a(1+u)k^2,

B_0=40+20u-20au-13au^2+7a^2u^2+7a^2u^3,
B_1=36+26u-10au-7au^2+3a^2u^2+3a^2u^3.
```

The signs do not rely on a numerical search:

```text
B_0 >=40+20u(1-a)-13au^2 >=27,
B_1 >=36+u(26-10a-7au) >=36+9u.
```

Therefore both eigenline comparisons hold.  On a singleton, `L3=2/d` and
the desired right side is `2/[d(2-mu)]<=2/d`.  This proves

```text
L3(C)>=(2/d)[C+(1-mu)I]^-1.                              (A3)
```

The endpoint `mu=1` forces `C=I`, so the apparent `a=0` degeneracy is simply
equality and causes no division-by-zero step in this proof.

## 3. Outer Schur-envelope reconstruction

For `mu<1`, write an admissible one-coordinate extension as
`A=[[1,b^T],[b,C]]`, `c=C^-1b`, and parameterize `c=tv` in
`range(C-mu I)`.  Saturating `A-mu I>=0` gives

```text
t^2 v^T C^2(C-mu I)^-1v=1-mu.
```

If `s=1-b^TC^-1b`, the denominator which converts `t^2` to `t^2/s` has the
spectral identity

```text
lambda^2/(lambda-mu)-(1-mu)lambda
 =mu lambda(lambda+1-mu)/(lambda-mu).                    (A4)
```

Maximizing the resulting rank-one form over `v` (ordinary weighted
Cauchy--Schwarz) shows that uniform recovery is equivalent to

```text
Q(C)>=[2(1-mu)/d](C-mu I)[C(C+(1-mu)I)]^-1,
Q=L3-(2mu/d)C^-1.
```

Adding the inverse term simplifies eigenvalue by eigenvalue because

```text
2mu/(d lambda)
+2(1-mu)(lambda-mu)/[d lambda(lambda+1-mu)]
=2/[d(lambda+1-mu)].                                    (A5)
```

Thus (A3) is exactly the uniform outer Schur-envelope condition, including
the range convention on the `lambda=mu` eigenspace.  The claimed consequence
for every admissible outer extension is valid.

## 4. Evidence and caveats

Independent regression checker:

```text
research/iteration6/route_stitch/independent_w4_matching_audit.py
```

Evidence snapshot:

```text
research/iteration6/route_stitch/W4_MATCHING_BLOCK_INDEPENDENT_AUDIT.json
```

The proof uses `H^2=D`, which fails as soon as a support vertex has degree at
least two.  It therefore does not cover paths of length two, stars, dense
blocks, or arbitrary children.  No claim about general fourth depth or the
full RPCD conjecture follows from this audit alone.
