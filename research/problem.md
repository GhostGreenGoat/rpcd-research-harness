# RPCD problem statement and research ledger baseline

## Current finite-time target

For a general quadratic Hessian `Q`, normalize coordinate smoothness by

```text
D=Diag(Q),  A=D^(-1/2)QD^(-1/2),  mu=lambda_min(A).
```

Then `A` has unit diagonal.  The raw value `lambda_min(Q)` is not scale
invariant, while `mu` is the correct RPCD parameter.  RPCD draws a fresh
independent uniform permutation in every epoch.  The actual finite-time target
is: there exist universal constants `c,C>0` such that, for every dimension,
every such `A`, every starting point, and every epoch count `k`,

```text
E||x_k||_A <= C exp(-c mu k)||x_0||_A.                  (G-FT)
```

Thus relative expected `A`-distance `epsilon` costs
`O((1/mu)log(1/epsilon))` epochs and
`O((n/mu)log(1/epsilon))` coordinate updates.  This is expectation of distance,
not the weaker distance of the expected iterate.  Claim `C050` is the master
claim for `(G-FT)`.

### Strong one-epoch sufficient certificate

Let `M_pi` be the permuted lower-triangular Gauss--Seidel factor and define

```text
K(A)=E_pi[(M_pi M_pi^T)^(-1)].
```

A major current route seeks a universal numerical constant `c_K>0` such that

```text
K(A) >= c_K mu A^(-1).                                  (S-K)
```

This gives the stronger conditional statement

```text
E[||x_(k+1)||_A^2 | x_k] <= (1-c_K mu)||x_k||_A^2,
```

so `(S-K)` implies `(G-FT)` by iteration and Jensen.  The converse is neither
known nor assumed: `(S-K)` fixes the `A`-energy metric and is strictly stronger
than the requested complexity statement.  A counterexample to an over-strong
one-step certificate must not be reported as an RPCD counterexample.  Claim
`C051` tracks `(S-K)`.  Prefix matrices `J_t` and the exact transfer identity
are defined in `research/iteration6/route_l3/n_le_6_finite_time.md`.

Current audited progress on this sufficient route is summarized in
`research/iteration6/PORTABLE_HANDOFF.md`: `c=1/2` is proved for `n<=6` and
several all-dimensional spectral families; every dimension has the weaker
`K(A)>=(3mu/n)A^-1`.  General `n>=7` remains open.

The original covariance-rate conjecture below (`C001`) is another route.  Its
self-adjoint finite-time bridge currently carries a dimension-dependent
prefactor, so an additional uniform bridge is needed before it yields `(G-FT)`
with universal constants.

## Exact target of the original asymptotic conjecture

Let

$$
f(x)=\tfrac12 x^\top A x,
\qquad A\in\mathbb S_{++}^n,
\qquad A_{ii}=1,
\qquad \lambda_{\min}(A)=\sigma\in(0,1].
$$

For a permutation `p=(p_1,...,p_n)`, one exact coordinate update is

$$
U_i=I-e_i e_i^\top A,
\qquad T_p=U_{p_n}\cdots U_{p_1}.
$$

RPCD draws a fresh uniform permutation each epoch. Its covariance map is

$$
\mathcal M_A(X)=\mathbb E_p[T_pXT_p^\top],
$$

represented on vectorized matrices by
`E_p[T_p \otimes T_p]` (the transpose convention has the same spectrum).

Kim–Lee–Yun Conjecture 4.1 asks whether, for every such `A`,

$$
\rho(\mathcal M_A)
\le
\max\left\{
  (1-1/n)^n,
  (1-\sigma/n)^{2n}
\right\}.
$$

This spectral statement is sufficient for the stated asymptotic squared-norm bound. When a task
concerns a particular initial point rather than the worst reachable second-moment mode, it must say so.

## Original-conjecture public status (literature audit dated 2026-08-19)

- **External theorem:** the bound and a strict RPCD-vs-RCD gap are proved for the
  permutation-invariant class `A = sigma I + (1-sigma) 11^T` (up to the paper's normalization/sign
  symmetries).
- **Open conjecture:** extension to every unit-diagonal SPD Hessian.
- **Published evidence:** algorithmic searches for `n=3,4,5,6` and several `sigma` values returned
  structured worst cases, but this is not a proof.
- **Harness candidate C010:** a matrix-Jensen energy contraction bound described below. It is not
  recorded as a theorem until the audit tasks close.

Primary source: Donghwa Kim, Jaewook Lee, Chulhee Yun, *Provable Benefit of Random Permutations
over Uniform Sampling in Stochastic Coordinate Descent*, ICML 2025, arXiv:2505.23152.

## Candidate C010: matrix-Jensen bound

Write `H=A-I`. For a permutation, let `M_p` be the permuted lower-triangular Gauss–Seidel factor,
so `T_p=I-M_p^{-1}A`. Define

