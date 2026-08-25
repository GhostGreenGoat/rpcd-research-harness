# Locked adaptive-Bellman route: audit, direct-C050 repair, and cone duality

## Status and evidence discipline

This is a cumulative development of the immutable statement-first route card
`R100-l0-adaptive-bellman-capture`, whose SHA-256 is
`6f6c32dc47396bd06e660d29895af2df800f8e2ae9103809b8a8fe1918e5c2e0`.
The card was not modified.  General identities and conditional implications below are proof
drafts (at most E3) from this run and have not received a different-run hostile audit.  Exact
rational instances are finite verification (E2).  No unrestricted claim C050 or C051 is proved.

Throughout, `A` is a real unit-diagonal SPD `n` by `n` matrix,
`mu=lambda_min(A)`,

```
U_i = I-e_i e_i^T A,
T_pi = U_(pi_n)...U_(pi_1),
```

and every epoch uses a fresh independent uniform permutation.  Define the covariance map and its
adjoint by

```
M(X)  = avg_pi T_pi X T_pi^T,
M*(P) = avg_pi T_pi^T P T_pi.
```

The adjoint notation is used only to keep metric pullbacks and covariance propagation distinct.

## 1. First bad edge: the frozen Bellman capture is exactly K(A)

Let `r=Ax`.  One coordinate update has

```
r' = (I-Ae_i e_i^T)r,
||x'||_A^2 = ||x||_A^2-r_i^2.                            (1.1)
```

Fix a chronological order `pi=(pi_1,...,pi_n)`.  Let `z_s` be the selected residual just before
updating `pi_s`, let `P_pi r=(r_(pi_1),...,r_(pi_n))`, and let

```
(L_pi)_(s,t) = A_(pi_s,pi_t)  for t<=s, and 0 for t>s.
```

The residual recursion is triangular:

```
z_s + sum_(t<s) A_(pi_s,pi_t) z_t = r_(pi_s),
z = L_pi^(-1) P_pi r.                                   (1.2)
```

Summing (1.1) along the order gives the exact capture

```
sum_s z_s^2
 = r^T P_pi^T L_pi^(-T)L_pi^(-1)P_pi r.                 (1.3)
```

Therefore the frozen Bellman recursion unrolls to

```
H_[n] = avg_pi P_pi^T L_pi^(-T)L_pi^(-1)P_pi = K(A),    (1.4)
```

with the same triangular orientation as
`avg_pi (M_pi M_pi^T)^(-1)`.  In particular,

```
M*(A) = A-A H_[n] A = A-A K(A) A.                       (1.5)
```

The locked core candidate `H_[n] >= eta mu A^(-1)` is thus precisely the stronger C051
certificate in residual coordinates.  Its transfer to C050 is correct, but its universal existence
is the first unsupported edge.  The within-epoch state is adaptive during its computation but
collapses at the boundary to a single fixed-`A` one-epoch energy inequality.  This does not refute
the route card or C050; it explains why the card cannot be used as a direct-C050 escape from C051.

The exact script independently checks (1.4) and (1.5) on the rational noncommuting instance in
Section 6.  The inherited C046 inverse-remaining-frame counterexample is not used as if it refuted
(1.4): C046 concerns a different proposed potential.

## 2. Direct repair A: permutation-history quadratic metrics

Let `N=n!`.  For fixed proposed constants `0<c0<1`, `kappa>=1`, put

```
q = 1-c0 mu,       0<q<1.
```

Attach a metric `P_pi` to the permutation used in the immediately preceding epoch.  Define the
common next-history pullback

```
S(P) = (1/N) sum_pi T_pi^T P_pi T_pi.                   (2.1)
```

The proposed history-metric certificate is the finite set of LMIs

```
A <= P_pi <= kappa A                 for every pi,       (H1)
S(P) <= q P_h                        for every h.        (H2)
```

For fixed `A,q,kappa`, these constraints form an exact finite-dimensional SDP feasibility problem.
There are `N*n(n+1)/2` scalar metric variables and `3N` matrix inequalities of order `n`.  The
metrics are selected by observed history; this is not a common quadratic Lyapunov function and does
not assume C051.

### Conditional target-transfer proposition (proof draft, E3 ceiling)

Assume universal `c0,kappa` make (H1)--(H2) feasible for every admissible `A`.  Introduce an
arbitrary initial label `h_0`.  After epoch `k`, let `h_k=pi^(k)` and

```
V_k = x_k^T P_(h_k) x_k,       V_0=x_0^T P_(h_0)x_0.
```

Conditionally on the past through epoch `k-1`, the new permutation is fresh and uniform, so

```
E[V_k | F_(k-1)]
 = x_(k-1)^T S(P) x_(k-1)
 <= q x_(k-1)^T P_(h_(k-1)) x_(k-1)
 = q V_(k-1).                                             (2.2)
```

Iteration, (H1), and Jensen give, for every deterministic initial point,

```
E||x_k||_A^2 <= E V_k <= q^k V_0 <= kappa q^k ||x_0||_A^2,
E||x_k||_A   <= sqrt(kappa) q^(k/2)||x_0||_A
              <= sqrt(kappa) exp(-(c0/2)mu k)||x_0||_A.  (2.3)
```

