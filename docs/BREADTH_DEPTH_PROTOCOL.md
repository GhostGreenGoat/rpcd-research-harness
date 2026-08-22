# RPCD breadth/depth portfolio protocol

This document governs route selection for an open mathematical problem. A
route score is a research-management diagnostic, not mathematical evidence.
Evidence levels and theorem-language gates remain those in `docs/METHOD.md`.

## 1. One target, several representations

The level-zero target is the strong finite-time statement: for every real
unit-diagonal SPD matrix `A`, with `mu=lambda_min(A)`, fresh independent
uniform permutations each epoch, every initial point, and every `k>=0`, prove
for universal numerical `c,C>0` that

```text
E ||x_k||_A <= C exp(-c mu k) ||x_0||_A.
```

One epoch costs `n` coordinate updates, so this implies
`O((n/mu) log(1/epsilon))` updates. It is stronger than a bound on
`||E x_k||_A`. Any high-probability substitute must state its confidence
parameter and must not be silently rewritten as the expectation statement.

Routes form a DAG whose `parent_ids` point one layer upward toward this target:

- `L0`: the end-to-end finite-time target;
- `L1`: a genuinely different proof architecture or representation;
- `L2`: the first unresolved bridge lemma for that architecture;
- `L3`: a repair, minimal obstruction, or sharper invariant for the `L2` edge;
- `L4`: audit/formalization work after a proof candidate exists.

Every route records a signature: representation, state/invariant, core lemma,
information retained and discarded, target implication, expected failure, and
verifier class. Similar prose with different signatures stays separate;
different prose with the same signature is a duplicate candidate.

## 2. Sealed breadth before inherited depth

The active portfolio must eventually contain at least one Agent-generated
`sealed_breadth` route:

1. expose only the exact normalized statement, sampling/norm semantics, and—when doing a
   stratified fanout—the assigned high-level method family;
2. require a route card before showing derivation history;
3. hash the immutable card with SHA-256 and store the digest in the route node;
4. only then reveal the declared failure map and controls;
5. retain the pre-reveal card even when later work pivots.

The checked-in coordinator precommit is only a problem specification or route
assignment. It contributes no realized breadth. After a fanout rollout finishes,
import its immutable card through the controlled registry gate:

```text
rpcd-harness route-import-card \
  runs/<task>/<run>/artifacts/route_card.json \
  --route-id R150-example-family
```

The importer accepts only a completed, non-dry sealed run whose route-card phase
and final run both have `validation.valid=true`. It recomputes the card hash and
checks both
invocation hash records. For a fanout run it ignores incomplete shard ensembles
and reconstructs the rollout only from one canonical `complete=true` full or
merged ensemble and its hashed source manifest. The selected run's canonical
task snapshot, invocation, validation, result, artifact manifest, trusted
verifier reports, artifact tree, and verifier-log tree must match its
`run_attestation`. A task that declares an official `fanout_manifest` cannot
fall back to a standalone import. A standalone `run-codex` sealed task is
allowed without an ensemble only when its card uses
`rollout_id=task_id` and the task's own base method family. It represents one
independent route, not a multi-family fanout. The importer refuses overwrites,
arbitrary JSON files, coordinator-precommitted cards, and any invocation carrying
`resume_lineage`: a checkpoint resume is useful depth, but is not another independent
statement-only sample. It copies the immutable
card to tracked `research/routes/cards/<route-id>.json`; `route-audit` re-hashes
that portable copy and checks that its mathematical fields still match the route
node. Every mathematical, context, and parent field in the selected final
avenue must equal the immutable card exactly; changing only the failure story
after inherited context is revealed is rejected too. A matching positive final
avenue creates only an `L1/proposed/unreviewed` node. It becomes an active scout
only through

```text
rpcd-harness route-review-target R150-example-family \
  runs/<review-task>/<review-run>/artifacts/review.json
```

