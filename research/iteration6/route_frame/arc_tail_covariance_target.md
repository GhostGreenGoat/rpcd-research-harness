# Minimal arc-tail covariance inequality

Status: exact reduction to one dimension-free matrix inequality, together
with a sharp barrier to scalar Hardy/Cauchy closure.  The inequality itself
is open.

Use the cyclic notation of `cyclic_cut_freezing.md`.  For a fixed directed
cycle define row matrices

```
b_(j,s)=sum_(delta=s)^m
        C_(j-delta,j) d_(j-delta)^circ,
        1<=s<=m.                                         (A1)
```

The exact dual-tail covariance averaged over its `n` cuts is

```
S_cycle:=E_cut[T_cut^TT_cut]
        =(1/n)sum_j sum_(s=1)^m b_(j,s)^T b_(j,s).        (A2)
```

Let

```
S=E_cycle[S_cycle],   P=E_pi[D_pi^TD_pi].                (A3)
```

Since `M^TR=D+T`, the parameterized matrix square inequality gives, for
every `eta>0`,

```
Q=E[(D+T)^T(D+T)]
 <=(1+eta)P+(1+1/eta)S.                                 (A4)
```

Consequently the concrete dimension-free tail estimate

```
S<=C_tail P                                               (A5)
```

would imply

```
Q<=(1+sqrt(C_tail))^2P,
PQ^-1P >=P/(1+sqrt(C_tail))^2.                           (A6)
```

Combined with any generic local-frame preconditioner lower bound
`P>=c_P mu A^-1`, (A6) proves the desired update order with the explicit
constant `c_P/(1+sqrt(C_tail))^2`.  Thus (A5) is a smaller and more transparent
covariance target than the original `Q<=(C/mu)PAP`: it involves only the
frozen cyclic local rows and nested arc sums.

## Why a scalar Hardy bound cannot prove (A5)

For arbitrary row-vector coefficients `a_delta`, Cauchy gives

```
sum_(s=1)^m ||sum_(delta=s)^m a_delta||^2
 <=sum_delta [delta(m+1)-delta(delta+1)/2] ||a_delta||^2
 <=m sum_delta delta ||a_delta||^2.                      (A7)
```

After the `1/n` normalization this still has a coefficient of order `m`,
not a numerical constant.  This loss is intrinsic to the arc kernel alone:
if all `a_delta=a`, then the left side is exactly

```
m(m+1)(2m+1)||a||^2/6,                                  (A8)
```

whereas `sum_delta||a_delta||^2=m||a||^2`.  Since
`m=Theta(n)`, the ratio after division by `n` is `Theta(n)`.

The equal-coefficient sequence in (A8) is not asserted to arise from an SPD
local inverse.  It is an exact proof-method barrier: (A5) must exploit the
Gram/Bessel constraints linking `C_(i,j)` and `d_i^circ`, plus the random
cycle, rather than treating the arc coefficients independently.

## Generic closure for complement size at most two

The Schur constraint is already enough when the cyclic complement has at
most two labels.  If `m=1` (exactly `n=4,5`), (A2) has no cross-row term and

```
S_cycle=(1/n)sum_i C_(i,j_i)^2(d_i^circ)^Td_i^circ.
```

The residual Schur bound gives `C_(i,j_i)^2<=1-mu`.  Averaging cycles turns
`(1/n)sum_i(d_i^circ)^Td_i^circ` into the window increment `A_(q+1)`, while
the exact frame identity has

```
P=J_q+(n-q)A_(q+1)>=2A_(q+1).
```

Therefore

```
S<=(1-mu)P/2<=P/2.                                      (A8a)
```

If `m=2` (exactly `n=6,7`), write the two nested coefficients as `a_1,a_2`.
The exact two-layer nested-square operator has scalar Gram matrix
`[[1,1],[1,2]]`, whose largest eigenvalue is `(3+sqrt(5))/2`.  Hence

```
(a_1+a_2)^T(a_1+a_2)+a_2^Ta_2
 <=[(3+sqrt(5))/2](a_1^Ta_1+a_2^Ta_2).                  (A8b)
```

For each cyclic row, its two correlations form `c_i`; since the complement
principal matrix has largest eigenvalue at most its trace two,

```
||c_i||^2<=2 c_i A_O^-1c_i^T<=2(1-mu).
```

Now `n-q=3`, so averaging (A8b) yields

```
S<=(3+sqrt(5))(1-mu)A_(q+1)
 <=[(3+sqrt(5))/3](1-mu)P <(7/4)P.                     (A8c)
```

Thus the generic arc covariance target holds with `C_tail=1/2` for
`n=4,5`, and with `C_tail=7/4` for `n=6,7` (`n<=3` has no tail).  This is a
finite-dimensional analytic proof candidate; it does not provide a
dimension-uniform argument because the bare nested-square constant grows
with `m`.

The next genuinely minimal analytic question is therefore whether those
local-solve constraints force (A5) with a universal constant after cycle
averaging.  This is the unresolved multirow frame cancellation in its most
compressed form.

## Exact diagonal/cross decomposition of the remaining target

Expanding the Brownian arc kernel `min(delta,delta')` in (A2) separates a
diagonal contribution

```
S_diag=(1/n) E_cycle sum_i sum_(delta=1)^m
             delta C_(i,i+delta)^2 (d_i^circ)^T d_i^circ. (A19)
```

There is a useful exact conditional averaging statement here.  Condition on
the label `i`, its **ordered** `q` predecessors, and the unordered complement
set `O`; then `d_i^circ` and the residual vector
`c_i=(C_(i,j):j in O)` are fixed, while the cyclic order of `O` is uniform.
Therefore

```
E[sum_delta delta C_(i,i+delta)^2 | i,past,O]
       =[(m+1)/2] ||c_i||_2^2.                          (A20)
```

