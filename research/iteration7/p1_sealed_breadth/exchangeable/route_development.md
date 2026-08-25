# Locked route development: exchangeable transpositions and RPCD dissipation

Run: `20260825T123453Z-c7e1b13a`
Worker: `sealed-exchangeable-coupling`
Route card: `R143-exchangeable-transposition-dissipation`
Locked SHA-256: `a3b904849b72c6467cda29b520d59f789b55d9a948c1290d9f1a8450c6b11bec`

## 1. Status and evidence discipline

The locked core lemma is **refuted by an exact rational witness**.  This is a
route-local refutation, not a counterexample to C050.  The attack also proves a
sharp replacement for a pure Euclidean-residual comparison: its best universal
coefficient has infimum `1/n`, so changing `1/16` to another positive universal
constant cannot repair that edge.

The exchangeable-pair representation nevertheless yields a different, precise
repair candidate: combine the mean endpoint with the sharp random-transposition
Dirichlet form.  Three rational structured slices and an all-dimensional
signed `2 x 2` block calculation support that repair.  No general proof is
claimed.  The general candidate is E0; seeded null searches are E1; exact
finite slices are E2; analytic route-local identities and structured-family
proof drafts are at most E3 pending a different-run hostile audit.

C050 remains an open conjecture.  The repair would imply a strong one-epoch
energy inequality and hence C051, but it does not assume C051 and C050 is not
treated as equivalent to C051.

## 2. Exact residual representation

Let

```text
U_i = I-e_i e_i^T A,
X_0=x,
X_t=U_{pi_t}X_{t-1},
r_t=A X_t,
d_t=e_{pi_t}^T r_{t-1}.
```

Because `A_ii=1`, one coordinate update gives

```text
||X_t||_A^2=||X_{t-1}||_A^2-d_t^2.
```

Consequently

```text
D_pi(x):=sum_{t=1}^n d_t^2,
||T_pi x||_A^2=||x||_A^2-D_pi(x).                 (2.1)
```

This identity is pathwise.  Only the later expectation over a fresh uniform
permutation is probabilistic.

For completeness, let `P_pi` have rows `e_{pi_t}^T`, put
`A_pi=P_pi A P_pi^T`, and let `M_pi=tril(A_pi)` including its diagonal.
If `b=P_pi Ax` and `d=(d_1,...,d_n)^T`, then the residual recurrence is

```text
b=M_pi d,
d=M_pi^{-1}P_pi Ax,
D_pi=||M_pi^{-1}P_pi Ax||_2^2.                    (2.2)
```

Equation (2.2) is used only as an exact check; the developed repair retains the
paired trajectories rather than diagonalizing a covariance superoperator.

## 3. First bad edge: the locked core lemma is false

The card proposed

```text
E_pi D_pi(x) >= (1/16)||Ax||_2^2.                 (L)
```

Take an arbitrary sign vector `s in {+1,-1}^n` and

```text
A=(1-rho)I+rho ss^T,       0<rho<1,
x=s/[1+(n-1)rho].
```

Then `A` is unit diagonal, its eigenvalues are `1-rho` with multiplicity
`n-1` and `1+(n-1)rho` on `span{s}`, and `Ax=s`.

Write `delta=1-rho`.  In any update order, induction gives

```text
d_t=s_{pi_t} delta^(t-1).                          (3.1)
```

Indeed, if (3.1) holds before position `t`, the initial residual at the new
coordinate is `s_{pi_t}`, while every earlier update contributes
`rho s_{pi_t} delta^(u-1)` with the same sign after the two sign factors
cancel.  The geometric sum leaves `s_{pi_t}delta^(t-1)`.  Thus

```text
D_pi=sum_{t=0}^{n-1} delta^(2t),
D_pi/||Ax||_2^2=(1/n)sum_{t=0}^{n-1}delta^(2t).    (3.2)
```

For the exact witness use

```text
n=17, rho=99/100, delta=1/100,
s=(-1,1,1,-1,1,1,-1,1,1,-1,1,1,-1,1,1,-1,1).
```

