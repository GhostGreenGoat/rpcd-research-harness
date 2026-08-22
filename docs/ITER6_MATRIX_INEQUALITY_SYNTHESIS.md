# Iteration 6: analytic matrix-inequality synthesis

Date: 2026-08-22 (Asia/Shanghai).

Status: research synthesis.  The unrestricted RPCD conjecture remains open.
Evidence labels follow `docs/METHOD.md`; none of the new claims has Lean,
external-human, or priority validation.

## 1. Target and normalization

For a general quadratic Hessian `Q`, put

```
D=Diag(Q),       A=D^(-1/2)QD^(-1/2),
mu=lambda_min(A).
```

Exact coordinate-descent iterates are invariant under scalar rescaling, so
the scale-free parameter is this normalized `mu`, not raw
`lambda_min(Q)`.  The desired strong finite-time conclusion is

```
E||x_k||_A <= exp(-c mu k)||x_0||_A
```

per epoch, for a numerical `c>0`; an epoch uses `n` coordinate updates.

## 2. Strongest positive result: the third weighted Bellman level

The explicit anisotropic state `L3` now has an independently audited proof:

```
C3(A):=J3(A)-(1/2)J2(A) >=L3(A)>=(2mu/n)A^-1.            (I6.1)
```

The proof does not scalarize the child Schur defect.  It uses the exact
surplus `Q(C)-beta C^-1`, proves a sharp directionwise Schur-envelope
inequality, and pays the parent rank-one defect with that same directional
surplus.  This is the first successful general use of the anisotropy that
earlier Jensen/Bessel compressions discarded.

Combining (I6.1) with the audited level-two bound gives

```
J3(A)>=(3mu/n)A^-1.                                     (I6.2)
```

Consequences:

- for every `n>=3`, a rigorous strong-expectation benchmark of
  `O(n^2/mu log(1/epsilon))` coordinate updates;
- for every `n<=6`, choosing the half prefix proves
  `K(A)>=(mu/2)A^-1`, and therefore the conjectured
  `O(n/mu log(1/epsilon))` order;
- the expected-distance statement is
  `E||x_k||_A<=(1-rho_n mu)^(k/2)||x_0||_A`, not the weaker
  `||E x_k||_A` statement.  A Ville supermartingale argument gives a
  simultaneous high-probability version without a `log k` union penalty.

The next exact hierarchy step is no longer vague.  For child size `d=n-1`,
`W4` asks whether the retained `L3` surplus recovers

```
[2mu/(d s_i)]c_i c_i^T                                  (I6.3)
```

for every outer Schur direction, or whether the averaged unrecovered defects
fit inside the explicit allowance in
`research/iteration6/route_l3/general_t_schur_recursion.md`.  The purely
spectral part is exactly insufficient; the anisotropic remainder is
essential.  Several genuinely anisotropic slices are now proved and
independently audited: arbitrary signed matching-support children, and every
weighted three-vertex path plus isolated coordinates in every child dimension
`d>=6`, as well as every equal-magnitude signed star plus isolates.  The path
closes the first non-matching interaction uniformly in dimension, while the
star closes the fully symmetric degree-at-least-three sector.  These
structured results do not prove general `W4`; the next minimal unsupported
states are overlapping degree-two interactions, a sign-frustrated cycle, or
an unequal-weight star.

## 3. New all-dimensional spectral regions

The exterior/volume prefix certificate diagonalizes spectrally.  With
`r=ceil(n/2)` its minimum coefficient is always on the minimum eigenspace,
and it proves the target whenever

```
e_(r-1)(lambda_2,...,lambda_n) >=binom(n,r)/2.            (I6.4)
```

An independent hostile audit closed two useful corollaries:

1. (I6.4) holds for every unit-diagonal SPD matrix having at most two
   eigenvalues strictly below one.  Hence any counterexample must satisfy
   `lambda_3(A)<1`.
2. It also holds, for every `n` and every `mu`, on the two-point spectral
   families
   `A=aI-(a-mu)P` whenever `P` is a constant-diagonal projector of rank at
   most three.  These families include open spectral neighborhoods and are
   not covered by the determinant bound at small `mu`.

The threshold is meaningful: for a rank-four constant-diagonal low space,
`n=9` and `mu->0`, the same exterior coefficient is exactly
`729/1750<1/2`.  This is a barrier to the bare certificate, not an RPCD
counterexample.  Likewise the spectrum
`(mu,mu,mu,1,1,1,1,4-3mu)` defeats the exterior certificate on a nonempty
small-`mu` interval, yet it is realized by
`diag(mu I_4+(1-mu)J_4,I_4)`, a structured RPCD family already known to
satisfy the target.  This cleanly proves that scalar spectral data alone
discard useful coordinate geometry.

