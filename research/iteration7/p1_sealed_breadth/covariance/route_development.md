# T143 covariance-superoperator block-power development

## Status and evidence discipline

This file develops the immutable card `RC-T143-CBP-01`; it does not replace
that card.  The card SHA-256 remains
`8b812b514379cc34b952dce069b91d184e0947e45ecb417a69e8c8fda400784f`.
The unrestricted block lemma and C050 remain open.  Exact identities and the
analytic family results below are route-local E3 proof drafts (no hostile
audit).  Listed rational instances are E2 finite verifications.  The seeded
scan is E1 only.

## 1. Exact energy-coordinate covariance representation

Let `v_i=A^(1/2)e_i`, `Z_i=I-v_i v_i^T`, and for an update-order permutation
`pi` let

```
P_pi=Z_(pi_n)...Z_(pi_1)=A^(1/2) T_pi A^(-1/2).
```

On `Sym_n` define

```
C(X)=E_pi[P_pi X P_pi^T].
```

For fresh independent epochs and `Y_0=y y^T`, the covariance is
`Y_k=C^k(Y_0)`, and

```
E||x_k||_A^2 = tr(C^k(yy^T)) = y^T (C^*)^k(I)y.       (1)
```

Reversing a uniform permutation preserves its law and
`P_reverse(pi)=P_pi^T`.  Therefore

```
C^*(H)=E[P_pi^T H P_pi]
      =E[P_reverse(pi) H P_reverse(pi)^T]=C(H).          (2)
```

Thus the full covariance superoperator is self-adjoint in Frobenius inner
product.  This removes all Jordan/non-normal power prefactors at the
superoperator level even though every individual epoch product may be very
non-normal.  It does **not** finish the finite-time transfer.

Each `Z_i` is an orthogonal projection, so `P_pi P_pi^T<=I`.  Positivity of
`C` and (2) give the monotone order-unit orbit

```
H_k:=C^k(I),             0<=H_(k+1)<=H_k<=I.             (3)
```

Under the inverse energy-coordinate congruence, (3) is exactly the card's
`(L_A^*)^k(A)` orbit.

## 2. Full `Sym_n` versus reachable covariance semantics

The representation acts on all of `Sym_n`, which is useful for (2), but a
physical deterministic initial point supplies only `Y_0=yy^T`.  Requiring
(1) for every `y` is equivalent by conic linearity to requiring it for every
PSD initial covariance, not for every indefinite matrix.  In the dual this
is precisely the Loewner test

```
H_L=C^L(I) <= I/2.                                      (4)
```

A norm contraction on every indefinite direction of `Sym_n` is stronger
than (4), while an eigenvalue observed only on an indefinite direction is
not by itself a counterexample to (4).  Conversely, (4) does not assert
`C^L(X)<=X/2` for every PSD `X`; it asserts the energy functional bound
`tr(C^L(X))<=tr(X)/2`.

Self-adjoint spectral control alone has the exact but inadequate transfer

```
y^T C^k(I)y
 <= ||C^k||_(F->F) ||I||_F ||yy^T||_F
 = sqrt(n) rho(C)^k ||y||^2.                            (5)
```

The `sqrt(n)` is the first bad edge.  At a putative `rho(C)<=1-c mu`, (5)
needs an extra `(log n)/mu` warm-up.  No inequality in this pass removes that
factor from the full-space Hilbert--Schmidt norm alone.

## 3. Locked block lemma and observability form

The immutable card asks, with `L=ceil(16/mu)`, for (4).  Put

```
D=I-C(I)>=0.
```

Then the exact telescoping identity

```
I-C^L(I)=sum_(j=0)^(L-1) C^j(D)                       (6)
```

shows that the card is a finite observability inequality for the specific
order-unit orbit.  This retains the PSD cone information discarded by (5).
It is not a bare spectral-radius assertion.

## 4. Repair child: one warm-up epoch

