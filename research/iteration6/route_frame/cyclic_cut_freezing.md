# Cyclic-cut freezing of the half-window residual

Status: exact random-window/cut representation (E3 proof candidate).  It
freezes both `F` and the whole dual-tail addend `F^TD` conditional on the
cycle, but leaves an interval-overlap covariance problem and a cut-dependent
baseline/cross term.

## 1. Freeze the local solves on a directed cycle

A uniform linear permutation can be generated bijectively by first choosing
a uniform directed cyclic order (modulo rotation) and then a uniform cut.
Fix one such cycle and `q=ceil(n/2)`.  For each label `i`, solve once on the
cyclic ordered window consisting of its `q` immediate predecessors followed
by `i`; call the embedded last inverse row `d_i^circ`.

Put `m=n-q-1`.  The labels outside that cyclic window are precisely the
first `m` successors of `i`.  For a successor `j` at forward cyclic distance
`1<=delta(i,j)<=m`, define the fixed correlation

```
C_ij=d_i^circ A_(window_i,j).                             (C1)
```

For any cut, let `D_cut` be the ordinary linear `q`-window inverse and
`F_cut=D_cut M_cut-I`, embedded in label coordinates.  Then exactly

```
(F_cut)_ij=C_ij 1{j occurs before i after the cut}.       (C2)
```

All other entries vanish.  To prove (C2), a nonzero residual needs a linear
gap larger than `q`; therefore its row lies after the first `q` positions,
where its linear predecessor window is exactly its fixed cyclic window.
Conversely, if a cyclic successor at distance at most `m` wraps across the
cut and occurs before `i`, its linear gap is `n-delta>=q+1`, so it is exactly
a forgotten entry.

Thus the local-solve feature rows in the residual are **frozen conditional
on the cycle**.  The apparent dependence on a sliding early suffix in the
linear representation was partly a coordinate artifact.

## 2. Exact interval-overlap covariance

Identify a cut with one of the `n` cyclic edges.  The indicator in (C2) is
the incidence vector of the forward cut arc from `i` to `j`.  Hence

```
Pr_cut[(F_cut)_ij=C_ij]=delta(i,j)/n,                    (C3)

E_cut[1_(ij)1_(kh)]
 = |Arc(i,j) intersect Arc(k,h)|/n.                      (C4)
```

The four-index mask in (C4) is a Gram kernel of cyclic-arc incidence
vectors, and is therefore positive semidefinite.  This gives a precise
conditional covariance object, rather than a rowwise bound or a heuristic
martingale.

The identity is weaker than the independent-rank formula (G3w): only `n`
rotations are averaged conditional on a cycle, so interval lengths and
overlaps remain.

There is a stronger consequence for the covariance itself.  Since

```
M_cut^T R_cut=E_cut^T D_cut=D_cut+F_cut^TD_cut,
```

and every nonzero row `i` of `F_cut` is late, the row of `D_cut` selected by
that product is exactly the fixed row `d_i^circ`.  Therefore the entire
dual-tail addend is

```
T_cut:=F_cut^TD_cut
 =sum_(i,j) 1_Arc(i,j)(cut) C_ij e_j(d_i^circ).           (C5)
```

Thus `T_cut`, not only `F_cut`, is a fixed matrix-valued arc-mask process.
The cut dependence left in `Q=E[(D_cut+T_cut)^T(D_cut+T_cut)]` occurs only
in the baseline `D_cut` and its cross term with (C5).

For a test vector `z`, arcs ending at a fixed successor `j` are nested.  If
`i=j-delta` in cyclic notation and
`a_delta=C_(j-delta,j)d_(j-delta)^circ z`, then exact cut counting gives

```
E_cut||T_cut z||^2
 =(1/n)sum_j sum_(s=1)^m (sum_(delta=s)^m a_delta)^2.     (C6)
```

This is a concrete operator-valued Copson/Hardy form.  Its norm is not
dimension-free for arbitrary coefficients, so a closure must combine it
with the local-solve Gram/Bessel constraints and the random choice of the
cycle; applying a generic scalar Hardy bound would reintroduce a factor of
`n`.  Nevertheless (C5)--(C6) eliminate one major false barrier: no
comparison of unrelated moving solve rows is needed in the covariance tail.

`scripts/verify_cyclic_cut_freezing.py` checks (C1)--(C6) for exact rational
matrices and every cut of finite cycles.
