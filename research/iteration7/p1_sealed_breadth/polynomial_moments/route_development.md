# Development of RC-T143-NCPM-001

Run: `20260825T123453Z-077c1385`
Worker: `sealed-polynomial-moments`
Method family: noncommutative-polynomial-moment-method
Parent: `R100-l0-finite-time`

Evidence discipline: all general derivations below are at most E3 proof
drafts and have not been independently audited.  Exact finite rational checks
are E2.  Float64 scans are E1.  C050 remains open.

## 1. Frozen route and first bad edge

The immutable card has SHA-256
`d61b9e0c14382ec49d8fc5db5dc7d677e57ea70a06b3cb18fe71f0321524db69`.
The card uses the subscript on its prefix hierarchy for the number of
coordinates, so its complete-epoch matrix is `H_n`.  From this point onward,
the subscript counts **complete epochs**:
`H_k=Phi^k(I)`.  Thus development `H_1` equals card `H_n` (uniform reversal
also identifies the `QQ^T` and `Q^TQ` averages).  No prefix is being dropped.
In this compact epoch notation, the frozen card fixes

```
Q_pi=P_(pi_n)...P_(pi_1),
H_1=E[Q_pi^T Q_pi],
D=I-H_1,
```

and proposes `D>=(mu/16)I`.

After the declared context was revealed, the identity in
`target_transfer.md` (T12) showed that this exact edge is equivalent to the
constant-`1/16` instance of the strong K-matrix certificate C051.  The card
did not assume C051—it independently selected an equivalent one-epoch
inequality—but completing only this edge would not be a new, weaker direct
C050 architecture.  This is the first structural obstruction.

The locked edge is retained and attacked.  A repair child retains the same
noncommutative covariance state but replaces the one-epoch full-space gap by
the multi-epoch orbit `H_m=Phi^m(I)` and its logarithmic-order trace moment.
The precise repaired lemma is (MC) in `target_transfer.md`.

The first draft of (MC) used the fixed-dimension estimate
`lambda_max(H)<=n^(1/p)tau(H^p)^(1/p)` and therefore proposed the
overstrong threshold `tau(H_m^p)<=exp(-3p/2)`.  A block-replication attack
showed both why this was unnecessary and what the exact bridge is.  For
`ell` identical block copies, `H_m` is the direct sum of `ell` copies while
`p=ceil(log(ell*n))` tends to infinity.  Thus a uniform inequality

```
tau(H_m^p)<=exp(-p/2)                                  (MC)
```

already implies `lambda_max(H_m)<=exp(-1/2)` by taking the copy number to
infinity.  Conversely that block operator bound implies (MC).  The selected
candidate is therefore the exponent `1/2` statement, and its proof method—not
its logical endpoint—is the noncommutative trace polynomial.  The preliminary
`3/2` threshold is retained below as a failed-overstrong formulation and as a
stronger stress margin on several families.

There is one exact low-moment simplification.  Frobenius self-adjointness of
`Phi` gives

```
tr(H_m^2)=<Phi^m(I),Phi^m(I)>=<I,Phi^(2m)(I)>=tr(H_(2m)). (M1)
```

Thus for dimensions `3<=n<=7`, where `p=ceil(log n)=2`, (MC) is the scalar
temporal moment condition `tr(H_(2m))/n<=e^-1`.  The inherited all-dimensional
floor `D>=(3mu/n)I` implies

```
tr(H_(2m))/n <=(1-3mu/n)^(2m) <=exp(-6/n).             (M2)
```

This closes the selected moment lemma for `n<=6` and stops just short at
`n=7`.  It is a consistency reconstruction of declared progress, not a new
claim.  The first genuinely new low-dimensional scalar target from this
route is therefore to improve (M2) by the factor `7/6` at `n=7`, using more
than the uniform floor of `D`.

The full `n=7` gap can be closed by retaining one more prefix loss.  The
first projection loses trace one.  Conditional on two distinct first
coordinates `i,j`, the second projection loses

```
tr(P_i B_j P_i)=1-A_ij^2.
```

Since `tr(A)=n` and every eigenvalue of `A` is at least `mu`, convexity on
the eigenvalue simplex gives

```
tr(A^2)<=[n-(n-1)mu]^2+(n-1)mu^2.
```

Averaging the second loss over ordered distinct pairs therefore gives at
least `2mu-mu^2`.  In particular,

```
tr(D)>=1+2mu-mu^2,
tr(H_1)<=n-1-2mu+mu^2.                                 (M3)
```