A concrete sufficient sublemma, still open in general, emerged from (6):

```
W(A):  H_2 <= (1-mu) H_1,                              (7)
where H_j=(L_A^*)^j(A).
```

In energy coordinates (7) is `C^2(I)<=(1-mu)C(I)`.  It is not C051: C051
requires a fixed-`A` contraction from every initial direction in the first
epoch, while (7) only contracts the covariance/order-unit state reachable
after one epoch.  Equivalently, using `D=I-C(I)`, (7) is

```
C(D) >= mu C(I).                                       (8)
```

This says the first-epoch loss observable is coercive only after filtering
through one fresh epoch.  It is exactly tailored to reachable covariance.
Self-adjointness also makes (8) the orbit-restricted gap statement
`(I-C)H_1>=mu H_1`.  It asks for a gap only on the order-unit image `H_1`,
not an operator inequality `I-C>=mu I` on all of `Sym_n`.

If (7) holds, positivity gives for every `j>=1`

```
H_(j+1)=C^(j-1)(H_2) <=(1-mu)C^(j-1)(H_1)=(1-mu)H_j.
```

For `0<mu<1` and `L=ceil(16/mu)`, this yields

```
H_L <=(1-mu)^(L-1)A <=exp(-mu(L-1))A <=exp(-15)A < A/2.
```

For `mu=1`, unit diagonal and trace `n` force `A=I`, and one epoch is the
zero map.  Thus (7) proves the locked lemma with a large margin and handles
non-normal prefactors by an explicit warm-up, not asymptotics.

The coefficient `1` in (7) is the largest globally meaningful coefficient
in an ansatz `1-c mu`: any `c>1` makes the right-hand scalar negative for
some `mu<1` while `H_1,H_2` remain PSD.  A more informative exact rational
four-direction example in `falsifier_results.json` refutes `c=4/3` already
at `mu=7/10`, where the right-hand scalar is still positive.  The same
example verifies (7) exactly and has diagnostic effective coefficient
`1.2921219505...`.

The seeded all-permutation scout tested (7) on 1,792 matrices in dimensions
3--6, including signed random correlations, blocks, and rank-two through rank-four singular
boundary mixtures, at
`mu in {0.9,0.7,0.5,0.2,0.1,0.03,0.01}`.  No float64 violation was found;
the smallest diagnostic effective coefficient was about `1.0811`.  This is
E1 and not a proof.

## 5. Analytic falsifier A: the card's noncommuting equicorrelation family

Take

```
A_n=(1/n)I+(1-1/n)11^T,       mu=1/n,       n>=2.       (9)
```

The coordinate projections do not commute.  Permutation symmetry keeps the
dual orbit in `span{I,J}`.  For the canonical order and `a=1/n`,
`rho=1-a`, the epoch matrix entries (indices start at one) are

```
(T_n)_(ij)=rho[-a^(i-1)+1_(j<i)a^(i-j)+1_(j=i)].       (10)
```

For `H=alpha I+beta J`, `H'=L_A^*(H)=alpha'I+beta'J` is determined by
`tr(H')` and `1^T H'1`.  If

```
f=||T_n||_F^2, b=||1^T T_n||^2,
c=||T_n 1||^2, d=(1^T T_n 1)^2,
```

then

```
[alpha';beta'] = 1/[n(n-1)]
  [[n f-c, n b-d], [c-f,d-b]] [alpha;beta].            (11)
```

Transforming (11) to the two energy-projector coefficients gives a
nonnegative `2 x 2` cone matrix.  Its row sums, i.e. the two eigenvalues of
`C(I)`, simplify exactly to

```
r_perp = [n^4-2n^3-n^2+2n+2-(n^2+1)n^(-2n)]/(n^2-1)^2,
r_par  = [n-2+(n^2-n+1)n^(-2n)]/(n^2-1).               (12)
```

Direct subtraction gives