Thus the certificate would prove C050 with universal `C=sqrt(kappa)` and `c=c0/2`, and with
`n` coordinate updates per epoch.  Equation (2.2) is expectation of the random distance squared,
not the squared norm of the expected iterate.

## 3. Exact semidefinite dual obstruction for the history SDP

For each history `h`, introduce PSD matrices `L_h,U_h,X_h`.  If

```
L_j-U_j+qX_j-(1/N)T_j (sum_h X_h) T_j^T = 0             (3.1)
```

for every `j`, then summing the Frobenius products with the three primal gaps gives the constant

```
sum_h <L_h,P_h-A>
+sum_h <U_h,kappa A-P_h>
+sum_h <X_h,qP_h-S(P)>
= -sum_h <L_h,A> + kappa sum_h <U_h,A>.                 (3.2)
```

Every term on the left is nonnegative under (H1)--(H2).  Consequently PSD rational matrices
`L_h,U_h,X_h` satisfying (3.1) and

```
sum_h <L_h,A> > kappa sum_h <U_h,A>                     (3.3)
```

are an exact finite-dimensional infeasibility certificate.  This is a one-way certificate and does
not rely on a floating-point SDP optimum.  For rational `A,q,kappa`, all stationarity and sign checks
can be performed over the rationals.  No general dual witness was found in this pass.
No direct instance-specific witness of the form (3.1) was found either; the later tail-dual
certificate plus the exact history-to-tail compression gives an indirect finite history
infeasibility result at `q=3/20,kappa=6/5`.

## 4. Exact non-normal prefactor necessity

The history LMIs cannot hide transient growth in the second-moment dynamics.  From (H1)--(H2),

```
M*(A) <= S(P) <= q kappa A.                              (4.1)
```

Also (H2) gives `P_h>=q^(-1)S(P)`, and positivity of `M*` gives

```
M*(S(P)) <= q S(P).                                      (4.2)
```

Combining (4.1)--(4.2), for every integer `m>=1`,

```
(M*)^m(A) <= kappa q^m A.                                (4.3)
```

Hence a necessary metric-comparison factor is

```
kappa >= sup_(m>=1) q^(-m)
         lambda_max(A^(-1/2)(M*)^m(A)A^(-1/2)).          (4.4)
```

Any rational vector `z` with

```
z^T[kappa q^m A-(M*)^m(A)]z < 0                         (4.5)
```

is an exact obstruction to the proposed constants for this route.  It refutes only the bounded
history certificate, not C050.

This interface finds a genuine exact finite obstruction on the rational matrix (6.1).  For
`q=7/50`, `kappa=2`, and `m=11`, the integer ray `z=(-2,4,-3)` gives

```
z^T[2(7/50)^11 A-(M*)^11(A)]z
= -24928476171595089761902606634110545859
  /256000000000000000000000000000000000000000000000 < 0. (4.6)
```

Thus those particular rate/prefactor constants are exactly impossible for every adaptive
history/cone certificate covered by (4.3).  The tiny rational margin explains why it was first
located numerically, but the recorded decision is exact.  It is not an RPCD counterexample: slower
`q` or larger `kappa` remain possible, and C050 asks only for some universal constants.

There is also a direct reason that C050 itself must control a non-normal prefactor.  Coordinate
descent decreases `A`-energy pathwise, so `Z_k=||x_k||_A<=||x_0||_A`.  Therefore a C050 bound
`E Z_k<=C exp(-c mu k)Z_0` would imply

```
E Z_k^2 <= Z_0 E Z_k <= C exp(-c mu k)Z_0^2,
(M*)^k(A) <= C exp(-c mu k) A.                           (4.7)
```

Conversely, a bound in (4.7) implies the expected-distance statement by Jensen with constants
`sqrt(C)` and `c/2`.  This finite-time bridge uses neither C051 nor a bare spectral radius.

## 5. Direct repair B: a cone-dependent max-of-quadratics functional

### 5.1 Every feasible history certificate compresses to two cone facets

The factorial history state is not intrinsically necessary after feasibility has been established.
Given (H1)--(H2), set

```
R=S(P)/q.                                                 (5.1)
```

Equations (4.1)--(4.2) give the one-matrix **tail-majorant SDP**

```
0 <= R <= kappa A,
M*(A) <= qR,
M*(R) <= qR.                                             (T)
```

Consequently `V(X)=max{<A,X>,<R,X>}` contracts by `q`.  Thus every history certificate
automatically yields a two-facet cone certificate.  The history variables may be useful for
constructing `R`, but they do not justify treating `n!` metrics as an unavoidable mathematical
state.

For fixed rational `A,q,kappa`, (T) is an SDP in only one symmetric matrix.  It has a particularly
small exact dual obstruction.  If PSD `L,U,X,Y` satisfy

```
L-U+qX+qY-M(Y)=0,                                        (5.2)
<X,M*(A)> > kappa <U,A>,                                 (5.3)
```

