# Hostile audit: fixed two-satellite asymptotics

Audited source: `research/iteration5/route_b/satellite_asymptotics.md`.

Outcome: **PASS for the stated satellite-difference direction**, both in the
all-fixed-`k` limit and on the finite orthogonal two-satellite ray.  This is
not a proof for every invariant sector or for growing satellite size.

## 1. Effective relaxation

With `alpha=1-mu`, the majority/satellite cumulative combination
`D=S_A+tS_B` changes under a majority pivot by exactly `D->mu D`.  For two
fixed satellite coordinates, every intervening majority gap tends to
infinity in probability as the majority size tends to infinity.  Hence the
effective satellite coupling is

```
eta=alpha(1-t^2).
```

After a satellite solve `y`, the majority relaxation energy is the geometric
sum

```
alpha^2 t^2 y^2/(1-mu^2)=alpha t^2 y^2/(1+mu),
```

so the total multiplicative weight is
`w=(2-eta)/(1+mu)`.  The remaining determinant certificate vanishes because
the remaining majority-transverse eigenvalue `mu` has multiplicity tending
to infinity.

## 2. Two-satellite coefficient

The half-prefix inclusion law tends to independent Bernoulli one half.  On
the satellite difference, zero, one, or two selected satellites contribute
energies `0`, `1`, and `1+(1+eta)^2`.  Division by the input squared norm two
therefore gives

```
h_2=1/2+eta/4+eta^2/8.
```

Multiplication by `w` reconstructs exactly

```
R_2=(8-eta^3)/[8(1+mu)].
```

For fixed `mu`, this is minimized at `t=0`, and with `alpha=1-mu`,

```
R_2-1/2=alpha(1-alpha^2/4)/[2(2-alpha)]>0.
```

Thus the new rank-two degeneration approaches one half from above when the
majority size tends to infinity before `mu` tends upward to one; it is not a
counterexample.

## 3. Finite orthogonal ray

When `t=0`, the majority block decouples.  For even `n=2h`, direct
hypergeometric counting gives

```
P_0=P_2=(h-1)/[2(2h-1)],  P_1=h/(2h-1).
```

For odd `n=2h+1`, `P_2=(h+1)/[2(2h+1)]` and `P_1=2P_2`.
Substituting the satellite energies independently reconstructs equations
(18)--(19) of the source, both strictly above one half for `0<mu<1`.
`orthogonal_satellite_exact.py` reproduces the rational probabilities and
coefficients through dimension 1000.

## 4. Independent all-fixed-`k` reconstruction

Fix the satellite count `k` before sending the majority size to infinity,
and take a satellite vector `z` with zero coordinate sum.  Conditional on at
least `j` satellites entering the prefix, the first `j` satellite labels are
a uniform ordered sample without replacement.  Put `rho=1-eta` and

```
W_j=sum_{r=0}^{j-2}rho^r,  Q_j=sum_{r=0}^{j-2}rho^(2r).
```

Unrolling the triangular recurrence gives

```
y_j=z_{pi_j}-eta sum_{l<j}rho^(j-1-l)z_{pi_l}.
```

Using `E[z_pi_i z_pi_j]=-||z||^2/[k(k-1)]` for distinct
positions, I independently obtain

```
E[y_j^2 | S>=j]/||z||^2
 =1/k+eta^2(k Q_j-W_j^2)/[k(k-1)]
      +2 eta W_j/[k(k-1)].
```

Every correction is nonnegative: `eta,W_j>=0` and Cauchy gives
`W_j^2<=(j-1)Q_j<=kQ_j`.  If `p_j=Pr(S>=j)` for
`S~Binomial(k,1/2)`, then

```
sum_j p_j/k=E[S]/k=1/2.
```

Consequently the limiting transverse prefix coefficient satisfies
`h_k(eta)>=1/2` for every fixed `k>=2`.  Since
`eta=(1-mu)(1-t^2)<=1-mu`, its relaxation multiplier
`(2-eta)/(1+mu)` is at least one, so the full reduced transverse ratio also
stays above one half.  The symbolic verifier independently expands the
finite ordered-prefix model for `k=2,...,8`; these checks agree identically
with the exchangeable second-moment formula.

## 5. Scope

The audit validates the satellite-transverse sector after first fixing `k`
and then taking the majority limit, plus the finite orthogonal
two-satellite-difference direction.  It does not validate the other
group-constant sector, any regime in which `k` grows with `n`, or the finite
nonorthogonal family.  Those parts remain E1/E3 as labelled in the source.