```
1-1/n-r_perp
 =(n^2+1)(n^2-n-1+n^(1-2n))/[n(n-1)^2(n+1)^2] >0,

1-1/n-r_par
 =[n(n-1)^2+1-(n^3-n^2+n)n^(-2n)]/[n(n^2-1)] >0.      (13)
```

For the second line, `(n^3-n^2+n)n^(-2n)<1` for `n>=2`; all other signs are
immediate.  Thus this entire noncommuting, dimension-growing, near-singular
family obeys

```
C(I)<=(1-1/n)I,
C^(16n)(I)<=(1-1/n)^(16n)I<=e^(-16)I<I/2.              (14)
```

This is an analytic all-`n` survival of the locked falsifier, not evidence
for arbitrary SPD matrices.  The exact recurrence and powers for
`n=2,3,4,5,8,12,16` are also machine checked.

## 6. Analytic falsifier B: symmetry-breaking singular boundary

Let

```
C = Gram(e_1,e_2,(3e_1+4e_2)/5)
  = [[1,0,3/5],[0,1,4/5],[3/5,4/5,1]],
A_eps=eps I+(1-eps)C,                  0<eps<=1.         (15)
```

The eigenvalues are exactly `eps,1,2-eps`.  The unequal `3/5,4/5`
couplings break permutation symmetry, and the coordinate updates have a
nonzero exact commutator.  Exhaustive averaging of all six permutations
gives `H_1=E[T_pi^T A_eps T_pi]`.  For `0<eps<1`, the leading principal
minors of `(1-eps)A_eps-H_1` factor as

```
(1-eps) p_1(eps)/1250,
(1-eps)^2 p_2(eps)/781250,
eps^2(2-eps)(1-eps)^3 p_3(eps)/1562500.                (16)
```

The Bernstein coefficients of the three polynomials on `[0,1]` are

```
p_1: 1202, 1100, 1175, 1250;
p_2: 722402, 1878125/3, 594625, 2429875/4,
     1958125/3, 4296875/6, 781250;
p_3: 2349910, 16768051/8, 53462569/28, 49662455/28,
     11746750/7, 90439375/56, 44190625/28, 1562500, 1562500.
```

All are positive.  Sylvester's criterion therefore proves the route-local
all-parameter result

```
H_1 <=(1-eps)A_eps.                                    (17)
```

Consequently (15) satisfies the locked block lemma by direct iteration.
The exact finite members `eps=1/2,1/5,1/10,1/25,1/50` were separately raised
to `ceil(16/eps)` dual powers; all Loewner margins were strictly positive.

## 7. Signed and block controls

For every diagonal sign matrix `S`, exact conjugacy gives

```
U_i(SAS)=S U_i(A)S,       T_pi(SAS)=S T_pi(A)S.         (18)
```

Thus every inequality above holds on its full signed-conjugacy orbit.

If `A=A_1 direct_sum ... direct_sum A_m`, a uniform global permutation
induces uniform relative order within every block.  Starting from
`H_0=A`, the dual orbit stays block diagonal and its block marginals are
exactly the separate dual orbits.  Hence the locked lemma is stable under
direct sums of matrices for which it is known, with the global
`mu=min mu_i`.  Cross-block indefinite directions of the full superoperator
are deliberately not substituted for the reachable order-unit orbit.

## 8. First bad edge and current decision

The exact representation and the block-to-C050 transfer are closed.  Both
analytic falsifiers survive with a far stronger one-epoch bound.  The first
bad edge is now precise:

```
Does every unit-diagonal SPD A satisfy C(D)>=mu C(I),
D=I-C(I)?                                               (19)
```

No inherited inverse-frame potential is used; the known counterexample to
that potential does not decide (19).  Bare self-adjoint spectral control
still loses `sqrt(n)` by (5).  The route should be deepened at (19), with an
attack branch seeking an exact rational failure of `(1-mu)H_1-H_2>=0` and a
repair branch retaining a longer reachable chain if two epochs fail.

