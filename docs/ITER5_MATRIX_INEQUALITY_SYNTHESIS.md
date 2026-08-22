# Iteration 5 synthesis: linear-depth matrix certificates

Date: 2026-08-21.  General status: the normalized RPCD
`O(n/mu log(1/epsilon))` bound remains open for an arbitrary unit-diagonal
SPD matrix.  This iteration produced new audited matrix inequalities,
structured-family complexity bounds, and a substantially narrower generic
blocker.

## 1. Target and finite-time transfer

Let `K(A)` be the exact one-permutation residual-energy decrease matrix.  A
universal certificate

```
K(A) >= c mu A^{-1}                                      (S1)
```

for any numerical constant `c>0` is sufficient; sharp `c=1/2` is not needed
for the requested order.  With fresh independent permutations it gives

```
E||x_t||_A^2 <=(1-c mu)^t||x_0||_A^2,
E||x_t||_A   <=(1-c mu)^(t/2)||x_0||_A.                  (S2)
```

Moreover `||x_t||_A^2/(1-c mu)^t` is a nonnegative supermartingale.  Ville's
inequality therefore gives, with probability at least `1-delta`, the
simultaneous-in-time bound

```
||x_t||_A^2 <=delta^{-1}(1-c mu)^t||x_0||_A^2
```

for every `t`, without a union-bound `log t` penalty.

Thus expected `A`-distance needs
`O((n/(c mu))log(1/epsilon))` coordinate updates.  Euclidean distance still
incurs the usual square-root condition prefactor unless a direct Euclidean
certificate is added.

## 2. New general inequalities

### 2.1 Weighted two-prefix theorem

For every dimension and every unit-diagonal SPD matrix,

```
J_2-(1/2)J_1 >= (3mu/(2n))A^{-1}.                         (S3)
```

The proof uses the exact `J_2` formula, the zero-diagonal row-square lemma
`H^2<=(n-1)Diag(diag H^2)`, and a scalar spectral endpoint argument.  It has
passed an independent hostile reconstruction.  It preserves first-step
surplus, unlike the exactly false statement that every new position supplies
`mu/n` progress.

The live general hierarchy is

```
C_t:=J_t-(1/2)J_{t-1}
   >=[(t+1)mu/(2n)]A^{-1},  t<=ceil(n/2).                 (S4)
```

Level two is (S3).  Level three has survived 12,800 hostile cases and is
proved on the complete equicorrelation interval, but its general matrix SOS
has not closed.

### 2.2 Random path preconditioner

For the adjacent conditional-difference matrix `D_pi`,

```
P=E[D_pi^T D_pi]
 =[(n+1)I-2A+Diag(diag A^2)]/n >=mu A^{-1}.               (S5)
```

This is an audited all-dimensional inequality.  It does not by itself prove
(S1): both the direct and squared fixed-adjacency regression states have
exact equicorrelation obstructions, and the latter certificate decays as
`3/[n rho(1-rho)]` for fixed positive `rho`.

### 2.3 Generic local-inverse Schur residual

Let a row `d` invert the triangular problem on its current coordinate and
the previous `q` coordinates, and let `r` be its forgotten-history defect.
With `sigma=dB_Td^T=2-||d||^2`, Schur complementation gives

```
r B_O^{-1}r^T <=sigma-mu||d||^2 <=1-mu.                  (S6)
```

This is a genuine pathwise matrix residual bound.  The missing generic step
is a frame inequality for many such rows after random-order averaging.
Scalar summation is insufficient: an exact `n=5,q=2` rational example makes
one small old subset capture more than 0.92 of `sigma`, refuting the natural
cardinality damping.

### 2.4 Explicit general near-identity band

For every unit-diagonal SPD matrix, put `theta=n(1-mu)`.  The trace constraint
and triangular Frobenius split give the audited pathwise estimate

```
K(A) >=[1+theta/sqrt(2)]^{-2}mu A^{-1}.                   (S6a)
```

Thus every matrix with `theta<=1` satisfies `K>(mu/4)A^{-1}` and already has
the requested `O(n/mu)` complexity.  The sharper half constant holds when
`theta<=2-sqrt(2)`.  This is a dimension-uniform explicit region, unlike the
compactness-only identity neighborhood.

## 3. Audited structured theorems

1. **Complete equicorrelation first-half curve.**  For every positive or
   negative equicorrelation and every `t<=ceil(n/2)`,
   `J_t>=(t mu/n)A^{-1}`.  This is leaf-free and includes diagonal sign
   conjugates.
