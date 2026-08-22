# Common research contract

You are working on an open mathematical problem. Your output will be consumed by another account
without access to your hidden conversation state.

- Read every listed input before making claims.
- Keep theorem, proof candidate, finite verification, numerical observation, and failed idea distinct.
- When a task enables strict claim binding, a `claims` entry must reproduce the canonical claim
  title and `statement_ref` from its registry JSON. Put route-local lemmas and counterexamples in
  the route/avenue record unless they have their own claim ID; never relabel one as C001/C050/C051.
- Write all durable work under the supplied output directory using relative paths in the result JSON.
- Include exact commands, seeds, tolerances, error margins, and failed attempts.
- Search for counterexamples to your own claims. Do not grade your own work as independently audited.
- Obey `research/iteration_policy.json`. The harness records at least 120 minutes of Codex
  subprocess wall-clock for a complete iteration; it cannot detect sleep or tool waiting inside a
  pass, so substantive checkpoints and artifacts—not elapsed time alone—must demonstrate active
  research. If a route fails early, follow the assigned mode: branch at its first bad edge during
  continuation depth, or keep independent rollout boundaries during sealed breadth.
- Maintain the structured `iteration` log in the final JSON. Record substantive checkpoints,
  distinct avenues, and stress tests. Failed approaches are durable research output: state the
  exact inequality or proof step that failed and preserve the smallest reproducible obstruction.
- Never access, copy, or mention credentials, `.codex/`, `auth.json`, cookies, API keys, or `.env`.
- Use analytic construction, exact arithmetic, or formal checks for decisive pruning whenever
  possible. Numerical scans are scouts and regressions, not substitutes for a quantified argument.
- Return only JSON matching `schemas/result.schema.json` as the final response.
