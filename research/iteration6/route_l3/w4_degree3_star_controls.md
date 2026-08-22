# Exact controls at the next degree-three star frontier

Date: 2026-08-22

Status: **E2 fixed exact controls only**.  This is neither a search result nor a
universal theorem.

After the dimension-uniform three-path theorem, the smallest new tree
interaction is a degree-three star.  For

```text
H=[[0,w^T],[w,0]],  t^2=w^Tw,
```

one has

```text
H^2=[[t^2,0],[0,ww^T]],
D=diag(t^2,w_1^2,w_2^2,w_3^2),
F_leaf=ww^T-D_leaf.
```

Thus the new anisotropy is genuinely two-dimensional: after removing scale,
it lives on the simplex `q_i=w_i^2/t^2`, rather than the one interval used for
a three-path.  A plausible exact continuation is a simplex-Bernstein
certificate for the active `4 x 4` principal minors.

At the hostile near-singular point `d=6,t=99/100`, all active principal minors
of the uniform shifted-inverse gap are strictly positive for the three exact
rational sphere directions

```text
(1,2,2)/3,
(36,24,23)/49,
(12,4,3)/13.
```

This rules out only these three fixed witnesses.  It is not evidence that the
whole simplex is positive and is not promoted above E2.

Artifacts:

```text
scripts/iter6_w4_degree3_star_controls.py
research/iteration6/route_l3/evidence/W4_DEGREE3_STAR_CONTROLS.json
```
