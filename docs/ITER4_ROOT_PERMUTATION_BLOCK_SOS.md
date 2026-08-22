# Iteration 4 root route: consecutive-block Bessel/SOS hierarchy

Date: 2026-08-21

## Status

This route studies the singular-boundary target

\[
 K_0(C):=\mathbb E_\pi[M_\pi(C)^{-T}M_\pi(C)^{-1}]
 \succeq 2P_{\ker C}                                      \tag{R4.1}
\]

for every singular unit-diagonal correlation matrix `C`.  The Bessel hierarchy below is an exact
general algebraic lemma and is currently an **E3 proof draft**.  The fixed-depth conclusions are
only E1 float64 evidence:

- the adjacency level `q=2` has an exhaustive `n=7` counterexample;
- `q=3` survived exhaustive attacks through `n=9`;
- a two-pole-ring family at `n=10` gives a reproducible Monte Carlo counterexample candidate to
  `q=3`.

None of these statements proves or refutes (R4.1), the strong one-epoch inequality, C001, or the
target RPCD complexity.

## 1. A permutation Hilbert-space formulation

Let `Omega=S_n` with the uniform measure and put

\[
 B_\pi:=M_\pi(C)^{-1}.
\]

Regard

\[
 \mathscr B:z\longmapsto(\pi\mapsto B_\pi z)
\]

as an operator from `R^n` to `L^2(Omega;R^n)`.  Then

\[
 K_0(C)=\mathscr B^*\mathscr B.                            \tag{R4.2}
\]

For an ordered tuple of distinct vertices

\[
 \tau=(i_1,\ldots,i_\ell),
\]

let `phi_tau(pi)` be the indicator that `tau` occurs as a consecutive block in `pi`.  For
`2<=q<=n`, define the scalar feature space

\[
 \mathcal V_q=\operatorname{span}\left(
 1,\ \phi_\tau:2\le |\tau|\le q
 \right)\subseteq L^2(\Omega),                             \tag{R4.3}
\]

and let `Pi_q` be its orthogonal projector.  The matrix certificate is

\[
 K_q(C):=\mathscr B^*(\Pi_q\otimes I_n)\mathscr B.          \tag{R4.4}
\]

### Lemma R4.1 (monotone permutation-SOS hierarchy; proof draft)

For every unit-diagonal symmetric `C` for which all triangular factors are invertible,

\[
 \boxed{
  0\preceq K_2(C)\preceq K_3(C)\preceq\cdots
  \preceq K_n(C)=K_0(C).
 }                                                          \tag{R4.5}
\]

**Proof.**  Bessel's inequality gives
`0 <= Pi_q <= I` on the permutation Hilbert space, and the spaces (R4.3) are nested.  Congruence by
`mathscr B` proves every inequality in (R4.5).  At level `n`, the feature list contains the
indicator of every complete permutation, so `V_n=L^2(Omega)` and `Pi_n=I`.  This proves equality at
the final level.  `square`

This construction preserves positivity before expanding the alternating self-avoiding-path formula
for `B_pi`.  It is therefore a concrete implementation of the open SOS projection proposed in
`docs/ITER2_ROUTE_D_ORDER_POSET_EXPANSION.md`.

## 2. Explicit finite formula and exact feature Gram matrix

Let `Phi_q(pi)` collect a redundant generating list for (R4.3), including the constant feature, and
write

\[
 G_q=\mathbb E[\Phi_q\Phi_q^T].
\]

For output row `a`, define

\[
 H_{q,a}=\mathbb E[\Phi_q(\pi)e_a^TB_\pi].
\]

Then the orthogonal projection formula with the Moore--Penrose inverse is

\[
 \boxed{
 K_q(C)=\sum_{a=1}^n H_{q,a}^T G_q^\dagger H_{q,a}.
 }                                                          \tag{R4.6}
\]

Redundancy of the block indicators does not affect (R4.6).

There is also a closed combinatorial formula for `G_q`.  Take two block constraints and combine
their oriented adjacency edges.  If a vertex gets two different predecessors or successors, or the
union contains a directed cycle, the constraints are incompatible and the Gram entry is zero.
Otherwise the union is a disjoint collection of directed paths.  If it contains `e` distinct edges,
contracting all those paths leaves `n-e` freely permuted objects, hence

\[
 \boxed{(G_q)_{\tau,\eta}={(n-e)!\over n!}.}                \tag{R4.7}
\]

This proves (R4.7) directly and lets the verifier use an exact feature Gram without storing an
`n!` by `O(n^q)` dense matrix.

## 3. Exact sharpness test: signed rank one is captured at level two

By a diagonal sign conjugation it suffices to take `C=11^T`.  In chronological order `pi`, the
triangular inverse is the first-difference operator

