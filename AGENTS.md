# RPCD research protocol

This repository studies an open mathematical problem. Treat every assertion as a
claim with an evidence level, not as a theorem by default.

1. Read `research/problem.md`, the assigned JSON task, and its role prompt.
2. Put task-specific work under the output directory supplied in the prompt.
3. Never promote numerical exploration to a theorem. Use the evidence ladder in
   `docs/METHOD.md` and state all quantifiers and assumptions.
4. Record failed approaches, counterexample searches, commands, seeds, tolerances,
   and unresolved objections. A null search result is not a proof.
5. Proof candidates require a hostile audit by a different run and an independent
   reconstruction before they may be called theorem candidates.
6. Do not edit or copy account credentials, `.codex/`, `auth.json`, or `.env` files.
7. Prefer exact algebra or certified finite statements; label floating-point checks
   as numerical evidence even when their margins are large.
8. Do not cite priority from memory. Use primary sources and give URLs, versions,
   dates, and the exact claim each source supports.