This is a two-prefix trace statement, not a Loewner estimate.  Also, for PSD
`X`, self-adjointness and the inherited floor `H_1<= (1-3mu/n)I` give

```
tr(Phi(X))=tr(H_1 X)<=(1-3mu/n)tr(X).
```

Therefore, with `m=ceil(1/mu)` and `n=7`,

```
tr(H_(2m))/7
 <=[(6-2mu+mu^2)/7](1-3mu/7)^(2m-1).                  (M4)
```

For each fixed ceiling interval with `m>=2`, the right side decreases with
`mu`, so it is at most

```
c_m=[(6-2/m+1/m^2)/7](1-3/(7m))^(2m-1).               (M5)
```

Put `x=3/(7m)` and `y=(1+2/m-1/m^2)/7`.  The elementary bounds
`log(1-z)<=-z-z^2/2` give

```
log(c_m)+1
 <=-[m^4+8m^3-21m^2-4m+1]/(98m^4)<0                 (M6)
```

for every integer `m>=3`: the numerator is `97` at three, its derivative is
`194` there, and its second derivative is positive thereafter.  For `m=2`,
`c_2=3993/10976`; the series tail estimate
`e<8/3+5/96=87/32<10976/3993` (cross-product gap `3841`) gives the same strict
comparison.  Finally `m=1` forces `mu=1`; trace and the unit diagonal then
force `A=I`, for which `H_1=0`.  Thus (M1) and (M4)--(M6) prove the selected
scalar `p=2` instance of (MC) for **every** `n=7` unit-diagonal SPD matrix.
This is an E3 proof draft pending different-run audit.  It still does not by
itself enable the direct-sum amplification used for C050, because repeated
copies live in larger dimensions and have moment order at least three.

This also identifies a real moment-order transition.  At `p=2`, every
replica word has `tr(S_1S_2)>=0` and self-adjointness collapses the entire
moment to (M1).  Starting at `p=3` (the selected order for dimensions
`8<=n<=20`), neither simplification survives: Section 7 gives an exact
negative RPCD replica word.  Thus the first unresolved logarithmic moment is
not merely a larger version of the `p=2` scalar temporal calculation; it
requires cancellation control.

The exact temporal collapse (M1) also cannot be extended by the seemingly
useful inequality `tr(H_m^p)<=tr(H_(mp))`.  For

```
A=[[1,1/10],[1/10,1]],   m=1,   p=3,
```

the subset recursion gives

```
tr(H_1^3)=103/400000000,
tr(H_3)=10201/40000000000,
tr(H_1^3)-tr(H_3)=99/40000000000>0.                    (M7)
```

Thus scalar temporal decay cannot upper-bound the first unresolved replica
moment by simply multiplying the time index.  This exact obstruction is
small but decisive for that implication; no assertion is made about the
reverse inequality.

As a direct finite stress at the first unresolved dimension, take eight
rational unit rows in `Q^3`, including both signs and the triples
`(3/5,4/5,0)`, `(0,5/13,12/13)`, and `(12/13,-5/13,0)`, as listed exactly in
`moment_falsifiers.py`.  Set `A=(I+BB^T)/2`.  Then `rank(BB^T)=3`, so
`mu=1/2`, `m=2`, and `p=3`; the interaction graph is connected and
`(U_1U_4-U_4U_1)_(1,1)=9/100`.  Exact subset recursion gives

```
tau(H_2^3)=0.000051207963695235490221... <1/8<exp(-3/2). (M8)
```

Moving down the same singular ray to `mu=1/4`, hence `m=4`, gives the second
exact value `tau(H_4^3)=0.0001208742541555429206493907...<1/8`.  The full
135/139- and 329/333-digit rationals are reproduced by the exact command.
These are E2 finite verifications, not a proof for `n=8`; they show that a
fully coupled signed noncommuting instance does not expose a failure at the
moment-order transition or at the additional singular-ray point.

## 2. Exact orientation and subset recursion

In x-coordinates let

```
U_i=I-e_i e_i^T A,       T_pi=U_(pi_n)...U_(pi_1).
```

For a coordinate set `S`, define `F_S(X)` as the average of
`T^T X T` over all orders that use every element of `S`.  Conditioning on
the first-applied coordinate gives the exact recursion

```
F_empty(X)=X,
F_S(X)=(1/|S|) sum_(i in S) U_i^T F_(S\{i})(X) U_i.    (R1)
```

Thus `F_[n](A)=E[T_pi^T A T_pi]` without enumerating `n!` products, and

