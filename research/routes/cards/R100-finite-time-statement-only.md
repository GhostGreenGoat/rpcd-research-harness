# Minimal RPCD finite-time statement for sealed search

For every real unit-diagonal SPD matrix `A`, let
`mu=lambda_min(A)`. Each RPCD epoch draws a fresh independent uniform
permutation `pi=(pi_1,...,pi_n)`. With
`U_i=I-e_i e_i^T A`, define the epoch map in update order by
`T_pi=U_{pi_n}...U_{pi_1}` and the epoch-boundary iterate by
`x_{k+1}=T_{pi^(k)}x_k`, where the epoch permutations `pi^(k)` are fresh and
independent. Seek
universal numerical constants `c,C>0` and a mathematical
argument implying

```text
E ||x_k||_A <= C exp(-c mu k) ||x_0||_A
```

for every initial point and every epoch count `k`. One epoch consists of `n`
coordinate updates, so this is the desired
`O((n/mu) log(1/epsilon))` update complexity. The quantity is expectation of
distance, not distance of the expected iterate.

Before any derivation history is revealed, choose a mathematical
representation and write `route_card.json` containing:

1. the representation and retained state or invariant;
2. one falsifiable core lemma and its exact implication to the target;
3. information deliberately retained and discarded;
4. a predicted first failure edge;
5. an analytic falsifier capable of rejecting that edge.

No proof family is prescribed by this statement. Numerical null searches may
select or prune a route but cannot certify a general claim.
