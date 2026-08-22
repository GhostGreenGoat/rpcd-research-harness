# Higher Bellman closure: adaptive square state, subsets, and SOS barriers

Date: 2026-08-21 (Asia/Shanghai)

Status: the weighted level-two result is internal E4 after an independent
hostile audit; other proof candidates are labelled E3, finite hostile
searches are E1, and strict rational route counterexamples are E2.  No claim
here has formal-assistant or external validation.  The universal half-depth
RPCD inequality remains open.

## 1. Weighted Bellman target

For a unit-diagonal `m x m` SPD matrix `A`, put
`mu=lambda_min(A)` and let `J_t(A)` be the exact decrease matrix for a
uniform ordered prefix of `t` distinct coordinates.  Define

```
C_t(A)=J_t(A)-(1/2)J_{t-1}(A).
```

The hierarchy

```
C_t(A) >= [(t+1)mu/(2m)]A^-1                              (W_t)
```

would inductively imply `J_t>=(t mu/m)A^-1` through half depth.  The
determinant-seeded Bellman hierarchy satisfies `H_t>=J_t`, so this stronger
prefix statement would also imply the requested `H_t` certificate.  The
level-two case is proved in `weighted_prefix_sos.md`.  This note develops a
matrix state for the next target

```
C_3(A) >= (2mu/m)A^-1.                                    (W_3)
```

All third-level formulas below assume `m>=3`; dimensions one and two are
trivial lower-depth cases.

If proved, `(W_3)` would settle the desired half-prefix certificate through
dimension six.

## 2. Adaptive matrix-state lift

Let

```
H=A-I,  D=Diag(diag H^2),  E=Diag(diag H^3),
F=H+H^2-D.
```

Both `H` and `F` have zero diagonal.  If coordinate `i` is first, let
`C_i=A_{-i,-i}` and `L_i=[-b_i I]` be its residual lift.  The exact matrix
state retained by lifting the level-two polynomial proof is

```
S(A)=sum_i L_i^T(C_i-I)^2L_i.                             (B1)
```

To expand it, embed the child product as

```
W_i=H-E_iH-FE_i,
```

where `E_i=e_i e_i^T`.  Then

```
S=sum_i W_i^T W_i
 =(m-3)H^2-2H^3+HD+DH+Diag(diag F^2).                    (B2)
```

This identity is exact and was checked independently on rational matrices
in dimensions four and five.  It retains diagonal fourth moments and their
orientation relative to `H`; replacing it by a multiple of an older scalar
state would discard precisely the anisotropy exposed by the Iteration-4
direct-sum barrier.

There is also a useful exact cubic diagonal bound.  In the block
`H=[[0,b_i^T],[b_i,H_i]]`,

```
(H^3)_ii=b_i^T H_i b_i,       (H^2)_ii=||b_i||^2.
```

Interlacing and `tr(C_i)=m-1` put the spectrum of
`H_i=C_i-I` in `[-(1-mu),(m-2)(1-mu)]`.  Therefore

```
-(1-mu)D <= E <=(m-2)(1-mu)D.                            (B2a)
```

This improves the global spectral bound by one dimension and is sharp on
the positive rank-one family.  On its own it still leaves a negative
interior scalar proxy (recorded in `failed_attempts.md`), so it does not
replace the fourth-moment state in (B2).

The level-two proof gives, for a child of dimension `d=m-1`,

```
C_2(C_i) >= P(C_i),
P(C)=[(3d+1)I-4C+2(C-I)^2/(d-1)]/[2d(d-1)].              (B3)
```

Consequently the Bellman identity gives `C_3>=L_3`, where

```
L_3=I/(2m)+(1/m)sum_i L_i^T P(C_i)L_i                    (B4)
```

and exact collection of terms yields

```
L_3={4(m-1)(m-2)I-10(m-2)H+8H^2+(3m-14)D-4E
     +2S/(m-2)} / [2m(m-1)(m-2)].                        (B5)
```

The missing universal lemma has now been reduced to the explicit degree-four
matrix inequality

```
L_3(A) >= (2mu/m)A^-1.                                   (B6)
```

Unlike a child scalar floor, (B6) retains the complete square state (B1).
The E1 search in `evidence/ADAPTIVE_STATE_HOSTILE_SEARCH.json` evaluated
17,920 random-rank, signed-rank-one, simplex, and two-block hostile cases for
`3<=m<=12`.
No violation of (B6) was found; the closest cases approach equality near
`A=I`.  This is route-selection evidence only.

