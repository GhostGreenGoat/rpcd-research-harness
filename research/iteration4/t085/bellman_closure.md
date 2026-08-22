# T085 Bellman closure attempt and precise remaining blocker

Status: proof-draft identities plus explicitly labelled numerical conjectures.  No claim here closes
the all-dimensional RPCD problem.

## 1. Exact loss hierarchy

Let `F(B)=B^{-1}-K(B)` be the exact one-sweep order loss and define

```
R_1(B)=bar(D)_B,
R_{ell+1}(B)=m^{-1} sum_i L_i^T R_ell(C_i)L_i.
```

Take `R_ell=0` once fewer than two coordinates remain.  Subtracting the exact Bellman recursion for
`K` from

`G=I/m+m^{-1}sum_i L_i^T C_i^{-1}L_i+bar(D)_B`

gives

```
F(B)=bar(D)_B+m^{-1}sum_i L_i^T F(C_i)L_i
    =sum_{ell=1}^{m-1} R_ell(B).                             (1)
```

Thus `R_2` is exactly the matrix compressed in `compression_lemma.md`; higher `R_ell` are not
independent numerical artifacts but the successive Bellman Schur losses.

## 2. What the new second-level state closes

Suppose a child lower certificate contains

`a C_i^{-1}+bI-c bar(D)_{C_i}`.

Its Bellman image is

```
aG+(1-a)I/m-a bar(D)_B+b Jcal_B-c R_2(B),                   (2)
```

where

`Jcal_B=[mI-2B+Diag(diag(B^2))]/m`.

The new result replaces the last term rigorously by

`-c R_2(B) >= -c P_B`,

where `P_B=2(U_B:W_B)` is the parallel compression.  The state needed at this level is finite:

- parent leverage `s_i=1/G_ii`;
- child floors `mu_i=lambda_min(C_i)`;
- child normalized-loss trace and trace-square;
- post-lift Schur-loss trace and trace-square;
- the matrix `U_B` and scalar multiple `W_B`.

This is strictly more informative than the old basis `{G,I,bar(D)}` and passes both singular
geometries.

## 3. Why it is not yet closed at the next lift

The next Bellman step contains

`m^{-1}sum_i L_i^T P_{C_i}L_i`.                             (3)

Parallel sum is nonlinear, and no proved Jensen direction turns (3) into `P_B` or a fixed linear
combination of `G,I,bar(D)_B,P_B`.  In fact:

1. Parallel sum is jointly concave, so Jensen naturally gives an **upper bound on a parallel sum
   of averages**, not the upper bound on the average (3) needed after its negative sign.
2. Replacing `P_{C_i}` by its scalar parent rate discards the anisotropy that (6) was designed to
   retain.
3. A new post-lift normalization of (3) is valid, but it introduces third-order trace/cross moments.
   Repeating this operation gives an adaptive hierarchy rather than a fixed finite basis.

Consequently the present construction closes the second Schur moment but not all higher moments.

## 4. Failed shortcuts, with exact breakpoints

### 4.1 Compressing into the first loss

No finite universal `C` satisfies `R_2(B)<=C bar(D)_B`.  The exact SPD example

```
B=[[1,1/3,1/4],[1/3,1,0],[1/4,0,1]],
v=(0,1/4,-1/3)
```

has `bar(D)_Bv=0` and `v^T R_2(B)v=263/124416`.  Thus second-level directions genuinely escape
the range of the first-level moment.  The weaker coefficient-one guess also fails on the
3-dimensional regular-simplex lift at `mu=1/5`, with transverse eigenvalue
`lambda(bar(D)-R_2)=-32/5625`.

### 4.2 Childwise scalarization, even with the exact child rate

The bound `bar(D)_{C_i}<=eta_iC_i^{-1}` gives the closed weighted matrix `U_B`, but on the
simple-null regular-simplex limit its normalized rate exceeds the exact `R_2` rate by
`m(m-2)^2`.  This is an unbounded loss.  The post-lift Schur factor in `W_B` is therefore not
optional.

### 4.3 A generic second upper bound and naive parallel sum

Since `bar(D)_{C_i}<=C_i^{-1}`, one also has

`R_2<=V_B:=G-bar(D)_B-I/m`.

Although `R_2<=2(U_B:V_B)` is valid, it remains worse by order `m^3` on the simplex limit.  Replacing
`V_B` by the post-lift moment bound `W_B` is the material correction.