\[
 (B_\pi z)_{\pi_1}=z_{\pi_1},\qquad
 (B_\pi z)_{\pi_k}=z_{\pi_k}-z_{\pi_{k-1}}\quad(k\ge2).
                                                               \tag{R4.8}
\]

Thus `B_pi` is already a linear combination of the constant and oriented-adjacency indicators, so

\[
 K_2(C)=K_0(C).                                             \tag{R4.9}
\]

The first vertex is uniform, and an unordered pair is adjacent in a random Hamilton path with
probability `2/n`.  Therefore

\[
\begin{aligned}
 \mathbb E\|B_\pi z\|^2
 &= {1\over n}\|z\|^2
   +{2\over n}\sum_{i<j}(z_i-z_j)^2\\
 &=\left(2+{1\over n}\right)\|z\|^2
   -{2\over n}(\mathbf1^Tz)^2.
\end{aligned}                                               \tag{R4.10}
\]

Equivalently,

\[
 \boxed{K_2(\mathbf1\mathbf1^T)
 =2P_{\mathbf1^\perp}+{1\over n}I.}                        \tag{R4.11}
\]

This both proves T080 on the signed-rank-one boundary and shows that the constant `2` cannot be
uniformly improved by a dimension-independent amount.

## 4. Fixed-depth attacks

All entries below are float64 E1 calculations.  For `n<=9`, every order was enumerated.  The
reported target margin is

\[
 \lambda_{\min}(K_q(C)-2P_{\ker C}).                        \tag{R4.12}
\]

### 4.1 Adjacency features are insufficient

At `n=7`, a two-pole ring with latitude `0.6625` gives

```text
q=2 projected margin = -0.03982363115691987
exact K0 margin       = +0.13784328863552717
```

Thus the Bessel lemma is valid, while the proposed fixed certificate `K_2>=2P_ker` is false.  This
is not a T080 counterexample.

### 4.2 Consecutive triples repair all exhaustive tests through n=9

Adding all three-vertex consecutive blocks gives:

| test set | evaluations | minimum `q=3` margin |
|---|---:|---:|
| `n=7`, random ranks/circles/two-pole grid | 360 | `+0.0510077241` |
| `n=8`, random ranks and dangerous two-pole hexagon | 27 | `+0.0302090353` |
| `n=9`, full two-pole grid | 10 | `+0.0107351967` |

An independent `n=9` hostile search also tested block sums `J_5 direct-sum J_4`, `J_7 direct-sum
J_2`, three rank-one clusters, and random ranks two and three; its minimum remained positive.
These null searches do not establish a general `q=3` theorem.

### 4.3 The triple level has an n=10 counterexample candidate

Full `10!` enumeration is expensive.  The script therefore keeps the exact Gram (R4.7), estimates
the cross moment `H` on two independent halves, and uses the unbiased cross-fit estimator

\[
 \widehat K_q={1\over2}\sum_a
 \left(\widehat H_{a,1}^TG_q^\dagger\widehat H_{a,2}
      +\widehat H_{a,2}^TG_q^\dagger\widehat H_{a,1}\right). \tag{R4.13}
\]

For the `n=10` two-pole ring, independent seeds gave:

| latitude | orders | seed | projected margin | sampled exact-`K0` margin |
|---:|---:|---:|---:|---:|
| `0.765` | 400,000 | `20260830` | `-0.00759570` | `+0.06380458` |
| `0.780` | 400,000 | `20260830` | `-0.00812527` | `+0.05814297` |
| `0.765` | 600,000 | `20260831` | `-0.00775640` | `+0.06396667` |
| `0.780` | 600,000 | `20260831` | `-0.00828123` | `+0.05827916` |

The agreement across independent samples makes this a strong E1 route-counterexample candidate,
but it is not an exact or interval certificate.  It refutes neither T080 nor RPCD.  It says that a
universal proof probably needs depth growing with dimension, a different feature family, or an
analytic coupling to the volume-basis circuit identities found in the parallel T080 route.

## 5. Failed attempts and precise obstructions

1. **Reverse-pair Loewner coercivity.**  Pairing `pi` with its reverse changes `M` to `M^T`, but on
   `C=11^T` the pair is only a path-graph energy and has low-frequency eigenvalues `O(n^-2)` on the
   kernel.  Full permutation coverage is essential.
2. **The stronger spectral-function bound `K0>=2(I+C)^-1`.**  It already fails on signed rank one
   in dimension two because its range-space requirement is too strong.
3. **Kernel compression alone.**  Proving `P_N K P_N>=2P_N` does not control the kernel--range
   cross block; T080 requires the full Loewner inequality or the equivalent inverse compression.
