# Direct multi-epoch moment transfer to C050

Status: route-local proof draft (E3 maximum), not independently audited.  This
note proves only a sufficient transfer.  It does **not** prove the proposed
uniform trace-moment estimate below, C050, or C051.

## 1. Orientation and the exact covariance orbit

Let `a_i=A^(1/2)e_i`, `B_i=a_i a_i^T`, and `P_i=I-B_i`.  For update order
`pi=(pi_1,...,pi_n)`, one energy-coordinate epoch is

```
Q_pi=P_(pi_n)...P_(pi_1).
```

Define the positive map on real symmetric matrices

```
Phi(X)=E_pi[Q_pi X Q_pi^T].
```

If `rev(pi)=(pi_n,...,pi_1)`, then
`Q_rev(pi)=Q_pi^T`.  Since reversal preserves the uniform permutation law,

```
Phi*(X)=E_pi[Q_pi^T X Q_pi]=Phi(X).                 (T1)
```

Thus `Phi` is Frobenius-self-adjoint even though individual `Q_pi` are
non-normal.  Fresh independent epoch permutations give, for deterministic
`y_0=A^(1/2)x_0`,

```
R_k=Phi^k(y_0 y_0^T),
E||y_k||_2^2=tr(R_k)=y_0^T H_k y_0,
H_k:=Phi^k(I).                                       (T2)
```

The last equality uses (T1).  It is a worst-initial-state identity, not a
bound on `||E y_k||`.  Since each `Q_pi` is a product of orthogonal
projections, `Phi(I)<=I`.  Positivity then gives

```
0<=H_(k+1)<=H_k<=I.                                  (T3)
```

With `D=I-Phi(I)`, the exact noncommutative loss hierarchy is

```
I-H_m=sum_(j=0)^(m-1) Phi^j(D).                       (T4)
```

No factors in (T1)--(T4) have been commuted.

## 2. Block certificate and constants

Assume that universal `B>0` and `q in (0,1)` have the following property:
for every real unit-diagonal SPD `A`, with `mu=lambda_min(A)`, there is an
integer `m=m(A)` such that

```
m <= B/mu,       H_m <= q I.                          (T5)
```

Write `k=am+r`, `0<=r<m`.  Positivity, (T3), and (T5) imply inductively

```
H_k=Phi^(am)(H_r) <= q^a I.
```

Consequently, for every initial point,

```
E||x_k||_A
 =E||y_k||_2
 <=sqrt(E||y_k||_2^2)
 <=q^(floor(k/m)/2)||y_0||_2
 <=q^(-1/2) exp[-(-log q) mu k/(2B)] ||x_0||_A.       (T6)
```

This proves C050 from (T5) with the universal constants

```
C=q^(-1/2),       c=(-log q)/(2B).                    (T7)
```

One epoch has `n` updates, so (T6) gives
`O((n/mu) log(1/epsilon))` coordinate updates.  The block inequality controls
the full non-normal transient directly; it uses neither an asymptotic
spectral-radius statement nor eigenvector-conditioning constants.

## 3. A logarithmic-order Schatten-moment certificate

For `n>=2`, set

```
p=ceil(log n),       m=ceil(1/mu),       tau(X)=tr(X)/n.
```

The following is the route's repaired, falsifiable moment lemma:

```
tau(H_m^p) <= exp(-p/2).                               (MC)
```

It is open in general.  The moment-to-worst-state bridge uses the fact that
the RPCD class is closed under block-diagonal replication, rather than
silently dropping a dimension factor.  Fix a base matrix `A_0` of dimension
`d` and form `A_0^(direct-sum ell)`.  Updates from distinct blocks commute,
and the restriction of a uniform global permutation to each block is a
uniform internal order.  Starting from `I`, the multi-epoch orbit is therefore

```
H_m(A_0^(direct-sum ell))=H_m(A_0)^(direct-sum ell).   (T8)
```

The replicated matrix has the same `mu` and `m`.  Apply (MC) in dimension
`N=ell*d`, with `p_ell=ceil(log N)`, to obtain

```
[(1/d)tr(H_m(A_0)^p_ell)]^(1/p_ell) <=exp(-1/2).
```

Letting `ell` tend to infinity makes `p_ell` tend to infinity, and the left
side tends to `lambda_max(H_m(A_0))`.  Hence

```
H_m(A_0) <=exp(-1/2)I.                                (T9)
```

This amplification is a dimension-free bridge and proves worst-initial-state
control; it does not identify normalized trace with operator norm at a fixed
dimension.  Conversely, (T9) trivially implies (MC), so on this
direct-sum-closed class the uniform moment lemma is equivalent to the stated
block-orbit contraction.  Its possible advantage is a noncommutative trace
polynomial proof route, not a logically weaker endpoint.