then (T) is infeasible.  Indeed, inner-producting `L,U,X,Y` with, respectively,
`R`, `kappa A-R`, `qR-M*(A)`, and `qR-M*(R)` cancels `R` by (5.2) and leaves the negative
constant `kappa<U,A>-<X,M*(A)>`.  This is the cheapest exact attack interface found in this pass.

It is useful to name the route-local optimization value

```
kappa_tail(A,q)=inf{kappa: there exists R satisfying (T)}. (5.3a)
```

The precise universal edge is whether some fixed `0<c0<1` has
`sup_(n,A) kappa_tail(A,1-c0 mu)<infinity`.  A family of exact dual witnesses whose certified lower
bounds diverge would refute this two-facet lemma while leaving C050 and larger cone closures open.
Equivalently, after the exact normalization `<U,A>=1`, every dual tuple satisfying (5.2) gives the
certified lower bound

```
kappa_tail(A,q) >= <X,M*(A)>.                            (5.3b)
```

This converts a putative dimension-growth obstruction into a rational SDP-dual target rather than
a floating-point optimum.

The converse history reconstruction is not claimed: (T) may hold without any metrics satisfying
(H1)--(H2).  For C050 transfer, (T) alone is sufficient.

A standard resolvent construction shows why (T) is still stronger than the bare target.  If one
already knew

```
(M*)^k(A) <= C q_0^k A       with q_0<q,
```

then

```
R=sum_(k>=1) q^(-k)(M*)^k(A)                              (5.4)
```

satisfies `qR=M*(A)+M*(R)`, hence (T).  But its direct comparison is only

```
R <= C q_0/(q-q_0) A.                                    (5.5)
```

For `q_0=1-a mu` and `q=1-b mu` with fixed `a>b>0`, this loses
`Theta(1/mu)`.  Therefore a Neumann-series synthesis cannot provide the universal `kappa` needed
for C050.  This is a precise failed repair, not a counterexample to a sharper order-theoretic
construction.  A generic Loewner supremum of the normalized powers is unavailable because the PSD
order is not a lattice; the multi-facet maximum below retains those incomparable directions.

### 5.2 General finite-facet cone closure

Let `P_0,...,P_(m-1)` be PSD facets with

```
P_0=A,             P_j <= kappa A.                       (5.6)
```

Fix a row-stochastic routing matrix `W` and impose

```
M*(P_j) <= q sum_l W_(j,l)P_l.                           (5.7)
```

For PSD covariance states define

```
V(X)=max_j <P_j,X>.                                      (5.8)
```

Then (5.6) gives `<A,X><=V(X)<=kappa<A,X>`, while (5.7) gives

```
V(M(X))
=max_j <M*(P_j),X>
<=q max_j sum_l W_(j,l)<P_l,X>
<=q V(X).                                                (5.9)
```

This again implies (2.3).  For fixed `W,q,kappa`, (5.6)--(5.7) is an SDP,
not a bilinear search.  A dual infeasibility witness consists of PSD `L_j,U_j,X_j` and an
unrestricted symmetric multiplier `Y` for `P_0=A` satisfying

```
L_l-U_l+q sum_j W_(j,l)X_j-M(X_l)+1_(l=0)Y=0,            (5.10)
kappa sum_j <U_j,A>-<Y,A> < 0.                          (5.11)
```

Indeed, their inner product with the primal gaps is the negative constant in (5.11).  Equations
(5.10)--(5.11) are an exact finite-facet dual obstruction.

The canonical infinite-facet construction exposes what remains to be compressed.  If (4.3) holds,
put

```
P_j=q^(-j)(M*)^j(A),       j=0,1,... .                   (5.12)
```

Then `0<=P_j<=kappa A`, `M*(P_j)=qP_(j+1)`, and the supremum version of (5.3) is an exact cone
Lyapunov functional.  Conversely its metric comparison gives (4.3).  A finite certificate needs an
exact terminal closure, for example

```
M*(P_(m-1)) <= q sum_l w_l P_l,       w_l>=0, sum_l w_l=1. (5.13)
```

Failure of (5.13) has an immediate PSD, and often rational rank-one, separating ray.  Phase 002
treated a universal bound on the number of facets as the next edge.  Section 11 repairs that
over-strong requirement: C050 needs a universal comparison constant, while an `O(1/mu)` reset
horizon is sufficient.  The corrected edge is a fixed-factor block contraction by such a horizon.

## 6. Analytic falsifier 1: exact noncommuting rational family

Take

```
A = [[1,3/10,0],
     [3/10,1,2/5],
     [0,2/5,1]].                                        (6.1)
```

Its eigenvalues are exactly `1/2,1,3/2`, so `mu=1/2`.  The coordinate updates are genuinely
noncommuting:

```
||U_1U_2-U_2U_1||_F^2 = 1053/5000,
||U_2U_3-U_3U_2||_F^2 = 241/625.                         (6.2)
```

At `q=7/40`, the common fixed-`A` inequality fails exactly:

```
z=(-2,4,-3)^T,
z^T[qA-M*(A)]z = -137/3125,                              (6.3)
det[qA-M*(A)] = -686889/16000000000.                     (6.4)
```

Thus this rate cannot be certified by a single fixed `A` one-epoch metric.

