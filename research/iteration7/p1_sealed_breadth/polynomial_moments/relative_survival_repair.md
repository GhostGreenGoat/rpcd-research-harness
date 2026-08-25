# Positive relative-survival repair of the p-replica edge

Status: route-local proof draft (E3 maximum), with an open RPCD-specific
sublemma.  The two rational stresses are E2 and the seeded scan is E1.  This
note does not prove the unrestricted moment certificate, C050, or C051.

## 1. The live obstruction

Keep the locked representation and the phase-2 notation

```
Phi(X)=E_pi[Q_pi X Q_pi^T],       H_j=Phi^j(I),
m=ceil(1/mu),                     p=ceil(log n).
```

The map is positive and Frobenius-self-adjoint, and `Phi(I)<=I`, so

```
0 <= H_(j+1) <= H_j <= I.                                  (RS1)
```

At `p>=3`, the independent-replica expansion of `tr(H_m^p)` contains signed
words.  The phase-2 endpoint linearization also loses the finite contribution
of almost-annihilated directions.  The objective here is to retain that
nonlinear contribution while avoiding termwise signs.

## 2. Araki--Lieb--Thirring reduction

Put `X=H_j` and `Y=H_(j+1)`.  If `X` is singular, (RS1) implies
`ker(X) subset ker(Y)`; restrict all matrices to `supp(X)`.  Define the
relative survival and loss

```
C=X^(-1/2)Y X^(-1/2),       G=I-C,       0<=C<=I.          (RS2)
```

For an integer `p>=1`, the Araki--Lieb--Thirring trace inequality, with its
parameters specialized to exponent `p` and trace power one, gives

```
tr(Y^p)
 =tr[(X^(1/2) C X^(1/2))^p]
 <=tr(X^(p/2) C^p X^(p/2))
 =tr(X^p C^p).                                             (RS3)
```

The cited external theorem is H. Araki, *On an inequality of Lieb and
Thirring*, Letters in Mathematical Physics 19 (1990), 167--170,
https://doi.org/10.1007/BF01045887.  Only this established trace inequality is
external; every RPCD-specific implication below is derived here and remains at
most E3.

For exact rational checking, the square roots in (RS3) are unnecessary.
Cyclicity gives

```
tr(X^p C^p)
 =tr[X^(p-1)Y(X^(-1)Y)^(p-1)].                            (RS4)
```

The pair `X,Y` may therefore be replaced by any simultaneous similarity.  In
particular, the rational x-coordinate orbit `A^(-1)G_j,A^(-1)G_(j+1)` used by
`phase3_relative_survival.py` computes (RS4) exactly.

Subtracting (RS3) yields the positive nonlinear loss

```
tr(X^p)-tr(Y^p) >=tr[X^p(I-C^p)].                         (RS5)
```

This is not the false assertion that individual replica words are positive.
It bounds their assembled trace by a different positive functional.

## 3. Saturation and a scalar spectral measure

Let `E_G` be the spectral resolution of `G`.  When `tr(X^p)>0`, define the
probability measure

```
nu_j(S)=tr[X^p E_G(S)]/tr(X^p).                           (RS6)
```

The weights are nonnegative even when `X` and `G` do not commute, because the
trace of the product of two PSD matrices is nonnegative.  Equations (RS5)--
(RS6) give

```
tr(X^p C^p)/tr(X^p)=integral_[0,1] (1-t)^p d nu_j(t),     (RS7)
```

and the ALT lower loss is the same integral with response
`1-(1-t)^p`.  Thus noncommutativity remains in the orbit-dependent measure,
but the nonlinear response is a positive scalar saturation function.

For `0<=t<=1`, elementary calculus gives

```
1-(1-t)^p >=(1-e^(-1)) min{p t,1}.                       (RS8)
```

Indeed `(1-t)^p<=e^(-pt)`; on `0<=pt<=1`, concavity of
`1-e^(-u)` puts it above `(1-e^(-1))u`, and for `pt>=1` it is at least
`1-e^(-1)`.  Functional calculus, (RS5), and (RS8) yield

```
tr(X^p)-tr(Y^p)
 >=(1-e^(-1)) tr[X^p min{pG,I}].                         (RS9)
```

Unlike the failed derivative at `t=0`, (RS9) gives order-one weight to a
relative loss at least `1/p`.

## 4. Exact cumulative certificate

Define

```
r_j=tr(H_j^p C_j^p)/tr(H_j^p)                            (RS10)
```

whenever the denominator is nonzero, and set the iteration complete if it is
zero.  Applying (RS3) successively gives

```
tr(H_m^p)/n <= product_(j=0)^(m-1) r_j.                 (RS11)
```

Consequently the following route-local lemma is sufficient for the selected
moment certificate `(MC)`:

```
sum_(j=0)^(m-1) [-log r_j] >=p/2.                       (CRS)
```

Then (RS11) gives `tr(H_m^p)/n<=exp(-p/2)`.  The already
proved direct-sum bridge and block transfer in `target_transfer.md` yield

```
E||x_k||_A <=exp(1/4) exp(-mu*k/8)||x_0||_A
```

