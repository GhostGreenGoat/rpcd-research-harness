# Hostile audit: exterior spectral regions

Date: 2026-08-22 (Asia/Shanghai)

Audited source:
`research/iteration6/route_stitch/spectral_geometry_region.md`, especially
Section 1.1 and Section 2b.

Verdict: **PASS for the intended range, with one minor scope correction**.
The two-subunit corollary should explicitly say `n>=3`; `n=2` is true by the
separate direct certificate, but the displayed compression with `N=n-3` is not
defined there.  No mathematical blocker was found for `n>=3`.  This is an
independent hostile reconstruction, not a formal/Lean verification or external
review.

## 1. Exterior ordering and degree

Let the `n-2` eigenvalues other than `lambda_i,lambda_j` have elementary
symmetric polynomials `E_l`.  Then

```text
lambda_i e_(r-1)(hat i)
 =lambda_i[E_(r-1)+lambda_j E_(r-2)],
lambda_j e_(r-1)(hat j)
 =lambda_j[E_(r-1)+lambda_i E_(r-2)].
```

The mixed terms cancel, leaving

```text
(lambda_i-lambda_j)E_(r-1).
```

Thus the degree in (G3) really is `r-1`, not `r-2`.  It is positive for SPD
spectra in the relevant range, so the weakest exterior coefficient is exactly
on the minimum eigenspace.

## 2. Section 1.1: at most two subunit eigenvalues

The trace constraint is essential and is used correctly.  Write the minimum
eigenvalue as `mu<1`, adjoin `y=1` if there is no second subunit eigenvalue, and
hold the sum of the remaining `n-2` eigenvalues fixed.  For a pair `x,z>=1`,

```text
e_k(x,z,rest)=xz E_(k-2)+(x+z)E_(k-1)+E_k.
```

At fixed `x+z`, only the first term varies; because `E_(k-2)>=0`, its minimum
on `x,z>=1` is attained when one member is `1`.  Iterating this exact
two-variable move leaves `n-3` ones and

```text
L=n-mu-y-(n-3)=3-mu-y>=1.
```

For `N=n-3`, direct expansion of the remaining variables gives (G4b).  The
coefficient of `y(3-mu-y)` is nonnegative, so concavity reduces to `y=mu,1`;
the exact comparison

```text
(2-mu)-mu(3-2mu)=2(1-mu)^2
```

selects `y=mu`.  The resulting expression is concave in `mu`, so its minimum
is at `mu=0` or `mu=1`.  At `mu=1`, Vandermonde gives `r/n`.  Reconstructing
the other endpoint gives exactly

```text
n=2m:   E_min(0)/C(n,r)=m/(2m-1)>1/2,
n=2m+1: E_min(0)/C(n,r)
         =(m+1)(4m-1)/[2(2m-1)(2m+1)]>1/2.
```

This proves the stated all-dimensional corollary for `n>=3`, with no
eigenvector symmetry assumption.  Consequently any hostile spectrum outside
the exterior region must indeed contain at least three eigenvalues below one.

## 3. Rank-two realization and derivative

For a rank-two projector `P` with `diag(P)=2/n`,

```text
A=aI-(a-mu)P,  a=(n-2mu)/(n-2)
```

has diagonal `[a(n-2)+2mu]/n=1` and spectrum `mu,mu,a,...,a`.
Such projectors are nonempty for every `n>=3` (for example, use a planar
finite unit-norm tight frame); the theorem is correctly quantified over every
such projector.  Direct differentiation reconstructs (G8), and

```text
B0/A0=(r-1)/(n-r),
1/(n-r)-2/(n-2)<=0 <=> 2r<=n+2.
```

The remaining derivative term is nonpositive.  Hence the rank-two monotonicity
and endpoint `R(1)=r/n` are correct.

### Audit of the later Section 1.2 finite-vertex reduction

The sequential concavity argument is valid and does not lose the constraint on
the compensating high eigenvalue.  If there are `q` subunit eigenvalues in
total, then after compressing the high variables the spectrum has the form