4. **Naive n=3 stereographic elimination.**  Direct substitution produced a degree-48 polynomial
   with mixed signs and no useful factorization (`scripts/iter4_root_n3_symbolic.py`).  The parallel
   route succeeded only after switching to the invariant variables `abc` and
   `a^2b^2+a^2c^2+b^2c^2`; see the separately audited n=3 proof.
5. **Fixed short feature depth.**  Exhaustive and cross-fit examples above rule out `q=2` and give a
   robust candidate against `q=3`.  Monotonicity of the hierarchy survives these failures.

## 6. Next proof targets

The most concrete continuations are:

1. exploit the permutation and dihedral representations to compute `K_4` on the `n=10` two-pole
   family without forming its `5851` by `5851` redundant Gram matrix;
2. prove a dimension-dependent depth statement, for example
   `K_{ceil(n/2)}(C)>=c P_ker(C)` with a universal `c>0`;
3. couple a random order to a volume-sampled Gram basis and use the exact circuit-frame identity
   from the parallel T080 route;
4. independently reconstruct Lemma R4.1 and the exact Gram count (R4.7), then replace the `n=10`
   Monte Carlo candidate by a symmetry-reduced rational certificate.

## 7. Reproducible artifacts

- `scripts/iter4_adjacency_bessel.py`
- `scripts/iter4_root_n3_symbolic.py`
- `research/evidence/ITER4_ADJACENCY_BESSEL_N6_N7.json`
- `research/evidence/ITER4_BLOCK3_BESSEL_N7_STRESS.json`
- `research/evidence/ITER4_BLOCK3_BESSEL_N8_RANDOM.json`
- `research/evidence/ITER4_BLOCK3_BESSEL_N9.json`
- `research/evidence/ITER4_BLOCK3_BESSEL_N10_CROSSFIT_400K_A.json`
- `research/evidence/ITER4_BLOCK3_BESSEL_N10_CROSSFIT_600K_B.json`

## 8. Checkpoint 3: an exact failure of the duplicate-child induction

The parallel duplicate-direction route reduced one proposed induction to the auxiliary claim

\[
 ((I+B)e_i)^T K_0(B)((I+B)e_i)\geq 3.                    \tag{R4.14}
\]

It proves (R4.14) through dimension three, but the unrestricted statement is false.  Let

\[
B=\begin{pmatrix}
1&1&4/5&4/5&4/5\\
1&1&4/5&4/5&4/5\\
4/5&4/5&1&23/50&23/50\\
4/5&4/5&23/50&1&23/50\\
4/5&4/5&23/50&23/50&1
\end{pmatrix}.                                             \tag{R4.15}
\]

This is the Gram matrix of two copies of a pole and an equilateral triangle at latitude `4/5`.
Its exact spectrum is `98/25, 27/50, 27/50, 0, 0`, so it is a correlation matrix.  For `i=1`
(using one-based indexing),

\[
 z=(I+B)e_i=(2,1,4/5,4/5,4/5)^T,
\]

and the exact rational subset recursion gives

\[
 z^TK_0(B)z={7204453277\over2441406250}
 =3-{119765473\over2441406250}<3.                         \tag{R4.16}
\]

This is an exact route counterexample, not a counterexample to T080.  It was first found by a
latitude-grid attack, converted to rational arithmetic, and then independently reproduced by
direct enumeration of all `120` orders.  Thus the general duplicate-vector induction must be
discarded, while its already closed low-dimensional cases remain valid.

Adding more copies of the pole to (R4.15) gives a useful separate stress family: float64 subset
recursion puts the full boundary Schur coefficient above two but decreasing from about `2.1207`
with two pole copies to `2.0441` with eight.  These values are E1 guidance only, but they identify
another asymptotically near-sharp family that any general proof must accommodate.

Exact reproducer and evidence:

- `scripts/iter4_duplicate_child_counterexample.py`
- `research/evidence/ITER4_DUPLICATE_CHILD_EXACT_COUNTEREXAMPLE_2026_08_21.json`

## 9. Checkpoint 4: why the half-depth prefix bound needs a matrix-valued state

A stronger route to the desired complexity would prove

\[
 J_t(B)\succeq {t\mu\over m}B^{-1}.                       \tag{R4.17}
\]

If the same scalar statement is inserted for every child in the exact Bellman recursion, the
induction from `t` to `t+1` reduces to the sufficient one-level inequality

\[
 (m-1-t\mu)I-mt\mu\,\overline D_B
 -\mu(m-t-1)B^{-1}\succeq0.                               \tag{R4.18}
\]

This natural closure is false even though the desired prefix bound remains true.  Take

\[
 B={1\over5}I+{4\over5}J,\qquad m=3,\quad t=1.
\]

On either transverse direction, the left side of (R4.18) has the exact eigenvalue `-28/225`.
By contrast, the actual closed two-prefix matrix satisfies

