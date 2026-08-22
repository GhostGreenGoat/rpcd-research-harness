# Nilpotent half-memory shear and dual variational reduction

Status: exact general identities and an operator-Schur reduction.  The final
averaged multirow estimate remains open.

Fix `q=ceil(n/2)`, one chronological order, its triangular factor `M`, and
the `q`-window inverse `D`.  Put

```
E=DM=I+F,   R=D^TD.                                      (N1)
```

## 1. The defect is square-zero

An entry `F_kj` can be nonzero only if `k-j>q`.  Two nonzero factors in
`(F^2)_k ell` would require

```
k-j>q,   j-ell>q,
```

and hence `k-ell>2q>=n`, impossible for positions in `{1,...,n}`.  Thus

```
F^2=0,   E^-1=I-F.                                      (N2)
```

This gives the exact full inverse and the dual regression test matrix

```
X:=M^-1=(I-F)D,
Y:=M^T R=E^T D=(I+F^T)D.                                (N3)
```

They are pathwise biorthogonal:

```
X^T Y=R.                                                 (N4)
```

Writing

```
K=E_pi[X^TX],   P=E_pi[R],   Q=E_pi[Y^TY],
```

the usual dual certificate is `P Q^-1 P`.  The square-zero structure also
gives the exact error identity

```
V:=E_pi[(X-Y)^T(X-Y)]
 =E_pi[D^T(F^TF+FF^T)D]
 =K+Q-2P.                                                (N5)
```

Equivalently, the two one-sided errors are

```
||Xz-Yz||^2=||FDz||^2+||F^TDz||^2.                      (N6)
```

The regression variational formula and the deterministic choice of
coefficient `I` yield

```
K-PQ^-1P <=V,
PQ^-1P >=K-V=2P-Q.                                      (N7)
```

The last expression is only the tangent inequality
`PQ^-1P-(2P-Q)=(P-Q)Q^-1(P-Q)>=0`; it can be indefinite and does not close
the target.  Its value is conceptual: a successful proof can equivalently
show that the symmetrized local-inverse error `V` consumes at most a fixed
fraction of the exact RPCD energy `K`.

## 2. Exact early/late operator-Schur reduction

Let

```
m=n-q-1.
```

Only the first `m` columns and last `m` rows of `F` can be nonzero.  After
splitting positions into early, middle, and late blocks,

```
F=[[0,0,0],[0,0,0],[G,0,0]].                            (N8)
```

Every early row has seen at most `m-1<q` predecessors, so the early block
of `D` is the **full** inverse `M_E^-1`.  Consequently the primal truncation
error is exactly

```
FD=[0;0; G M_E^-1].                                     (N9)
```

For any unit-diagonal SPD matrix `B` and either chronological orientation,
the coordinate-descent energy identity gives

```
M^-T M^-1 <=B^-1,   M^-1 M^-T<=B^-1.                   (N10)
```

Indeed, for `T=I-M^-1B`,

```
B-T^TBT=B M^-T M^-1B>=0;
```

the second inequality is the same statement for the reversed order.  Thus

```
(G M_E^-1)(G M_E^-1)^T <=G A_E^-1G^T.                  (N11)
```

For one row `g_r`, triangular support makes `g_rM_E^-1` depend only on its
own forgotten prefix `O_r`; the local Schur lemma therefore gives the
sharper diagonal estimate

```
||g_rM_E^-1||^2
 <=g_r A_(O_r)^-1 g_r^T <=1-mu.                         (N12)
```

But summing (N12) loses a factor `m`.  The skew-Hilbert family proves that
the operator norm in (N11) can grow like `log(m)^2` for a fixed order, even
when `mu` is bounded below.  Hence the unresolved statement is precisely a
cross-row, cross-order bound on the off-diagonal part of the Gram matrix in
(N11); scalar Schur residuals cannot supply it.

The dual truncation term has the complementary exact form

```
||F^TDz||^2=||G^T(Dz)_late||^2.                          (N13)
```

Equations (N9) and (N13) are the two pieces that the frozen random-rank
identity balances in the non-adapted model.  In the true process their
dependence on the sliding solve window is the remaining obstruction.

## 3. Falsifiable closure target

A genuinely new sufficient lemma would bound the *sum* of the two adapted
Gram errors in (N6), after all internal ranks are averaged, directly by a
dimension-free multiple of `PAP/mu` (or by a strict fraction of `K`).  It
must use the full permutation distribution: pathwise control, reversal
pairing, and separate scalar row summation are all analytically refuted in
the companion notes.