The local Schur residual lemma gives the exact pointwise constraint

```
||c_i||_2^2
 <=lambda_max(A_O)c_i A_O^-1c_i^T
 <=lambda_max(A_O)(1-mu||d_i^circ||_2^2).               (A21)
```

Equations (A19)--(A21) isolate why neither a scalar row sum nor successor
randomization alone closes (A5): `lambda_max(A_O)` can be as large as `m`.
The off-diagonal part is the signed sum of
`min(delta,delta') C_(i,j)C_(k,j) Sym(d_i^T d_k)` over two source rows ending
at the same target.  Its coefficients and rows are jointly adapted to the
cycle, so the fixed-coefficient random-rank identity cannot simply be
conditioned and applied.  A generic proof must control (A21) mode-by-mode
*and* retain this off-diagonal cancellation; discarding either recreates a
factor of order `m`.

One conditional slice does follow immediately.  If all complement principal
blocks encountered in the averaging satisfy `lambda_max(A_O)<=Lambda`, then
using `||d_i^circ||>=1`, (A20), (A21), and
`P>= (m+1)A_(q+1)` gives

```
S_diag <=[Lambda(1-mu)/2]P.                              (A22)
```

Thus the diagonal arc energy is already dimension-free in every bounded
complement-spectrum regime.  What remains even there is the signed
off-diagonal source-row covariance.  Conversely, any global argument must
replace the worst-case `Lambda=Theta(m)` in (A22) by a modewise residual
decay, as happens explicitly for positive equicorrelation.

## Exact validation on positive equicorrelation

The minimal inequality does close cleanly on the positive-equicorrelation
control family.  Let

```
A=(1-rho)I+rho J,   mu=1-rho,   0<rho<1.
```

Every cyclic local row is a shift of

```
d=(1,-rho,-rho mu,...,-rho mu^(q-1)),
```

and every complement correlation is the same scalar

```
c_0=rho mu^q.                                            (A9)
```

For `ell=m-s+1`, (A1) is `c_0` times a sum of `ell`
consecutive cyclic shifts of `d`.  Therefore

```
lambda_parallel(S)
 =c_0^2 mu^(2q)/n sum_(ell=1)^m ell^2,                   (A10)

tr(S)
 <=c_0^2 ||d||^2 sum_(ell=1)^m ell^2.                   (A11)
```

Use

```
c_0m<=rho q mu^q<=1/e,
||d||^2<2,
sum_(ell=1)^m ell^2<=m^3,
2m<n-1.
```

The averaged linear frame has
`lambda_parallel(P)>=mu^(2q)` because every row sum is at least `mu^q`,
and `lambda_transverse(P)>=1` because every row has diagonal coefficient
one while its row sum is at most one.  Equations (A10)--(A11) now give

```
lambda_parallel(S)/lambda_parallel(P) <=1/(2e^2),
lambda_transverse(S)/lambda_transverse(P) <1/e^2.         (A12)
```

Hence (A5) holds on the whole family with `C_tail=1/e^2`.  Substitution in
(A6) recovers

```
Q<=(1+1/e)^2P,                                           (A13)
```

the finite equicorrelation covariance constant previously obtained by a
pathwise norm argument.  This does not enlarge the solved matrix class, but
it validates that the arc-tail target has the correct scale and loses no
essential constant on a sharp control family.

The same architecture gives a finite constant for **negative**
equicorrelation, which was not covered by the positive-family pathwise tail
bound.  Write `rho=-t`,

```
0<t<1/(n-1),   a=1+t.
```

Now the cyclic row sums are `a^q` and `|c_0|=t a^q`.  The elementary bound

```
(1+1/(n-1))^q<2   (n>=4)                                (A14)
```

follows by checking `n=4,5` and monotonicity separately on the even and odd
subsequences.  Explicitly, the logarithmic derivative of
`(1+1/(2x-1))^x` is
`log(1+1/(2x-1))-1/(2x-1)<0`; for
`(1+1/(2x))^(x+1)` it is
`log(1+u)-u(1+2u)/(1+u)<0`, `u=1/(2x)`.  It implies

```
|c_0|m<1,
||d||^2=1+[t/(2+t)](a^(2q)-1)<3/2.                       (A15)
```

For the averaged linear frame, `p_parallel>=1`.  Moreover, putting
`gamma=t/(2+t)`, the exact trace relation is

```
tr(P)=n(1-gamma)+gamma n p_parallel.
```

Since `n gamma<1` and `p_parallel<=a^(2q)`, this gives

```
p_transverse >=[n-a^(2q)]/(n-1)>=1/4.                   (A16)
```

For the last inequality, (A14) gives `a^(2q)<4` for `n>=5`; the `n=4`
endpoint is the exact comparison `(4/3)^4<13/4`.

Equations (A10)--(A11), now with `mu^q` replaced by `a^q`, yield

```
S_parallel/P_parallel<2,
S_transverse/P_transverse<3,
```

and therefore

```
S<=3P.                                                    (A17)
```

Using `eta=2` in (A4) gives `Q<=(15/2)P`.  The spectral eigenvalues of the
negative-equicorrelation matrix are `mu=1-(n-1)t` in the parallel direction
and `a` transversely.  From `p_parallel>=1` and (A16),

```
P>=(mu/4)A^-1,
PQ^-1P >=(2/15)P >=(mu/30)A^-1.                          (A18)
```

Thus the half-memory conditional-tail route proves a finite
`O(n/mu log(1/epsilon))` certificate on all negative equicorrelation
matrices and, by diagonal-sign conjugation, on all their signed conjugates,
albeit with a deliberately loose constant.  This is a
structured-family proof candidate, not the generic matrix inequality.