There are two exact adaptive repairs at the same rate.  The literal history metrics use
`kappa=2`; the compressed two-facet certificate has the sharper exact comparison
`kappa=509/500`.

First, for every permutation choose a nonzero `w_pi in ker(T_pi^T)` and set

```
Q_pi = w_pi w_pi^T/(w_pi^T A^(-1)w_pi),
P_pi = A+Q_pi.                                           (6.5)
```

Rank-one Cauchy--Schwarz gives `0<=Q_pi<=A`, so `A<=P_pi<=2A`, and the matched correction is
invisible on the pullback: `T_pi^TQ_piT_pi=0`.  Hence `S(P)=M*(A)`.  For the rational kernel
witnesses recorded in `exact_falsifier_output.json`, all six matrices

```
(7/40)P_pi-M*(A)                                         (6.6)
```

are positive definite by exact Sylvester minors; the smallest listed determinant is
`10899/250000000>0`.

Second, a two-facet cone certificate closes with

```
P_0=A,
P_1=(40/7)M*(A),
W: 0->1, 1->1.                                           (6.7)
```

Exact principal minors show

```
0<=P_1<=(509/500)A,
M*(P_0)=(7/40)P_1,
M*(P_1)<=(7/40)P_1.                                     (6.8)
```

The determinant in the final strict LMI is
`27468213498549/17150000000000000000>0`.  This finite example proves that the adaptive
history/cone mechanisms are mathematically broader than the failed fixed-`A` LMI.  It does not
establish uniform constants over all `A,n`.

As a non-normal regression, (4.3) was checked exactly for this certificate for `m=1,...,8`; every
principal minor of `(509/500)(7/40)^m A-(M*)^m(A)` is nonnegative.  Eight successful powers are a finite
check, not an all-`m` proof (although the exact two-facet proof already implies all powers for this
specific instance).

### 6.1 Connected six-coordinate ladder: adaptive success beyond the fixed facet

To ensure the Section 6 improvement is not an artifact of three coordinates or a disconnected
block, couple two copies of (6.1) by matching edges of weight `1/10`:

```
A_6 = [[1,3/10,0,1/10,0,0],
       [3/10,1,2/5,0,1/10,0],
       [0,2/5,1,0,0,1/10],
       [1/10,0,0,1,3/10,0],
       [0,1/10,0,3/10,1,2/5],
       [0,0,1/10,0,2/5,1]].                             (6.9)
```

Its graph is connected, its unequal edge weights break full permutation symmetry, and its exact
eigenvalues are `2/5,3/5,9/10,11/10,7/5,8/5`, so `mu=2/5`.  All `6!=720` epochs were enumerated
over the rationals.  At `q=1/4`, the fixed facet fails on

```
z=(-1,2,-2,1,-2,2)^T,
z^T[qA_6-M*(A_6)]z = -16791023523/1250000000000.         (6.10)
```

In contrast, with

```
R=4M*(A_6),       kappa=11/10,                           (6.11)
```

all leading principal minors of `R`, `(11/10)A_6-R`, and
`(1/4)R-M*(R)` are strictly positive exact rationals.  Sylvester's criterion therefore proves the
two-facet tail SDP exactly on this connected instance.  This is a second finite demonstration that
the cone repair is strictly broader than the single fixed-`A` metric; it remains E2 and supplies no
all-dimensional constant.

### 6.2 Exact five-phase closure after the first tail self-loop fails

Return to the `n=3` matrix (6.1), but demand the more aggressive exact rate `q=3/20`.  Define the
canonical phase facets

```
P_0=A,
P_(j+1)=q^(-1)M*(P_j),       j=0,1,2,3.                  (6.12)
```

The fixed facet fails on the rational ray `z=(-1,1,-1)`:

```
z^T[qP_0-M*(P_0)]z = -657/50000.                         (6.13)
```

The first canonical tail self-loop also fails on the same ray:

```
z^T[qP_1-M*(P_1)]z = -339047/50000000.                   (6.14)
```

This second failure by itself rejects only the choice `R=P_1`; it is not a dual proof that every
two-facet tail matrix is infeasible.  Nevertheless, continuing the exact phase chain closes:

```
M*(P_j)=qP_(j+1)  for j<4,
M*(P_4)<=qP_4,
0<P_j<=(6/5)A     for j=0,...,4.                         (6.15)
```

Every comparison in (6.15) is certified by positive rational leading principal minors.  Thus
`V(X)=max_(0<=j<=4)<P_j,X>` is an exact five-facet Lyapunov functional at `q=3/20,kappa=6/5`.
All four shorter canonical truncations fail: exact negative principal minors of
`qP_j-M*(P_j)` for `j=0,1,2,3` are, respectively,

```
-2025621/8000000000,       -6639206179/10000000000000000,
-31337609/12000000000,     -28362395399/60000000000000.
```

This finite result demonstrates genuine canonical phase depth.  In fact, an exact dual
certificate proves that no two-facet tail metric can attain the same `q=3/20,kappa=6/5` constants.
Set `L=0` and write the other dual matrices as the following positive rational rank-one sums:

