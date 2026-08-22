# Checkpoint 2: adaptive state is exact; repeated compression is not

Local checkpoint time: `2026-08-21 21:05 +08:00`.

## Higher Bellman state

The weighted hierarchy

```
C_t=J_t-(1/2)J_{t-1}
```

has an all-dimensional E3 proof draft at `t=2` and a hostile-tested target
at `t=3`.  Lifting the *matrix polynomial* behind the `t=2` proof, rather
than only its scalar conclusion, introduces the exact state

```
S=sum_i L_i^T(C_i-I)^2L_i.
```

With `H=A-I`, `D=Diag(diag H^2)`, and
`F=H+H^2-D` (which has zero diagonal), exact expansion gives

```
S=(m-3)H^2-2H^3+HD+DH+Diag(diag F^2).
```

This is a genuine third-order anisotropic closure state.  It is not a
function of the older scalar/Bellman moments alone.

## Exact new barrier

Writing `R=(m-2)H-H^2+D`, rowwise Cauchy yields the valid compression

```
S>=R^2/(m-1).
```

But applying it loses the full weighted-`t=3` constant.  On
`A=(1/100)I+(99/100)11^T` in dimension four, the resulting lower state's
transverse generalized ratio over `mu` is exactly

```
187276289/400000000
 = 1/2-12723711/400000000.
```

Thus repeating the successful level-two row-square compression cannot
prove `C_3>=(2mu/m)A^-1`.  The uncompressed `S` contains the missing
transverse surplus.  This is a route counterexample, not an RPCD
counterexample.

## Subset/complement and dual audits

The tempting local three-subset proxy
`K(C)-(1/2)J_2(C)>=(3I-C)/3` also fails exactly, with quadratic witness
`-11/48`; the subset average must retain compensation from the spectral
floor rather than demand every local triple be PSD.

Separately, the Route-A preconditioner lemma
`E[D_pi^TD_pi]>=mu B^-1` was independently reconstructed.  Its proposed
fixed-adjacency closure is not repairable by a larger universal constant:
on fixed positive equicorrelation its normalized parallel certificate is
asymptotic to `3/[n rho(1-rho)]`.  A half-linear-memory replacement was then
hostile-audited successfully on the positive-equicorrelation family,
including all parity and `n=2` endpoint checks.  These cross-audits support
the architectural conclusion that a successful state needs memory growing
with dimension.
