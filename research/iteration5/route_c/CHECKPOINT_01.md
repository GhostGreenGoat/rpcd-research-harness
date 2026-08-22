# Checkpoint 1: anisotropy survives, three scalar shortcuts do not

Local checkpoint time: `2026-08-21 20:08 +08:00` (about 30 minutes after
the root-observed start bound).

## Exact route barriers

The portable verifier `scripts/iter5_route_c_exact_barriers.py` records three
strict rational failures.  None refutes the half-depth conjecture.

1. **Uniform gain per newly revealed coordinate is false.**  For

   ```text
   A = [[1,2/3,2/3],[2/3,1,3/4],[2/3,3/4,1]],  mu=1/4,
   ```

   the tempting incremental inequality
   `(J2-J1) >= (mu/3) A^{-1}` fails.  The gap has positive first two leading
   principal minors but determinant
   `-1624139/2499268608`.  Thus a proof cannot allocate `mu/m` progress to
   every stage separately; earlier surplus must amortize later weak stages.

2. **Even exact child floors are not a sufficient matrix state.**  At
   `mu=1/100`, take the direct sum of a size-two signed-rank-one block and a
   size-three regular-simplex block.  Lifting only the already proved child
   scalar bound `(mu/2) C_i^{-1}` gives generalized ratio
   `4129401/10100000 < 1/2`.  The witness quadratic gap is
   `-2761797/10100000`.  The exact lifted child `J2` matrices are far larger;
   the failure precisely measures the anisotropic surplus discarded by
   scalarization.

3. **The determinant/volume part alone is insufficient.**  On
   `A=mu I+(1-mu)11^T`, with `m=6,t=3,mu=1/10`, the volume-adjugate subset
   certificate has parallel coefficient `11/400`, below `mu/2` by `9/400`.

## Exterior/subset identity obtained

Conditioning a uniform prefix of length `t` on its unordered coordinate set
`S` gives the exact representation

```text
A^(1/2) J_t(A) A^(1/2)
 = average_{|S|=t} V_S K(A_SS) V_S^T,
```

where the columns of `V=A^(1/2)` are unit vectors.  Inserting the local Gram
determinant certificate and differentiating the elementary symmetric
polynomial gives the general lower certificate

```text
A^(1/2) J_t(A) A^(1/2)
 >= [1/binom(m,t)] A * grad e_t(A).
```

Its eigenvalue on an eigenline `lambda_i` is exactly
`lambda_i e_{t-1}(lambda without lambda_i)/binom(m,t)`.  This is a genuine
all-dimensional polynomial/exterior certificate, but barrier 3 shows why it
cannot close the low-`mu` half-depth problem without order variance.

## New SOS target

An exact third-prefix expansion was derived.  With
`D_q=Diag(diag(A^q))` and

```text
T(A)=sum_{i != j} [(A^2)_jj-A_ij^2]
     (e_j-A_ij e_i)(e_j-A_ij e_i)^T,
```

one has

```text
J3 = I/m + { (2m-3)[mI-2A+D_2]
             -2[mA-2A^2+D_3] + T(A) }
            / [m(m-1)(m-2)].
```

This retains the codimension-two anisotropic frame exactly.  The current
dual/SOS candidate is

```text
J3 - (1/2)J2 >= (2mu/m) A^{-1}.                 (C3-SOS)
```

If true, the known `J2 >= (2mu/m)A^{-1}` would imply
`J3 >= (3mu/m)A^{-1}`, settling the desired half certificate through
dimension six.  It is being attacked rather than assumed.