```
U=(5/73)(2,-4,3)(2,-4,3)^T,
X=(296787247287700/522071912478423)(0,2,-1)(0,2,-1)^T
 +(276309626450300/522071912478423)(1,-4,1)(1,-4,1)^T
 +(28251437487400/522071912478423)(2,-3,-1)(2,-3,-1)^T,
Y=(67310843487500/174023970826141)(1,-2,2)(1,-2,2)^T
 +(552078332950000/522071912478423)(2,-3,3)(2,-3,3)^T
 +(542010212500/2383890011317)(3,-4,3)(3,-4,3)^T.            (6.16)
```

An independent exact reconstruction from these terms verifies

```
L-U+qX+qY-M(Y)=0,
<U,A>=1,
<X,M*(A)>-(6/5)<U,A>
  =2528037273317241/174023970826141000 > 0.               (6.17)
```

Thus (5.2)--(5.3) refute (T) at these constants and certify the sharper lower bound

```
kappa_tail(A,3/20)
 >=211356802264686441/174023970826141000
>6/5.                                                    (6.18)
```

For an integer-only check, the least common multiple of all active coefficient denominators in
(6.16) is `522071912478423`.  Multiplying every dual variable by
`522071912478423000` makes every rank-one weight integral and changes the positive gap in (6.17) to
the integer `7584111819951723`; homogeneity leaves stationarity and the contradiction unchanged.

This makes the five-phase maximum strictly better in comparison constant than the optimal
two-facet tail architecture at the same `q`; it still does not establish a uniform phase count as
`n` grows.  The radius-2 and radius-3 integer-ray dual subcones gave null searches before the
radius-4 cone found (6.16).  Those earlier null results were not treated as feasibility evidence.
By the exact history-to-tail compression (4.1)--(4.2), (6.18) also rules out every
permutation-history metric certificate satisfying `A<=P_pi<=(6/5)A` at `q=3/20`.  Hence this is a
strict finite separation between the five-phase max cone and both simpler adaptive architectures,
not merely a failure of the canonical choice `P_1`.  The separation is possible because a cone
facet need only obey `P_j<=(6/5)A`; unlike every history metric, an individual facet need not
dominate `A`, since the maximum already contains `P_0=A`.

The full two-facet SDP does become feasible at a larger comparison constant.  A float64 scout
(seed `20260825`) selected the rational matrix

```
R_alt=[[153/500,3/200,2283/10000],
       [3/200,833/1250,13/625],
       [2283/10000,13/625,4767/10000]].                  (6.19)
```

Zero-tolerance rational Sylvester checks prove

```
0<R_alt<(13/10)A,
M*(A)<qR_alt,
M*(R_alt)<qR_alt.                                        (6.20)
```

Thus the failed canonical `P_1` self-loop does **not** refute the two-facet tail SDP.  It only shows
that selecting the first normalized block power is too rigid.  The five-phase maximum nevertheless
has the strictly sharper certified comparison `6/5`; (6.18) proves that no alternative tail reaches
that boundary, while (6.19)--(6.20) give the upper bracket `kappa_tail<13/10`.  The earlier
seed-`20260825` float64 search of 500,000 bounded tail matrices at `kappa=6/5` found no feasible
point (best terminal eigenvalue `-0.000972542063040333` at tolerance `1e-9`), but it remains E1 and
is not used in this exact conclusion.

The exact resolvent exposes why replacing those facets by their sum is costly.  Solving over the
rationals

```
(qI-M*)R_res=M*(A)                                       (6.21)
```

gives a valid two-facet tail because `qR_res=M*(A)+M*(R_res)`.  However, exact Sylvester minors show
only the recorded comparison `R_res<51A`, while `kappa=50` already fails on
`z=(-2,4,-3)`:

```
z^T[50A-R_res]z = -12670903894/3100918155.               (6.22)
```

Thus, on the same finite instance and at the same rate, the direct resolvent/sum construction has a
comparison factor greater than 50, whereas the five-phase maximum has `kappa=6/5`.  This is an
exact finite demonstration—not merely an asymptotic estimate—of why the max-of-facets cone retains
non-normal/order information that a summed tail can discard.

### 6.3 Exact canonical phase-depth stress

On the same matrix, moving the rational target rate closer to the observed limiting pullback rate
increases the depth of the canonical deterministic-phase construction.  At
`q=147/1000,kappa=5/4`, define `P_(j+1)=q^(-1)M*(P_j)` as before.  For every `j=0,...,7`, the exact
output records a negative principal minor of `qP_j-M*(P_j)`.  In contrast, every principal minor of

```
qP_8-M*(P_8)
```

is positive, and exact leading principal minors prove `0<P_j<(5/4)A` for all `j=0,...,8`.
Therefore the nine-facet chain `0->1->...->8`, `8->8` closes exactly, whereas each of its eight
shorter canonical truncations fails.  This is an exact fixed-dimensional phase-depth stress, not a
lower bound for arbitrary facets and not evidence that depth grows with dimension.  Section 11
clarifies that the target permits phase depth to grow as `O(1/mu)`; what must remain universal is
the metric comparison and the proportionality constant in that horizon.

## 7. Analytic falsifier 2: symbolic near-singular unit-diagonal family

For `0<rho<1`, take

```
A_rho = [[1,rho],[rho,1]],       mu=1-rho.               (7.1)
```

