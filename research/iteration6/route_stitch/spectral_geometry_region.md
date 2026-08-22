# New rank-two/rank-three spectral regions and a no-gain stitching theorem

Date: 2026-08-22 (Asia/Shanghai)

Status: **internal E4 proof candidates** for the at-most-two-subunit,
rank-two, rank-three, and finite-extremal-reduction regions, after an independent hostile reconstruction in
`research/iteration6/route_l3/spectral_geometry_hostile_audit.md`; exact
barriers remain E2.  There is no
Lean/formal or external review.  The argument uses the previously proved
exterior-prefix certificate and is not a proof of the unrestricted
half-depth conjecture.

Let `A` be an `n x n` unit-diagonal SPD matrix, with ordered eigenvalues

```text
mu=lambda_1<=lambda_2<=...<=lambda_n,
r=ceil(n/2).
```

Throughout the exterior discussion assume `n>=3`, and use the convention
`binom(N,j)=0` for `j<0` or `j>N`.  The case `n=2` is immediate from
`J_1=I/2>=(mu/2)A^-1`.

## 1. The exterior certificate has only one spectral bottleneck

The Iteration-5 exterior certificate says

```text
A^(1/2) J_r(A) A^(1/2)
 >= [1/binom(n,r)] A grad e_r(A).                         (G1)
```

Its coefficient on eigenline `i` is

```text
v_i=lambda_i e_(r-1)(lambda_1,...,hat(lambda_i),...,lambda_n)
      /binom(n,r).                                        (G2)
```

For two indices `i,j`, let `E_(r-1)` denote the elementary symmetric
polynomial of degree `r-1` in the other `n-2` eigenvalues.  Direct expansion
gives the exact cancellation

```text
v_i-v_j=(lambda_i-lambda_j) E_(r-1)/binom(n,r).           (G3)
```

Thus the exterior coefficients are ordered exactly like the eigenvalues.
In particular their minimum occurs on the `mu` eigenspace.  Therefore (G1)
proves the half-depth target whenever, for one (equivalently every) minimum
eigenvalue index,

```text
e_(r-1)(lambda_2,...,lambda_n) >= binom(n,r)/2.           (G4)
```

Condition (G4) is a genuine all-dimensional spectral region.  It reduces an
`n`-direction matrix test to one scalar elementary-symmetric inequality.

### 1.1 A broad corollary: at most two subunit eigenvalues

Condition (G4) always holds if at most two eigenvalues of `A` are strictly
below one.  This statement imposes no symmetry on the eigenvectors or on the
eigenvalues above one.

To prove it, fix `lambda_1=mu<1`, put `k=r-1`, and, if necessary, adjoin
`y=1` so that `mu<=y<=1` represents the only other possible subunit
eigenvalue.  All remaining `n-2` eigenvalues are at least one.  Holding their
sum fixed, the pairwise identity

```text
e_k(x,z,rest)=xz e_(k-2)(rest)+(x+z)e_(k-1)(rest)
              +e_k(rest)                                 (G4a)
```

shows that `e_k` is minimized by pushing one of every pair `x,z>=1` to the
endpoint one.  Repeating leaves `n-3` ones and a single eigenvalue

```text
L=3-mu-y.
```

For `N=n-3`, the resulting elementary symmetric polynomial is

```text
E(mu,y)=binom(N,k)+(3-mu)binom(N,k-1)
         +y(3-mu-y)binom(N,k-2).                          (G4b)
```

The last factor is concave in `y`, so its minimum on `[mu,1]` is at an
endpoint.  Moreover

```text
(2-mu)-mu(3-2mu)=2(1-mu)^2>=0,
```

so the worse endpoint is `y=mu`.  Hence it remains to bound

```text
E_min(mu)=binom(N,k)+(3-mu)binom(N,k-1)
           +(3mu-2mu^2)binom(N,k-2).                     (G4c)
```

This is concave in `mu`, so only `mu=0,1` matter.  At `mu=1`, Vandermonde
gives

```text
E_min(1)/binom(n,r)=r/n>=1/2.
```

At `mu=0`, parity gives explicit margins.  If `n=2m,r=m`, then

```text
E_min(0)/binom(n,r)=m/(2m-1)>1/2.                         (G4d)
```

If `n=2m+1,r=m+1`, then

```text
E_min(0)/binom(n,r)
=(m+1)(4m-1)/[2(4m^2-1)]>1/2.                            (G4e)
```

Thus

```text
boxed: #{i:lambda_i(A)<1}<=2
       ==> J_r(A)>=(mu/2)A^-1.                            (G4f)
```

The same calculation gives a useful robustness margin for the exterior
coefficient on the minimum eigenspace.  For even `n=2m`, its excess over one
half is at least

```text
(1-mu)[1+(m-2)mu]/[2(2m-1)].                             (G4f')
```