The review format is specified by `schemas/route-target-review.schema.json`.
`reviewer_task_id`, `reviewer_run_id`, and `reviewer_worker` must identify one
real standalone harness run whose canonical task/source snapshot, invocation,
successful validation, exhaustive artifact manifest, trusted reports/logs, phase
timings, and 120-minute floor all revalidate. The review JSON and every evidence
artifact must belong to that run's attested `artifacts/` tree. The stored nine-hash
run attestation is rechecked by `route-audit` whenever the source run is present.
This is machine-verifiable process lineage, not a cryptographic account-identity
signature. The review also binds the exact pre-review node and card hashes, is
authored by a different worker, and checks the normalized SPD quadratic, fresh independent
epoch permutations, every initial point, expectation of A-distance (not merely
distance of the expected iterate),
dimension-uniform transfer, C050/C051 non-equivalence, and genuine method-family
distinction. This is a target-fidelity/allocation gate, not proof evidence. A
generating worker's own `refuted`/`prune` verdict is
preserved only as `suspended/suspend`, with a reopen condition requiring an
independent critic's E2+ resolution: an exact/certified counterexample leads to a
controlled hard-prune, while an exact rejection of the purported counterexample
allows active reconsideration. It cannot hard-prune its own route. A blocked
avenue without an explicit schema-valid reopen condition
remains `proposed/unreviewed`, never falsely active. In every case
`route_card_origin=agent_generated` records independent search provenance, not
mathematical correctness.

A coordinator precommit is useful for scheduling but does not satisfy this
requirement. Its provenance is `coordinator_precommit`; only a validated,
independently target-reviewed `agent_generated` card with a concrete rollout ID counts toward realized
search breadth. Until T143 runs, `route-audit` therefore reports a portfolio
blocker rather than pretending that planned breadth has already occurred.

The seal is about intellectual independence, not secrecy. Credentials and
private state are never inputs. A sealed rollout may be constrained to a
method family so that it does not merely rediscover a dominant existing
route. `continuation_depth` may read declared predecessor artifacts;
`critic_validation` may read only the candidate statement, declared inputs,
and controls needed for an independent attack.

The first phase runs from an ephemeral directory outside the Git worktree so
repository ancestor instructions are not automatically inherited. Its staged
metadata lists only copied allowlist paths, never the names of denied claims or
failure maps. This reduces predictable context leakage but remains cooperative,
not sandbox-enforced.

Cheap inherited checks use verifier phase `preflight`. For continuation and
critic tasks they run before the first research subprocess. For sealed breadth
they are deliberately hidden until the route card is hashed, then run before
history is revealed and depth work begins. A failed preflight stops the run
without consuming the two-hour research floor. Use `when=both` for invariants
that must also survive the final state, and reserve `when=final` for checks that
depend on artifacts produced by the new route.

## 3. Decision gates

Apply the gates in order. Failure at an earlier gate prevents promotion at a
later one.

| Gate | Required question | Allowed decision on failure |
|---|---|---|
| G0 target fidelity | Are unit diagonal, normalized `mu`, fresh permutations, full initial-point quantifiers, and expectation-of-distance semantics explicit? | repair or hard-prune a semantics-changing route |
| G1 exact representation | Is the proposed covariance, Bellman, cycle, or shorted-operator identity exact with dimensions and transpose order checked? | branch to an exact repair or record an exact barrier |
| G2 falsifiability | Is there a minimal analytic falsifier and a deterministic verifier for every finite identity? | keep scouting; do not call the route deep |
| G3 target transfer | Would the core lemma actually yield a dimension-uniform `c>0` and the claimed update count without a hidden condition number? | branch at this implication edge |
| G4 depth | Are equality cases, singular limits, and at least two known route barriers handled analytically? | deepen or suspend with a concrete reopen condition |
| G5 hostile audit | Has a different run attacked all RPCD-specific failure modes? | retain `proof_candidate` at most |
| G6 reconstruction | Has another run rebuilt the statement without copying the proof, followed separately by priority/formalization review? | no theorem-candidate promotion |

Each route score has five integer components in `[0,2]`:
`target_transfer`, `counterexample_resistance`, `blocker_specificity`,
`falsifiability`, and `recent_information_gain`. The checked-in policy
recommends scouting at total score at least five and deepening at total score
at least eight, but both recommendations require positive target-transfer and
counterexample-resistance scores. Scores never raise an evidence level.

Use `python -m rpcd_harness route-plan` (or add
`--breadth-snapshot research/breadth_reviews/<current>.json`; the API is
`plan_route_allocation(routes, policy, effective_breadth=...,
breadth_review_kind=...)`) for the portfolio decision. It first
checks global breadth gates: missing realized sealed breadth, method-family
concentration, and concentration on configured stronger certificate claims such
as C051. Any such finding returns `expand_breadth` before considering local
scores. Once an Agent-generated sealed route is active, omitting a complete
current-frontier snapshot of kind `post_rollout_review` is itself a breadth
finding; a pre-rollout planning estimate cannot authorize depth. A value below
`portfolio.min_effective_breadth` is an explicit `expand_breadth` finding even
when the frontier has only one or two routes. Otherwise the planner scores only
deepest active frontier leaves. Every tied depth leader is returned, while any
reviewed Agent-generated direct-C050 scout is included as a protected mixed
allocation instead of being starved by high static scores on C051-sufficient
lines. The API deliberately has no hidden lexicographic tie-break.

