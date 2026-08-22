# RPCD research protocol

This repository studies an open mathematical problem. Treat every assertion as a
claim with an evidence level, not as a theorem by default.

The master target is `C050`, the finite-time expectation-of-distance bound.
`C051` is a stronger sufficient `K(A)` certificate and `C001` is the related
original asymptotic covariance-rate conjecture.  The recorded implications are
not equivalences; never substitute one statement for another without proving
the missing finite-time bridge.

1. Read `research/problem.md`, the assigned JSON task, and its role prompt.
   For a `sealed_breadth` task, obey the staged allowlist until the immutable
   route card is hashed; do not search for inherited proofs or failure maps
   before the harness reveals them.
2. Put task-specific work under the output directory supplied in the prompt.
3. Never promote numerical exploration to a theorem. Use the evidence ladder in
   `docs/METHOD.md` and state all quantifiers and assumptions.
4. Record failed approaches, counterexample searches, commands, seeds, tolerances,
   and unresolved objections. A null search result is not a proof.
5. Proof candidates require a hostile audit by a different run and an independent
   reconstruction before they may be called theorem candidates. A separate
   domain expert must check that the mathematical and formal specifications
   match, and priority/novelty review is a different gate from proof correctness.
6. Do not edit or copy account credentials, `.codex/`, `auth.json`, or `.env` files.
7. Prefer exact algebra or certified finite statements; label floating-point checks
   as numerical evidence even when their margins are large.
8. Do not cite priority from memory. Use primary sources and give URLs, versions,
   dates, and the exact claim each source supports.
9. Record the route ID and its mathematical signature. Branch at the first bad
   implication edge; route scores and portfolio breadth are allocation signals,
   not mathematical evidence.
10. Treat task-declared verifiers as trusted repository code. Their shell-free
    runner and path checks reduce accidents but do not sandbox hostile code, and
    a PASS supports only the statement and finite scope actually checked. Use
    preflight checks for cheap pruning and final checks for candidate artifacts;
    sealed breadth reveals preflight checks only after its route card is locked.
11. A staged or sealed working directory is an intellectual-context control,
    not an operating-system security boundary. Do not probe outside the declared
    context, and never rely on staging to protect local credentials.
12. Fanout rollouts must have distinct worker labels and method families. Keep
    their lineage and failures separate until an explicit route merge or an
    independent reconstruction gate justifies combining them.
