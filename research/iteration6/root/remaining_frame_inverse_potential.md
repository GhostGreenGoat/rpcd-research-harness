# Remaining-frame inverse potential

Status: **refuted**, both for arbitrary projections and for the special RPCD
covariance-lift family.  The six-vector example in Section 4 closes the
universal form; the exact lifted example summarized in Section 5 closes the
intended structured form.  The inequality is nevertheless valid for one and
two arbitrary projections.

Let `Q_i` be orthogonal projections on a finite-dimensional real Hilbert
space, `P_i=I-Q_i`, and for a nonempty remaining set `U` put

```
F_U=sum_(i in U) Q_i,        H_U=(I+F_U)^-1.              (R1)
```

## 1. The dynamic inequality

The desired one-step Bellman inequality is

```
(1/|U|) sum_(i in U) P_i H_(U\{i}) P_i <= H_U.            (R2)
```

If (R2) holds, apply it successively to a uniform random permutation.  At
the empty set `H_empty=I`, so

```
E||P_(pi_n)...P_(pi_1)x||^2
 <= <x,(I+sum_i Q_i)^-1 x>.                               (R3)
```

For the lifted RPCD projections in `projection_lift.md`,
`sum_iQ_i>=mu I`.  Therefore (R3) would give

```
E||P_pi x||^2 <=(1+mu)^-1||x||^2,                         (R4)
```

and hence an unrestricted `O(n/mu log(1/epsilon))` finite-time bound.  Thus
(R2) is strong enough to solve the requested order, even though it does not
claim the sharp RPCD rate.

## 2. Equivalent leave-one-out form

Writing `m=|U|` and `F=F_U`, (R2) is exactly

```
(1/m) sum_i P_i (I+F-Q_i)^-1 P_i <=(I+F)^-1.              (R5)
```

Since `I+F-Q_i=F+P_i`, the summands also satisfy the parallel-sum identity

```
P_i(F+P_i)^-1P_i=P_i-(P_i:F),                             (R6)
```

where `:` is the Anderson--Duffin parallel sum.  This form exposes why joint
concavity alone has the wrong direction: it gives an upper, not the needed
lower, control on `sum_i(P_i:F)`.

## 3. Exact base cases

- `m=1`: the left side is `P_1`, while
  `(I+Q_1)^-1=P_1+Q_1/2`.
- `m=2`: Halmos's two-projection decomposition reduces the only noncommuting
  part to a two-dimensional principal-angle block.  With the rational angle
  parametrization
  `cos(theta)=(1-t^2)/(1+t^2)`, `sin(theta)=2t/(1+t^2)`, the leading
  principal minor and determinant of the right-minus-left gap are

  ```
  [t^12+4t^10+11t^8+32t^6+11t^4+4t^2+1]
   /[(1+t^2)^4(t^2+3)(3t^2+1)],

  t^2(t^6+t^4+5t^2+1)(t^6+5t^4+t^2+1)
   /[(1+t^2)^6(t^2+3)(3t^2+1)].                           (R7)
  ```

  Both are nonnegative for `t>=0`, proving (R5) for two arbitrary
  orthogonal projections.

## 4. Exact rank-one counterexample at six projections

The general Bellman conjecture (R5) already fails for six rank-one
projections.  Let `Q_i=u_i u_i^T`, where the six unit vectors have Gram
matrix

```
G=U^T U=(I+J)/2.
```

This Gram matrix is positive definite, so such vectors exist.  Put
`R=(I+G)^-1`.  A direct Sherman--Morrison expansion shows that for an
arbitrary rank-one frame, (R5) is equivalent to

```
Diag(diag R) >= (I-R)^2.                                (R8)
```

Indeed, for a test vector `x`, write
`p_i=<u_i,x>`, `q_i=<u_i,(I+UU^T)^-1x>`, and
`a_i=<u_i,(I+UU^T)^-1u_i>`.  The sum of the scalar gaps is

```
sum_i [2p_iq_i-a_i p_i^2-q_i^2]/(1-a_i),
```

and Woodbury plus congruence by `I+G` reduces this exactly to (R8).

For the displayed `G`, the parallel and transverse eigenvalues of `R` are
`2/9` and `2/3`, while every diagonal entry is `16/27`.  Hence on the
all-ones direction the right-minus-left gap in (R8) is

```
16/27-(1-2/9)^2 = -1/81.                               (R9)
```

This is a fully analytic obstruction, not a numerical near miss.  It closes
the universal projection-family route.  By itself it does **not** refute the
RPCD claim because the lifted projections in `projection_lift.md` have a
more rigid quadratic form; the next section checks that restriction
separately.

## 5. The special covariance-lift form also fails

The restriction of (R5) to the intended RPCD lift is false as well.  Take

```
n=9,       A=(I+J)/2,       mu=1/2,
v_i=(e_0+e_i)/sqrt(2).
```

Then the rational projectors
`R_i=(e_0+e_i)(e_0+e_i)^T/2` realize the Gram matrix `A`, and

```
Pi_i(X)=(I-R_i)X(I-R_i),       Q_i=Id-Pi_i
```

are exactly the rank-nine RPCD covariance-lift projections on `Sym(span
{v_i})`.  An exact `S_8` symmetry reduction gives a two-dimensional standard
block of the Bellman gap whose determinant is

```
-121894976/123981.
```

More explicitly, the rational test matrix specified by coefficient vector
`(-132,125,1,1)` in the invariant basis of the independent audit satisfies

```
<X, [H_U-(1/9)sum_i Pi_i H_(U\i)Pi_i] X>
 =-2422114/12155<0.                                    (R10)
```

The full ambient inverse residuals were checked exactly; this is not an
artifact of compressing the operators.  See
`../route_frame/special_lift_bellman_counterexample.md` and its verifier.
This closes the inverse-potential route, while leaving the actual RPCD epoch
rate untouched.

## 6. A closed shortcut

A tempting sufficient estimate is

```
P:F >=[P phi(F)+phi(F)P]/2,  phi(F)=F(I+F)^-1.           (R11)
```

It is exactly false already on the same two-dimensional block: its gap
determinant is

```
-t^2(t-1)^2(t+1)^2/[(t^2+3)^2(3t^2+1)^2].               (R12)
```

The termwise parallel-sum/anticommutator comparison is therefore closed
independently of the stronger counterexamples above.

## 7. Evidence boundary

The earlier small scout in `scripts/iter6_remaining_frame_inverse.py`
missed the structured six-vector obstruction, illustrating why the exact
family reduction is more informative than broader random testing.  The
two-projection certificate is generated by
`scripts/iter6_remaining_frame_inverse_symbolic.py`; the exact
counterexample is generated by
`scripts/iter6_remaining_frame_inverse_counterexample.py`.  No general
Bellman theorem is claimed.  The structured exact counterexample and its
independent script are in `../route_frame/`.
