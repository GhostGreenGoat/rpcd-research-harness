# Hostile audit: equicorrelation half-prefix theorem

Audited source: `docs/ITER5_EQUICORRELATION_HALF_PREFIX.md`.

Outcome: **PASS after one endpoint clarification, including the strengthened
simultaneous prefix quantifier**.  For every `1<=s<=ceil(n/2)`, the conclusion
is valid for the full positive and negative equicorrelation interval.  The source must
handle `rho=0` separately because its displayed geometric quotient is `0/0`
there.  No extension to general correlation matrices follows.

## 1. Recurrence reconstruction

For a transverse right side `e_1-e_2`, a nonspecial first pivot occurs with
probability `(k-2)/k` and leaves child energy `2a`.  A special pivot occurs
with probability `2/k`; its child transverse squared norm is
`(k-2)/(k-1)` and its child parallel squared norm is
`[1+(k-1)rho]^2/(k-1)`.  Dividing by the parent norm squared two, the two
transverse contributions combine as

```
(k-2)/k + (k-2)/[k(k-1)] = (k-2)/(k-1).
```

This independently reconstructs (E3), including its easily missed
normalization.  The parallel child is `(1-rho)1`, giving (E2), and
`q=kp` then gives the geometric sum (E4).

## 2. Positive correlations

The pathwise special-coordinate count is correct.  Between the two specials,
ordinary solves multiply the running sum by `alpha=1-rho`; the second special
has magnitude `1+rho alpha^ell>=1`.

For `rho>0`, the inverse-binomial step, cancellation, and polynomial in (E8)
were independently expanded symbolically.  The last two terms are at least
`4s^2 delta^2`, and the other coefficients are nonnegative for `s>=2`.
The `s=1` case is direct.

At `rho=0`, however, (E7) is displayed as

```
[1-(1-delta)^(2s)]/[delta(2-delta)],
```

which is `0/0`, and the proof later cancels `s delta`.  This is repaired by a
separate one-line argument: `A=I`, and a uniform `s`-prefix gives
`J_s=(s/n)I`, exactly the target.  The alternate verifier includes this
endpoint and checks that both margins are zero.

## 3. Negative correlations

With `rho=-beta`, the second special solve is
`-1+beta(1+beta)^ell`.  The inequality

```
(1-beta alpha^ell)^2 >= 1-2 beta alpha^(n-2)
```

holds because `ell<=n-2`; no assumption on the sign of the solve is needed.
The exact probability that both special coordinates lie in the prefix is
`s(s-1)/[n(n-1)]`.  After division by two this gives precisely (E10), with no
missing factor.

The rearrangement to (E11) is equivalent because
`mu/alpha=1-n beta/alpha`.  Finally

```
alpha^(n-1)(s-1)/(n-1)
 <= (1+1/(n-1))^(n-1) < e <= n
```

is valid for `n>=3`, while `n=2` is direct.  The parameter restriction
`beta<1/(n-1)` is used correctly.

The proof actually needs only `n>=2s-1` in the positive block.  This holds
simultaneously for every `1<=s<=ceil(n/2)`.  The negative proof uses only
`(s-1)/(n-1)<=1`, so it also holds throughout that range.  There is no hidden
endpoint-only step in (E2)--(E11).  Therefore the stronger conclusion is

```
J_s(A_n(rho)) >= (s mu/n) A_n(rho)^-1,
1<=s<=ceil(n/2).
```

## 4. Independent finite reconstruction and scope

`scripts/verify_equicorrelation_independent.py` uses a separate chronological
solve and recurrence implementation.  It enumerates all orders through
dimension seven for positive, negative, and zero correlations at **every**
prefix depth through `ceil(n/2)`, verifies the two invariant margins with
`Fraction`, reconstructs (E8) symbolically, and
checks every possible negative-correlation gap on a denser finite grid.

Evidence: `evidence/equicorrelation_hostile_audit.json`.

This supports internal E4 status for the equicorrelation family only.  It is
leaf-free (`J_s`), hence also implies the corresponding `H_s` inequality by
`H_s>=J_s`.  It neither proves the general half-prefix/half-depth statement
nor C001, and it has no Lean/E6 certificate.