For odd `n=2m+1`, concavity and the two endpoint values give the uniform
excess at least `1/[2(2m+1)]`.  Hence the region is stable under sufficiently
small spectral perturbations (with the even identity endpoint understood as
the equality case).

This is an all-dimensional spectral region, not merely a two-point-spectrum
family.  Equivalently, it covers every `A` for which the negative inertia of
`A-I` is at most two.  In particular, any counterexample must have at least
three subunit eigenvalues.

For a strict non-two-point diagnostic, take `n=7` and spectrum

```text
(1/10,1/10,1,1,1,1,14/5).
```

The normalized exterior low coefficient is exactly `563/875>1/2`, while
`det(A)/(mu/2)=14/25<1`.  Thus this broad inertia region also extends beyond
the scalar determinant band.

### 1.2 Extremal reduction for a bounded number of subunit modes

The preceding mass-transfer proof gives a more general finite extremal
reduction.  Suppose at most `s` eigenvalues are below one.  After fixing the
minimum eigenvalue, concentrate all eigenvalues above one into a single
coordinate as in (G4a).  If `y` is any remaining subunit eigenvalue and `L`
is the compensating large eigenvalue, varying `y` at fixed `y+L` changes
`e_k` only through

```text
yL e_(k-2)(rest)=y(constant-y)e_(k-2)(rest),
```

a concave quadratic.  Iterating over the low variables shows that the
minimum occurs at a vertex where every one is either `mu` or one.

Consequently it suffices to inspect, for some `1<=p<=min(s,n-1)`, the spectrum

```text
(mu repeated p times,
 1 repeated n-p-1 times,
 L_p=p+1-pmu).                                           (G4g)
```

On a minimum eigenline its exact unnormalized exterior coefficient is

```text
E_(n,p)(mu)=sum_j binom(p-1,j)mu^j
 [binom(n-p-1,k-j)+L_p binom(n-p-1,k-j-1)],              (G4h)
```

with the usual out-of-range binomial convention.  Thus a spectral-inertia
slice can be certified by finitely many one-variable polynomials, without
optimizing over an elliptope.  The proof for `s=2` above verifies the two
polynomials uniformly.  For `s=3`, the `p=3,n=8,mu->0` vertex is precisely
the `2/5` barrier below.  This finite extremal reduction is exact for the
exterior certificate; it says nothing negative about the larger RPCD
matrix.

## 2. Rank-two isotropic low space: an all-`mu`, all-`n` family

Consider the spectrum

```text
lambda_1=lambda_2=mu,
lambda_3=...=lambda_n=a=(n-2mu)/(n-2).                    (G5)
```

This is realized by every matrix

```text
A=aI-(a-mu)P,                                             (G6)
```

where `P` is a rank-two orthogonal projector with constant diagonal `2/n`.
There is a large Gram-frame family of such projectors, not just one
permutation-invariant matrix.

For a minimum eigenline, (G2) divided by `mu` is

```text
R(mu)=a^(r-2)[A0*a+B0*mu],                                (G7)
A0=r(n-r)/[n(n-1)],  B0=r(r-1)/[n(n-1)].
```

Since `a'= -2/(n-2)=-c`, differentiation gives

```text
R'(mu)=a^(r-3){a[B0-A0*c(r-1)]-B0*c(r-2)mu}.              (G8)
```

Moreover

```text
B0-A0*c(r-1)
=A0(r-1)[1/(n-r)-2/(n-2)] <=0,                            (G9)
```

because `2r<=n+2` for `r=ceil(n/2)`.  Hence `R` is
nonincreasing in `mu`, and

```text
R(mu)>=R(1)=A0+B0=r/n>=1/2.                              (G10)
```

Combining (G1)--(G3) proves

```text
boxed: J_r(A) >= (mu/2)A^-1                              (G11)
```

for every matrix (G6), every `0<mu<=1`, and every `n>=3`.
Consequently `H_r>=J_r` and the requested `O(n/mu)` finite-time certificate
hold on this entire rank-two-isotropic-low-space family.

This is strictly beyond the scalar determinant region.  Here

```text
det(A)=mu^2 a^(n-2),
```

so `det(A)>=mu/2` fails for all sufficiently small `mu`.  For `n>=7`, the
generic scalar consequence of the new `L3` theorem is only
`J_3>=3mu A^-1/n`, also below the half target; (G11) uses the half-depth
exterior geometry rather than fixed depth.

The inequality in (G10) is strict for every even `n` when `mu<1`, and for
every odd `n` already at `mu=1`.  Hence by continuity (G4) also contains an
open spectral neighborhood of (G5), not only the exact two-point spectrum.

## 2b. The same conclusion for a rank-three isotropic low space

There is a second all-dimensional family.  For `n>=4`, let

```text
lambda_1=lambda_2=lambda_3=mu,
lambda_4=...=lambda_n=a=(n-3mu)/(n-3).                    (G10a)
```

