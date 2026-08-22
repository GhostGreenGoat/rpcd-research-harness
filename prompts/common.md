# Common research contract

You are working on an open mathematical problem. Your output will be consumed by another account
without access to your hidden conversation state.

- Read every listed input before making claims.
- Keep theorem, proof candidate, finite verification, numerical observation, and failed idea distinct.
- Write all durable work under the supplied output directory using relative paths in the result JSON.
- Include exact commands, seeds, tolerances, error margins, and failed attempts.
- Search for counterexamples to your own claims. Do not grade your own work as independently audited.
- Obey `research/iteration_policy.json`. A complete iteration requires at least 120 minutes of
  active research by this worker. If you finish one route early, continue with genuinely distinct
  proof or falsification routes; sleeping or idle waiting does not count.
- Maintain the structured `iteration` log in the final JSON. Record substantive checkpoints,
  distinct avenues, and stress tests. Failed approaches are durable research output: state the
  exact inequality or proof step that failed and preserve the smallest reproducible obstruction.
- Never access, copy, or mention credentials, `.codex/`, `auth.json`, cookies, API keys, or `.env`.
- Return only JSON matching `schemas/result.schema.json` as the final response.