## 9. Reachable-cone polar form of the repair

The warm edge has an exact formulation that separates the physical covariance
cone from the full PSD cone.  Let

```
K_1(A)=cone{C(yy^T): y in R^n} subseteq PSD_n.          (20)
```

For every `y`, self-adjointness of `C` gives

```
y^T[C(D)-mu C(I)]y
 = <yy^T,C(D-mu I)>_F
 = <C(yy^T),D-mu I>_F.                                (21)
```

Consequently (19) is equivalent to the polar inclusion

```
D-mu I in K_1(A)^*.                                   (22)
```

This is the precise reachable rank-one covariance semantics.  The shortcut
`D>=mu I` tests `D-mu I` against the entire PSD cone and is strictly stronger
as a logical statement; it is the unit-coefficient fixed-energy certificate
and is not assumed here.  Conversely, an indefinite direction of `D-mu I`
would not refute (22) unless a covariance in `K_1(A)` has negative trace
pairing with it.  The next analytic target is therefore (22), not positivity
on all of `Sym_n` and not a bare spectral-radius estimate.

## 10. Continuation falsifiers at the warm edge

Two new analytic slices survived exactly.

First, take the rank-three singular correlation boundary

```
C_3=Gram(e1,e2,e3,(36e1+24e2+23e3)/49),
A_eps=eps I+(1-eps)C_3.                                (23)
```

The couplings are unequal and their squares sum to one.  Thus the exact
eigenvalues are `eps,1,1,2-eps`, so `mu=eps` on `0<eps<1`; coordinate updates
do not commute.  Averaging all 24 permutations and factoring the four leading
principal minors of `(1-eps)A_eps-H_1` leaves residual polynomials whose
Bernstein coefficients on `[0,1]` are all strictly positive.  Sylvester's
criterion proves the stronger slice statement

```
H_1 < (1-eps)A_eps,       every 0<eps<1.               (24)
```

The exact coefficients are in `rank_three_star_exact.json`.  This is an E3
proof draft for (23), its signed conjugates, and covered direct sums only.

Second, take the signed tight-frame rank-two boundary generated by

```
(1,0), (0,1), (3,4)/5, (4,-3)/5.                       (25)
```

For `A_eps=eps I+(1-eps)C_2`, where `C_2` is the Gram matrix of (25), the
eigenvalues are `eps,eps,2-eps,2-eps`.
Exact averaging of all 24 permutations produces leading-minor polynomials of
degrees `16,32,48,64` for `(1-eps)H_1-H_2`.  After removing endpoint factors,
exact Sturm counts find zero residual roots in `(0,1)`, and the rational signs
at `eps=1/2` are positive after restoring the endpoint factors.  Hence

```
H_2 < (1-eps)H_1,       every 0<eps<1                 (26)
```

on this family.  The complete factors, root counts, and signs are in
`rank_two_warm_exact.json`.  Again this is only an E3 analytic slice.

The adversarial scout `attack_warm_start.py` used seed `2026082503` and
all permutations in each tested dimension.  It optimized singular-boundary
Gram families of ranks two through six in dimensions four through seven,
covering high, intermediate, and small `mu`.  Among 14 search configurations
it found no coefficient below one; the smallest diagnostic value was about
`1.0444548306` at `n=5, mu=0.95`.  A separate full-PSD-versus-reachable scout
used seed `2026082604`; it found neither a unit-coefficient one-epoch failure
nor a cone-separation candidate in seven configurations.  Both are float64 E1
null results and supply no general evidence beyond scouting.

## 11. Failed generic symbolic lift and branch decision

The same exact Sturm plan was attempted on the generic unequal signed
rank-two boundary generated by

```
(1,0), (-24,7)/25, (-35,12)/37, (-63,16)/65.           (27)
```

