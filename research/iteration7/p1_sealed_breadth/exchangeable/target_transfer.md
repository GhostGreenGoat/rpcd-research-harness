# Target transfer audit

## Canonical target binding

- Claim ID: `C050`
- Canonical title: **General finite-time expected-distance RPCD complexity**
- Statement reference: `research/problem.md#current-finite-time-target`
- Status in the registry: open conjecture

The target quantifies over every real unit-diagonal SPD `A`, every initial
point, and every integer epoch count.  It uses a fresh independent uniform
permutation in each epoch and asks for expectation of `A`-distance, not the
distance of the expected iterate.

## 1. Transfer promised by the locked card

For a deterministic epoch-boundary state `x`, the pathwise identity is

```text
||T_pi x||_A^2=||x||_A^2-D_pi(x).                     (1.1)
```

If the locked lemma had held, then

```text
E_pi D_pi(x) >= (1/16)||Ax||_2^2
              >= (mu/16)||x||_A^2,                   (1.2)
```

because `A^2 >= mu A`.  Equations (1.1)--(1.2) would give the conditional
statement

```text
E[||x_{k+1}||_A^2 | x_k]
 <=(1-mu/16)||x_k||_A^2.                              (1.3)
```

Fresh independence of the next epoch permutation is essential in (1.3).
Iterating conditional expectation and applying Jensen only after the complete
second-moment iteration gives

```text
E||x_k||_A
 <=sqrt(E||x_k||_A^2)
 <=(1-mu/16)^(k/2)||x_0||_A
 <=exp(-mu k/32)||x_0||_A.                            (1.4)
```

Thus the card's implication had no nonnormal spectral prefactor: `C=1` and
`c=1/32`, uniformly for every initial point.  It concerns expected distance,
not `||E x_k||_A`.  The failure is entirely in (1.2)'s first inequality, which
is exactly refuted in `falsifier_results.json`.

## 2. What the sharp surviving residual bound actually gives

The general exact lower bound

```text
E_pi D_pi(x)>=(1/n)||Ax||_2^2
             >=(mu/n)||x||_A^2                       (2.1)
```

does prove

```text
E||x_k||_A <= exp[-mu k/(2n)]||x_0||_A.               (2.2)
```

This costs `O(n/mu log(1/epsilon))` epochs and
`O(n^2/mu log(1/epsilon))` coordinate updates.  It is dimensionally too weak
for C050.  The signed equicorrelation family proves that no pure comparison to
`||Ax||_2^2` can remove this factor `n`.

## 3. Transfer for the exchangeable-pair repair

Let `pi'` be obtained from `pi` by a uniformly random unordered position
transposition, and define

```text
B_A(x)=||E_pi T_pi x||_A^2
       +(n-1)/4 E_{pi,pair}||T_pi x-T_pi' x||_A^2.   (3.1)
```

The Hilbert-valued random-transposition Poincare inequality has sharp gap
`2/(n-1)`, hence

```text
E_pi||T_pi x||_A^2 <= B_A(x).                         (3.2)
```

Suppose a future proof establishes, for some universal `0<c_*<=1`,

```text
B_A(x)<=(1-c_* mu)||x||_A^2                           (EP)
```

for every dimension, every unit-diagonal SPD `A`, and every `x`.  Combining
(3.2) with `(EP)` gives, conditionally at every epoch boundary,

```text
E[||x_{k+1}||_A^2 | x_k]
 <=(1-c_*mu)||x_k||_A^2.                              (3.3)
```

The same fresh-epoch iteration and Jensen step as above yield

```text
E||x_k||_A
 <=(1-c_*mu)^(k/2)||x_0||_A
 <=exp(-c_*mu k/2)||x_0||_A.                          (3.4)
```

Therefore `(EP)` would prove C050 directly with `C=1` and `c=c_*/2`.  To reach
relative expected distance `epsilon`, it suffices to take

```text
k >= [2/(c_*mu)] log(1/epsilon)
```

epochs, or

```text
n k = O((n/mu)log(1/epsilon))
```

coordinate updates.  There are no asymptotic-only steps, covariance spectral
prefactors, condition-number conversions, or incomplete epoch blocks in this
calculation.

## 4. C050 versus C051

`(EP)` is not known.  If proved for every `x`, (3.2)--(3.3) would also yield the
strong fixed-`A` one-epoch energy certificate recorded as C051 (equivalently,
the corresponding quadratic matrix inequality).  Hence `(EP)` is a stronger
sufficient route to C050.

This pass does **not** assume C051, does not claim C050 implies C051, and does
not call them equivalent.  The exact refutation of the still stronger locked
residual lemma also does not refute either C051 or C050.

## 5. Fixed multi-epoch exchangeable-pair alternative

For a fixed universal `m_0`, apply the same sharp transposition Poincare bound
separately to each of `m_0` fresh independent epoch permutations and let
`B_A^(m_0)` be the mean endpoint squared plus the sum of the `m_0` Dirichlet
terms.  If a universal `0<c_0<=1` satisfies

```text
B_A^(m_0)(x)<=(1-c_0 mu)||x||_A^2,
```

then blocks of `m_0` epochs contract conditionally.  For `k=q m_0+r`, the
remaining `r<m_0` epochs are pathwise nonexpansive, and

```text
E||x_k||_A
 <=exp(c_0/2) exp[-c_0 mu k/(2m_0)]||x_0||_A.
```

This supplies universal `C=exp(c_0/2)` and `c=c_0/(2m_0)`, controls incomplete
blocks, and would prove C050 without implying a one-epoch C051 certificate.
Because `m_0,c_0,C` are universal constants, reaching relative expected
distance `epsilon` still costs `O(mu^{-1}log(1/epsilon))` epochs and
`O(n mu^{-1}log(1/epsilon))` coordinate updates.
The restriction `c_0<=1` is necessary already at `A=I`, where `mu=1` and the
proxy vanishes; it also makes the displayed prefactor bound uniform.
The multi-epoch proxy is an open E0 fallback, with an exact two-epoch control
at equicorrelation `n=3` and exact one-through-four-epoch controls on one
interacting signed rational `n=4` family only.  The latter use the exact
metric-map recursion recorded in `route_development.md`; they do not prove a
uniform block length.

## 6. Current transfer verdict

- Locked transfer algebra: valid conditional on its antecedent.
- Locked antecedent: exactly false.
- Sharp residual fallback: rigorous but loses `n` and misses C050.
- Compensated exchangeable-pair transfer: valid conditional on `(EP)`.
- `(EP)`: open route-local candidate with E2 finite slices and E3 structured
  block evidence only.
- Fixed-block `(EP-m)`: direct-C050 E0 fallback; exact transfer including its
  universal leftover-block prefactor is valid, but the candidate inequality is
  unproved.
- C050: remains open.
