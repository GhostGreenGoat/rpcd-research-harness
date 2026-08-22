# Abstract Schur-envelope lemma and the next adaptive state

Date: 2026-08-22

Status: exact proof draft (E3 pending independent audit).  This note isolates
the reusable mechanism behind `schur_compensation_proof.md`; it is not a proof
of a fourth or general Bellman level.

## 1. Sharp rank-one completion lemma

Let `0<mu<1` and

```text
A=[[1,b^T],[b,C]] >=mu I,
c=C^-1b,
s=1-b^TC^-1b>0.                                         (1.1)
```

Let `q` be strictly positive on the spectrum of `C`, and let `kappa>=0`.
Then the following scalar condition is sufficient:

```text
q(lambda) >= kappa (lambda-mu)(1-mu)
             /[mu lambda(lambda+1-mu)]                    (1.2)
```

for every eigenvalue `lambda>mu` of `C`.  Under (1.2),

```text
boxed: q(C)>=(kappa/s)cc^T.                               (1.3)
```

### Proof

The Schur complement of `A-mu I` gives

```text
sum_(lambda>mu) lambda^2 c_lambda^2/(lambda-mu)<=1-mu,   (1.4)
```

and forces `c_lambda=0` at `lambda=mu`.  Taking reciprocals in (1.2),

```text
kappa/q(lambda)
 <=mu lambda(lambda+1-mu)/[(lambda-mu)(1-mu)]
 =lambda^2/[(lambda-mu)(1-mu)]-lambda.                   (1.5)
```

Therefore

```text
kappa c^Tq(C)^-1c
 <=1-c^TCc=s.                                            (1.6)
```

The rank-one domination criterion for a positive definite matrix proves
(1.3).

## 2. The scalar envelope is sharp

Fix an eigenpair `Cu=lambda u`, `||u||=1`, with `lambda>mu`, and choose

```text
b=sqrt((1-mu)(lambda-mu)) u.                              (2.1)
```

Then `A-mu I>=0` with zero Schur complement.  The new parent still has unit
diagonal whenever `C` does.  Moreover,

```text
c=sqrt((1-mu)(lambda-mu))/lambda u,
s=mu(lambda+1-mu)/lambda.                                 (2.2)
```

Testing (1.3) on `u` gives exactly (1.2).  Hence, for a fixed spectral child
state `q(C)`, (1.2) is not merely a convenient sufficient bound: it is the
sharp condition for uniform domination over all admissible one-coordinate
extensions in each child eigen-direction.

This explains the exact `d=2` barrier.  At `mu=1/4`, `lambda=7/4`, the full
coefficient `kappa=beta=3mu/4` violates (1.2) by `-3/160`, and the saturated
extension is precisely the size-three positive equicorrelation matrix used in
`evidence/EXACT_ROUTE_BARRIERS.json`.

## 3. Exterior/volume interpretation

The scalar `s` is the determinant ratio

```text
s=det(A)/det(C).                                          (3.1)
```

The rank-one inverse defect is

```text
A^-1-e_i e_i^T-L_i^TC^-1L_i
 =(1/s)L_i^Tcc^TL_i.                                     (3.2)
```

Thus (1.3) says that the non-volume child surplus `q(C)` pays for the
directional derivative of the codimension-one volume ratio, not for a scalar
worst-child inverse.  This is the Schur-complement form of the exterior
compensation missing from the volume-only certificate.  The determinant
factor alone remains insufficient (Iteration-5 exact gap `-9/400`); the
spectral surplus controls the derivative direction `c`.

## 4. A viable higher-depth adaptive state

Suppose a later child certificate has the form

```text
P(C)=alpha C^-1+Q(C),       Q(C)>0,                       (4.1)
```

where `Q(C)` need not commute with `C`.  For the actual parent extension,
define the exact recoverable Schur coefficient

```text
kappa(A,i;Q)=s/[c^TQ(C)^-1c]                              (4.2)
```

with the convention `+infinity` if `c=0`.  Then

```text
Q(C)>=[kappa(A,i;Q)/s]cc^T,                               (4.3)
```

and consequently

```text
L_i^TP(C)L_i
 >=alpha(A^-1-e_i e_i^T)
   -(alpha-kappa(A,i;Q))D_i.                              (4.4)
```

Equation (4.2) is the maximal possible coefficient by the rank-one
domination criterion.  Unlike the failed Jensen parallel-sum route, it does
not average inverses before applying the directional test.  At level three,
the scalar envelope proves `kappa>=alpha` for every `d>=3`; at higher levels,
the open task is to control the averaged negative parts
`(alpha-kappa_i)_+D_i` while retaining the anisotropy of `Q(C_i)`.

This is a concrete, Bellman-compatible state for a fourth-level attempt.  It
does not claim closure: `Q(C_i)` is generally non-spectral after the next
lift, so a new multirow or matrix-fractional estimate is still required.