## 4. Boundary-ray interpolation and stitching

For every singular correlation matrix `C` and
`A_mu=mu I+(1-mu)C`, the orderwise triangular factorization gives the
dimension-free comparison

```
K(A_mu)>=(1+mu)^(-2)K(C).                                (I6.5)
```

This nonnormal inequality passed an independent audit.  A full shorted
boundary certificate `K(C)>=kappa P_tau` can be harmonically stitched with
the exact two-prefix spectral bound, yielding the explicit coefficient in
`research/claims/C047-boundary-ray-stitching.json`.

The remaining assumption is substantive: a compression
`P_tau K(C)P_tau>=kappa P_tau` is not enough, and exact elliptope examples
show a nonzero Schur-cross budget.  Endpoint-only scalar stitching also
loses the mesoscale signed-rank-one regime.  The useful open statement is a
full low-spectral-layer shorting inequality, not merely a kernel Rayleigh
bound.

## 5. Projection-superoperator lift: useful reduction, failed potential

In energy coordinates, RPCD covariance is exactly a fully symmetrized
product of orthogonal projections on `Sym_n`:

```
C_A=(1/n!)sum_pi Pi_(pi_1)...Pi_(pi_n),
Pi_i(X)=(I-v_iv_i^T)X(I-v_iv_i^T).                       (I6.6)
```

The complementary projection frame has the sharp floor

```
sum_i(I-Pi_i)>=mu I.                                    (I6.7)
```

Thus a weak symmetrized-product gap in terms of (I6.7) would solve the rate
problem.  The full noncommutative AGM inequality is known to be false, so
only the weaker structured gap is plausible.

A natural inverse remaining-frame Bellman potential was proved for one and
two projections but then refuted exactly:

- six rank-one equicorrelated projections give transformed gap `-1/81`;
- more importantly, the genuine lifted family at
  `n=9,A=(I+J)/2` has an exact rational quadratic gap
  `-2422114/12155`.

This closes that potential even under the RPCD structure.  It does not
refute (I6.6)'s spectral-gap target.

## 6. Random-window dual route: a conditional hierarchy

Fixed/pathwise triangular bounds and order/reversal pairing were closed by
analytic Hilbert-kernel examples: their required constants diverge.  Full
internal-rank averaging is therefore necessary.

The surviving replacement is an exact conditional regression hierarchy.
For any order-information sigma-field `G`, define conditional moments
`P_G,Q_G`.  Then

```
K>=C_G:=E[P_G Q_G^-1P_G],
G subset H  ==> C_G<=C_H<=K.                             (I6.8)
```

The refinement gain has the exact Pythagorean form

```
C_H-C_G
 =E[(W_H-W_G)^T Q_H(W_H-W_G)]>=0.                       (I6.9)
```

Revealing a directed cyclic order but hiding its cut produces a particularly
useful intermediate level.  Half-window residual rows freeze on the cycle;
the random cut becomes an arc-incidence Gram kernel, and the tail covariance
is an explicit nested Hardy/Copson form.  What remains is to control that
nested form together with the baseline/cross term and the outer random-cycle
average.  This is a precise analytic target, not a broad covariance guess.

The arc target is already closed for signed equicorrelation and when the
forgotten complement has size at most two.  These are structured E3 proof
candidates rather than a generic theorem.  The unresolved term is now the
adapted signed off-diagonal arc covariance; scalar Hardy estimates lose a
factor of order `n`, so a proof must use modewise residual decay or the exact
Pythagorean information increments in (I6.9).

## 7. Current frontier

The unrestricted target is not solved.  The smallest live bottlenecks are:

1. prove `W4` Schur recovery (I6.3), then find a stable growing-depth
   recursion rather than recomputing unstructured high-degree polynomials;
2. prove a full boundary low-layer shorting inequality suitable for (I6.5),
   with cross blocks retained;
3. bound the cycle-conditioned dual certificate using its arc Gram and
   Pythagorean information increments;
4. alternatively, prove the weak structured projection-product gap implied
   by (I6.6)--(I6.7), without invoking the false noncommutative AGM or the
   refuted inverse potential.

The exact failures now sharply constrain the next iteration: avoid fixed
memory, pathwise triangular norms, reversal-only averaging, scalarized Schur
defects, and convex mixtures of spectral certificates whose weakest
eigenline is the same.