There is one exact all-dimensional control for the sufficient state itself.
For `A=(1-a)I+a11^T`, `m>=3`, put `r=m-3`.  When `a>=0`, the transverse gap in
(B6), after removing its manifest positive factor, has degree-three
Bernstein coefficients

```
10(r+1), (3r^2+31r+32)/3,
2(r^2+12r+15)/3, r^2+9r+12,
```

and the parallel gap has degree-four coefficients

```
2(2r+1), (6r+1)/4, (7r+9)/6, (4r+9)/4, r+3.
```

For `a<0`, the parallel gap factors as
`a(a-2)(2a^2-4a+5)/(2m)>=0`; after substituting
`a=-c/(m-1)`, all five Bernstein coefficients for the transverse gap are
polynomials with strictly positive coefficients in `r`.  Thus (B6), not
only the exact `C_3` target, holds on the full positive and negative
compound-correlation family.  The exact coefficient reconstruction is in
`WEIGHTED_PREFIX_EXACT_CHECKS.json`.

## 3. Why a second identical compression fails

The matrices `W_i` satisfy

```
sum_i W_i=R:=(m-2)H-H^2+D.                               (B7)
```

For every fixed output row `j`, the `j`th row of `W_j` is zero.  Rowwise
Cauchy therefore uses only `m-1` terms and proves the sharp generic Bessel
compression

```
S >= R^2/(m-1).                                          (B8)
```

Despite being valid, (B8) is too lossy for `(W_3)`.  On

```
A=(1/100)I+(99/100)11^T,  m=4,
```

substituting (B8) into (B5) gives transverse normalized ratio

```
187276289/400000000
 =1/2-12723711/400000000.                                (B9)
```

The target ratio is `2/m=1/2`.  Thus the natural shallow SOS/Bessel dual
certificate fails exactly.  The residual

```
S-R^2/(m-1)
```

must remain an explicit adaptive state, or be replaced by a richer
direction-sensitive certificate.  This is the same architectural lesson as
`R_2` escaping the range of `R_1`; it is not a counterexample to `(W_3)`.

The obstruction is dimension-uniform, not an isolated four-dimensional
accident.  On `A=mu I+(1-mu)11^T`, the transverse ratio of the compressed
state has the exact boundary limit

```
lim_{mu->0} ratio
 =(3m-1)/[2m(m-1)].                                      (B9a)
```

Its gap to `2/m` is `-(m-3)/[2m(m-1)]`, so it fails for every `m>3`.
Multiplying (B9a) by `m` gives `3/2+1/(m-1)`: the repeated compression
asymptotically retains only the weaker constant `3/2`, with vanishing
surplus `1/(m-1)`.

This suggests a smaller still-open partial target.  Let `tilde L_3` denote
(B5) with `S` replaced by `R^2/(m-1)`.  The E1 search found no violation of

```
tilde L_3 >= (3mu/(2m))A^-1.                              (B9b)
```

On the rank-one boundary its exact surplus over `3/(2m)` is
`1/[m(m-1)]`, so (B9b) is asymptotically calibrated.  If proved, it would
combine with `J_2>=(2mu/m)A^-1` to give
`J_3>=(5mu/(2m))A^-1`, settling the desired half certificate through
dimension five.  At present (B9b) is only a numerically supported fallback,
not a theorem claim.

There is a precise adaptive parallel-sum refinement.  For a fixed output row
`j` and witness `x`, put `u_i=(W_i x)_j`, `i!=j`, and use the two row
features `1,H_ji`.  Define

```
s_j=sum_{i!=j}H_ji,  d_j=sum_{i!=j}H_ji^2,
G_j=[[m-1,s_j],[s_j,d_j]],
Y=Diag(H1)H-(H hadamard F).
```

Then the two feature moments are

```
sum_i u_i=(Rx)_j,        sum_i H_ji u_i=(Yx)_j.
```

Least-squares/Bessel, with the Moore--Penrose inverse at singular rows,
gives the exact adaptive lower state

```
x^T Sx >= sum_j [(Rx)_j,(Yx)_j] G_j^dagger
                         [(Rx)_j,(Yx)_j]^T.               (B10a)
```

