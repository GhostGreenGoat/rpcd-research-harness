# Iteration 6 Route A — multirow frame/covariance report

## Outcome

The general half-memory covariance/frame inequality is **not proved**.  The
route did, however, replace the vague “cross-row cancellation” blocker by an
exact cyclic-arc matrix inequality, prove several exact structural lemmas,
close signed equicorrelation and the generic cases with complement size at
most two, and analytically refute three tempting stronger proof routes.

For a uniform order, let `D` be the `q=ceil(n/2)` local inverse,
`F=DM-I`, `R=D^TD`, and

```
P=E[R],
Q=E[RMM^TR]=E[(D+F^TD)^T(D+F^TD)].
```

The target remains a numerical `c>0`, independent of `n,A,mu`, such that

```
P Q^-1 P >= c mu A^-1.                                  (T)
```

No claim below is promoted beyond its evidence level.  In particular, the
new positive arguments have not yet received an independent hostile audit.

## Exact positive structure

### 1. Conditional dual hierarchy

For any sigma-field `G` describing partial order information, define
`P_G=E[R|G]`, `Q_G=E[RMM^TR|G]`, and

```
C_G=E[P_G Q_G^-1P_G].
```

Exact square completion gives `K=E[M^-TM^-1]>=C_G`.  If `G` is coarser than
`H`, then `C_G<=C_H<=K`, and the gain has the quantitative Pythagorean
identity

```
C_H-C_G
 =E[(W_H-W_G)^TQ_H(W_H-W_G)],
W_G=Q_G^-1P_G.                                          (H)
```

Thus revealing a directed cycle but hiding its cut is a strictly stronger
legal dual certificate than applying a single global inverse after all
averaging.  Exact enumeration in dimensions three and four reconstructs
both hierarchy steps and (H).  This is an E3 proof candidate, not a uniform
lower bound.

### 2. Frozen random-rank Gram identity

For a fixed coefficient matrix `C`, independently random row/column ranks
give lower-inclusive and strict-upper masks `G,H` satisfying, for every
fixed symmetric column weight `W`,

```
E[G W G^T]=E[H W H^T]+(1/m)C W C^T.                    (G)
```

All four equality/distinct-label probability cases have lower-minus-upper
probability exactly `1/m`.  Matrix Bessel controls the last full-Gram term.
The identity is exact and is verified by enumeration through `m=4`.

Its application to RPCD stops at a precise measurability barrier: actual
local-solve rows change with the moving rank boundary, and the complementary
upper block is not the retained coefficient block of `D`.  The reverse
filtration formula in `conditional_random_rank_gram.md` records the adapted
operator Hardy/Bessel inequality still required.

### 3. Cycle-plus-cut representation

A uniform permutation is exactly a uniform directed cycle modulo rotation
plus a uniform cut.  Conditional on a cycle, solve one cyclic local row
`d_i^circ` per label.  If `C_ij` is its correlation with a forgotten cyclic
successor, then for every cut

```
(F_cut)_ij=C_ij 1_Arc(i,j)(cut),
T_cut:=F_cut^TD_cut
 =sum_(i,j)1_Arc(i,j)(cut) C_ij e_j(d_i^circ).           (C)
```

Thus the whole dual tail, not only `F`, has fixed matrix coefficients and
random arc masks.  The exact cut covariance is

```
S_cycle=E_cut[T_cut^TT_cut]
 =(1/n)sum_j sum_(s=1)^m
   (sum_(delta=s)^m C_(j-delta,j)d_(j-delta)^circ)^T
   (sum_(delta=s)^m C_(j-delta,j)d_(j-delta)^circ).      (A)
```

The verifier checks the defect, tail, single-arc, pairwise-overlap, and
nested-Hardy identities for every cut in dimensions five through eight.

### 4. Minimal generic covariance target

Let `S=E_cycle[S_cycle]`.  Matrix Cauchy gives

```
Q<=(1+eta)P+(1+1/eta)S.
```

Therefore the single dimension-free inequality

```
S<=C_tail P                                             (A5)
```

would imply `Q<=(1+sqrt(C_tail))^2P`.  Together with a generic local-frame
lower bound `P>=c_P mu A^-1`, it would prove (T) with constant
`c_P/(1+sqrt(C_tail))^2`.  This is the smallest falsifiable generic target
found in this route.

The bare arc kernel cannot prove it: equal arbitrary coefficients give a
`Theta(n)` normalized Hardy loss.  Exact successor-rank conditioning gives

```
E[sum_delta delta C_(i,i+delta)^2 | ordered past,O]
 =(m+1)||c_i||^2/2,
||c_i||^2<=lambda_max(A_O)(1-mu||d_i^circ||^2).          (D)
```

Consequently the diagonal arc energy obeys
`S_diag<=Lambda(1-mu)P/2` whenever all relevant complement blocks have
`lambda_max(A_O)<=Lambda`.  The unresolved general term is the adapted,
signed off-diagonal source-row covariance, together with modewise decay
when `lambda_max(A_O)=Theta(m)`.

### 5. Closed slices

- If `m=n-q-1=1` (`n=4,5`), Schur residual control gives
  `S<=P/2`.
- If `m=2` (`n=6,7`), the two-layer nested-square Gram has exact top
  eigenvalue `(3+sqrt(5))/2`, and
  `S<[(3+sqrt(5))/3]P<(7/4)P`.
- For positive equicorrelation, exact block formulas give
  `S<=e^-2P`, recovering `Q<=(1+1/e)^2P`.
- For negative equicorrelation `rho=-t`, `0<t<1/(n-1)`, exact parallel and
  transverse estimates give `S<=3P`, `P>=(mu/4)A^-1`, and hence
  `PQ^-1P>=(mu/30)A^-1`.  Diagonal-sign conjugates inherit the result.

