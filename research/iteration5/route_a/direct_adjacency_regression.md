# Direct adjacency regression: a simpler live dual route

Status: exact general identities (E3 proof draft), an E3 preconditioner
inequality, and an **exactly refuted** final matrix inequality.  The failure is
of this restricted dual feature, not of the RPCD half-constant target.

This is a simplification of `weighted_adjacency_dual.md`.  Keep the same
weighted adjacent-difference matrix `D_pi`, but use the nonsymmetric dual test

```
R_pi=D_pi^T
```

instead of `D_pi^T D_pi`.

## 1. Exact regression certificate

The random-test completion-of-squares identity gives

```
K(B) >= P_B Q_B^{-1} P_B,                                 (A1)
P_B=E[D_pi^T],
Q_B=E[D_pi M_pi M_pi^T D_pi^T].                           (A2)
```

An oriented adjacency has probability `1/n`, so

```
P_B=[(n+1)I-B]/n.                                         (A3)
```

This preconditioner obeys

```
P_B >= mu B^{-1}.                                         (A4)
```

Indeed its normalized eigenvalue is

```
lambda(n+1-lambda)/n.
```

This is concave on the feasible interval
`[mu,n-(n-1)mu]`.  At the lower endpoint it is at least
`mu`; at the upper endpoint, writing `a=(n-1)mu`, the required inequality is

```
(n-a)(1+a) >= n mu,
```

whose left side minus the right side is
`[n+mu(n-1)^2](1-mu)>=0` after expansion.  Thus (A4) is
an exact all-dimensional proof candidate.

## 2. Conditional-covariance defect

Put

```
N_pi=D_pi M_pi.
```

In permutation order, `N_pi` has diagonal one, zero first subdiagonal, and

```
(N_pi)_(pi_k,pi_l)
 =B_(pi_k,pi_l)
  -B_(pi_k,pi_(k-1))B_(pi_(k-1),pi_l),   l<=k-2.          (A5)
```

Thus

```
Q_B=E[N_pi N_pi^T].                                       (A6)
```

The entries in (A5) are conditional-covariance numerators.  They vanish both
at `B=I` and at every signed-rank-one boundary.  Consequently `Q_B=I` on
those two canonical geometries, while `P_B` retains the correct adjacency
mass.

For later algebra, if `E_pi=N_pi-I`, then for `i!=j`

```
E[(E_pi)_ij]
 =[n B_ij-(B^2)_ij]/(2n).                                 (A7)
```

The event behind (A7) is that some `p` is immediately before `i` and `j`
lies before that block; it has probability `1/(2n)` for every distinct triple
`(i,j,p)`.  The diagonal is zero.  The remaining term
`E[E_pi E_pi^T]` is a PSD conditional-covariance triple frame, not discarded
variance.

## 3. The natural closing lemma is false

By (A1), the global sharp half constant would have followed from

```
refuted route target:
Q_B <= (2/mu) P_B B P_B.                                  (A8)
```

The right side is the explicit spectral polynomial

```
(2/(mu n^2)) B[(n+1)I-B]^2.
```

The conjecture looked naturally calibrated:

- on a near-null eigenvalue `lambda=mu`, its limiting allowance is two;
- on high eigenvalues it grows, paying for large conditional-covariance
  variance;
- at identity and signed-rank-one boundaries the defect matrix vanishes.

Exhaustive float64 enumeration through `n=7` found no violation, but the full
positive equicorrelation family exposes a finite exact failure.  Put
`B=mu I+(1-mu)J`, `rho=1-mu`, and `c=rho*mu`.  In a fixed order,
`N=D M` has diagonal one, zero first subdiagonal, and every entry farther below
the diagonal equal to `c`.  Permutation averaging makes `Q` exchangeable.  If
`q_parallel,q_perp` are its ordinary eigenvalues, then

```
tr(Q)=n+c^2(n-1)(n-2)/2,
n q_parallel
 =n+c(n-1)(n-2)
   +c^2(n-2)(n-1)(2n-3)/6,
q_perp=[tr(Q)-q_parallel]/(n-1).                           (A9)
```

Also

```
p_perp=(n+rho)/n,
p_parallel=[n-(n-1)rho]/n.                                (A10)
```

At the rational point `n=20, mu=rho=1/2`, the generalized ratios of the
certificate `P Q^-1 P`, after division by `mu`, are

```
transverse =1681/1585 >1,
parallel   =9261/18985
           =1/2-463/37970 <1/2.                           (A11)
```

Thus (A8) and this direct-adjacency regression are exactly refuted.  The
failure occurs in the parallel direction because a fixed adjacency feature
does not retain the long geometric triangular tail.  It does not refute the
actual `J_s`, `H_s`, `K`, or global half-constant inequalities; indeed the
equicorrelation half-prefix theorem proves the desired statement on this same
matrix.

The surviving dual route must use feature depth growing with dimension, an
exact geometric-tail state, or the richer weighted frame in
`weighted_adjacency_dual.md`; a fixed immediate-adjacency predictor is not
enough.