```
L_x=A-F_[n](A),
D=A^(-1/2)L_x A^(-1/2).                               (R2)
```

`moment_falsifiers.py` implements (R1) exactly over `sympy.Rational` and in
float64 for scouts.  It also checks the update commutators rather than
assuming they vanish.

## 3. Commuting control

For `A=I_n`, every `P_i` deletes one orthogonal coordinate, the factors
commute, and a complete epoch has `Q_pi=0`.  Hence `D=I`, `mu=1`, and both
the card edge and (MC) hold exactly.  This is only a normalization control.

An exact two-dimensional high-`mu` control separates the repaired block
condition from the convenient family-local `3mu/2` one-step estimate used
below.  For

```
A=[[1,1/10],[1/10,1]],       mu=9/10,
```

the two generalized one-epoch loss eigenvalues are `1989/2000` and
`1991/2000`, both below `(3/2)mu=27/20`.  Thus the `3mu/2` one-step bound
fails.  Nevertheless `m=ceil(1/mu)=2`, `p=ceil(log 2)=1`, and exact recursion
gives

```
tau(H_2)=101/4000000 <1/100<exp(-3/2).                 (C1)
```

The last elementary comparison follows, for example, from `e<3`, hence
`e^(3/2)<3 sqrt(3)<6<100`.  Thus (MC) can hold through a genuine finite block
even when this stronger auxiliary one-step rate does not.

In fact (MC) holds for every two-dimensional instance.  Up to a diagonal
sign conjugation write

```
A=[[1,t],[t,1]],       0<=t<1,       mu=1-t.
```

The exact mean/contrast calculation shows that the smaller one-epoch loss
eigenvalue is

```
d_min=mu[1+(2-mu)^2]/2,
1-d_min=(1+t)t^2/2.                                    (C2)
```

(The other loss exceeds this by `(1-mu)^3=t^3`.)  With
`m=ceil(1/mu)` and positivity,

```
H_m <=[(1+t)t^2/2]^m I.
```

Using `log t<=-(1-t)` and
`log((1+t)/2)<=-(1-t)/2` gives

```
[(1+t)t^2/2]^(1/(1-t)) <=exp(-5/2).                    (C3)
```

Thus `H_m<=exp(-5/2)I`, which is stronger than (MC) for `p=1`.  This is an
all-instance `n=2` analytic control, not evidence for higher dimensions.

## 4. Positive equicorrelation falsifier, all n

Take

```
A_delta=delta I+(1-delta)11^T,       delta=n^(-2),
rho=1-delta,                         mu=delta.
```

Permutation conjugacy makes the averaged loss scalar on the mean line and
the `(n-1)`-dimensional contrast space.  It therefore suffices to analyze
the fixed order `(1,...,n)`.  Its lower triangular factor has diagonal one
and every strict-lower entry `rho`.  Writing `R=M^(-1)`, direct multiplication
gives

```
R_ii=1,
R_ij=-rho delta^(i-j-1)  (i>j),
R 1=(1,delta,...,delta^(n-1))^T.                       (E1)
```

The fixed-order loss is `(M^(-1)A)^T(M^(-1)A)`.  With
`P_c=I-11^T/n` and `lambda_1=n-(n-1)delta`, the two eigenvalues of the
whitened, permutation-averaged loss are

```
d_c =delta ||R P_c||_F^2/(n-1),
d_1 =lambda_1 ||R1||_2^2/n.                            (E2)
```

For every diagonal entry,
`(R P_c)_ii=1-delta^(i-1)/n >=1-1/n`.  For `i>=2`, its first subdiagonal
entry is `-rho-delta^(i-1)/n`, whose squared magnitude is at least `rho^2`.
Therefore, for `n>=4`,

```
d_c/delta >=(n-1)/n+rho^2
             >=3/4+(15/16)^2 >3/2.                   (E3)
```

The exact values `65/32` (`n=2`) and `41851/19683` (`n=3`) close the two
small dimensions.  Also

```
d_1 >=lambda_1/n >=1-delta >=3/4 >=(3/2)delta.         (E4)
```

Hence this analytic falsifier returns

```
D >=(3/2)mu I                                          (E5)
```

for every `n>=2` on the prescribed `delta=n^-2` family.  In particular it
does not realize the card's predicted `o(mu)` failure.  Moreover (E5) proves
(MC) on this family: for `m=ceil(1/mu)`,
`H_m<=(1-3mu/2)^m I<=exp(-3/2)I`.