Equivalently, `A=aI-(a-mu)P` for any rank-three orthogonal projector with
`diag(P)=3/n`.  On a low eigenline the exterior coefficient divided by `mu`
is

```text
R3(mu)=a^(r-3)(A3*a^2+B3*mu*a+C3*mu^2),                  (G10b)

A3=r(n-r)(n-r-1)/[n(n-1)(n-2)],
B3=2r(r-1)(n-r)/[n(n-1)(n-2)],
C3=r(r-1)(r-2)/[n(n-1)(n-2)].
```

Put `c=3/(n-3)`, so `a'=-c`.  Direct differentiation gives

```text
R3'(mu)=a^(r-4)[a^2 d0+mu*a*d1-mu^2 d2],                 (G10c)
d0=B3-A3*c(r-1),
d1=2C3-B3*c(r-2)<=0,
d2=C3*c(r-3)>=0.
```

The inequality for `d1` is equivalent (when `r>2`) to
`3r<=2n+3`, which holds for `r=ceil(n/2)`.  With `t=mu/a`, the bracket divided
by `a^2` is `d0+d1*t-d2*t^2`, a nonincreasing function of `t`.  Moreover
`dt/dmu=(a+c mu)/a^2>0`.  Hence `R3'` changes sign at most once, from positive
to negative.  Thus `R3` has no interior minimum and it suffices to check
`mu=0,1`.

At `mu=1`, `R3(1)=r/n>=1/2`.  At `mu=0`, split by parity.

For `n=2m`, `r=m`,

```text
R3(0)=m/[4(2m-1)] * (1+3/(2m-3))^(m-1).
```

The first four binomial terms exceed `4-2/m`; after subtraction the exact
positive remainder lower bound is

```text
[3k^4+41k^3+48k^2+12k+4]/[2m(2m-3)^3],  k=m-2>=0.
```

This gives `R3(0)>=1/2`.  For `n=2m+1`, `r=m+1`, the required power estimate
is

```text
(1+3/[2(m-1)])^m >=4+3/(m^2-1).
```

Again the first four binomial terms suffice; their exact gap is

```text
3m(m^2+13m-20)/[16(m-1)^2(m+1)]>0,  m>=2.
```

Therefore (G11) also holds for every rank-three constant-diagonal projector
lift (G10a), all `0<mu<=1`, and all `n>=4`.  Its determinant
`mu^3 a^(n-3)` again misses `mu/2` for small `mu`, so this is another genuine
non-determinant region.  As in the rank-two case, strict margins away from
the identity give open spectral neighborhoods.

This particular exterior argument does not extend blindly to rank four.  At
`n=9`, `r=5`, four zero low eigenvalues and five equal high eigenvalues
`a=9/5` give the limiting normalized low coefficient

```text
binom(5,4)(9/5)^4/binom(9,5)=729/1750<1/2.               (G10d)
```

By continuity the exterior certificate misses the target for sufficiently
small positive `mu` on the corresponding rank-four projector lifts.  This is
a barrier to the certificate only, not a counterexample to RPCD or to the
half-depth inequality.

Nor can the broad corollary (G4f) be changed from two to three without an
extra isotropy assumption.  At `n=8,r=4`, the limiting spectrum

```text
(0,0,0,1,1,1,1,4)
```

has, on a zero eigenline,

```text
[binom(4,3)+4binom(4,2)]/binom(8,4)=2/5<1/2.              (G10d')
```

Small positive lifts therefore escape the bare exterior certificate.  The
rank-three result above succeeds because its positive spectrum is isotropic;
it should not be generalized to every matrix with three low modes.

This control has an exact positive-`mu` form.  It is realized by

```text
A_mu=diag(mu I_4+(1-mu)J_4, I_4),
```

whose spectrum is `(mu,mu,mu,1,1,1,1,4-3mu)`.  For a low eigenline, after
clearing the positive factor `binom(8,4)`, the exterior gap to one half is

```text
(1-mu)(3mu^2+19mu-7).                                    (G10d'')
```

It is negative for

```text
0<mu<(sqrt(445)-19)/6 =0.349... .
```

Thus the failure is a finite open interval, not only a formal singular
endpoint.  Again this refutes only the exterior certificate; the exact RPCD
half-depth matrix may contain additional order variance.

More generally, for a fixed low multiplicity `q` and `mu->0`, the normalized
low-line exterior coefficient is exactly

```text
R_(n,q)(0)=binom(n-q,r-1)/binom(n,r)
            *[n/(n-q)]^(r-1).                            (G10e)
```

With fixed `q` and `n->infinity`, `r/n->1/2`, so

```text
R_(n,q)(0) -> e^(q/2)/2^q=(sqrt(e)/2)^q.                 (G10f)
```