This family approaches singularity as `rho` tends to one.  Let

```
Q_12=[[rho^2,rho],[rho,1]],
Q_21=[[1,rho],[rho,rho^2]],
P_pi=A_rho+Q_pi.                                        (7.2)
```

Both `Q_pi` are PSD, `A_rho-Q_12=diag(1-rho^2,0)`, and
`A_rho-Q_21=diag(0,1-rho^2)`.  Thus `A_rho<=P_pi<=2A_rho`.  Direct symbolic multiplication gives
`T_pi^TQ_piT_pi=0`, and

```
S(P)=M*(A_rho)=s I,       s=rho^2(1-rho^2)/2.            (7.3)
```

The exact boundary for `qP_pi-sI>=0` is

```
q_*(rho)=rho^2[3+rho^2+sqrt(1+14rho^2+rho^4)]/8.         (7.4)
```

In particular `q=rho=1-mu` is feasible for every `0<rho<1`; the exact determinant at `q=rho`
factors as

```
rho^2(rho-1)^2(rho+1)(rho^3+3rho^2+2rho+8)/4 > 0.       (7.5)
```

The sharper boundary has the singular expansion

```
q_*(1-mu)=1-(11/4)mu+(43/16)mu^2+O(mu^3).               (7.6)
```

This history improvement is strict relative to the best fixed `A_rho` LMI throughout the family.
Because `M*(A_rho)=sI`, the fixed-metric threshold is

```
q_fixed=s/(1-rho)=rho^2(1+rho)/2
       =1-(5/2)mu+2mu^2-(1/2)mu^3.                      (7.7)
```

The inequality `q_*<q_fixed` is equivalent to
`sqrt(1+14rho^2+rho^4)<1+4rho-rho^2`; the right side is positive and the exact difference of
squares is

```
8rho(1-rho)(1+rho)>0.                                   (7.8)
```

Thus the bounded history metric improves the leading singular contraction coefficient from `5/2`
to `11/4`.  This is a genuine all-parameter adaptive advantage in dimension two, not a statement
that either coefficient is globally sharp.
Conjugating by `diag(1,-1)` gives the identical result for the negative-correlation line
`[[1,-rho],[-rho,1]]`, including its signed near-singular limit.

Thus this analytic near-singular stress test does not force either the metric comparison factor or
the rate constant to deteriorate in dimension two.

It also does not falsify the frozen C051-equivalent lemma.  The two generalized eigenvalue ratios
of `H_[2]` relative to `mu A_rho^(-1)` are

```
1+rho+rho^2/2,
(1+rho)(1-rho+rho^2/2)/(1-rho),                          (7.9)
```

whose difference (second minus first) is `rho^3/(1-rho)>0`; the minimum is at least one.  This is
an exact null result on a structured family, not evidence for a general theorem.

### 7.1 Symbolic noncommuting near-singular chain

The noncommuting matrix in Section 6 sits in the full symbolic family

```
A_r=[[1,3r/5,0],[3r/5,1,4r/5],[0,4r/5,1]],   0<r<1.     (7.10)
```

Its eigenvalues are exactly `1-r,1,1+r`, hence `mu=1-r`, and both adjacent update commutators are
nonzero for `r>0`.  Put `q=r` and `R=q^(-1)M*(A_r)`.  The exact generator expands every principal
minor of

```
R,                 A_r-R,                 qR-M*(R).      (7.11)
```

For each numerator polynomial it records the complete Bernstein coefficients on `[0,1]`; every
coefficient is nonnegative and every denominator is a positive integer.  Since nonnegative
Bernstein coefficients give nonnegative polynomials on `[0,1]`, and a symmetric matrix is PSD iff
all principal minors are nonnegative, (7.9) proves throughout this parameter interval that

```
0<=R<=A_r,       M*(A_r)=qR,       M*(R)<=qR.            (7.12)
```

In fact `R<=A_r` makes the adaptive tail redundant here:
`M*(A_r)<=qA_r=(1-mu)A_r`.  Therefore this entire fixed-dimensional,
noncommuting, near-singular chain has

```
E||x_k||_(A_r) <= (1-mu)^(k/2)||x_0||_(A_r)
                <= exp(-mu k/2)||x_0||_(A_r).            (7.13)
```

This is an all-parameter `n=3` proof draft with an exact polynomial certificate (E3 ceiling), not an
unrestricted theorem and not evidence that a fixed metric suffices in general.  It is retained as a
hostile control: neither noncommutativity nor the singular limit alone breaks the candidate route.

## 8. Analytic falsifier 3: signed block closure and multiplicative facets

Signed instances are not silently treated as new positive-correlation cases.  If `D` is a diagonal
signature matrix, then

```
A' = DAD,
U_i(A')=D U_i(A)D,
T_pi(A')=D T_pi(A)D.                                    (8.1)
```

Therefore every history or cone certificate conjugates exactly, with the same `q,kappa`.  The
script checks (8.1) for all six orders of the Section 6 chain with `D=diag(1,-1,1)`.

For a block diagonal matrix `A=A_1 direct_sum A_2`, updates in different blocks commute.  A global
uniform permutation induces independent uniform relative orders inside the two blocks, so for
block-diagonal facets