The selected, weaker `exp(-1/2)` moment threshold can be proved on the whole
positive-equicorrelation parameter range `0<delta<=1`.  The diagonal terms
above give `d_c>=delta(n-1)/n>=delta/2`.  For the mean term set
`t=1-delta`.  Its exact value can be written

```
d_1=[1+delta/(nt)](1-delta^(2n))/(1+delta).            (E5a)
```

Since `(1-t)^(-2n)>=1+2nt`,
`1-delta^(2n)>=2nt/(1+2nt)`.  Substitution in (E5a) gives
`d_1>=delta/(1+delta)>=delta/2`.  (The endpoint `delta=1` follows by
continuity or directly from `A=I`.)  Thus

```
D >=(mu/2)I,       H_(ceil(1/mu))<=exp(-1/2)I          (E5b)
```

for every positive equicorrelation matrix, proving the selected (MC) on the
entire family without a numerical grid.

### Raw-trace obstruction on the same family

The family nevertheless exactly rejects a scalar trace-to-worst-direction
shortcut.  From (E1), using `delta<=1/4`,

```
||R||_F^2
 <=n+n sum_(g>=0)delta^(2g)
 <=(31/15)n.
```

Thus `lambda_min(D)<=d_c<(5/n^2)`, while
`tr(D)>=d_1>=3/4`.  Therefore

```
lambda_min(D)/(tr(D)/n) <=20/(3n) ->0.                 (E6)
```

So a lower bound on normalized trace cannot be promoted to a Loewner lower
bound with a dimension-free constant.  This is why the repair uses an upper
Schatten moment of `H_m` with `p=ceil(log n)` and keeps the exact
`n^(1/p)` transfer.

### Negative equicorrelation, all n

There is also an exact signed all-dimensional control.  Put `mu=n^-2` and
give every off-diagonal entry the value
`alpha=-(1-mu)/(n-1)`.  The mean eigenvalue is `mu`, while the contrast
eigenvalue is `s=1-alpha>1`.  The same triangular calculation gives

```
d_mean/mu=(1/n)sum_(j=0)^(n-1)s^(2j),
d_contrast=s||R P_c||_F^2/(n-1),
R1=(1,s,...,s^(n-1))^T.                                (E7)
```

Bernoulli's inequality yields

```
d_mean/mu >=(1/n)sum_j[1+2j(s-1)]
             =2-mu >=7/4.                              (E8)
```

The first row of `R P_c` alone has squared norm `(n-1)/n`, so

```
d_contrast >=s/n >=1/n >=2mu.                          (E9)
```

Thus `D>=(7/4)mu I` for every `n>=2` on this sign-frustrated family.  This
proves (MC) there as well and rules out both positive and negative
equicorrelation as the predicted `o(mu)` mechanism.

As on the positive side, the selected `exp(-1/2)` threshold extends to the
full negative-equicorrelation range.  Keep arbitrary `0<mu<=1`, put
`s=1+(1-mu)/(n-1)`, and use the same formulas.  The mean loss satisfies
`d_mean>=mu`.  For contrast there are two cases.

- If `mu<=2/n`, the first row of `R P_c` gives
  `d_contrast>=s/n>=1/n>=mu/2`.
- If `mu>=2/n`, then
  `s^(n-1)<=exp(1-mu)<=1/mu`; the last inequality is
  `log(mu)<=mu-1`.  Every diagonal entry of `R P_c` is at least
  `1-1/(mu n)`, so, with `z=mu n in [2,n]`,

```
d_contrast >=[n/(n-1)](1-1/z)^2 >=z/(2n)=mu/2.        (E10)
```

For the last scalar inequality,
`2n^2(z-1)^2/z^3` has its minimum on `[2,n]` at an endpoint;
the endpoint checks reduce to `(n-2)^2>=0` and `2(n-1)>=n`.
Consequently every positive or negative equicorrelation matrix satisfies

```
D >=(mu/2)I,       H_(ceil(1/mu))<=exp(-1/2)I.         (E11)
```

This is an analytic structured-family proof of the selected moment/block
certificate, not a general RPCD result.

## 5. Anisotropic, symmetry-breaking, noncommuting singular ray

Let the four unit rows of `B` be

```
(1,0), (0,1), (3/5,4/5), (4/5,3/5),
```

put `C=BB^T`, and set

```
A_eps=eps I+(1-eps)C.
```

Its spectrum is exactly

```
eps, eps, (26-eps)/25, (74-49eps)/25,
```

so it is unit diagonal SPD with `mu=eps`.  Its off-diagonal entries are
nonconstant, and at `eps=1/1000`