```text
mu, y_1,...,y_(q-1), 1,...,1, L,
L=q+1-mu-sum_j y_j.
```

For every point of the full box `mu<=y_j<=1`, one has

```text
L>=q+1-mu-(q-1)=2-mu>=1.
```

Thus varying any one `y` over its whole interval while compensating in `L`
never leaves the high-eigenvalue domain.  With all other variables fixed,
`y+L` is constant and the only varying term is
`yL e_(k-2)(rest)`, a concave quadratic with a nonnegative coefficient.
Moving that coordinate to an endpoint cannot increase the objective.  Repeating
coordinate by coordinate proves that a minimum lies at a box vertex; variable
coupling through `L` causes no obstruction.

If `p` coordinates, including the distinguished minimum line, end at `mu`,
trace gives `L_p=p+1-pmu`, and direct counting reconstructs (G4h).  The only
minor quantifier clarification is

```text
1<=p<=min(s,n-1),
```

because trace `n` and `mu<1` force at least one compensating eigenvalue at or
above one.  In the intended bounded-inertia regime `s<=n-1`, the source's
shorter `p<=s` notation is harmless.  The `s=3,n=8,p=3,mu=0` endpoint is
indeed `(C(4,3)+4C(4,2))/C(8,4)=28/70=2/5`.

## 4. Section 2b: rank-three quantifiers and endpoints

For a rank-three projector with `diag(P)=3/n`, the same diagonal calculation
gives one on the stated trace line, and real constant-diagonal projectors exist
for all `n>=4` (equivalently by the finite-dimensional Schur--Horn theorem).
Counting zero, one, or two of the other low eigenvalues reconstructs `A3,B3,C3`
in (G10b).

Differentiation with `a'=-3/(n-3)` gives (G10c) exactly.  In particular

```text
d1=2r(r-1)(r-2)(3r-2n-3)
   /[n(n-1)(n-2)(n-3)] <=0,
```

and `d2>=0`.  Since

```text
t=mu/a=mu(n-3)/(n-3mu)
```

is strictly increasing, `d0+d1 t-d2 t^2` is nonincreasing.  The derivative
therefore changes sign at most once, from positive to negative; this permits
an interior maximum but no interior minimum.  The endpoint reduction is valid,
including the small cases `n=4,r=2` and `n=5,r=3` where some coefficients
vanish.

At `mu=0`, independent expansion gives:

```text
n=2m:   R3(0)=m/[4(2m-1)](1+3/(2m-3))^(m-1),
n=2m+1: R3(0)=A3(1+3/[2(m-1)])^m.
```

For the even case, the first four binomial terms minus `4-2/m`, after
`k=m-2`, equal

```text
[3k^4+41k^3+48k^2+12k+4]
 /[2(k+2)(2k+1)^3] >0.
```

For the odd case, the first four terms minus `4+3/(m^2-1)` equal

```text
3m(m^2+13m-20)/[16(m-1)^2(m+1)]>0,  m>=2.
```

Thus both endpoint estimates and all stated `n>=4` quantifiers pass.  Since the
even case has `R3(1)=1/2` but `R3(0)>1/2` and the analytic derivative cannot
create an interior minimum, the claimed strict margin for `0<mu<1` also holds.

## 5. `J2` weakest endpoint

With `L=n-(n-1)mu`, exact substitution gives

```text
f(L)-f(mu)=2mu(n-2)(1-mu)/(n-1)>=0.
```

This is the same as (G15) after cancellation.  Concavity of `f` on
`[mu,L]` therefore makes `mu`, not `L`, the weak endpoint.  The no-gain convex
stitching conclusion is consequently correct.

## 6. Independent exact artifact

```text
scripts/iter6_spectral_geometry_hostile_audit.py
research/iteration6/route_l3/evidence/SPECTRAL_GEOMETRY_HOSTILE_AUDIT.json
```

The script reconstructs the derivative identities, parity endpoint ratios,
rank-three binomial remainders, and the `J2` endpoint gap without importing the
source route's verifier.  It prints `PASS_WITH_SCOPE_CORRECTION`.