Here `mu=1/100`, the high eigenvalue is `421/25`, and `x=(25/421)s`.
An exact positive `LDL^T` certificate is also available.  After diagonal sign
conjugation, the leading `k x k` determinant is
`delta^(k-1)(delta+k rho)`, so the pivots are `1` and
`delta(delta+k rho)/(delta+(k-1)rho)` for `k=2,...,17`; all are positive
rationals.  The exact margin is recorded in `falsifier_results.json`; it is positive and
approximately `0.0036705876469999943`.  A short exact comparison avoids the
large fraction:

```text
D_pi < 1/(1-10^-4)=10000/9999,
16*10000=160000 < 169983=17*9999.
```

Therefore `D_pi/17<1/16`.  The coordinate updates are genuinely
noncommuting: the exact checker obtains
`||(U_1U_0-U_0U_1)x||_2^2=9801/5000>0`.

This witness does **not** attack C050.  In fact its residual lies in the high
eigenspace, so the card's later use of
`||Ax||_2^2 >= mu||x||_A^2` has enormous slack on the witness.

There is also a matching universal lower bound.  The first term of `D_pi` is
`(Ax)_{pi_1}^2`, and `pi_1` is uniform, so

```text
E_pi D_pi(x) >= (1/n)||Ax||_2^2.                   (3.3)
```

Together, (3.2)--(3.3) show that the infimum of the best coefficient in a
pure initial-Euclidean-residual comparison is exactly `1/n`.  The locked edge
cannot be repaired by changing `1/16` to another dimension-free number.
Moreover, (3.3) proves the locked `1/16` comparison for every `n<=16`.
Therefore dimension 17 is not merely the first witness found in this run: it
is the smallest dimension in which any counterexample to `(L)` can exist.

## 4. Required exact adjacent-transposition identity

Let two adjacent positions contain coordinates `a,b`, let `z` be their common
prefix state, and write

```text
r=Az, alpha=r_a, beta=r_b, q=A_ab.
z_ab=U_b U_a z,          z_ba=U_a U_b z.
```

Direct expansion gives

```text
z_ab-z_ba=q(alpha e_b-beta e_a),                    (4.1)
```

and their two-coordinate dissipation difference is

```text
[alpha^2+(beta-q alpha)^2]
 -[beta^2+(alpha-q beta)^2]
 =q^2(alpha^2-beta^2).                              (4.2)
```

If `S` is the common suffix product, the terminal difference is exactly
`S q(alpha e_b-beta e_a)`.  Thus no commutativity or independence inside the
epoch has been inserted.

The checker verifies (4.1)--(4.2) over the rational SPD matrix

```text
[[1,   1/3, -1/5],
 [1/3, 1,    1/4],
 [-1/5,1/4,  1  ]],
```

whose leading principal minors are `1,8/9,2711/3600`, using
`alpha=7/6`, `beta=-2/5`.  The endpoint-difference squared Euclidean norm is
`1369/8100` and the two-step dissipation difference is `1081/8100`.

In energy coordinates `v_i=A^(1/2)e_i`, `Z_i=I-v_iv_i^T`, the same identity is
the rank-two commutator formula

```text
(Z_bZ_a-Z_aZ_b)y
 = A_ab[(v_a^T y)v_b-(v_b^T y)v_a].                 (4.3)
```

This connects the locked residual trajectory to a Hilbert-valued
exchangeable pair without invoking the lifted covariance spectrum.

For a nonadjacent transposition at positions `i<j`, let `R` be the product of
the energy-coordinate projections strictly between those positions and `S`
the common suffix after position `j`.  If the two swapped labels are `a,b`,
the complete terminal discrepancy is exactly

```text
F(pi)-F(pi')=S[Z_b R Z_a-Z_a R Z_b]y,                 (4.4)
```

where `y` is the common prefix endpoint.  Equation (4.4) is the interval state
promised by the locked card.  Replacing it by a sum of `2(j-i)-1` adjacent
commutators and then applying scalar Cauchy--Schwarz is precisely the failed
telescoping attempt: interval length is paid before the global permutation-gap
factor.  The repair must average (4.4) as a whole or exploit its signed
cross-terms.

## 5. Why scalar exchangeable-pair variance cannot close the route

Let `pi'` be obtained by swapping a uniformly chosen unordered pair of update
positions.  The pair `(pi,pi')` is exchangeable and respects the
without-replacement law exactly.