Direct symbolic construction of `H_2` and its principal minors exceeded the
120-second command budget before producing a certificate.  The smaller
tight-frame family (25) closes, but its squared spectral symmetry is precisely
the information discarded by (27).  Thus the exact failed step is not a
negative minor; it is expression swell before the Sturm factors are obtained.
A future repair should reconstruct the minors by exact interpolation or exploit
the rank-two angular state rather than expanding the full polynomial matrices.

No counterexample to (19) was found.  The route remains deepened at the polar
inclusion (22).  If an exact covariance `X=C(yy^T)` with
`tr((D-mu I)X)<0` is found, branch immediately to the longer observability
window

```
sum_(j=1)^m C^j(D) >= gamma C(I)                       (28)
```

for `m=O(1/mu)` and a universal `gamma>0`, rather than changing the locked
covariance-block-power representation.

## 12. Exact repair of the generic unequal signed rank-two timeout

The timed-out family (27) can be reconstructed without symbolic matrix
expression swell.  Regard every matrix entry as a coefficient vector over
`QQ[eps]`.  For `n=4`, every epoch product has degree at most four, while the
actual degrees are

```
deg H_1=8,       deg H_2=16,
deg[(1-eps)H_1-H_2]=16.                               (29)
```

Exact convolution over all 24 permutations gives leading-principal-minor
degrees `16,32,48,64`.  After removing their exact endpoint factors

```
(1-eps)^3,
(1-eps)^6,
eps^2(1-eps)^9,
eps^4(1-eps)^12,
```

the residual degrees are `13,26,37,48`.  Every Bernstein coefficient of each
signed residual polynomial on `[0,1]` is strictly positive; no subdivision is
needed.  Sylvester's criterion therefore proves the route-local slice

```
H_2 < (1-eps)H_1,       every 0<eps<1.                 (30)
```

At `eps=7/10`, all four coefficient-polynomial minor digests exactly equal the
earlier direct rational-matrix digests.  The certificate and its full primitive
coefficient lists are in `generic_rank_two_warm_exact.json`.

Two computational attempts are retained as failed approaches.  Direct
symbolic expansion exceeded 120 seconds in phase 3.  A first coefficient-matrix
implementation then exceeded 600 seconds, and a sparse implementation using a
degree-48 Sturm count also exceeded 600 seconds after the first three minors
had closed.  Sparse scalar-polynomial convolution plus Bernstein positivity
reduced the complete exact check to under one second.  Runtime failures were
never used as sign evidence.

## 13. Higher-rank sign-frustrated cycle attack

To leave the rank-two/tight-frame geometry, take the five rational unit vectors
in `R^4`

```
e1,
(3e1+4e2)/5,
(5e2+12e3)/13,
(7e3+24e4)/25,
(8e1-15e4)/17.                                         (31)
```

Their Gram matrix `C_4` has rank four.  Along the five displayed cycle edges,
the product of the exact inner products is negative, so no diagonal sign
conjugacy makes all cycle edges positive.  Put
`A_eps=eps I+(1-eps)C_4`; then `mu=eps` for `0<eps<1`.  Coordinate updates do
not commute.

Exact coefficient convolution averages all 120 permutations.  The five
leading minors of `(1-eps)H_1-H_2` have degrees
`20,40,60,80,100`; after endpoint factors are removed, every residual already
has positive Bernstein coefficients on `[0,1]`.  Thus

```
H_2 < (1-eps)H_1,       every 0<eps<1,                 (32)
```

on this sign-frustrated rank-four family.  A separate direct rational-matrix
evaluation at `eps=1/2` matches all five coefficient-polynomial minor digests.
This is E3 only for (31), its signed conjugates, and covered direct sums.

## 14. Higher-dimensional subset-dynamic-program attack

For a subset `S` of the coordinate normals, define the average projection
product on a PSD input `X` recursively by

```
F_empty(X)=X,
F_S(X)=|S|^(-1) sum_(i in S) Z_i F_(S\{i})(X) Z_i.      (33)
```