$$
S=\tfrac13H^2+\tfrac16\operatorname{Diag}(\operatorname{diag}(H^2)),
\qquad
\theta=\lambda_{\max}(A^{-1/2}SA^{-1/2}),
\qquad
r_{MJ}=\frac{\theta}{1+\theta}.
$$

The proposed chain is

$$
\mathbb E[M_pM_p^\top]=A+S,
$$

$$
T_p^\top A T_p=A-A(M_pM_p^\top)^{-1}A,
$$

and operator convexity of inverse gives

$$
\mathbb E[T_p^\top A T_p]
\preceq A-A(A+S)^{-1}A
\preceq r_{MJ}A.
$$

The algebra is plausible and the finite identities are covered by verifiers. Research tasks must still
check quantifiers, Jensen direction, singular limits, norm conversion, novelty, and whether `r_MJ` is
strong enough to imply the ICML conjectured bound in any nontrivial regime.

### Known finite obstruction to the raw scalar comparison

The implication `C010 => C001` cannot be completed merely by asserting
`r_MJ(A) <= max((1-1/n)^n,(1-sigma/n)^(2n))`. A reproducible rational candidate uses
unit diagonal and off-diagonal entries with denominator 1000:

$$
A=\begin{pmatrix}
1&-.754&.816&-.783\\
-.754&1&-.858&.771\\
.816&-.858&1&-.696\\
-.783&.771&-.696&1
\end{pmatrix}.
$$

Float64 evaluation gives

```text
lambda_min(A)              = 0.10018415...
exact RPCD covariance rate = 0.7557607407401463
ICML conjectured bound     = 0.8163433709286394
matrix-Jensen scalar bound = 0.8527799042424034
```

Thus the tested RPCD matrix still satisfies C001, while the raw Jensen upper bound is too loose by
about `0.03644`. Claim C011 tracks interval certification of this rational route barrier. Any successful use of C010
must retain more order/symmetry information or combine it with a sharper inequality.

## Iteration 2 analytic progress (2026-08-20)

The conjecture remains open in general. The second iteration produced several analytic proof drafts
and route barriers, summarized in `docs/ITER2_SYNTHESIS.md`.

The strongest partial result is the hostile-audited-local proof candidate

$$
\rho(\mathcal M_A)
\le 1-\det A
\le 1-\sigma^{n-1}(n-(n-1)\sigma).
$$

It proves C001 for all `n=2` instances and for every `n>=2` in an explicit high-`sigma` region. The
first inequality specializes the classical Meany/Gram-determinant bound; priority and independent
reconstruction are still pending, so it is tracked as C023 rather than promoted to a theorem.

Other second-round artifacts are:

- C020: an exact variance-resolvent identity and a monotone finite inverse-polynomial hierarchy that
  sharpens bare Jensen at its canonical scale;
- C021: an exact remaining-set Bellman recursion and a cumulative Schur-loss representation;
- C022: a universal two-step PSD advantage for sampling without replacement;
- C024: an exact fixed-`sigma` counterexample to the orbit-concavity needed by naive Hessian
  symmetrization;
- C025: an exact increasing-path/order-poset expansion for the expected inverse Gram matrix.

None of C020--C025 supplies the missing uniform low-`sigma`, all-dimension bound by itself.

## Iteration 5 matrix-inequality frontier (2026-08-21)

The general finite-time `O(n/mu log(1/epsilon))` result is still open, but the
frontier is now more precise; see `docs/ITER5_MATRIX_INEQUALITY_SYNTHESIS.md`.

- C036 proves the all-dimensional weighted two-prefix inequality
  `J_2-J_1/2>=(3mu/(2n))A^{-1}`.  The analogous level-three matrix residual
  is the first open weighted Bellman step.
- C035 proves the complete leaf-free first-half prefix curve for positive and
  negative equicorrelations; C037 proves the whole weighted hierarchy in a
  fixed-dimensional neighborhood of identity.
- C038 and C040 develop a growing-memory local-inverse dual state.  Sublinear
  memory is analytically insufficient in the sharp `rho=c/n` scaling, while
  half-linear memory gives an audited finite coefficient larger than
  `mu/4` on positive equicorrelations.
- C041 gives a general, explicit dimension-scaled region: if
  `n(1-mu)<=1`, then `K(A)>(mu/4)A^{-1}` for every unit-diagonal SPD matrix.
- The generic remaining blocker is a random-order multirow frame inequality
  for the half-window Schur residual.  Every individual residual row obeys
  `rB_O^{-1}r^T<=1-mu`, but an exact rational example shows that independent
  scalar row summation cannot close the bound.

Exact failures now include fixed adjacency of either orientation, per-stage
uniform progress, scalar child lifting, and determinant-volume-only closure.
They are proof-route barriers, not counterexamples to RPCD itself.

## Non-goals

- A large random search with no counterexample does not solve the conjecture.
- A bound for the structured class is not silently generalized to arbitrary SPD matrices.
- A one-epoch expectation inequality is not rewritten as an almost-sure trajectory inequality.
- “Claude/Code/Codex found a proof” is never evidence by itself; only inspectable artifacts count.
