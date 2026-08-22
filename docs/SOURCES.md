# Source audit for harness design

As-of date: 2026-08-19 (Asia/Shanghai).

## Anthropic Riemann-zeta project

Primary page: <https://www.anthropic.com/research/riemann-zeta>, published 2026-08-10.

Scope correction: the project did **not** prove the Riemann hypothesis. It reports an improvement in
the proved lower bound for the fraction of nontrivial zeta zeros on the critical line, from 41.6% to
67.2%.

Process facts used by this harness:

- two main Claude Code sessions and roughly 31 million output tokens;
- an initial breadth phase tried about 650 ideas without success;
- a subsequent coordinated phase used roughly 60 subagents, about 2,400 shell commands and hundreds
  of Python scripts;
- thousands of numerical checks against known zeta zeros;
- agents reviewed one another, followed by adversarial proof review and counterexample search;
- a priority search downloaded 54 arXiv papers;
- an independent proof was reconstructed from scratch, followed by Lean formalization and human
  mathematical review.

The harness copies the loop, not Anthropic's scale or any claim that volume guarantees correctness.

## Reference Codex reproduction repository

Repository: <https://github.com/EMOAIRX/constant-error-ordinary-dynamic-approximate-membership>

Inspected commit: `431171a8775cd61300e65d91124f4ca46bfab3f1` (2026-08-18).

Mechanisms reused:

- explicit tables separating external theorem, repository theorem, conditional theorem, class-only
  optimum, structural theorem and numerical exploration;
- dedicated hostile proof audits, counterexample reports, priority audits, theorem packages and
  new-thread handoff documents;
- separate `search_*`, `explore_*` and `verify_*` programs;
- a reviewer-safe rule that a result enters the theorem table only when finite statement, error/
  quantifier semantics and hostile audit all close;
- compact verifier entry points that fail on the first broken certificate.

No code was copied from the reference repository; the RPCD linear algebra and portable task layer in
this project were implemented independently.

## RPCD primary source and open-status search

Primary paper: Donghwa Kim, Jaewook Lee, Chulhee Yun, *Provable Benefit of Random Permutations over
Uniform Sampling in Stochastic Coordinate Descent*, ICML 2025,
<https://proceedings.mlr.press/v267/kim25x.html>, arXiv version
<https://arxiv.org/abs/2505.23152> (first submitted 2025-05-29).

The paper proves a gap for a permutation-invariant Hessian class and labels the general unit-diagonal
SPD statement as Conjecture 4.1. Searches for the exact conjecture text, title citations, RPCD general
quadratics and 2026 follow-ups found no primary source claiming a general proof or certified
counterexample. This is a dated search conclusion, not a proof of absence; task T001 must periodically
repeat it.

Earlier context includes:

- Sun, Luo, Ye, *On the Efficiency of Random Permutation for ADMM and Coordinate Descent*, first
  preprint 2015, journal 2020: <https://arxiv.org/abs/1503.06387>.
- Gurbuzbalaban, Ozdaglar, Vanli, Wright, *Randomness and Permutations in Coordinate Descent Methods*,
  2018: <https://arxiv.org/abs/1803.08200>.

## Iteration 2 projection-algebra sources

- A. Galantai, *On the rate of convergence of the alternating projection method in finite
  dimensional spaces*, JMAA 310 (2005), 30--44,
  <https://doi.org/10.1016/j.jmaa.2004.12.050>.  This is the classical source used for the
  Meany/Gram-determinant alternating-projection estimate; the bound itself is not a harness novelty.
- Liang Dai and Thomas B. Schon, *On the exponential convergence of the Kaczmarz algorithm*,
  arXiv:1411.4017v2 (2015), <https://arxiv.org/abs/1411.4017>.  Section III-A restates the square,
  normalized-row form `rho^2 <= 1-product_i sigma_i(B)^2` used to cross-check the specialization.
- Zehua Lai and Lek-Heng Lim, *Recht-Re Noncommutative Arithmetic-Geometric Mean Conjecture is
  False*, ICML 2020, <https://arxiv.org/abs/2006.01510>.  This supports only the generic
  noncommutative-AM--GM barrier from degree five onward; it does not refute the special RPCD tensor
  inequality or the upper Loewner half needed here.
- Benjamin Recht and Christopher Re, *Beneath the Valley of the Noncommutative
  Arithmetic-Geometric Mean Inequality: Conjectures, Case-Studies, and Consequences*, 2012,
  <https://arxiv.org/abs/1202.4184>.  This is the original without-replacement projection/least-
  squares AGM architecture; it is background for the Iteration-6 projection-superoperator lift,
  not a proof of its weaker structured gap.
- Deren Han and Jiaxin Xie, *A Simple Linear Convergence Analysis of the Randomized Reshuffling
  Kaczmarz Method*, arXiv v1 2024, revised 2025,
  <https://arxiv.org/abs/2410.01140>.  Its reshuffling rate is controlled by an instance-specific
  maximum product norm.  It does not quantify that norm solely by the lifted frame floor `mu`, so
  it does not close claim C001 or the Iteration-6 projection gap.

The harness-specific deductions `rho(M_A)<=1-det(A)`, the `n=2` corollary, and the explicit
high-`sigma` region are recorded as C023 proof candidates pending an independent priority audit.

## Codex execution and authentication

Official Codex documentation used for the adapter:

- Non-interactive execution and JSONL events:
  <https://developers.openai.com/codex/noninteractive/>.
- Authentication and credential handling:
  <https://developers.openai.com/codex/auth/>.

The adapter uses `codex exec --json`, a JSON output schema and a saved final result. It deliberately
does not copy `auth.json`; the official documentation treats that file as credential material. Each
account authenticates locally, while Git/zip/checkpoint artifacts carry the research state.