Since a unit-diagonal SPD matrix has `mu<=1`,
`m=ceil(1/mu)<=2/mu`.  Applying (T7) with
`q=exp(-1/2)` and `B=2` yields the explicit implication

```
E||x_k||_A <= exp(1/4) exp(-mu k/8)||x_0||_A.         (T10)
```

For `n=1`, the sole coordinate update annihilates the error after one epoch,
so it is handled separately.

The order `p=ceil(log n)` is deliberate because it diverges under replication.
A fixed moment order would not recover `lambda_max` in the limit.  A
preliminary fixed-dimension bridge used
`n^(1/p)<=e` and therefore required the unnecessarily stronger right side
`exp(-3p/2)`; that attempted threshold is retained in `route_development.md`
as a failed-overstrong formulation, not as the selected lemma.

## 4. Explicit noncommutative trace polynomial

Let one realization of `m` epochs be

```
Z_omega=Q_(pi^(m))...Q_(pi^(1)),
S_omega=Z_omega Z_omega^T.
```

Then `H_m=E_omega[S_omega]`.  For independent replicas
`omega_1,...,omega_p`,

```
tr(H_m^p)
 =E tr(S_(omega_1) S_(omega_2)...S_(omega_p)).        (T11)
```

Equation (T11) is the precise noncommutative polynomial to be bounded.  The
factor order in every `Z_omega` and between replicas is retained.  The exact
anisotropic falsifier in `falsifier_results.json` proves that already
`H_2 != H_1^2`, with an indefinite difference, so replacing (T11) by powers
of a commuting one-epoch surrogate is invalid.

Individual replica traces also need not be positive: the exact
three-dimensional equicorrelation control in `falsifier_results.json` has a
`p=3` word equal to `-415506/30517578125`.  Only the fully averaged matrix
power is PSD-controlled.

## 5. Relation to the frozen one-epoch edge

Let `M_pi` be the permuted lower-triangular Gauss--Seidel factor.  The exact
identity

```
A-T_pi^T A T_pi=A(M_pi M_pi^T)^(-1)A
```

gives

```
D=I-E[Q_pi^T Q_pi]
 =A^(1/2) E[(M_pi M_pi^T)^(-1)] A^(1/2).              (T12)
```

Therefore the frozen card lemma `D>=(mu/16)I` is exactly the strong
one-epoch `K(A)>=(mu/16)A^(-1)` certificate.  It was selected before C051 was
revealed and is not assumed here.  The block/Schatten condition (MC) is a
weaker sufficient condition at the implication level: it constrains only a
multi-epoch orbit of `I`; no converse to the one-epoch certificate is claimed
or used.

## 6. What remains

The first open implication is (T11) -> (MC), uniformly over arbitrary
unit-diagonal SPD `A`.  Exact controls in `falsifier_results.json` establish
the selected block/moment certificate for all two-dimensional instances,
all seven-dimensional instances at the low moment order `p=2`,
two exact points on a fully coupled signed eight-dimensional `p=3` ray,
the full positive and negative equicorrelation parameter ranges, the full
rational anisotropic one-parameter ray, their controlled block sums, and a
signed finite block.  These structured E2/E3 results do not establish the
unrestricted lemma.  Numerical null results are E1 only.  In particular,
this transfer note does not close C050.

## 7. Phase-3 positive relative-survival sufficient edge

The locked-route development now has a positive sufficient reduction for the
open step `(T11) -> (MC)`.  For fixed `p=ceil(log n)`, put

```
X=H_j,  Y=H_(j+1),  C_j=X^(-1/2)Y X^(-1/2)
```

on `supp(X)`, and

```
r_j=tr(X^p C_j^p)/tr(X^p).
```

Araki--Lieb--Thirring gives `tr(Y^p)<=r_j tr(X^p)`.  Therefore

```
sum_(j=0)^(m-1)-log(r_j)>=p/2,      m=ceil(1/mu),       (T13)
```

is sufficient for `(MC)`.  Combining (T13) with the already proved
direct-sum amplification (T8)--(T9) and block transfer (T5)--(T7) yields
exactly the same worst-initial-state expected-distance bound (T10), including
the dimension-free non-normal prefactor.  No raw trace-to-operator conversion
is inserted: operator control still comes only from applying the uniform
moment statement to arbitrarily many direct-sum copies.

The derivation of (T13), its saturated loss form, exact finite stresses, and
two information barriers are in `relative_survival_repair.md`.  The
RPCD-specific lower bound (T13) is open.  Thus this additional sufficient edge
does not prove `(MC)` or C050 and does not assume C051.