Indeed the binomial ratio contributes
`(r/n)(1-r/n)^(q-1)->2^(-q)`, while the high-eigenvalue
factor tends to `e^(q/2)`.  The limit is above one half for `q=3`
(`e^3>16`, already from the first five exponential-series terms) and below
one half for `q=4` (`e<11/4` implies `e^2<8`).  Thus the rank-three/rank-four
transition is the exact fixed-multiplicity asymptotic threshold of the bare
exterior certificate.  This supplies a structural reason, not just the
finite `n=9` diagnostic, for why a growing low spectral layer needs a richer
shorted/order-memory certificate.

## 3. Exact strict witness beyond determinant, `J2`, and fixed `L3`

Take `n=8`, `r=4`, `mu=1/100`, and `a=133/100`.  A rational rank-two
constant-diagonal projector is obtained from eight planar unit vectors made
of two orthonormal bases and their antipodes:

```text
(1,0),(-1,0),(0,1),(0,-1),
(3/5,4/5),(-3/5,-4/5),(-4/5,3/5),(4/5,-3/5).
```

If `U` has these rows divided by two, then `P=UU^T` is an exact rational
projector with `diag(P)=1/4`.  The matrix (G6) is therefore an explicit
rational, unit-diagonal SPD example.

On either low eigenline, the exterior normalized coefficient is

```text
v_low/mu = 270389/400000 > 1/2.                           (G12)
```

In contrast,

```text
det(A)/(mu/2)=2mu a^6 <1,
f_J2(mu)/mu=799/2800<1/2,
(3mu/n)/mu=3/8<1/2.                                      (G13)
```

Thus the new spectral region is not a restatement of any of those three
scalar certificates.

## 4. Why `J2` plus exterior convex stitching gives no extra region

The exact `J2` polynomial lower bound has energy-coordinate eigenvalue

```text
f(lambda)=2lambda(n-lambda)/[n(n-1)].                    (G14)
```

Trace and the spectral floor give
`lambda<=L=n-(n-1)mu`.  Concavity of `f` reduces its minimum on `[mu,L]` to
an endpoint, and

```text
f(L)-f(mu)
=2mu*n(n-2)(1-mu)/[n(n-1)] >=0.                          (G15)
```

Therefore `f`, like `v`, is weakest at the minimum eigenvalue.  If both
`f(mu)<mu/2` and `v_min<mu/2`, every convex combination of the two is still
strictly below the target on that same eigenline.  Conversely, if either
minimum is at least `mu/2`, that certificate alone closes the target.

So a convex spectral mixture of `J2` and the volume/exterior certificate has
**no region beyond their union**.  Adding a scalar determinant or
near-identity coefficient below `mu/2` cannot help for the same reason.  A
successful stitch outside (G4) must use a noncommuting/shorted cross-block
certificate, not scalar spectral weights.

## 5. Necessary conditions and witness localization for a counterexample

Let `a_(n,r)(mu)` be the inherited determinant-tail scalar recurrence

```text
a_(n,r)={mu(1-mu^r)/(1-mu)+mu^r d delta_d(mu)}/n,
d=n-r,
delta_d(mu)=mu^(d-1)[d-(d-1)mu].                          (G16)
```

Any counterexample to `H_r>=(mu/2)A^-1` must now satisfy all of:

```text
n>=7,
lambda_3(A)<1,
a_(n,r)(mu)<mu/2,
e_(r-1)(lambda_2,...,lambda_n)<binom(n,r)/2.              (G17)
```

The first condition uses the independently hostile-audited `L3` theorem,
which closes the half target through `n=6`; the second and third use the
determinant-tail and exterior certificates respectively.

There is also a quantitative localization statement.  If `u` is a unit
energy-coordinate witness, put `p_i=|u_i|^2`, `t=mu/2`, and
`f0=f(mu)`.  Choose a cutoff `tau` for which

```text
g_tau=min{f(tau),f(L)}>t.
```

Since `H_r>=J_2>=F(A)`, a violating witness must obey

```text
sum_(lambda_i>=tau) p_i
 <(t-f0)/(g_tau-f0),                                      (G18)
```

or equivalently must put more than
`(g_tau-t)/(g_tau-f0)` of its mass below `tau`.  Thus any hostile example in
the low-`mu` regime must combine many small eigenvalues with a witness
concentrated on their joint low spectral layer.  This matches, but does not
prove, the need for a full shorted low-space certificate in the boundary-ray
stitching analysis.

## 6. Evidence and reproduction

`verify_spectral_rank2_region.py` constructs the rational `n=8` matrix,
checks (G12)--(G13), the projector identities, and reconstructs the two
parity endpoint polynomials in the rank-three proof.  Its output is
`SPECTRAL_RANK2_EXACT.json`.  The universal arguments are symbolic; the
finite matrix is a regression check, not the source of the quantifiers.