For `h(pi)=r_{pi_1}`, elementary counting gives

```text
Var(h)=||r-r_bar 1||_2^2/n,
(1/2)E(h(pi)-h(pi'))^2
  =2||r-r_bar 1||_2^2/[n(n-1)].                     (5.1)
```

The ratio is `2/(n-1)`, the sharp random-transposition spectral gap, so a
Poincare inversion costs `(n-1)/2`.  This is an analytic factor-`n` control,
not a numerical inference.

For reference, the sharp gap used here has a finite representation-theoretic
verification.  Averaging right multiplication over all transpositions is a
central operator on `S_n`.  On the irreducible indexed by a partition
`lambda`, its eigenvalue is the transposition character ratio

```text
r_lambda=
 [sum_i binom(lambda_i,2)-sum_j binom(lambda'_j,2)]/binom(n,2).
```

Among nontrivial partitions this is maximized by `(n-1,1)`, giving
`r=(n-3)/(n-1)` and gap `1-r=2/(n-1)`; moving any further box out of the first
row only decreases the content sum.  Orthogonal expansion of a Hilbert-valued
function into these finite eigenspaces gives exactly the Poincare coefficient
used in (6.1).  No RPCD covariance spectrum enters this calculation.

The scalar statistic `D_pi` is worse.  On the signed equicorrelation witness,
(3.2) is independent of `pi`, hence `D_pi-D_pi'=0` for every transposition.
At the commuting control `A=I`, every epoch reaches zero and
`D_pi=||x||_2^2` for every order, yet its pair variance is again zero.  A
variance proxy based only on scalar dissipation therefore discards both a
sharp noncommuting family and the easiest commuting family.

The vector endpoint retains more information, but its raw scale still loses
`n`.  For positive equicorrelation with `delta=mu` and `Ax=1`, swapping
positions `i<j` yields the exact terminal difference

```text
(delta^(j-1)-delta^(i-1))(e_a-e_b),
```

whose squared `A`-norm is

```text
2 delta (delta^(i-1)-delta^(j-1))^2.                (5.2)
```

Averaging (5.2) over all unordered pairs is
`4 delta/n+o(delta)`, while `mu||x||_A^2=delta+o(delta)`.
Thus the unamplified vector proxy also loses `n`.  Crucially, its loss matches
the sharp Poincare inverse in (5.1), suggesting that exactly one compensated
use of the transposition gap may survive.

## 6. Repair child: mean plus sharp Dirichlet proxy

Define the Hilbert-valued endpoint

```text
F_x(pi)=T_pi x,              ||.||=||.||_A,
```

and the quadratic proxy

```text
B_A(x)=||E_pi T_pi x||_A^2
       +(n-1)/4 E_{pi,pair}||T_pi x-T_pi' x||_A^2.  (6.1)
```

The sharp Hilbert-valued Poincare inequality on the random-transposition chain
gives

```text
E_pi||T_pi x||_A^2 <= B_A(x).                        (6.2)
```

The route-faithful repair lemma is now the explicit falsifiable statement

```text
There is a universal c_*>0 such that, for every real unit-diagonal
SPD A and every x,

B_A(x) <= (1-c_* mu)||x||_A^2.                       (EP)
```

This retains fresh uniform permutations, the paired endpoint discrepancy, and
the exact global transposition constant.  It does not assume independent
coordinate samples and does not replace the vector pair by scalar bounded
differences.

The normalization `c_*<=1` is necessary, not cosmetic.  At `A=I` one epoch
annihilates every vector, so `B_I=0` and `mu=1`; `(EP)` would have the
right-hand side `(1-c_*)||x||_2^2`, which cannot be negative.  Thus the value
`c_*=1` seen in the structured controls is the largest possible universal
constant and has the correct equality case at identity.

The first bad edge of the repair is exactly `(EP)`.  Generic Poincare uses the
slowest permutation mode.  If `pi -> T_pi x` has substantial higher-mode
content, the second term of (6.1) can overestimate its variance; that slack may
consume the RPCD dissipation.  A decisive attack must therefore create a
unit-diagonal SPD family whose endpoint depends strongly on high permutation
modes and show that

```text
inf_x [||x||_A^2-B_A(x)]/[mu||x||_A^2] -> 0
```