## 4. Branch at the first bad edge

Verification walks from the deepest supplied artifact upward through
`parent_ids` to `L0`. The first implication that is unproved, false, or loses a
dimension-dependent factor is the first bad edge. Stop polishing downstream
algebra and open at least two distinguishable children there:

- a **repair child** that retains the information lost at that edge; and
- an **attack child** that tries to refute the exact edge on the smallest
  admissible family.

A third child is justified when it changes representation rather than a
constant. For example, failure of scalar Schur recovery may branch to an
anisotropic aggregate state; failure of scalar arc Hardy control may branch
to modewise Pythagorean increments. Merely increasing a numerical search grid
is not a new branch.

A `continuation_depth` task names exactly one active frontier node. Its result
must record `source_layer`, the immediately adjacent `next_layer`,
`parent_route_ids`, `first_bad_edge`, and `branch_kind`; a task may not attach
itself to an ancestor and skip the unresolved bridge. Import one selected child
through

```text
rpcd-harness route-import-continuation runs/<task>/<run>/result.json --avenue-index 0
```

The importer revalidates the result, requires the exact one-element parent,
the parent's actual source layer, and the adjacent next layer, then creates only
a `proposed/unreviewed` child with an immutable result hash. Continuation provenance
always records `independent_breadth_eligible=false`; when the invocation carries a
valid `resume_lineage` (`independence=false`, `eligible_for_fanout=false`), it also
records `resumed_from_checkpoint=true`. Thus cross-account continuation preserves
depth on the same branch and never manufactures a new breadth sample. It cannot
activate, merge, or hard-prune the generating worker's own branch.

If the edge is refuted exactly, mark that node `refuted` and preserve its
barrier. If only a particular proof loses a factor, branch or suspend; do not
claim that the underlying RPCD statement is false.

## 5. Merge, suspend, and prune

Merge only when two nodes are in the same layer, target the same claim, and have
the same normalized-exact representation, state/invariant, core lemma, and
target-transfer edge. Normalization only case-folds and collapses whitespace; it
does not infer semantic similarity. Failure prose, retained/discarded metadata,
and verifier implementation do not manufacture a new mathematical route. The merged node points
to `merge_target_id`; artifacts and provenance from both parents remain.
Independent proofs of the same candidate are not merged before they have
served the reconstruction gate.

Hard pruning requires one of:

- an exact or certified counterexample to the route's stated bridge lemma;
- a proof that its target transfer necessarily loses the required dimension
  factor; or
- logical duplication of a strictly stronger retained route.

The sealed-card importer never treats its generating worker's self-reported
refutation as this decision evidence. A later hostile critic or controlled
transition must attach the exact/certified witness before `refuted/hard_prune`.
The current controlled transition deliberately implements only the first,
machine-auditable case:

```text
rpcd-harness route-prune R150-example \
  runs/<review-task>/<review-run>/artifacts/prune-verdict.json
```

`schemas/route-prune-verdict.schema.json` requires a different reviewer, E2+
`exact_counterexample` or `certified_counterexample`, the exact route-local
statement, current route/card hashes, and `master_claim_affected=false`. The
reviewer strings are not trusted alone: the verdict and every certificate must
belong to a canonical completed, validated, standalone 120-minute reviewer run,
whose nine-hash attestation is stored in route provenance. The transition copies
and hashes the certificate artifacts into portable
`research/routes/certificates/`, hashes the verdict under
`research/routes/verdicts/`, and only then writes `refuted/hard_prune`.
Consequently editing a route JSON by hand cannot manufacture a valid prune.
The transition also refuses to prune a parent while proposed, active, or
completed dependent children still rely on it; those children must first be
resolved or suspended explicitly.
The other two logical prune cases remain suspended until an equally explicit
controlled transition is implemented; they are not authorization for a manual
status edit. A route-local counterexample never refutes C050.

A null search, a weak numerical margin, or two hours without progress permits
only `suspended`, with a nonempty and falsifiable `reopen_if`. Never delete a
failed route: its certificate is part of the research memory.

## 6. Active two-hour adaptation