```
(U_1 U_3-U_3 U_1)_(1,1)=8982009/25000000 !=0.         (A1)
```

This simultaneously supplies near-singularity, anisotropy, broken full
permutation symmetry, and noncommutativity.

At `eps=1/1000`, the exact subset recursion and Sylvester's criterion prove

```
L_x-(3eps/2)A_eps >0.                                  (A2)
```

All five operations here—forming `A`, recursion (R1), subtracting the
rational matrix, taking leading principal minors, and checking their signs—
are exact.  Since `3/2>1/16`, (A2) clears the frozen edge by an exact margin
of at least `(23/16)mu` in whitened coordinates, and it proves (MC) for this
finite instance.

The singular limit was also checked analytically.  A rational kernel basis is

```
K=[(-3,-4,5,0)^T, (-4,-3,0,5)^T].
```

Block Schur perturbation of `L_x` along `ker C` yields a two-by-two effective
generalized pencil whose characteristic polynomial factors as

```
481(42258593750 z-107203894091)
   (290185156250 z-664641094637)/3065704157562255859375.
```

The limiting `D/mu` coefficients are therefore the exact rationals

```
107203894091/42258593750 =2.53685427217984...,
664641094637/290185156250=2.29040349005446....          (A3)
```

Thus no sub-`1/16` singular trend is present on this ray.

An even stronger one-`mu` block certificate can be closed on the whole
anisotropic ray, not only at `eps=1/1000`.  Form the four leading principal
minors of

```
L_x(eps)-eps A_eps.
```

Their exact numerator degrees are `8,16,24,32`.  Conversion to the Bernstein
basis on `[0,1]` gives respectively `1,2,5,8` zero coefficients and **no
negative coefficients**; the numbers of positive coefficients are
`8,15,20,25`.  All denominators are positive.  Since every Bernstein basis
function is positive in the open interval, Sylvester's criterion proves
strict positivity for `0<eps<1`; at `eps=1`, `A=I` and the residual is zero.
Thus

```
L_x(eps)>=eps A_eps,       0<eps<=1.                   (A3a)
```

This is an exact polynomial certificate for a quantified one-parameter
family (E3 proof draft, not an independently audited general theorem).  It
proves the selected (MC) along a genuinely anisotropic, noncommuting,
symmetry-breaking family for its full SPD parameter range.

### General singular-ray falsifier reduction

The same calculation gives a compact analytic falsifier for every singular
correlation boundary.  Let `C>=0` have unit diagonal and nonzero kernel, put
`A_eps=eps I+(1-eps)C`, and define the boundary inverse moment

```
K_0=E_pi[M_pi(C)^(-T)M_pi(C)^(-1)].                    (A4)
```

Every triangular `M_pi(C)` has diagonal one, so (A4) is finite even though
`C` is singular.  Let `N` and `R` be orthonormal bases of `ker C` and
`ran C`.  The shorted matrix

```
S_C=N^T K_0 N
    -N^T K_0 R (R^T K_0 R)^(-1) R^T K_0 N             (A5)
```

controls the slow generalized loss.  Indeed
`L_eps=A_eps K_eps A_eps`.  A low vector has the form `x+eps r`, with
`x in ker C`; then

```
A_eps(x+eps r)=eps(x+C r)+O(eps^2).
```

Since `Cr` ranges over `ran C`, minimizing the leading `K_0` quadratic over
the range correction gives exactly the Schur complement (A5).  Hence

```
lim_(eps downarrow 0) lambda_min(D_eps)/eps
 =lambda_min(S_C)                                      (A6)
```

when `N` is orthonormal (or the corresponding generalized eigenvalue for a
nonorthogonal kernel basis).  Formula (A6) is a proof-draft singular
perturbation statement; it has not had an independent audit.  For the
rational anisotropic `C`, (A5) reproduces exactly the two roots in (A3).

This reduction turns the card's predicted coherent-frame failure into a
decisive boundary test: any `C` with
`lambda_min(S_C)<1/16` gives sufficiently small positive `eps` violating the
frozen lemma.  A float64 scout enumerated every permutation for 500, 300,
and 100 random singular Gram matrices in dimensions 5, 6, and 7,
respectively.  Its minimum was `2.1339160631905645`, with kernel tolerance
`1e-8`; this no-hit result remains E1.

## 6. Signed and block stress control

The exact five-dimensional block matrix

