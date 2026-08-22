# Audit: pole--simplex three-halves refinements

**Scope:** Equations (8.35)--(8.42) of
`docs/ITER4_T080_REVERSE_PAIR_SUBROUTE.md`, after the separately audited asymptotic upper bound.

**Outcome:** the exact energy rewrite, the all-\(k\) subcase \(a^2\le1/k\), and the fixed-\(t\)
first correction pass independent reconstruction. The finite Bernstein patterns were regenerated
exactly. The all-\(k\) positive-correlation claim and the two-scale remainder remain proof-draft
material, not audited theorems.

## 1. Exact energy and the negative-correlation subcase

Put \(t=a^2\), \(q=1-\rho=k(1-t)/(k-1)\),
\(S_m=\sum_{r<m}q^r\), and \(T_m=\sum_{r<m}q^{2r}\). Then

\[
 {1-q^m\over\rho}=S_m,
 \qquad {1-q^{2m}\over1-q^2}=T_m.
\]

Moreover

\[
 2-q^m-tS_m=1+(\rho-t)S_m=1-{q\over k}S_m,
\]

because \(\rho-t=-q/k\). This reconstructs

\[
 E_{m,\ell}=1+tT_m+(tS_m-2)^2
 +t(1-qS_m/k)^2T_\ell.                                  \tag{R1}
\]

If \(t\le1/k\), write \(t=(1-x)/k\),
\(q=1+x/(k-1)\), \(0\le x\le1\). Since

\[
 tS_m\le(1-x)(1+x/(k-1))^{k-1}\le(1-x)e^x\le1
\]

and \(T_m\ge S_m\), setting \(X=tS_m\) in (R1) gives

\[
 E_{m,\ell}\ge1+X+(2-X)^2=3+(1-X)(2-X)\ge3.
\]

Thus \(\lambda_{k,a}\ge3/2\) is proved word by word for \(a^2\le1/k\), with no
floating-point step.

## 2. Independent derivation of the fixed-\(t\) correction

Fix \(t\in(0,1)\), let \(h=1/k\), and put
\(q=(1-t)/(1-h)\). Away from the two finite-gap boundaries, replace the geometric sums in (R1)
by their infinite limits. Half the derivative at \(h=0\) of this typical word energy is

\[
 { (t-1)(t^2-3t+4)\over t(t-2)^2}.                       \tag{R2}
\]

The uniform composition law has
\(\Pr(m=j)=\Pr(\ell=j)=(k-j+1)/\binom{k+2}{2}=2/k+O(k^{-2})\) for fixed \(j\).
At \(h=0\), summing the finite-\(m\) and finite-\(\ell\) boundary deviations gives

\[
 -{2\over t(2-t)^2}+{2\over t}+{1\over t(2-t)}
 ={2t^2-9t+8\over t(t-2)^2}.                             \tag{R3}
\]

The intersection where both gaps stay finite has probability \(O(k^{-2})\). Adding (R2) and
(R3) yields

\[
 {2-t^2\over t(2-t)},                                    \tag{R4}
\]

which reconstructs the claimed \(1/k\) coefficient in

\[
 \lambda_{k,\sqrt t}=1+{1\over2-t}
 +{2-t^2\over t(2-t)}{1\over k}+O_t(k^{-2})+O_t(q^k).
\]

The coefficient is strictly positive. This audit checked the coefficient and boundary-layer
normalization; a fully quantified remainder remains part of the proof draft.

## 3. Exact finite patterns and remaining blocker

`scripts/iter4_t080_pole_simplex_three_halves_scout.py` regenerates with exact rational arithmetic:

- \(\lambda_{k,a}>3/2\) for \(2\le k\le15\);
- \(\lambda_{k,a}\ge1+1/(2-a^2)\) for \(2\le k\le15\);
- \(\lambda_{k,a}\ge\lambda_{k+1,a}\) for \(2\le k\le12\).

The artifact is
`research/evidence/ITER4_T080_POLE_SIMPLEX_THREE_HALVES_SCOUT_2026_08_21.json`. These are finite
certificates only. The same artifact contains an exact cyclic-gap counterexample blocking a
pointwise cyclic-orbit proof. No all-\(k\) Bernstein formula or coupling has been obtained.
Consequently the positive-correlation all-\(k\) lower bound, the two-scale expansion with a
controlled uniform remainder, and universal \(K_0\succeq(3/2)P_{\ker C}\) remain open.