The default worker floor is 120 measured subprocess minutes, with checkpoints
at most 30 minutes apart. The harness records wall-clock duration; it cannot
infer whether waiting inside a running subprocess was useful, so checkpoint
artifacts must demonstrate active progress.

- `0--20` minutes: freeze the route card, exact object, target edge, and two
  falsifiers. A continuation route instead reconstructs its inherited lemma.
- by `30` minutes: identify the first bad edge and run the cheapest exact or
  deterministic control.
- `30--60` minutes: pursue repair and attack children in parallel where
  possible; record information retained/discarded.
- by `60` minutes: rescore the node and choose `scout`, `deepen`, `branch`, or
  `suspend`; an early failed idea triggers another active branch rather than
  an idle wait.
- `60--90` minutes: develop the selected analytic core and attack singular or
  equality cases.
- `90--120` minutes: close reproducible artifacts, target transfer, hostile
  objections, and the next handoff. Recompute the portfolio concentration.

Reaching 120 minutes makes a decision eligible; it does not make a claim
true. A promising lemma also does not end the pass early: remaining time is
used for boundary cases, counterexamples, and transfer checks.

## 7. Effective breadth `B_eff`

Raw worker count overstates breadth when several agents use the same
representation. First collapse every active L1→L2→L3 chain to its deepest
eligible active frontier node; ancestor records on the same live branch are not
additional width. For those frontier routes choose nonnegative next-checkpoint weights
`w_i` and a symmetric similarity matrix `S` with `S_ii=1` and
`0<=S_ij<=1`. Use route signatures, not writing style, to score similarity:

- `0`: different representation, invariant, and bridge lemma;
- `1/4`: only the level-zero target is shared;
- `1/2`: one of representation or invariant is shared;
- `3/4`: the same core lemma is attacked by materially different proofs;
- `1`: equivalent signatures that should be merged.

Define

```text
B_eff = (sum_i w_i)^2 / sum_(i,j) w_i w_j S_ij.
```

Equal independent routes give their route count; identical routes give one.
This is a portfolio heuristic, not an independence probability or a proof
confidence. Record the weights and full similarity matrix. When at least
three viable routes exist but `B_eff<3`, add a statement-only sealed route in
the least represented method family or merge duplicates before allocating
more depth. No single method family may consume more than 60% of active
`L1--L3` routes. Likewise, no configured stronger proxy certificate (currently
C051) may consume more than 60%; this prevents several distinct techniques from
being mistaken for target-level breadth when all depend on the same overstrong
sufficient claim.

Machine-readable reviews use `schemas/breadth-snapshot.schema.json` and must
include every diagonal and unordered off-diagonal pair with a textual
rationale. Run `python -m rpcd_harness route-breadth SNAPSHOT.json` to recompute
the value. The harness deliberately does not infer similarities from prose or
embeddings: hidden automatic clustering would make the width score less
auditable than the routes it is meant to summarize. Portfolio counting uses
active frontier leaves, so an L1→L2→L3 depth chain contributes one live branch,
not three units of width.

## 8. Current RPCD route portfolio

| Architecture | First live bridge | Required anti-shortcut |
|---|---|---|
| Bellman/Schur | general directional `W4`, then a stable growing-depth state | no spectral-only or rowwise scalar Schur recovery |
| conditional frame | cycle-averaged signed arc covariance and Pythagorean gain | no pathwise, reversal-only, or scalar Hardy closure |
| spectral stitching | full low-layer Loewner shorting with cross blocks | no compression-only or endpoint scalar interpolation |
| sealed escape fanout | covariance block powers, exchangeable coupling, noncommutative moments, or adaptive cone duality | no inherited-history anchoring before the card and no silent reduction to C051 |

The first three inherit audited Iteration 6 artifacts. The fourth consists of
four distinct statement-only rollouts as breadth escape routes. Cross-route merging is
allowed only at an explicit shared bridge; agreement on the final target is
not itself a reason to merge.

## 9. Portable handoff checklist

Every route decision must leave:

1. its route JSON and immutable card hash when sealed;
2. the exact first bad edge and decision;
3. proof/counterexample status with evidence level;
4. commands, seeds, tolerances, margins, and verifier class;
5. failed children and `reopen_if` conditions;
6. target-transfer calculation in epochs and coordinate updates;
7. updated route signature and the inputs needed by the next account.

No route handoff includes `.codex/`, `auth.json`, `.env*`, cookies, API keys,
or account/session identifiers.