```
[ 1    15/16    0      0      0   ]
[15/16   1      0      0      0   ]
[ 0      0      1    -12/25 -12/25]
[ 0      0    -12/25   1    -12/25]
[ 0      0    -12/25 -12/25   1   ]
```

has spectrum
`{1/25,1/16,37/25,37/25,31/16}`.  The negative-equicorrelation triangle is
sign-frustrated (the product of its three off-diagonal signs is negative) and
its update factors do not commute; for example the displayed verifier obtains
commutator entry `144/625`.

Exact recursion and Sylvester signs prove

```
L_x-(3mu/2)A >0,       mu=1/25.                         (S1)
```

This covers a block/signed mechanism distinct from the positive
equicorrelation and anisotropic rays.  It is again a finite family result,
not a general theorem.

More generally, the controls are stable under block-diagonal sums.  If
`A=diag(A_1,...,A_r)`, updates from different blocks commute.  Restricting a
uniform global permutation to a block gives a uniform internal order, and
the complete epoch map is block diagonal regardless of the interleaving.
Consequently the loss is `D=diag(D_1,...,D_r)`.  If each controlled block
satisfies `D_b>=(3/2)mu_b I`, then, with
`mu=min_b mu_b`,

```
D >=(3/2)mu I.                                         (S2)
```

Thus arbitrary block sums of the positive/negative equicorrelation controls
and the exact anisotropic control also satisfy (MC).  This closure uses only
the marginal uniform internal orders; it does not pretend that coordinates
within a block commute.

## 7. Exact obstruction to a commuting multi-epoch shortcut

For the anisotropic instance, let `G_1=Psi(A)` and `G_2=Psi(G_1)`, where
`Psi(X)=E[T_pi^T X T_pi]`.  In energy coordinates,

```
H_2-H_1^2
```

is congruent to the rational matrix

```
Delta=G_2-G_1 A^(-1)G_1.
```

The verifier gives `tr(A^(-1)Delta)=0`, a nonzero `(1,1)` entry, and a
strictly negative exact determinant.  Hence the whitened difference is
indefinite.  Neither `H_2<=H_1^2`, nor `H_2>=H_1^2`, nor equality is valid on
this instance.  Any proof of (MC) must retain the actual noncommutative
replica polynomial (T11), not silently replace epochs by commuting powers.

Nor may (T11) be bounded term by term as a sum of nonnegative replica words.
For the exact positive equicorrelation matrix

```
A=[[1,1/5,1/5],[1/5,1,1/5],[1/5,1/5,1]],
spec(A)={4/5,4/5,7/5},
```

take the three zero-based update orders
`(1,2,0)`, `(1,0,2)`, and `(2,0,1)`.  If
`S_pi=Q_pi Q_pi^T`, exact rational calculation gives

```
tr(S_1 S_2 S_3)=-415506/30517578125 <0.             (F0)
```

The verifier avoids square roots by cyclically conjugating each factor to
`T_pi A^(-1)T_pi^T A`.  Thus even inside well-conditioned RPCD, individual
`p=3` replica traces have signs.  Positivity exists only after assembling the
full deterministic matrix power `tr(H_m^p)`; dropping unfavorable words or
using a termwise positive comparison is invalid.

A second tempting proof step also fails exactly.  Since
`H_k-H_(k+1)>=0`, convexity gives

```
tr(H_k^p)-tr(H_(k+1)^p)
 >=p tr(H_(k+1)^(p-1)(H_k-H_(k+1))).                   (F1)
```

One might try to lower-bound the right side by
`(3/2)p mu tr(H_k^p)`.  At `k=0`, take negative equicorrelation with
`n=10`, `mu=1/100`, and `p=3`.  Exact mean/contrast formulas give

```
tr(H_1^(p-1)D)/(mu tr(I^p))
 =0.296046249871272... <3/2.                            (F2)
```

The verifier stores the full rational and the strictly positive rational gap
to `3/2`.  The actual normalized trace-power ratio is only
`tr(H_1^p)/n=0.0911476463962104...`, so the desired nonlinear dissipation is
large; it is the linearization (F1) that throws it away.  Nearly annihilated
contrast directions contribute strongly to `tr(I^p)-tr(H_1^p)` but are
suppressed by the factor `H_1^(p-1)` in (F1).  A viable proof must retain this
nonlinear finite loss rather than only its endpoint derivative.

This is not merely a bad constant.  On the same negative-equicorrelation
family with `mu=n^-2`, put `s=1+(1-mu)/(n-1)` and
`p=ceil(log n)`.  The mean loss obeys `d_m<=e^2 mu`, because
`s^(n-1)<=e`.  For the contrast survival eigenvalue `h_c=1-d_c`, the exact
triangular formula gives