2. **Identity neighborhood.**  At each fixed dimension, the whole weighted
   hierarchy (S4) holds simultaneously in a neighborhood of identity.  The
   radius is not uniform in dimension.
3. **Half-linear local-inverse limit.**  Under `rho=c/n` and `q/n->1/2`, the
   positive-equicorrelation dual certificate has transverse limit one and
   parallel limit at least one half.  An all-positive Taylor series proves
   the remaining exponential inequality.  If `q=o(n)`, the parallel limit is
   `(1+c)/(1+c+c^2/3)`, below one half for
   `c>(3+sqrt(21))/2` and tending to zero as `c` grows.  Thus sublinear memory
   cannot retain even a nonsharp universal positive coefficient over this
   feature family; linear memory is necessary.
4. **Finite half-linear certificate.**  For positive equicorrelations and
   `q=ceil(n/2)`, the same dual construction proves

   ```
   K(A) >=(25mu/98)A^{-1} >(mu/4)A^{-1}.                  (S7)
   ```

   This is a genuine finite-time `O(n/mu log(1/epsilon))` result on that
   family, independently audited.

## 4. Counterexample search and sharp families

- Fixed-`mu` differential-evolution attacks covered low-rank and full-rank
  parameterizations through `n=8`; no half-prefix violation was found.
- A symmetry-reduced exchangeable-group Bellman engine reached `n=1000`.
  Its tight two-group satellite family attained about `0.50517`, with the
  bare prefix rather than the determinant leaf carrying the bottleneck.
- For every fixed satellite count, an exchangeable without-replacement
  second-moment formula proves that the limiting satellite-transverse ratio
  stays above one half.  At count two it reduces to the exact expression
  `(8-eta^3)/[8(1+mu)]`.  Larger finite searches continue to approach one
  half from above, so this is an extremal-family candidate rather than a
  counterexample.  The other invariant sector and satellite counts growing
  with dimension remain open.

All finite positive searches are null evidence only.  They do not replace a
quantified proof.

## 5. Failed routes retained as regression tests

1. Sharp one-epoch coefficient two, bare Jensen/Kadison, reverse-word and
   complementary-prefix pathwise pairings were already closed in Iteration 4.
2. In this iteration, an ordinary floor `J_t>=(t/n)I`, chronological-position
   monotonicity, per-stage `mu/n` gain, scalar child-half lifting,
   determinant-volume-only closure, and both fixed-adjacency dual states were
   refuted exactly.
3. The random-window identity

   ```
   P_q=E[D_q^TD_q]=J_q+(n-q)(J_{q+1}-J_q)                 (S8)
   ```

   shows why the growing-memory state is tied to the prefix hierarchy, but
   using the desired half-prefix inequality to lower-bound (S8) would be
   circular.  The unresolved information is the second moment of the window
   residual frame, not its mean.

## 6. Best next lemmas

There are now two focused, complementary general statements.

The first is the explicit third-level adaptive inequality

```
L_3(A)>=(2mu/n)A^{-1},
```

where `L_3` is the degree-four state in
`research/iteration5/route_c/higher_bellman_closure.md`.  It would imply
`J_3>=(3mu/n)A^{-1}` and settle the half certificate through dimension six.
It survived 17,920 hostile matrices and is proved on the complete
equicorrelation interval.  The exact obstruction to the current proof is
the anisotropic residual left after the sharp row-Bessel compression; that
residual cannot be discarded or scalarized.

The second is a random-order multirow frame bound for the half-window local
inverse.  It must combine (S6) across rows without scalarizing them and
should imply either

```
Q_q <= C P_q A P_q/mu
```

for a universal finite `C`, or directly
`P_q Q_q^{-1}P_q>=c mu A^{-1}`.  Fixed memory cannot work; half-linear memory
is exact on the sharp structured controls, passes all small-dimensional
generic stress tests so far, and exposes the precise covariance term still
missing.  The two targets retain the same missing anisotropic covariance in
Bellman and dual coordinates, respectively.

## 7. Timing and evidence boundary

The root-observed active interval was
`2026-08-21 19:37:57--21:39:05 +08:00` (121 minutes 8 seconds).  Every
parallel route was kept active through its own two-hour threshold.  Claims
`C035--C042` are internal proof candidates backed by independent hostile
reconstruction where stated; none has Lean formalization, external peer
review, or status as a solution of the unrestricted RPCD problem.