or becomes negative.  No such family was found in this pass.

This objection has an exact spectral form on the permutation space (not on the
RPCD covariance superoperator).  Let `P` be the random-position-transposition
Markov operator and decompose the centered endpoint function into its
orthogonal `P`-eigencomponents `F_lambda`.  Then

```text
E||F||_A^2=||EF||_A^2+sum_lambda ||F_lambda||_A^2,
B_A=||EF||_A^2+sum_lambda w_lambda||F_lambda||_A^2,
w_lambda=(n-1)(1-lambda)/2 >= 1.                       (6.3)
```

Combining (2.1) and (6.3), `(EP)` is equivalent to the stronger surplus
inequality

```text
E D_pi(x)
 -sum_lambda (w_lambda-1)||F_lambda||_A^2
 >= c_*mu||x||_A^2.                                   (6.4)
```

The standard representation has `w=1`, explaining exact compensation on the
equicorrelation obstruction.  The alternating/sign representation has
`lambda=-1` and `w=n-1`; it is the sharpest prospective falsifier.  Its endpoint
component is the explicit alternant

```text
Alt_A(x)=(1/n!)sum_pi sign(pi)T_pi x.                  (6.5)
```

A continuation should therefore maximize
`(n-2)||Alt_A(x)||_A^2` and the other high-mode terms relative to the
dissipation surplus.  This is more specific than a generic random scan and
pinpoints the first remaining implication edge.

### 6.1 Exact high-order structure of the alternating mode

Write `R_i=e_i e_i^T A`, so `U_i=I-R_i`.  Expanding the alternating sum
(6.5) by the subset of selected `R_i` factors gives a useful exact
cancellation.  If two or more labels are omitted, swapping two omitted labels
reverses the permutation sign and leaves the selected product unchanged, so
the term cancels.  If exactly one label is omitted, fixing the order of the
other labels and inserting the omission in the `n` possible slots produces an
alternating sign sum.  It is zero for even `n` and has magnitude one for odd
`n`.  Consequently:

```text
even n: Alt_A contains only products of all n distinct R_i;
odd  n: Alt_A contains only products of n-1 or n distinct R_i.       (6.6)
```

For distinct indices,

```text
R_(i_k)...R_(i_1)
 =e_(i_k) A_(i_k i_(k-1))...A_(i_2 i_1) e_(i_1)^T A.               (6.7)
```

Thus if `A=I+epsilon H` with zero diagonal in `H`, the alternating endpoint
component is `O(epsilon^(n-2))` for odd `n` and
`O(epsilon^(n-1))` for even `n`.  This explains why weak-coupling random
scans do not excite the worst Poincare weight, but it does not control
near-singular matrices whose correlations approach one.

At `n=3`, writing the off-diagonal entries as `u=A_12`, `v=A_13`, and
`w=A_23`, exact symbolic expansion gives

```text
6 Alt_A = [v^2-u^2, u(w^2-1), v(1-w^2);
           u(1-v^2), u^2-w^2, w(v^2-1);
           v(u^2-1), w(1-u^2), w^2-v^2],             (6.8)
det(Alt_A)=0.
```

The checker verifies (6.6)'s insertion coefficients through `n=12` and (6.8)
symbolically.  These identities are exact, but they do not establish the
surplus inequality (6.4).  A deliberately stronger attempted repair,
`E D-||Alt_A x||_A^2 >= ||Ax||_2^2` at `n=3`, is false: the recorded
near-rank-one signed rational matrix is SPD by three exact positive leading
principal minors, while the rational witness `x=(1,-1,1)` gives the strictly
negative quadratic value
`-16113381323284065408122430580636150673265345989286367874143 /
 900000000000000000000000000000000000000000000000000000000`.
That failed inequality must not be used as a route to `(EP)`; it does not
refute `(EP)`, whose right side is only `mu||x||_A^2`.

Indeed, the same rational matrix provides an exact separation between the
failed strong repair and `(EP)`.  Its shifted determinant at `1/550` is
negative, and `trace(A)=3` excludes all three eigenvalues lying below
`1/550`; hence `mu<1/550`.  Exact principal-minor checks give

```text
B_A <= (1-1/550)A <= (1-mu)A.                         (6.9)
```