### 4.4 Matrix-fractional Jensen

The map `(X,Y) -> XY^{-1}X^T` is jointly convex.  Applied to

`bar(D)_B=(G-I)Diag(diag G)^{-1}(G-I)/m`,

it supplies a lower bound on an average Schur loss.  Bellman closure needs an upper bound because
the loss enters with a minus sign.  A reverse inequality requires a condition-number factor and
recreates the boundary loss; this route did not close.

### 4.5 Shorted operators

For `v_i=(G-I)e_i`,

```
D_i=(1-s_i) short_G(span(v_i)),                              (4)
```

because `v_i^T Bv_i=G_ii-1`.  Formula (4) explains the exact coefficient `1-s_i`, but shorting does
not commute with averaging or with the child lifts.  The eigenvalue-one rational example above
shows the obstruction sharply: the first shorted ranges have a common kernel, while the second
lift rotates positive mass into that kernel.

### 4.6 Operator Kadison/Jensen

Writing `X_pi=M_pi^{-1}` gives

`K=E[X_pi^T X_pi]>=(E X_pi)^T(E X_pi)`.

Reversal symmetry makes `Z=E X_pi` symmetric.  On
`B_m(mu)=mu I+(1-mu)11^T`, its all-ones eigenvalue is exactly

`z_parallel=(1-mu^m)/[m(1-mu)]`.

The corresponding Kadison generalized coefficient divided by `mu` is

`[m-(m-1)mu] z_parallel^2/mu ~ 1/[m mu(1-mu)]`

for fixed `mu in (0,1)`.  It tends to zero.  Hence the variance discarded by Kadison is essential;
this route cannot prove a universal `c mu` bound.

### 4.6b Bare inverse Jensen

The stronger-looking bare certificate

`K>=(A+S)^{-1}`, with `S=(A-I)^2/3+Diag(diag((A-I)^2))/6`,

also discards too much variance.  On `A=mu I+(1-mu)11^T`, its parallel `S` eigenvalue is

`(1-mu)^2(m-1)(2m-1)/6`.

At `m=21,mu=9/20`, the certified generalized coefficient divided by `mu` is exactly
`3200/6401=1/2-1/12802`.  For fixed `mu in (0,1)` it is asymptotic to
`3/[m mu(1-mu)]` and therefore tends to zero.  Thus even this bare Jensen route cannot prove any
universal positive constant; the Bellman/variance state is essential.

A smaller transverse witness is `m=12,mu=1/100`, where the same ratio is exactly
`20000/42671=1/2-2671/85342`.

### 4.7 Iterating the two-step WOR bound

The exact formula

`J_2=[(2m-1)I-2B+Diag(diag B^2)]/[m(m-1)]`

does imply the improved theorem candidate

`J_2>=(2mu/m)B^{-1}`.                                       (5)

But replacing every child `J_2(C_i)` by its scalar consequence does not prove the third step.
For `B=(1/8)I+(7/8)11^T` in dimension three, that scalar lift has transverse coefficient
`1321/11520`, below `mu=1440/11520` by `119/11520`.  A direct float search also finds that the
Loewner comparison “three WOR updates are better than three with-replacement updates” is false.
Thus (5) is not multiplied across dependent pairs.

### 4.8 Pairing complementary half-prefixes pathwise

Another possible proof of the half-depth claim would pair the first half of a permutation with the
reversed complementary half, run both from the same initial point, and claim that their two energy
decreases sum to at least `mu A`.  This deterministic claim is false.  For the 3-dimensional
equicorrelation matrix with off-diagonal `1/3` (`mu=2/3`), take sequences `(1,2)` and `(3)` in
one-based notation.  If `Delta` is the sum of their two decrease matrices minus `mu A`, exact
rational arithmetic gives

`(-4,-5,7) Delta (-4,-5,7)^T=-440/81<0`.

This does not refute the averaged half-depth conjecture; it shows that the permutation average, not
a pathwise complementary-pair inequality, must do essential work.

## 5. Exact shallow-depth impossibility for the determinant tail

For the signed-rank-one family and `1<=r<=m-3`, let `a_{r,m}` be the ordinary eigenvalue of
`H_r(B_m(mu))` on `1^perp` in the limit `mu->0`.  At positive depth the all-ones eigenvalue is
`1/m`.  For a transverse unit vector, an averaged first deletion sends squared norm
`(m-2)/(m-1)` to the child transverse space and `m/(m-1)` to its parallel space.  Therefore