These are E3 analytic proof candidates with E2 exact finite controls.  The
signed-equicorrelation result is a structured-family conclusion, not the
generic matrix inequality.  The low-complement covariance result alone
does not silently supply the separate generic preconditioner lower bound.

### 6. Local identity jet

For `A=I+epsilon H`, `diag(H)=0`, the true half-memory tail satisfies

```
S(epsilon)=epsilon^2[p2 H^2+(p1-p2)Diag(diag H^2)]
             +O(epsilon^3),
p1<1/8.
```

If `||H||<=1`, the second-order coefficient is below `I/8` in every
dimension.  The remainder is only fixed-dimensional.  Uniform row-stability
estimates also hold when `||A-I||<1`, but the skew-Hilbert family shows that
rowwise stability does not control a stacked operator.  No dimension-free
neighborhood theorem follows from the jet alone.

## Exact negative results and stress tests

### Pathwise covariance is impossible

For `n=2a`, `q=a`, the unit-diagonal bipartite skew-Hilbert family

```
A=[[I,(1/4)C^T],[(1/4)C,I]],
C_ij=1/(i-j), i!=j,
```

has a uniform positive spectral floor.  For the group order, the exact
generalized quotient for `Q_pi/R_pi` is

```
1+(1/(16a))sum_(r=1)^a H_(r-1)^2,
```

which diverges as `Omega(log(a)^2)`.  Hence no proof can bound every order
before averaging.  This refutes only the pathwise sufficient inequality,
not RPCD or the averaged certificate.

### Full reversal pairing is also impossible

On the same family, pairing the bad order with its full reversal leaves an
exact Rayleigh lower bound diverging as `Omega(log(a)^2)`, even if a factor
`1/mu` is allowed.  Therefore an order/reversal coupling still lacks the
necessary internal-rank average.  It does not refute the full permutation
average.

### Remaining-frame inverse Bellman potential is false

The proposed inverse Bellman inequality was independently reconstructed and
refuted first on a rational six-vector rank-one family.  More decisively,
it fails on the intended RPCD covariance lift itself.  For

```
n=9, A=(I+J)/2, mu=1/2,
v_i=(e_0+e_i)/sqrt(2),
Pi_i(X)=(I-v_iv_i^T)X(I-v_iv_i^T),
```

an exact rational symmetry reduction produces a test matrix with original
Bellman gap

```
<X,Delta X>_F=-2422114/12155<0.
```

All leave-one-out inverse solutions were substituted into the full ambient
equations exactly.  This closes that potential even on its special lift; it
does not refute RPCD convergence.

### Scalar and tangent closures

- Scalar Hardy/Cauchy on (A) loses `Theta(n)` on equal coefficients.
- The nilpotent identity `F^2=0` gives
  `PQ^-1P>=2P-Q`, but this is only the tangent inequality and can be
  indefinite.
- Separate row Schur bounds lose a factor `m`; cross-row/cross-order
  cancellation is indispensable.

## Reproduction and validation

All durable finite claims use SymPy exact rational arithmetic.  There are no
random seeds, floating tolerances, or null-search claims in the final
evidence.  Decimal fields in two JSON files are display conversions of exact
rationals.

Portable Python command:

```
python --version
```

Final exact verifier sweep:

```powershell
$py='python'
Get-ChildItem research/iteration6/route_frame/scripts -Filter verify_*.py |
  Sort-Object Name |
  ForEach-Object {
    & $py $_.FullName
    if ($LASTEXITCODE -ne 0) { throw "FAILED: $($_.Name)" }
  }
```

It ran all ten scripts with exit code zero at
`2026-08-22 18:35:47--18:35:59 +08:00`.  An earlier bare `python` invocation
returned Windows exit code `9009` because that executable was not on PATH;
no mathematical check was inferred from that run.  Re-running with the
explicit bundled interpreter passed.

The ten evidence files are under `evidence/`; each verifier writes its own
portable JSON record.  PowerShell `Test-Json -SchemaFile
schemas/result.schema.json` returned `True` for `result.json`, and the
harness protocol content validator returned no errors.  The standalone CLI
wrapper additionally requires a harness-owned sibling `invocation.json` to
attest active seconds; this route instead records observed wall-clock timing
in `TIMING.json` and does not pretend it is harness-owned telemetry.

## Scope, deepest obstruction, and next exact target

The general RPCD `O(n/mu log(1/epsilon))` result remains open.  This route
does not prove a generic preconditioner bound for `P`, nor the generic arc
tail inequality (A5), nor an expectation-of-distance theorem.  It produces
no Lean/E6 certificate and makes no external priority claim.

The next minimum inequality should not revisit fixed adjacency, fixed
bandwidth, scalar row summation, pathwise norm control, reversal pairing, or
the false inverse Bellman potential.  It should prove a modewise,
cycle-averaged estimate for the signed off-diagonal part of (A), using the
joint local-solve/Schur constraints and the Pythagorean conditional hierarchy.
Equivalently, one may lower-bound selected cycle-to-cut information gains in
(H) so that their telescoping sum pays for the adapted off-diagonal arc
covariance.  Any proposed lemma should first reproduce the signed
equicorrelation blocks and the skew-Hilbert/reversal barriers exactly.

## Timing

Observed active start: `2026-08-22 16:34:50 +08:00`.

Required threshold: `2026-08-22 18:34:50 +08:00`.

Actual finalization time and total elapsed interval are recorded in
`TIMING.json` after the last schema and verifier checks.  No idle waiting is
counted as research activity.