Thus the strongest high-mode scout found here still satisfies the actual
`c_*=1` compensated proxy.  This is a single E2 finite certificate, not a
uniform high-mode bound.

### 6.2 Direct-C050 multi-epoch fallback

The one-epoch candidate `(EP)` would prove C051 as well as C050.  A strictly
more target-faithful fallback keeps the same coupling but applies it to a fixed
block of `m` fresh independent epoch permutations.  Put

```text
F_x^(m)(pi^1,...,pi^m)=T_(pi^m)...T_(pi^1)x.
```

For each epoch slot `j`, independently transpose two positions in `pi^j` and
call the resulting endpoint `F_x^(m,j)'`.  Tensorization of the same sharp
Poincare inequality gives

```text
E||F_x^(m)||_A^2 <= B_A^(m)(x),
 B_A^(m)(x):=||E F_x^(m)||_A^2
 +(n-1)/4 sum_{j=1}^m E||F_x^(m)-F_x^(m,j)'||_A^2.    (6.10)
```

It would suffice to prove, for one universal fixed integer `m_0` and one
universal `0<c_0<=1`,

```text
B_A^(m_0)(x)<=(1-c_0 mu)||x||_A^2.                    (EP-m)
```

Unlike `(EP)`, `(EP-m)` need not imply the one-epoch certificate C051.  It
targets C050 directly.  If `k=q m_0+r`, `0<=r<m_0`, pathwise nonexpansivity of
the `r` leftover epochs and `q>=k/m_0-1` give

```text
 E||x_k||_A
 <=exp(c_0/2) exp[-c_0 mu k/(2m_0)]||x_0||_A.         (6.11)
```

Thus the nonnormal/incomplete-block prefactor is the universal
`C=exp(c_0/2)`, and the exponent is `c=c_0/(2m_0)`.  This fallback uses fresh
independence explicitly and never substitutes distance of the expected
iterate.

The product-space falsifier is also exact.  On a tensor permutation mode
`(lambda_1,...,lambda_m)`, the Dirichlet coefficient in (6.6) is

```text
sum_j (n-1)(1-r_(lambda_j))/2,
```

where trivial slots contribute zero.  The smallest nonzero coefficient is one,
but modes nontrivial in several epochs or alternating in one epoch have larger
slack.  A fixed-block proof must show that the intervening RPCD products damp
those modes faster than their tensorized weight grows; mere tensorization does
not supply the contraction.

There is an exact recursion that avoids enumerating `(n!)^m` endpoint
sequences.  For a symmetric metric `Q`, define the two linear metric maps

```text
H(Q)=E_pi T_pi^T Q T_pi,
G(Q)=(n-1)E_(pi,pair)(T_pi-T_pi')^T Q(T_pi-T_pi')/4,
M=E_pi T_pi.
```

Conditioning on the perturbed epoch slot gives

```text
B_A^(m)=(M^m)^T A M^m
 +sum_(ell=1)^m H^(ell-1)(G(H^(m-ell)(A))).          (6.12)
```

This is just a bookkeeping identity for the product exchangeable pair; no
spectral decomposition of the covariance superoperator is used.  It also
separates the suffix metric seen by a changed epoch from the averaging over
its prefix.  A proof of `(EP-m)` would still need an order-free inequality for
these maps, so (6.12) is a computational reduction rather than a proof.

Two exact two-epoch controls are included in the checker: `n=3`, `rho=9/10`
equicorrelation (36 permutation sequences), and a genuinely interacting signed
`n=4` Hadamard family with off-diagonal parameters `1/2,1/4,-1/10`, exact
eigenvalues `3/20,17/20,27/20,33/20`, 576 permutation sequences, and 3,456
transposition cases per epoch slot.  Both pass all-principal-minor checks at
`c_0=1`.  They are only E2 finite evidence.  No general `(EP-m)` statement is
claimed.

Using (6.12), the same interacting signed `n=4` family passes exact
all-principal-minor checks at `c_0=1` for `m=1,2,3,4`.  The `m=2` determinant
agrees with direct enumeration, while `m=3,4` avoid enumerating `24^m`
sequences.  The exact minimum generalized gaps divided by `mu` are,
respectively, about `2.4050, 4.0774, 5.1031, 5.7232`; hence this slice does not
show tensorized overcount overwhelming the accumulated contraction.  This is
additional E2 finite evidence only.  In particular,
checking more powers of one matrix does not establish a universal block
length.

