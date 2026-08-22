# Checkpoint 04 — threshold passed and final audit

Recorded: `2026-08-22 18:35:25 +08:00`, 120 minutes 35 seconds after the
observed start.  The required active-research threshold
`2026-08-22 18:34:50 +08:00` has passed.

## Final analytic additions

1. The minimal covariance target is now the exact cyclic-arc inequality
   `S<=C_tail P`.  Its diagonal component has the conditional successor-rank
   identity

   ```
   E[sum_delta delta C_(i,i+delta)^2 | ordered past,O]
     =(m+1)||c_i||^2/2.
   ```

   If all complement blocks have spectral radius at most `Lambda`, this
   gives `S_diag<=Lambda(1-mu)P/2`.  The generic missing term is therefore
   the adapted signed off-diagonal row covariance, together with modewise
   control when `Lambda=Theta(m)`.
2. The generic low-complement cases close analytically: `C_tail=1/2` for
   `m=1` (`n=4,5`) and `C_tail<7/4` for `m=2` (`n=6,7`).  The latter uses the
   exact nested-square eigenvalue `(3+sqrt(5))/2`; exact all-permutation
   controls pass through `n=6`.
3. Positive equicorrelation satisfies `S<=e^-2P`; negative
   equicorrelation satisfies `S<=3P` and the full dual certificate
   `PQ^-1P>=(mu/30)A^-1`.  These are structured-family proof candidates,
   not generic results.
4. All unaudited new positive statements were relabeled `proof candidate`.
   No general theorem is claimed.

## Final boundary

The uniform multirow inequality remains open.  Exact Hilbert-family tests
refute pathwise and order/reversal-paired closure.  An exact `n=9`,
`rho=1/2` structured RPCD covariance-lift instance refutes the proposed
remaining-frame inverse Bellman potential.  Scalar Hardy summation has an
intrinsic `Theta(n)` loss.  Thus any continuation must average genuinely
inside the full permutation/cycle distribution and retain adapted
off-diagonal cancellation.

Final report, timing record, structured result, and one last exact verifier
pass are the only remaining actions.