```
a_{1,m}=1/m,
a_{r+1,m}=1/m+[(m-2)/(m-1)]a_{r,m-1}+m/(m-1)^2.
```

Putting `u_{r,m}=(m-1)a_{r,m}` yields

`u_{r+1,m}=u_{r,m-1}+2+1/[m(m-1)]`,

and telescoping proves

```
lim_{mu->0} c_r(B_m(mu))/mu
  =(2r-1-1/m)/(m-1).                                       (6)
```

The range ends at `m-3` because at the next step the determinant leaf reaches a 2-dimensional
child and contributes a nonzero boundary term.  Equation (6) proves that every `r=o(m)` strategy
based on this determinant tail fails to give `c_r>=c mu` for fixed `c>0`.

## 6. Surviving half-depth conjecture

Before stating the open target, there is a fully scalar closed bound that is useful in the
high-`mu` regime.  Let the desired depth be `r`, put `d=m-r`, and seed every `d`-dimensional leaf by

```
a_d=delta_d(mu):=mu^(d-1)[d-(d-1)mu].                       (7)
```

This is valid because every principal child has spectral floor at least `mu`, unit diagonal, and
determinant at least `delta_d(mu)`.  If every size-`k-1` child has coefficient `a_{k-1}`, (M2.8),
`bar(D)_B<=(1-mu)G`, and `I>=mu G` give the closed recurrence

```
a_k=mu/k+mu(k-1)a_{k-1}/k.                                  (8)
```

Writing `b_k=ka_k` solves it exactly:

```
a_m={mu(1-mu^r)/(1-mu)+mu^r d delta_d(mu)}/m,               (9)
```

with the continuous value `a_m=1` at `mu=1`.  Therefore `c_r(B)>=a_m` for every admissible `B`.
For half depth, (9) proves the desired `mu/2` bound whenever its explicit right-hand side is at
least `mu/2`; this sufficient high-`mu` region can be evaluated directly without any matrix search and
approaches one as `m` grows.  At low `mu`, however, `a_m/mu~1/m`; the scalarization loses exactly the
anisotropy needed for the universal result.

The shallow obstruction points to linear, not constant, depth.  The cleanest remaining target is

```
H_{ceil(m/2)}(B) >= (mu/2) B^{-1}.                          (10)
```

It would immediately give the requested complexity.  It is plausibly sharp for this depth: on
near-identity equicorrelation matrices whose off-diagonal size tends to zero slowly enough that the
determinant leaf vanishes, the prefix accounts for asymptotically only half the coordinates.

Evidence for (10) outside the proved high-`mu`/structured regimes is currently only numerical:

- seed `4085`, `250` random boundary matrices per dimension, `3<=m<=10`;
- structured rank-one and simplex sweeps;
- smallest observed `c_{ceil(m/2)}/mu = 0.825668143180067`.

The equicorrelation two-scalar recursion at larger `m` numerically approaches `1/2` from above,
and `structured_asymptotics.md` now proves the half-depth `mu/2` bound exactly for a single
signed-rank-one block at every positive `mu`.  There is also a boundary analytic extension: for
every block-diagonal union of signed-rank-one blocks,
hypergeometric averaging of the exact local prefix formula proves

`liminf_{mu->0}c_{ceil(m/2)}/mu>=1/2`.

The derivation is in `structured_asymptotics.md`.  It covers a broad high-nullity boundary class but
not arbitrary correlations.  The remaining numerical observations are not a proof.  The missing
universal lemma can be phrased equivalently as a prefix/tail
matrix inequality; the stronger sampled conjecture `J_t>=(t mu/m)B^{-1}` also implies (7), but is
unproved for `t>=3`.

## 7. Outcome

The second moment now has a valid, leverage-aware, child-floor-aware PSD compression that survives
both required boundary tests and clears the old `n=3,mu=1/5` H1 obstruction when the dimension-three
hierarchy is evaluated exactly.  The universal statement `c_r>=c mu` remains open.  Exact result
(6) narrows any successful determinant-tail proof to linear/adaptive depth, while (3) identifies
the third-order Bellman lift of the nonlinear parallel state as the current blocker.