```
M_A^*(P_1 direct_sum P_2)
=M_(A_1)^*(P_1) direct_sum M_(A_2)^*(P_2).               (8.2)
```

This was also checked by exhaustive exact enumeration of all `6!=720` global permutations for the
block sum of the Section 6 chain and its signed conjugate.  Taking all four products of the two
local facets gives a four-facet certificate at the same `q=7/40,kappa=509/500`, and every PSD comparison
is checked by exact principal minors.  More sharply, the tail-majorant form (T) compresses this
product: `R=R_1 direct_sum R_2` and the distinguished facet `A_1 direct_sum A_2` give only two
facets.  If the two blocks have different certified rates, the same argument uses their maximum
`q`; both block inequalities remain valid.  Thus the repair survives one signed, block,
noncommuting, and internally symmetry-broken finite stress case without multiplicative state
growth.

Naive max-facet products would still produce `2^b` facets across `b` blocks, so the automatic tail
compression is substantive.  The finite block success is not an all-dimensional proof that (T)
holds for arbitrary dense matrices.

Combining the exact symbolic chain result (7.13), sign conjugacy (8.1), and block factorization
(8.2) gives an all-dimensional **structured** corollary.  Take any finite direct sum of signed copies
of `A_(r_b)` from (7.10), plus optional identity blocks.  Then

```
mu_global = 1-max_b r_b,
M_A^*(A) <= (max_b r_b) A = (1-mu_global)A.              (8.3)
```

Thus this block/signed/noncommuting class obeys C050 with `C=1,c=1/2`.  The class has arbitrarily
large dimension but deliberately excludes dense cross-block couplings; it is an E3 structured proof
draft, not the unrestricted claim.

### 8.1 Regression against the inherited inverse-potential failure

The inherited C046 barrier gives a genuine RPCD failure of a particular inverse remaining-frame
potential at `n=9,A=(I+J)/2`.  That failed inequality is not an assumption of (T).  On the same
matrix, permutation conjugacy reduces `M*(A)` to two invariant eigenlines.  Exact one-order
trace/total-sum reconstruction gives

```
q=3/4,
[qA-M*(A)]_transverse = 121363/524288,
[qA-M*(A)]_parallel   = 160805/65536.                    (8.4)
```

Both margins are positive, so even the single `A` facet succeeds at this non-sharp test rate.  The
conjugacy shortcut was independently regressed in the script against exhaustive permutation
averaging at `n=3`.  This does not repair the refuted inverse potential; it confirms that the new
tail/cone route does not inherit that particular failure.

## 9. Adaptive-state dimension stress

The full history SDP is not scalable as a search parameterization without symmetry or compression.
With `d=n(n+1)/2` entries per metric, exact counts are:

| n | permutation metrics | scalar metric variables `n! d` | ordered-prefix states | subset states |
|---:|---:|---:|---:|---:|
| 2 | 2 | 6 | 5 | 4 |
| 3 | 6 | 36 | 16 | 8 |
| 4 | 24 | 240 | 65 | 16 |
| 5 | 120 | 1,800 | 326 | 32 |
| 6 | 720 | 15,120 | 1,957 | 64 |
| 7 | 5,040 | 141,120 | 13,700 | 128 |
| 8 | 40,320 | 1,451,520 | 109,601 | 256 |
| 9 | 362,880 | 16,329,600 | 986,410 | 512 |
| 10 | 3,628,800 | 199,584,000 | 9,864,101 | 1,024 |

For a generic `A` there need not be a permutation symmetry that identifies the raw metrics.
However, Section 5.1 proves that *any feasible history certificate* compresses automatically to the
two facets `A,R`; its target state has only `n(n+1)/2` free scalar entries.  The factorial table is
therefore a computational stress on that particular primal search, not a lower bound on Lyapunov
state dimension.  If the two-facet SDP (T) fails, the canonical general cone state (5.12) can still
require a horizon that grows as `mu` tends to zero.  Finite-dimensionality of `Sym_n` alone does not
give positive cone closure because a linear recurrence may have signed coefficients.  The phase-reset
equivalence in Section 11 shows that an `O(1/mu)` horizon is the correct target scale and is not a
dimension-dependent prefactor.

## 10. Smallest reproducible obstructions and route decision

1. **Frozen-card obstruction.**  Equations (1.2)--(1.4) show exactly that the card's terminal lemma
   is C051 in residual coordinates.  This blocks its use as a direct-C050 escape but does not
   refute C050 or C051.
2. **Fixed-metric obstruction.**  Equations (6.3)--(6.4) are the smallest exact witness found in
   this pass that the adaptive certificate can succeed at a rate where the fixed `A` LMI fails.
3. **Prefactor obstruction.**  Equations (4.3)--(4.5) show that every proposed adaptive rate must
   carry a dimension-uniform non-normal prefactor.  A spectral-radius-only statement is
   insufficient.