\[
 \lambda_{\perp}\left(J_2(B)-{2\mu\over3}B^{-1}\right)
 ={12\over25}>0.                                           \tag{R4.19}
\]

Thus this is a proof-route counterexample, not a counterexample to (R4.17).  The positive mass
lost by scalarizing each child is already essential in the smallest nontrivial rank-one example.
Any half-depth induction must retain at least an anisotropic child state, consistent with the
parallel pre-lift/post-lift compression developed in route T085.

Exact reproducer and evidence:

- `scripts/iter4_half_depth_scalar_induction_barrier.py`
- `research/evidence/ITER4_HALF_DEPTH_SCALAR_INDUCTION_BARRIER_2026_08_21.json`

## 10. Checkpoint 5: T080 and the strong one-epoch certificate are refuted

The near-sharp duplicate-pole stress search led to an exact boundary counterexample.  Let (C) be
the `8 by 8` correlation matrix with two poles and six exchangeable ring points:

\[
 C_{12}=1,\qquad C_{p r}=4/5,\qquad
 C_{rs}=71/125\quad(r\ne s).                              \tag{R4.20}
\]

Here `p` denotes either pole and `r,s` denote ring points; every diagonal entry is one.  It is the
Gram matrix of two copies of a pole and a regular five-simplex placed at latitude `4/5`.  Its exact
spectrum is

\[
 0,0,(54/125)^{[5]},146/25,                               \tag{R4.21}
\]

so it is PSD.  Put (u=e_1-e_2\in\ker C).  A pole swap fixes (C) and acts as minus one on (u),
so the odd line is reducing for the full permutation average (K_0(C)).  Exact rational averaging
gives

\[
 {u^TK_0(C)u\over\|u\|^2}
 ={2296209806050635263939777\over1164153218269348144531250}
 =1.972429204348\ldots<2.                                  \tag{R4.22}
\]

The strict gap is

\[
 -{32096630488061025122723\over1164153218269348144531250}.
\]

Equation (R4.22) has now been obtained in three structurally different ways: the discovery
calculation over the `56` ordered pole-position classes, an independent generic enumeration of all
`8!=40320` orders, and the present full `2^8` rational remaining-set recursion.  The last method
also verifies (K_0u=\lambda u) exactly.  Therefore T080 is refuted, not merely numerically
challenged.

There is also a finite positive-definite violation of the stronger M1 target.  For

\[
 A_\mu=\mu I+(1-\mu)C,\qquad\mu=1/100,
\]

the pole-odd line remains reducing.  The exact one-epoch energy identity makes its relative final
energy (1-\mu\kappa_\mu), where (kappa_\mu) is the corresponding eigenvalue of (K_0(A_\mu)).
Pure rational arithmetic yields

\[
 (1-\mu\kappa_\mu)-(1-\mu/8)^{16}
 ={139407497673157900331734058355416764719752656401774517490321089151
 \over
 655360000000000000000000000000000000000000000000000000000000000000000}>0.
                                                                    \tag{R4.23}
\]

Thus the fixed-(A) strong one-epoch Lyapunov inequality is false.  This does **not** refute the
original covariance-map spectral-radius conjecture C001: the latter permits compensation across
epochs and across covariance directions.  Exhaustive float64 covariance calculations on the same
ray give spectral radius `0.97698756 < 0.98018641` at `mu=0.01`, and
`0.99768598 < 0.99800187` at `mu=0.001`.  Those positive margins are only E1 scope checks, not a
proof of C001 on the ray.

Reproducers for the `4/5, 71/125` instance:

- `scripts/verify_iter4_t080_counterexample_independent.py`
- `scripts/iter4_root_t080_counterexample_audit.py`
- `scripts/iter4_t080_counterexample_covariance_check.py`
- `research/evidence/ITER4_ROOT_T080_COUNTEREXAMPLE_AUDIT_2026_08_21.json`
- `research/evidence/ITER4_T080_COUNTEREXAMPLE_COVARIANCE_CHECK_2026_08_21.json`

A separate, simpler rational member of the same two-pole/exchangeable-ring family has
`pole-ring=2/3` and `ring-off=1/3`.  The current
`scripts/iter4_t080_exact_counterexample.py` independently enumerates all `40320` labelled orders
for that matrix and obtains

\[
 {u^TK_0u\over\|u\|^2}={1057837\over531441}
 =1.990506942445\ldots<2.                                  \tag{R4.24}
\]

It is a second exact T080 counterexample, not the source of the fractions in (R4.20)--(R4.23).
Keeping the parameter sets separate is important for portable provenance.

This changes the proof strategy materially: future matrix-inequality work should target an adapted
Lyapunov metric or the covariance superoperator itself, not the fixed one-epoch (A)-energy metric.
