# Hostile audit: half-linear equicorrelation limit

Audited source: Section 4 of `linear_memory_dual.md`, independently of
`scripts/iter5_linear_memory_half_limit_proof.py`.

Outcome: **PASS** for the stated asymptotic positive-equicorrelation scalar
claim.  This is not a general-matrix result and not a finite-`n` proof.

## 1. Reconstruction of the limiting moments

For `rho=c/n`, `q/n->alpha`, the exact row sum of `D_q` is
`mu^min(q,i-1)`, giving

```
s(x)=exp[-c min(x,alpha)],   p=integral s^2.
```

The exact identity `E=D_qM` has residual `rho mu^q` precisely when the
position gap is greater than `q`.  Hence column `y` of `E^T D1` has limit

```
u(y)=s(y)+c exp(-2c alpha)(1-alpha-y)_+.
```

This independently reconstructs (L8).  The Frobenius traces of both order
matrices are `n+O(1)` in this scaling, so the transverse exchangeable blocks
tend to one; no transverse factor was lost.

At `alpha=1/2`, direct integration gives exactly

```
p=[1+(c-1)e^-c]/(2c),
q=(1-e^-c)/(2c)+3e^-c/2
  -2e^-c(1-e^(-c/2))/c+c^2e^(-2c)/24.
```

## 2. Independent exponential-algebra check

Let `F=2(1+c)p^2-q`.  Expanding first in powers of the exponentials, without
using the source verifier, gives

```
24c^2 F
 =12+(-12c^2+60c-24)e^-c
   +(-c^4+12c^3-12c^2-12c+12)e^-2c
   -48c e^(-3c/2).
```

Multiplication by `e^(2c)` is precisely (L15).  Its coefficients at degrees
zero through four are independently obtained as `0,0,24,36,9`.

For `k>=5`, the polynomial tail no longer contributes.  Multiplying the
three exponential coefficients by `k!/12` gives respectively

```
2^k,
-k(k-1)+5k-2=-k^2+6k-2,
-4k/2^(k-1)=-k/2^(k-3),
```

which reconstructs (L16) exactly.  The induction
`2^k>=k^2` for `k>=4` is valid because
`2k^2-(k+1)^2=k^2-2k-1>0` for `k>=4`.  Also
`6k-2>k/2^(k-3)` for `k>=5`.  Thus every remaining Taylor coefficient is
strictly positive.  Since the exponential series is entire, summing its
nonnegative coefficients proves `H(c)>0`, hence `F(c)>0`, for every `c>0`.

## 3. Quantifier and scope

The conclusion is exactly the limiting parallel certificate for fixed
`c>0` as `n->infinity`, `rho=c/n`, and `q/n->1/2`.  It does not establish the
finite-dimensional inequality uniformly over `c=c_n`, negative
equicorrelations, or arbitrary unit-diagonal SPD matrices.  Those limitations
are stated in the source.