The deterministic float64 Hadamard grid over
`{-0.6,-0.3,0,0.3,0.6}^3` contains 85 SPD cases.  Its minimum one-epoch and
two-epoch proxy gaps divided by `mu` are both `1`, attained at `A=I`.
This equality is the necessary constant-sharpness control, not evidence that
the grid covers general matrices; the grid remains E1.

The reproducible 2,000-sample two-epoch scouts on the `n=12` path, cycle,
frustrated cycle, AR(1), and weak matching chain, plus the `n=17` arrow, return
proxy-gap/`mu` values between about `3.726` and `5.641`.  The per-family seeds
are recorded in `falsifier_results.json`.  These are Monte Carlo null results,
not quantified lower bounds.

## 7. Structured controls for `(EP)`

### 7.1 Exact compensation on the locked obstruction mode (E3 draft)

On positive equicorrelation with `Ax=1`, write
`c=[1+(n-1)rho]^{-1}`.  The terminal coordinate assigned rank `t` is exactly

```text
c-delta^(t-1).
```

Thus `pi -> T_pi x` is a random relabelling of one fixed vector.  Its centered
part lies entirely in the standard permutation representation, on which the
random-transposition Poincare gap is exactly `2/(n-1)`.  Consequently (6.2) is
an equality for the high-eigenvalue obstruction mode: the factor `n` lost by
the raw endpoint discrepancy in (5.2) is restored, with no second loss, by the
coefficient `(n-1)/4` in (6.1).  Diagonal sign conjugation gives the same
conclusion for the signed family.

This explains why F1 kills the locked scalar residual lemma but not the
compensated repair.  It is a structured calculation, not a proof of `(EP)`.

The same calculation has an exact without-replacement martingale form.  Reveal
the visited labels successively and let `M_t=E[T_pi x | pi_1,...,pi_t]`.
After diagonal sign conjugation, the label revealed at step `t` receives the
weight `delta^(t-1)` and every unrevealed label has the average `a_t` of the
remaining powers.  If `m=n-t+1`, the `t`th innovation has zero coordinate sum
and exact `A`-energy

```text
E[||M_t-M_(t-1)||_A^2 | prefix]
 =delta*m*(delta^(t-1)-a_(t-1))^2/(m-1).             (7.M)
```

The checker sums (7.M) exactly at `n=17,delta=1/100` and obtains the centered
endpoint variance.  The global transposition Dirichlet term multiplied by
`(n-1)/4` gives the same value.  Thus neither the Doob decomposition nor the
exchangeable-pair decomposition loses a factor `n` on F1; both see only the
standard representation.  For a general matrix the martingale increments
involve averages of the nonadjacent interval discrepancy from Section 4, so
the decomposition is exact but does not itself establish a `mu`-scale gap.

### 7.2 Exact rational finite slices (E2)

The checker exhausts all permutations and all unordered position swaps, forms
the matrix of (6.1), and verifies all principal minors exactly.  At `c_*=1`,
both the Poincare slack

```text
B-E_pi[T_pi^T A T_pi]
```

and the proposed gap

```text
(1-mu)A-B
```

are PSD on each of these slices:

1. signed equicorrelation, `n=5`, `rho=9/10`;
2. hub-leaf star, `n=5`, `q=9/10`, hub-leaf entry `9/20`;
3. unequal signed `2 x 2` blocks, `n=4`, correlations `9/10,-4/5`;
4. unequal signed `2 x 2` blocks, `n=6`, correlations `9/10,-4/5,2/3`
   (720 permutations and 10,800 permutation/pair cases);
5. the interacting signed Hadamard `n=4` family with parameters
   `1/2,1/4,-1/10` and `mu=3/20`.

These are finite certificates, not evidence for all dimensions.

There is also a symbolic `n=3` positive-equicorrelation control for every
`0<=q<1`.  With `mu=1-q`, the two generalized proxy quotients on the symmetric
and transverse subspaces are

```text
R_sym=-q^2(q-1)(2q^2-5q+5)/3,
R_tr =q^2(q^4+4q^3-10q^2+8q+9)/12.
```