Conditioning on the last update proves that `F_[n](X)=C(X)` exactly.  This is
an algebraic representation of the same locked covariance map, not a sampling
approximation.  A float64 implementation was checked against explicit averaging
of all 120 permutations at `n=5`; the operator-norm errors were
`1.8100582404166803e-15` for `H_1` and `9.609015577781066e-16` for `H_2`, below
the declared `2e-12` regression tolerance.

With seed `2026082504`, (33) tested 252 singular-boundary Gram mixtures in
dimensions `8,10,12`, boundary ranks `2,3,n-1`, and
`mu in {0.95,0.7,0.2,0.03}`.  The violation threshold was `5e-9` and the SPD
tolerance was `5e-11`.  No warm violation occurred.  The smallest diagnostic
effective coefficient was `1.0256742913029933` at `n=12,mu=0.95`, rank two;
its normalized warm margin was `0.024390576737843353` and absolute margin was
`7.947519525089696e-05`.  This entire search is E1: exact conditioning removes
factorial enumeration, not floating-point uncertainty or the finite scope.

An optimized continuation with seed `2026082505` pushed the same recurrence to
`n=14`.  Its best rank-two case at `mu=0.95` has warm effective coefficient
`1.0179516813012113`, but full-PSD one-epoch coefficient
`0.9966983407678359`.  Thus it is an E1 candidate separating the stronger
shortcut `D>=mu I` from the reachable polar test (22), while still satisfying
the warm inequality.  An independent original-coordinate dual recursion,

```
G_S(H)=|S|^(-1) sum_(i in S) U_i^T G_(S\{i})(H) U_i,   (34)
```

conditioned on the first update, reproduced all coordinate-invariant
diagnostics within `1.34e-15`; raw absolute eigenvalue margins were correctly
excluded from the congruence comparison.  This re-evaluation remains float64,
not an exact or interval certificate, so the separation is not promoted above
E1.

## 15. Updated first bad edge and decision

The earlier generic symbolic obstruction is repaired, and the warm inequality
survives a rank-four sign-frustrated cycle.  Neither result describes the full
cone `K_1(A)` in (20).  The first mathematical bad edge remains

```
D-mu I in K_1(A)^* for every unit-diagonal SPD A.        (35)
```

The new subset recursions (33)--(34) are useful for attacks and possibly a subset
Bellman proof, but it currently supplies no dimension-uniform positive
functional on the polar cone.  The decision remains **deepen**, not promote:
the locked block lemma and C050 are open, while the exact family results stop
at E3 pending a different-run audit.

## 16. Reproduction commands

From this portable handoff directory, using the active Python interpreter:

```
{python} ./verify_rank_three_star.py
{python} ./verify_rank_two_warm_family.py
{python} ./attack_warm_start.py
{python} ./attack_reachable_cone.py
{python} ./verify_generic_rank_two_poly.py
{python} ./verify_rank_four_cycle_poly.py
{python} ./attack_subset_warm.py
{python} ./reevaluate_subset_candidate.py
```

The source-run aggregate verifier and broad E1 scout are intentionally omitted
from the curated Git handoff; the exact component verifiers and the retained
targeted subset attack remain reproducible here.

The exact verifiers use zero tolerance and no seed.  The phase-2 numerical
scout uses seed `20260825`, violation tolerance `2e-10`, SPD tolerance
`5e-12`, and superoperator symmetry tolerance `2e-10`.  The continuation warm
and cone scouts use seeds `2026082503` and `2026082604`; their decisive
threshold is `5e-10`.  The subset-DP scout uses seed `2026082504`, violation
tolerance `5e-9`, SPD tolerance `5e-11`, and factorial regression tolerance
`2e-12`.  The optimized continuation uses seed `2026082505` and the independent
formulation match tolerance is `2e-10`.  All numerical outputs remain E1.