```
||R P_c||_F^2=||R||_F^2-||R1||_2^2/n
             >=n-e^2,
h_c <=(e^2-1)/(n-1).                                  (F3)
```

Therefore the normalized linearized cross ratio is at most

```
e^2/n+n^2[(e^2-1)/(n-1)]^(p-1) ->0.                   (F4)
```

So no universal positive constant can close (F1) by this endpoint cross
term.  The repair must use the full nonlinear difference of trace powers (or
an equivalent replica polynomial), not a first derivative at the surviving
endpoint.

The exact retained replacement is the interpolation identity.  With
`X=H_k`, `Y=H_(k+1)`, and `E=X-Y>=0`, differentiation under the trace gives

```
tr(X^p)-tr(Y^p)
 =p integral_0^1 tr[(Y+tE)^(p-1)E] dt.                (F5)
```

This identity is valid without commuting `Y` and `E`: cyclicity makes the
`p` derivative terms equal after taking the trace.  The failed step (F1)
kept only the endpoint `t=0`.  Directions almost annihilated in one epoch
instead contribute through intermediate and `t` near one layers.  A scalar
relative survival `z` contributes the exact factor `1-z^p`, which both
amplifies small loss by `p` and saturates at one for large loss.

This suggests a resolvent/interpolation hierarchy retaining dyadic `t`
layers of `(Y+tE)^(p-1)`, rather than a single endpoint derivative.  It has
not been closed: the first bad edge is to use the RPCD frame floor and word
orientation to lower-bound the integral in (F5) uniformly on the reachable
orbit.  Replacing the integral by either endpoint is analytically
insufficient (for scalar `Y=X/2` and large `p`, both `tr(E^p)` and the
`t=0` derivative are exponentially small while the full loss tends to
`tr(X^p)`).

## 8. Numerical scouts (E1 only)

Seven deterministic float64 scouts were run:

1. Seed `20260825`, 250 rank-deficient Gram rays in each dimension
   `n=7,8,9,10`, `delta in [10^-5,10^-1]`.  The smallest observed
   `lambda_min(D)/delta` was `1.9758755109143034`; no value was below
   `1/16`.
2. Seed `91920260825`, 1000 hierarchical full-rank Gram trials in each
   `n=7,...,11`, with the conservative accepted range
   `10^-6<=mu<=0.2`.  The smallest observed ratio was
   `2.0454667440694614`; no hit occurred.
3. The proposed block trace moment was evaluated on positive and negative
   equicorrelations, the anisotropic rational ray, and the signed block.  At
   `m=ceil(1/mu)` the largest observed
   `tau(H_m^p)^(1/p)`, `p=ceil(log n)`, was approximately `0.10684618`,
   below the selected threshold `exp(-1/2)=0.60653066` and even below the
   preliminary overstrong threshold `exp(-3/2)=0.22313016`.
4. The singular-boundary shorting scout enumerated every order on 500, 300,
   and 100 random rank-deficient Gram matrices in dimensions 5, 6, and 7.
   Its minimum boundary coefficient was `2.1339160631905645` versus the
   frozen-edge threshold `1/16`.
5. The direct-sum base-block attack enumerated every permutation on accepted
   random instances in dimensions 3--6 (18,308; 5,383; 1,214; and 214
   accepted matrices).  The largest observed
   `lambda_max(H_(ceil(1/mu)))` was `0.08937130000511036`, below the selected
   replication threshold `exp(-1/2)=0.6065306597126334`.
6. On the fully coupled signed `n=8` rational ray, 25 log-spaced parameters
   in `[0.02,0.9]` plus `0.01,0.005,0.002` gave maximum selected third-moment
   root `0.0576327981119162` (at `eps=0.002,m=500`) and corresponding operator
   value `0.07379378538248739`.  This continuation is float64 E1; only the
   `eps=1/2,1/4` points above are exact E2.
7. Seed `70720260825`, 1000 normalized random Gram matrices in `n=7`, checked
   the orientation of the new trace formula.  The minimum observed margin in
   `tr(D)-(1+2mu-mu^2)` was `2.596211689698937` at tolerance `1e-10`; this is
   an E1 regression only, not support for the analytic quantifier.

The theoretical singular-ray construction makes `mu=delta`; observed
`lambda_min(A)-delta` discrepancies below `9e-16` are roundoff.  No interval
claim is made for the scouts.  Apparent negative loss eigenvalues from an
earlier experiment with `mu` around `10^-9` disappeared under symmetric
eigen-whitening/high-precision recomputation and were discarded as numerical
instability.

