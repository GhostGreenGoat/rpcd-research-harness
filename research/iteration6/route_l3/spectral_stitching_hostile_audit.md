# Hostile audit of spectral stitching S3--S5 and S11--S12

Date: 2026-08-22

Audit target:
`research/iteration6/route_stitch/spectral_stitching.md`.

Outcome: **PASS after one explicit scope correction**.  The nonnormal
factorization, congruence lower bound, spectral endpoint coefficient, and
harmonic stitching constant all reconstruct exactly.  As written, the
quantifier `tau>=0` also permits `Q_tau=0`, where the displayed interval
`[d_tau,L]` may be empty and S11 is not defined by its endpoint formula.  The
statement should either assume `Q_tau!=0` in S11--S12 or set
`r_tau=+infinity` when `Q_tau=0`; the latter gives `c_stitch=b`.  Also state
`n>=2` because S9--S11 divide by `n-1`.

This audit does not prove the open boundary certificate S7.

## 1. Independent reconstruction of S3--S5

In permutation coordinates write the chronological unit-lower factor of the
singular boundary correlation matrix as

```text
M_0=I+strictlower(C),     X_0=M_0^-1.
```

Since the off-diagonal entries on the ray scale by `1-mu`,

```text
M_mu=I+(1-mu)strictlower(C)
    =mu I+(1-mu)M_0
    =M_0[(1-mu)I+mu X_0].                                (A1)
```

Thus, with `B=(1-mu)I+mu X_0`,

```text
X_mu=B^-1X_0.                                             (A2)
```

Although `X_0` is generally nonnormal, no spectral-normality assumption is
needed.  First,

```text
Sym(M_0)=(I+C)/2>=I/2.                                   (A3)
```

For every real vector `x`,

```text
||M_0x||||x|| >= x^TM_0x=x^TSym(M_0)x >=||x||^2/2,
```

so `sigma_min(M_0)>=1/2` and `||X_0||<=2`.  Hence

```text
||B||<=1-mu+mu||X_0||<=1+mu.                             (A4)
```

For any invertible `B`, singular-value calculus gives

```text
B^-TB^-1 >=||B||^-2 I.                                   (A5)
```

Congruence by the possibly nonnormal `X_0` is legitimate:

```text
X_mu^TX_mu
 =X_0^TB^-TB^-1X_0
 >=(1+mu)^-2 X_0^TX_0.                                  (A6)
```

Here `B` is also a polynomial in `X_0`, so it commutes with `X_0`; however,
(A6) already follows from congruence and does not require simultaneous
diagonalization.  Averaging (A6) order by order proves

```text
K(A_mu)>=(1+mu)^-2K(C).                                  (A7)
```

Verdict on S3--S5: PASS.

## 2. Independent reconstruction of S11

The exact two-prefix formula is

```text
J_2=[(2n-1)I-2A+Diag(diag A^2)]/[n(n-1)].               (A8)
```

Since `Diag(diag A^2)>=I`,

```text
J_2>=F(A)=2(nI-A)/[n(n-1)].                              (A9)
```

The matrix `F(A)` is a polynomial in `A`.  On an eigenline of `A` with
eigenvalue `lambda`, its generalized coefficient relative to
`mu A^-1` is exactly

```text
phi(lambda)=2lambda(n-lambda)/[n(n-1)mu].                (A10)
```

If `Q_tau!=0`, every eigenvalue in that spectral block lies in the nonempty
interval

```text
[d_tau,L],
d_tau=mu+(1-mu)tau,
L=n-(n-1)mu.                                             (A11)
```

The concave quadratic `lambda(n-lambda)` attains its minimum on a compact
interval at an endpoint.  At the upper endpoint,

```text
phi(L)=2L[n-L]/[n(n-1)mu]=2L/n,                          (A12)
```

because `n-L=(n-1)mu`.  This reconstructs S11 exactly.

The missing scope case is concrete.  If `tau>lambda_max(C)`, then `Q_tau=0`
and `d_tau` can exceed `L` (indeed it can exceed `n`), so the notation
`min_(lambda in [d_tau,L])` and its endpoint evaluation are not a valid
spectral minimum.  In this case no high block needs control; define
`r_tau=+infinity` or handle it separately.

Verdict on S11: PASS for `Q_tau!=0`; scope correction required for the empty
high block.

## 3. Full shorting and the S12 coefficient

Assume the genuinely full Loewner certificate

```text
K(C)>=kappa P_tau.                                       (A13)
```

The weaker compressed statement
`P_tau K(C)P_tau>=kappa P_tau` would not imply (A13), because cross-block
coupling can make `K(C)-kappa P_tau` indefinite.  With (A13), S5 gives

```text
K(A_mu)>=bP_tau,       b=kappa/(1+mu)^2.                 (A14)
```

S11 and positivity of `F` give the global block-diagonal lower bound

```text
F(A_mu)>=r_tau mu A_mu^-1 Q_tau.                         (A15)
```

If a PSD matrix dominates two matrices, it dominates every convex
combination of them.  Put

```text
a=r_tau/(b+r_tau),
c=br_tau/(b+r_tau).                                      (A16)
```

On `P_tau`, `mu A_mu^-1<=I`, and the first lower bound supplies
`ab=c`.  On `Q_tau`, the second supplies `(1-a)r_tau=c`.  The projectors are
spectral projectors of `C` and hence commute with `A_mu`, `A_mu^-1`, and
`F(A_mu)`.  Therefore

```text
K(A_mu)>=c mu A_mu^-1.                                   (A17)
```

No block cross term was discarded: (A14) starts from the full shorted
inequality.  If `Q_tau=0`, simply use (A14) and
`mu A_mu^-1<=I` to get coefficient `b`, consistently with the convention
`r_tau=+infinity` in (A16).

Verdict on S12: PASS with the S11 scope convention above.

## 4. Evidence boundary

- This is an independent algebraic reconstruction, not a validation by the
  sibling script.
- S3--S5 and the corrected S11--S12 are eligible as internal E4 proof
  candidates after the source note adopts the empty-block convention.
- S7 remains an explicitly open assumption.  Consequently this audit does
  not yield a universal RPCD complexity theorem.