This is a legitimate matrix-fractional/parallel-sum lift and avoids the
incorrect Jensen direction from Iteration 4.  It does not close uniformly:
on the all-positive signed-rank-one representative every nonzero row has
`H_ji` constant in `i`, so `G_j` has rank one and (B10a) collapses exactly
to (B8).  Adding any fixed number of row features that are polynomial
functions only of these equal correlations has the same degeneracy.  To
recover the transverse residual on that boundary one needs
coordinate-distinguishing features whose rank grows with `m`, or one must
retain `S` itself.

## 4. Exterior/subset representation

Let `V=A^(1/2)` and write `V_S` for the columns indexed by a subset `S`.
Conditioning a uniform prefix on its unordered support gives the exact
identity

```
A^(1/2)J_t(A)A^(1/2)
 = average_{|S|=t} V_S K(A_SS)V_S^T.                      (B10)
```

Inserting the local determinant/Gram certificate and summing adjugates
gives the all-dimensional exterior lower bound

```
A^(1/2)J_t(A)A^(1/2)
 >= [1/binom(m,t)] A grad e_t(A).                         (B11)
```

On an eigenline with eigenvalue `lambda_i`, its coefficient is

```
lambda_i e_{t-1}(lambda without lambda_i)/binom(m,t).     (B12)
```

This is an exact polynomial certificate, not a numerical observation.
However it is insufficient by itself: for
`A=(1/10)I+(9/10)11^T`, `m=6,t=3`, its parallel coefficient is exactly
`11/400`, below `mu/2=1/20` by `9/400`.

A second subset shortcut also fails.  If every local triple satisfied

```
K(C)-(1/2)J_2(C) >= (3I-C)/3,                             (B13)
```

then averaging (B13) would produce a simple spectral proof of `(W_3)`.
But for

```
C=[[1,1/2,-2/3],[1/2,1,0],[-2/3,0,1]],
```

whose eigenvalues are `1/6,1,11/6`, the gap in (B13) has witness
`(1,0,-1)` with quadratic value `-11/48`.  Subset-complement compensation
must therefore occur only after averaging and using the global spectral
floor; it cannot be imposed triple by triple.

## 5. SDP/dual-SOS interpretation

Equations (B3)--(B8) define a small invariant SOS cone for the third Bellman
operator.  Its PSD generators are

```
Z_i=Diag(diag(C_i-I)^2)-(C_i-I)^2/(m-2),
sum_i L_i^T Z_iL_i,
S-R^2/(m-1),
A-mu I,
[m-(m-1)mu]I-A.                                          (B14)
```

Indeed,

```
C_3-L_3=[1/{m(m-1)(m-2)}]sum_i L_i^T Z_iL_i >=0.         (B15)
```

The fixed shallow dual choice that keeps only `R^2` is exactly the
compression refuted by (B9).  A viable SDP/SOS certificate must assign a
nonzero matrix-valued multiplier to the orthogonal residual
`S-R^2/(m-1)` or introduce higher conditional frames.  Treating that
residual as a scalar is not an innocent relaxation.

The independent dual audit supplies a complementary barrier.  For the
fixed-adjacency feature `R_pi=D_pi^TD_pi`, positive equicorrelation gives

```
c_parallel ~3/[n rho(1-rho)],                             (B16)
```

so no dimension-uniform finite regression constant exists.  By contrast,
the half-linear-memory feature survives a complete hostile audit on the
positive-equicorrelation family and yields a finite coefficient larger than
`mu/4`.  This does not prove the general case, but it confirms that the
required SOS/dual state must grow with depth or memory rather than use fixed
shallow Bessel features.

## 6. What this iteration establishes

1. **Internal E4 result:** the all-dimensional weighted level-two inequality
   `J_2-J_1/2>=(3mu/(2m))A^-1` passed an independent hostile audit.  It has
   no formal-assistant or external validation.
2. **Exact adaptive closure:** formulas (B1)--(B5), reducing level three to
   the explicit matrix inequality (B6).
3. **Structured E3 result:** `(W_3)` holds on the full positive and negative
   compound-correlation family (see `weighted_prefix_sos.md`).
4. **Exact hostile barriers:** per-stage uniform gain, child scalarization,
   volume-only subsets, local triple scalarization, and repeated row-square
   compression all fail.  None refutes the RPCD target.
5. **Open point:** prove (B6), or find a new counterexample to it.  A proof
   would close `(W_3)` and the desired half certificate through dimension
   six, but iterating the same construction to general half depth would
   still require an adaptive hierarchy of the residual states in (B14).
