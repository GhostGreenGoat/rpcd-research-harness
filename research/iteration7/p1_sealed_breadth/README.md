# P1 sealed-breadth RPCD exploration

This directory is the portable handoff for the formal four-way T143 run started
from the normalized C050 statement.  Each rollout committed an immutable route
card before inherited RPCD history was revealed, used a distinct method family,
ran for at least two active hours, passed final result validation, and passed the
two trusted exact regressions.  The canonical ensemble is
`ensemble-20260825T123453Z-161b71f1`.

No rollout proves or refutes C050.  Same-run general statements remain at most
E3, numerical null searches remain E1, and the imported routes remain subject
to an independent target-fidelity/hostile review.

| Rollout | Worker | Active seconds | Final gate |
| --- | --- | ---: | --- |
| covariance block powers | `sealed-covariance-block-powers` | 8121.031 | completed, final validation valid, 2/2 trusted verifiers passed |
| exchangeable coupling | `sealed-exchangeable-coupling` | 7364.437 | completed, final validation valid, 2/2 trusted verifiers passed |
| polynomial moments | `sealed-polynomial-moments` | 9473.687 | completed after an automatic schema-repair pass, final validation valid, 2/2 trusted verifiers passed |
| adaptive Lyapunov | `sealed-adaptive-lyapunov` | 9025.735 | completed after an automatic schema-repair pass, final validation valid, 2/2 trusted verifiers passed |

## Outcome by locked route

| Route | Locked first edge | Outcome | DAG disposition |
| --- | --- | --- | --- |
| Covariance block powers | `(L_A^*)^ceil(16/mu)(A) <= A/2` | General edge open.  Exact C050 transfer is correct; exact warm-start/polar reformulation and several nontrivial boundary slices were obtained. | Imported as `R150-covariance-block-powers`, proposed/unreviewed. |
| Exchangeable transpositions | `E D_pi(x) >= ||Ax||^2/16` | Exactly false on signed equicorrelation at the smallest violating dimension `n=17`; the sharp pure residual coefficient scales as `1/n`.  A multi-epoch repair remains open. | Imported as `R160-exchangeable-coupling`, suspended pending an independent exact prune review. |
| Noncommutative moments | One-epoch symmetrized frame loss `D >= (mu/16)I` | The locked edge is C051-strength and remains open.  A logarithmic trace-moment repair was reduced to an open cumulative relative-loss lemma. | Not imported: the final avenue changed the immutable `falsifier` text.  The integrity gate rejected it; see `import_rejection.json`. |
| Adaptive Lyapunov cone | Bellman capture `H_[n] >= eta mu A^{-1}` | Exact unrolling identifies the locked edge with the known stronger C051 certificate.  The useful repair is a bounded-horizon phase-reset/cone formulation; several exact small-dimensional separators and positive controls were obtained. | Imported as `R180-adaptive-lyapunov`, proposed/unreviewed; semantic target review should treat the locked card as C051-anchored. |

## Portfolio interpretation

The run produced real sampling width, but not four surviving direct-C050 routes.
At the immutable-card level:

- covariance block powers is the only surviving route with a clean direct C050
  transfer and should be the next T144 hostile-audit candidate;
- exchangeable transpositions is a useful exact failure branch, not a surviving
  proof candidate;
- the noncommutative and adaptive locked edges collapse to C051-strength
  one-epoch certificates, although their post-reveal multi-epoch repairs contain
  useful depth information;
- the polynomial-moment result is deliberately excluded from the route DAG
  because its final avenue did not reproduce all locked fields exactly.

Consequently, `route-audit` is expected to continue reporting that no
agent-generated sealed route is active until an independent target-fidelity
review accepts one.  This is not a failed fanout: it distinguishes realized
breadth from independently accepted frontier breadth.

## Next action

Run T144 against the covariance rollout first.  Its audit should attack the
reachable two-epoch edge

`C(I-C(I)) >= mu C(I)`, equivalently `H_2 <= (1-mu)H_1`,

or the exact polar inclusion `D-mu I in K_1(A)^*`.  If target fidelity and the
C050 transfer survive, the audit can supply the review artifact needed to
activate `R150`.  Separate cleanup work may independently certify the `n=17`
exchangeable counterexample and hard-prune `R160`; it should not consume the
first T144 slot.

## Evidence map

- `ensemble.json` preserves the canonical complete-fanout attestations.
- `import_rejection.json` records the fourth-card integrity failure without
  altering the attested run.
- `covariance/`, `exchangeable/`, `polynomial_moments/`, and
  `adaptive_lyapunov/` contain the curated mathematical handoff files and exact
  verifier sources.  Event streams, model transcripts, bytecode, draft results,
  and redundant broad E1 scan dumps are intentionally omitted.  The one 217 KB
  subset baseline required to replay the targeted `n=14` attack is retained and
  remains explicitly labeled E1.
- `portable_manifest.json` records both original and relocated SHA-256 values;
  a differing hash means only end-of-file whitespace and, where present, local
  interpreter/run paths were sanitized.

The curated Git subset is not a substitute for the complete nine-part run
attestation.  T144's canonical dependency gate still requires the original
validated runs, an audited `pack --include-runs` transfer, or a fresh T143 run.
The two harness-owned trusted verifiers check RPCD product orientation and the
projection lift; they do not independently prove any new route lemma.

From the repository root, verify every curated file hash, the four-way ensemble
shape, the three imported route-card hashes, and the rejected fourth import with
`python scripts/verify_iter7_p1_handoff.py`.