The exact factorizations

```text
q-R_sym=q(2q^4-7q^3+10q^2-5q+3)/3,
q-R_tr =-q(q-1)(q+1)(q^3+4q^2-9q+12)/12
```

are nonnegative on `[0,1]` (for the first polynomial use
`10q^2-7q^3>=3q^2` and `3q^2-5q+3>0`; for the second use
`q^3+4q^2-9q+12>=3`).  Hence `(EP)` with `c_*=1` holds on this continuous
positive `n=3` slice.

The sign-frustrated negative triangle slice is also exact.  Put `q=-a`, `0<=a<1/2`, so
`mu=1-2a`.  Substitution into the same symbolic proxy gives

```text
2a-R_sym=-a(a+2)(2a-1)(a^2+2a+3)/3 >=0,
2a-R_tr =-a(a^5-4a^4-10a^3-8a^2+9a-24)/12 >=0.
```

For the second line, the polynomial in parentheses is negative because
`a^5+9a<24` on `[0,1/2]` and all omitted terms are nonpositive.  Thus the
`c_*=1` proxy holds for every `n=3` equicorrelation.  This remains only a
structured E3 draft.

### 7.3 Analytic signed `2 x 2` block family (E3 draft)

For one block

```text
A_q=[[1,q],[q,1]],       0<=q<1,
```

the two endpoint matrices are

```text
T_+=[[0,-q],[0,q^2]],    T_-=[[q^2,0],[-q,0]].
```

In a global block-diagonal problem with `n` coordinates, the orientation of
this block is a fair bit.  A random position transposition reverses it with
probability

```text
p_n=2(2n-1)/[3n(n-1)].                                (7.1)
```

To see (7.1), condition on its two positions `a<b`.  Exactly
`n-(b-a)` unordered position swaps reverse their order, and the mean of
`b-a` over all pairs is `(n+1)/3`.

Thus the variance part of the proxy is inflated relative to the actual block
variance by

```text
c_n=(n-1)p_n=2(2n-1)/(3n)<4/3.                        (7.2)
```

Writing `M=(T_++T_-)/2`, `Delta=T_+-T_-`, the block of (6.1) is

```text
M^T A_q M + (c_n/4) Delta^T A_q Delta.
```

It is diagonal on `(1,1)` and `(1,-1)`.  For any `1<=c<=4/3`, its generalized
Rayleigh quotients are

```text
R_+(q,c)=q^2(1-q)[c(q+1)-q+1]/4,
R_-(q,c)=q^2(q+1)[c(1-q)+q+1]/4.                      (7.3)
```

Direct factorization gives `R_+(q,c)<=q` and `R_-(q,c)<=q` on
`0<=q<=1`, `1<=c<=4/3`.  Signs are removed by diagonal sign conjugation.
For unequal blocks let `Q=max_b |q_b|`, so `mu=1-Q`; (7.3) yields

```text
B_A <= Q A=(1-mu)A.                                   (7.4)
```

Hence `(EP)` with `c_*=1` holds on every all-dimensional direct sum of signed
`2 x 2` correlation blocks (and isolated coordinates).  This structured proof
does not address cross-block interactions.

### 7.4 Other analytic and numerical controls

- Near-singular signed equicorrelation gives the exact locked-lemma
  counterexample and the matching raw pair scale; it does not refute `(EP)`.
- A symmetry-breaking arrow with 16 leaves and `mu=1/100` has exact
  `D/||r||_2^2=1184088001/2560000000`; its `q->1`, `m->infinity` limit is
  `11/24`, so the equicorrelation `1/n` mechanism is absent.  On the genuinely
  dangerous low-eigenvalue residual `(-4,1,...,1)`, its exact
  `D/(mu||x||_A^2)=7029127201/2560000000`, again with no hit.
- An unequal signed three-block instance exhausts 720 permutations exactly and
  has `D/||r||_2^2=1949/1620`.
- The seeded float64 scout uses seed `14320260825`, 20 random correlation
  matrices for each `n=3,...,7`, and exhaustive permutation/pair averages.  Its
  smallest observed `(1-lambda_max(B))/mu` values range from about `1.257` to
  `1.943`.  This is a null E1 search with no certification tolerance and proves
  nothing generally.