4. **Compression obstruction.**  The literal permutation SDP is factorial but compresses
   automatically to the two-facet tail SDP (T) after feasibility.  Equations (6.16)--(6.18) show
   that a different five-phase cone can attain constants that (T) cannot attain, already in
   dimension three.  A uniform facet count is not required by C050; Section 11 identifies the
   necessary direct edge as a universal fixed-factor block contraction by horizon `O(1/mu)`.

The locked route should be **branched/deepened**, not declared solved or hard-pruned.  The next
mathematically adjacent edge is:

> prove a fixed-factor block contraction `(M*)^m(A)<=theta A` for some `m<=B/mu`, or construct a
> dense quantified family of exact PSD-dual separators defeating every proposed `B,theta`.  The
> resulting canonical phases reset after `m` epochs and have a universal comparison factor even
> though their count may grow as `1/mu`.

The exact n=2 and n=3 certificates justify continued scouting.  They do not justify promoting C050,
and an exact counterexample to this stronger adaptive certificate would remain route-local.

## 11. Phase-reset repair and corrected direct-C050 edge

The complete proof draft is in `phase_reset_equivalence.md`; this subsection records the route
change.  Fix `theta in (0,1)` and suppose some `m<=B/mu` obeys

```
(M*)^m(A)<=theta A.                                     (11.1)
```

Put `q=theta^(1/m)` and

```
P_j=q^(-j)(M*)^j(A),       j=0,...,m-1.                 (11.2)
```

Pathwise energy monotonicity gives `(M*)^j(A)<=A`.  Therefore every facet is below
`q^(-(m-1))A<=theta^(-1)A`, the transitions are exact until the last phase, and (11.1) closes the
deterministic reset

```
0 -> 1 -> ... -> m-1 -> 0.                              (11.3)
```

The max of the corresponding quadratic energies contracts by `q`, with comparison at most
`theta^(-1)`.  Hence

```
E||x_k||_A <=theta^(-1/2)
              exp(-[-log(theta)]mu k/(2B))||x_0||_A.    (11.4)
```

Conversely, C050 with constants `C,c` and pathwise monotonicity imply
`(M*)^k(A)<=C exp(-c mu k)A`; choosing
`m=ceil(log(2C)/(c mu))` gives (11.1) with `theta=1/2` and
`B=log(2C)/c+1`.  Thus the bounded-horizon block statement is quantitatively equivalent to C050.
This is a direct-C050 proof draft and neither assumes C051 nor makes it equivalent to C050.

For fixed rational data the exact dual obstruction at horizon `m` is a PSD matrix `X` with

```
<X,theta A-(M*)^m(A)><0;                                (11.5)
```

a rank-one `X=zz^T` suffices.  A finite attack on `m<=M` must supply one separator for every
horizon, while a general refutation requires a quantified family for arbitrary proposed `B`.

Two new exact controls passed.  On the noncommuting rational `n=3` chain at `q=3/20`, the reset
determinants are negative for horizons `1,...,8`, but every principal minor is positive at horizon
`9`; the nine facets close as `0->...->8->0` and remain below `(6/5)A`.  On the near-singular line
`A_rho=[[1,rho],[rho,1]]`, `99/100<=rho<1`, the choice
`q=1-(21/8)(1-rho)` has a negative one-epoch fixed-`A` eigenvalue but a positive two-epoch reset.
The latter sign is certified by seven strictly positive exact Bernstein coefficients after
`t=100(1-rho)`.  It gives

```
E||x_k||_A<=sqrt(800/779)exp(-(21/16)mu k)||x_0||_A     (11.6)
```

on that structured family.  These are E2/E3 scoped controls, not C050.

The literal reset list stores `m*n(n+1)/2=O(B n^2/mu)` scalars.  This stress is polynomial rather
than factorial, and it is a representation cost rather than the RPCD update complexity or a lower
bound on necessary state.

## 12. Reproduction

The decisive run is shell-free except for invoking the repository Python runtime:

```
{python} ./exact_adaptive_falsifiers.py \
  --output ./exact_falsifier_output.json
```

No seed is used by the exact generator.  Its decision tolerance is exactly zero: all asserted signs, identities, kernels,
and principal minors use symbolic expressions or rational arithmetic.  The generated JSON states
its finite scope and records every exact margin.

The float64 scouts that selected candidate parameters are separately reproducible as

```
{python} ./scout_adaptive_phase.py \
  --output ./scout_output.json
```

They use seed `20260825` for the sole random search and PSD tolerance `1e-9`; deterministic grids
and all raw margins are recorded.  Their evidence level is E1.  Every candidate used above was
recomputed by the exact generator, so no float64 sign is a decisive claim.

The exact tail-dual separation and its independent reconstruction are reproducible as

```
{python} ./exact_tail_dual_search.py \
  --radius 4 --output ./exact_tail_dual_output.json
{python} ./audit_tail_dual_certificate.py \
  ./exact_tail_dual_output.json
```

Both commands use exact rational arithmetic and tolerance zero.  The search is decisive only when
its dual gap is positive; the audit separately reconstructs every rank-one sum and both operator
orientations from the portable JSON certificate.

The phase-reset checks are reproducible as

```
{python} ./exact_phase_reset.py \
  --output ./exact_phase_reset_output.json
```

They use exact SymPy rationals and symbolic factorization, tolerance zero, and no seed.