for every initial point if (CRS) is proved uniformly.  This remains expected
distance via Jensen, not distance of the expected iterate.  The finite block
bound controls non-normal prefactors.  C051 is neither assumed nor inferred.

A stronger, algebraic per-step sufficient condition is

```
r_j <=(1-mu/2)^p,       0<=j<m.                         (LRS)
```

Indeed `(1-mu/2)^(pm)<=exp(-p*mu*m/2)<=exp(-p/2)`.
The exact and numerical tests below attack (LRS).  Failure of (LRS) would not
refute (CRS), (MC), or C050.

## 5. A quantified first-step region

The first step of (LRS) is provable in an ultra-near-singular region.  The
first projection in every epoch loses trace one, so

```
tr(H_1)<=n-1.                                            (RS12)
```

Since `0<=H_1<=I`, `tr(H_1^p)<=tr(H_1)`.  If
`mu<=2/(np)`, Bernoulli's inequality gives

```
n(1-mu/2)^p >=n(1-p*mu/2)>=n-1>=tr(H_1^p).              (RS13)
```

At `j=0`, `X=I` and ALT is equality, so (RS13) proves (LRS) for the first
epoch for every unit-diagonal SPD instance in that stated parameter region.
This E3 partial result does not propagate to later orbit steps.

## 6. Exact and numerical falsifiers

Run

```
{python} \
  ./phase3_relative_survival.py \
  --mode exact
```

The SymPy Rational suite checks:

1. On the anisotropic noncommuting ray at `mu=1/1000`, `j=1`, `p=3`,
   the actual trace-power loss, ALT loss, and endpoint loss are respectively
   `0.016647381461837112688...`, `0.016612035845113683694...`, and
   `0.016451180206996982272...`.  Both exact differences are positive.  The
   exact ratio `r_1=0.9916342305950991...` also clears (LRS).
2. On the fully coupled signed `n=8,mu=1/2` ray at `j=1,p=3`, the exact ratio
   is `0.007507655998537093...`, again below `(1-mu/2)^p`; the gap is an exact
   positive rational.

The seeded float64 attack uses seed `2718281828`, 125 singular Gram rays in
dimensions 8--10, `mu` log-uniform on `[10^-2.3,10^-0.25]`, and 3,403 sampled
orbit steps.  With support cutoff `1e-13`, ratio tolerance `1e-6`, and decision
margin `1e-8`, the minimum observed exponent

```
-log(r_j)/(p*mu)=2.3702105854001734
```

occurred at `n=10`, rank two, `mu=0.10290962086729599`, `j=9`, `m=10`.
It did not cross the (LRS) threshold `1/2`.  This null result is E1 only.

## 7. Two exact information barriers

### 7.1 ALT is trace-only

Take

```
X=diag(1,1/4),       C=[[1/2,2/5],[2/5,1/2]],
Y=X^(1/2) C X^(1/2),       p=3.
```

Both `C` and `I-C` have determinant `9/100`, so `0<C<I`.  The putative
Loewner residual

```
X^(3/2) C^3 X^(3/2)-Y^3
 =[[39/200,-9/320],[-9/320,-21/800]]
```

has positive trace `27/160` but negative determinant
`-15129/2560000`.  Therefore (RS3) cannot be promoted from trace order to
operator order.  This exact E2 obstruction enforces the rollout's prohibition
on an unproved trace-to-worst-state conversion; the worst-state transfer still
comes only after (MC), via direct-sum amplification.

### 7.2 Existing scalar prefix data are insufficient

At `n=8,p=3,mu=1/2`, the abstract spectrum

```
spec(H_1)={13/16 (seven times), 9/16}
```

saturates both inherited scalar consequences

```
lambda_max(H_1)<=1-3mu/n=13/16,
tr(H_1)<=n-1-2mu+mu^2=25/4.
```

Yet its cubic trace is `4027/1024`, strictly larger than
`8(1-mu/2)^3=27/8` by `571/1024`.  This is not an RPCD matrix; it proves only
that the one-epoch Loewner floor plus the two-prefix scalar trace bound cannot
by themselves establish (LRS).  A proof must retain the relative-loss
distribution (RS6) or additional RPCD word/orbit structure.

## 8. First bad edge and reopen condition

The signed-word obstruction has been repaired at the algebraic level by
(RS3)--(RS11).  The new first bad edge is the RPCD-specific inequality (CRS),
or any weaker cumulative small-relative-loss bound on the measures `nu_j`
that implies it.  A first-moment estimate of `nu_j` alone is insufficient:
mass `1-mu` at relative loss zero and mass `mu` at loss one has mean `mu` but
survival `1-mu`, larger than the desired `exp(-p*mu/2)` when `p>2` and `mu`
is small.  Quantitative control of the small-loss mass is essential.

Deepen this child if a dimension-uniform RPCD small-ball estimate for (RS6)
is found.  Refute only (LRS), not the parent moment lemma, if an exact/certified
reachable orbit step has `r_j>(1-mu/2)^p`.  Refute (MC) only with an
exact/certified instance satisfying `tr(H_m^p)/n>exp(-p/2)`.  C050 remains
open in either event.
