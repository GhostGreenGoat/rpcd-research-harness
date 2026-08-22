# Finite-time transfer for the new Iteration 5 slices

Status: rigorous transfer conditional only on the proof candidates cited
below.  This section introduces no new probabilistic assumption beyond fresh
independent permutations each epoch.

If an epoch certificate satisfies

```
K(B)>=gamma B^-1,
```

then for every deterministic initial point and `k` fresh RPCD epochs,

```
E||x_k||_B^2 <=(1-gamma)^k||x_0||_B^2,
E||x_k||_B   <=(1-gamma)^(k/2)||x_0||_B.                  (F1)
```

The second line is expectation of distance, not distance of the expected
iterate.  Consequently the following coordinate-update counts (`N=nk`) are
sufficient:

```
relative expected squared distance epsilon:
N <=(n/gamma) log(1/epsilon),

relative expected distance epsilon:
N <=(2n/gamma) log(1/epsilon),

failure probability delta for distance epsilon:
N <=(n/gamma)[2log(1/epsilon)+log(1/delta)].              (F2)
```

Ceilings can be added to the epoch counts.  The high-probability formula is
Markov applied to the squared-distance inequality; the existing
supermartingale/Ville argument also gives a simultaneous-in-epoch envelope.

## 1. General dimension-scaled identity band

Let `theta=n(1-mu)`.  The candidate in `uniform_near_identity_band.md` gives

```
gamma=mu/[1+theta/sqrt(2)]^2.                              (F3)
```

Thus:

- if `theta<=2-sqrt(2)`, one may take `gamma=mu/2`;
- if `theta<=1`, one may take the simpler `gamma=mu/4`.

For example, throughout `mu>=1-1/n`, expected squared distance needs at most

```
N <=(4n/mu)log(1/epsilon).                                (F4)
```

This is the requested `O(n/mu log(1/epsilon))` order for every matrix in that
spectral band.

## 2. Equicorrelation family

The independently audited direct-prefix proof candidate gives the better family
constant `gamma=mu/2`, hence

```
N <=(2n/mu)log(1/epsilon)                                 (F5)
```

for expected squared distance.  The half-linear dual construction separately
gives `gamma>25mu/98`; its importance is architectural, not a better constant.

## 3. Equality and sharpness diagnostics

The trace-to-Frobenius step behind (F3) is sharp: equality occurs when the
eigenvalues are

```
mu,...,mu,n-(n-1)mu,
```

the spectrum of the signed-rank-one/equicorrelation sharp family.  The later
replacement of triangular operator norm by Frobenius norm is not generally
sharp, so the thresholds in Section 1 are sufficient rather than necessary.

The global constant cannot exceed one half; the signed-rank-one sequence with
`n` increasing and then `mu->1` already enforces that upper bound.  Therefore
the first bullet of Section 1 reaches the correct constant within its band,
although the band itself is not claimed optimal.