- Additional float64 scouts of path, cycle, autoregressive, weak-frame, and
  weakly coupled signed matching families found no proxy violation.  They were
  used only to choose the analytic block calculation and are not promoted.

### 7.5 Weak-coupling local control (E3 draft)

Fix `n`, a nonzero symmetric `H` with zero diagonal, and a fixed epoch block
length `m`.  For `A_epsilon=I+epsilon H` and sufficiently small positive
`epsilon`, every epoch product satisfies

```text
T_pi(I)=0,                  T_pi(A_epsilon)=O(epsilon).
```

The first identity holds because the `n` coordinate projections at `I` zero
every coordinate exactly once.  The second follows from the finite polynomial
expansion in `epsilon`.  Hence every `m`-epoch endpoint is
`O(epsilon^m)` and its mean-plus-Dirichlet proxy is
`B_A^(m)=O(epsilon^(2m))` in any fixed matrix norm.  Since
`trace(H)=0` and `H` is nonzero, `lambda_min(H)<0`, while

```text
mu(A_epsilon)=1+epsilon lambda_min(H).
```

It follows that the smallest generalized gap divided by `mu` is

```text
lambda_min(A_epsilon^(-1/2)(A_epsilon-B_A^(m))
           A_epsilon^(-1/2))/mu(A_epsilon)
 =1-epsilon lambda_min(H)+O(epsilon^2)>1              (7.5)
```

for sufficiently small positive `epsilon`.  Thus `c_0=1` holds locally along
every fixed weak-coupling direction, for both the one-epoch and fixed-block
proxies.  The neighborhood is not uniform in `n` or `H`; this does not address
near-singular or growing-dimensional families and is not a proof of `(EP)` or
`(EP-m)`.

## 8. Relation to inherited barriers

The repair neither applies a black-box diagonalization of the full covariance
superoperator nor invokes the refuted remaining-frame inverse Bellman
potential C046.  It works on the vector endpoint as a function on `S_n` and
uses a sharp exchangeable-pair identity.

The inherited projection lift controls a symmetrized product on `Sym_n` and
then faces a structured product-gap problem.  `(EP)` is mathematically
different: it bounds one vector endpoint by its permutation mean and
transposition Dirichlet form.  If proved for every `x`, however, (6.2) would
give a one-epoch `A`-energy contraction and therefore would also prove the
stronger sufficient certificate C051.  That is a consequence of `(EP)`, not an
assumption and not an equivalence with C050.

## 9. Route decision and reopen condition

The locked child `(L)` is refuted at its first edge.  Under the portfolio
protocol this generating run does not independently hard-prune its own sealed
route.  The attack certificate should be checked by a different worker.

The representation is retained through repair child `(EP)`.  Its status is
`open/advanced`, not a proof candidate.  The route should be suspended after
this pass unless a continuation is assigned specifically to one of:

1. prove the reverse-energy estimate `(EP)` from the interval discrepancy
   `Z_b R Z_a-Z_a R Z_b`, with no second factor of `n`;
2. construct an exact rational high-permutation-mode family violating `(EP)`;
3. prove `(EP)` on a genuinely interacting extension of the signed block
   family, with constants uniform in the number of blocks;
4. prove or refute `(EP-m)` for one fixed universal block length without
   importing a covariance-spectrum argument.

An independent critic should first reconstruct F1 and verify that it affects
only the locked route-local lemma, not C050.

## 10. Reproducibility

Exact and finite command:

```text
{python} ./verify_exchangeable_route.py
```

Seeded numerical scout:

```text
{python} ./verify_exchangeable_route.py --scan --seed 14320260825 --samples 20
```

Extended structured/Monte Carlo scout:

```text
{python} ./verify_exchangeable_route.py --extended-scan --seed 14320260825
```

Required inherited-identity regressions:

```text
{python} scripts/verify_rpcd_identities.py
{python} scripts/iter6_projection_lift.py
```

The exact command has no tolerance.  The scout uses float64 and no pass/fail
tolerance; its null result remains E1.  The extended scout uses 2,000 samples
per recorded family and a `1e-12` SPD filter only for its deterministic grid.
Full fractions, SPD margins, seeds, cases, and finite counts are in
`falsifier_results.json`.