## 9. Decision and reopen condition

- Frozen edge: **suspend/branch**, not refute.  It survived every exact
  falsifier, but by (T12) it is the unresolved strong C051 edge rather than a
  new direct-C050 bridge.
- Repair child: **advance as an E0 candidate with an E3 transfer proof**.
  The open lemma is (MC), a dimension-uniform logarithmic-order trace moment
  of the genuine multi-epoch noncommutative polynomial.
- First bad edge of the repair: proving (MC) without commuting the factors or
  converting a raw trace estimate into operator control.
- Reopen the frozen one-epoch branch if a separate run supplies a general
  proof of `D>=(mu/16)I`, or an exact/certified unit-diagonal SPD
  counterexample.  Reopen the moment repair for depth when a dimension-free
  replica inequality for (T11), or a certified counterexample to (MC), is
  available.

## 10. Locked-route phase 3: positive relative survival

Phase 3 did not replace the representation.  It kept `H_j=Phi^j(I)` and
attacked the first unresolved `p>=3` edge.  For

```
X=H_j,       Y=H_(j+1),       C_j=X^(-1/2)YX^(-1/2),
```

restricted to `supp(X)`, Araki--Lieb--Thirring gives the route-local E3
reduction

```
tr(Y^p)<=tr(X^p C_j^p)
       =tr[X^(p-1)Y(X^(-1)Y)^(p-1)].                    (M9)
```

The second expression is exactly rational whenever a simultaneous rational
similarity of `X,Y` is available.  Subtracting (M9) retains the full nonlinear
loss `tr[X^p(I-C_j^p)]`; it neither commutes epoch factors nor declares signed
replica words positive.  If `G_j=I-C_j`, functional calculus gives

```
tr(X^p)-tr(Y^p)
 >=(1-e^-1)tr[X^p min{pG_j,I}].                         (M10)
```

Thus almost-annihilated directions receive saturated order-one weight, fixing
the precise defect of the failed `t=0` endpoint linearization.

Define

```
r_j=tr(H_j^p C_j^p)/tr(H_j^p).
```

Repeated use of (M9) proves

```
tr(H_m^p)/n <=product_(j=0)^(m-1)r_j.                  (M11)
```

The repaired first bad edge is now the cumulative positive certificate

```
sum_(j=0)^(m-1)-log(r_j)>=p/2.                          (M12)
```

Equation (M12) implies (MC) and hence the unchanged transfer in
`target_transfer.md`.  The stronger local inequality
`r_j<=(1-mu/2)^p` is a convenient falsifiable sublemma, not an assumption.

One quantified fragment closes analytically.  Since the first prefix loses
trace one, `tr(H_1)<=n-1`.  Therefore, for `mu<=2/(np)`,

```
tr(H_1^p)<=n-1<=n(1-mu/2)^p,                            (M13)
```

using Bernoulli's inequality.  This proves the local sublemma only at `j=0`
in the stated ultra-near-singular region.

Two exact information barriers delimit (M12).  First, the ALT comparison is
trace-only: the rational matrices in `relative_survival_repair.md` give a
positive trace residual `27/160` but determinant
`-15129/2560000`, so no Loewner promotion is available.  Second, at
`n=8,p=3,mu=1/2`, an abstract spectrum consistent with both the inherited
one-epoch floor and the two-prefix trace bound violates the desired local
moment estimate by `571/1024`.  It is not an RPCD counterexample; it proves
that those scalar summaries alone discard necessary orbit information.

Exact Rational stresses on the anisotropic noncommuting ray and the fully
coupled signed `n=8` ray survived the local half-`mu` inequality.  A seeded
float64 attack (seed `2718281828`) evaluated 3,403 orbit steps on 125
near-singular rays in dimensions 8--10.  Its minimum normalized exponent was
`2.3702105854001734` versus the rejection threshold `1/2`.  The null scan is
E1 only.

The deepest remaining obstruction is no longer signed replica algebra.  It
is a dimension-uniform small-relative-loss estimate for the orbit-weighted
spectral measures of `G_j`.  A first moment of that measure cannot suffice:
placing mass `1-mu` at loss zero and `mu` at loss one has mean `mu` but gives
survival `1-mu`, too large for an `exp(-p*mu/2)` bound when `p>2` and `mu` is
small.  A successful proof must control small-loss mass, not only mean loss.
