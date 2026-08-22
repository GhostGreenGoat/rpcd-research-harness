# Hostile audit：Iteration 2 main analytic lemmas

日期：2026-08-20
审计范围：`Lemma 2.1`、`Theorem 3.2`、`Lemma 3.3`、two-step identity `(19)`。
审计纪律：这里只报告 blocker、必要修正及逐式核验结论；不把 E3 声明晋级为定理。

## 总结

- **未发现会推翻四个核心公式的 blocker。** `(2)--(4)`、boxed inequality `(9)`、
  canonical choice `c=beta` 下的 `(10)--(14)`，以及 `(19)` 的乘法顺序和 Loewner
  方向均正确。
- **发现一处需要修正文案/量词的 P1 问题**：`Theorem 3.2` 对任意 `c>0` 都给出
  upper bound，但对任意 `c>0` 并不总是 bare Jensen 的“strict refinement”，也不总是
  单调 hierarchy。refinement/monotonicity 必须附加谱条件。后面的 canonical
  `c=beta` 满足所需的更强条件，因此该问题不破坏 `(13)--(14)` 或 C011 的 `c=beta`
  专门化。

## 1. Lemma 2.1：通过；建议澄清一次 resolvent 乘法顺序

令 `Delta=X-Y`。两个合法的 resolvent identity 是

$$
X^{-1}-Y^{-1}=-Y^{-1}\Delta X^{-1}
=-X^{-1}\Delta Y^{-1},
$$

以及

$$
Y^{-1}-X^{-1}=X^{-1}\Delta Y^{-1}
=Y^{-1}\Delta X^{-1}.
$$

因此

$$
\begin{aligned}
X^{-1}-Y^{-1}+Y^{-1}\Delta Y^{-1}
&=Y^{-1}\Delta(Y^{-1}-X^{-1})\\
&=Y^{-1}\Delta X^{-1}\Delta Y^{-1}.
\end{aligned}
$$

这正是 `(2)`。最后一步必须使用
`Y^{-1}-X^{-1}=X^{-1} Delta Y^{-1}`；若误用另一种书写而不调整左侧因子，会得到错误
的非交换乘法顺序。原文最终顺序是正确的，但建议把所用的第二个 resolvent identity
显式写出。

修正项确为 PSD，因为

$$
Y^{-1}\Delta X^{-1}\Delta Y^{-1}
=(X^{-1/2}\Delta Y^{-1})^\top
 (X^{-1/2}\Delta Y^{-1})\succeq0.
$$

对 `(2)` 取有限排列平均时，线性项严格由 `E[Delta_pi]=0` 消失，得到 `(3)`；左右乘
`A` 并代入 `(1)` 后，`(4)` 中的顺序

$$
AY^{-1}\,E[\Delta_pi X_pi^{-1}\Delta_pi],Y^{-1}A
$$

也正确。

**结论：PASS，无 blocker。**

## 2. Theorem 3.2：boxed upper bound 通过；“strict refinement for every c”需修正

由 `p_{r,c}(X_pi) <= X_pi^{-1}`，对称矩阵 `Delta_pi` 的 congruence 给出

$$
\Delta_pi p_{r,c}(X_pi)\Delta_pi
\preceq
\Delta_pi X_pi^{-1}\Delta_pi.
$$

所以 `C_{r,c} <= C_exact`。注意 `(9)` 中

$$
AY^{-1}(C_{\rm exact}-C_{r,c})Y^{-1}A
=(Y^{-1}A)^\top(C_{\rm exact}-C_{r,c})(Y^{-1}A)\succeq0.
$$

从 exact expression 中减去较大的 `C_exact`，确实得到

$$
E[T_pi^\top AT_pi]\preceq U_{r,c}.
$$

因此 boxed inequality `(9)` 的 Loewner 方向正确，对所有 `r>=1,c>0` 成立。

### 必要修正 P1

`p_{r,c}(X) <= X^{-1}` 不蕴含 `p_{r,c}(X) >= 0`。标量形式为

$$
p_{r,c}(x)=\frac{1-(1-x/c)^{2r}}x.
$$

例如 `x=3c,r=1` 时 `p_{1,c}(x)=-1/c<0`。所以对任意 `c>0`：

- `C_{r,c}` 未必 PSD；
- `U_{r,c}` 未必比 bare Jensen matrix
  `A-AY^{-1}A` 更小；
- 固定 `c` 后的 `r` 序列未必是单调收敛 hierarchy。

建议把 Theorem 3.2 后的句子改为：

> `(9)` 对所有 `c>0` 是合法 upper bound。若
> `lambda_max(X_pi) <= 2c` 对所有排列成立，则 `p_{r,c}(X_pi) >= 0`，从而它是
> bare Jensen 的 Loewner refinement；若采用 Lemma 3.3 的 canonical
> `c=beta >= lambda_max(X_pi)`，则还得到 `(13)` 的单调收敛 hierarchy。

若要避免边界退化并在一般 `c` 下声称收敛，还应使用严格条件
`lambda_max(X_pi)<2c`。canonical `c=beta` 不受影响，因为它把
`R_pi=I-X_pi/beta` 放在 `[0,1-beta^{-n}]`。

**结论：boxed `(9)` PASS；“strict analytic refinement”量词需按上文收紧。**

## 3. Lemma 3.3：beta、determinant 下界及单调极限均通过

### `(10)`

`M_pi` 的对角线上有 `n` 个一，严格三角部分对每个无序对 `{i,j}` 恰取一次
`A_ij`。所以

$$
\|M_pi\|_F^2=n+\sum_{i<j}A_{ij}^2.
$$

单位对角和对称性给出

$$
\operatorname{tr}(A^2)=n+2\sum_{i<j}A_{ij}^2,
$$

故 beta 公式正确，且与排列无关。

### `(11)--(12)`

`X_pi=M_pi M_pi^T` 严格正定，并且

$$
\lambda_{\max}(X_pi)=\|M_pi\|_2^2
\leq\|M_pi\|_F^2=\beta.
$$

`M_pi` 在置换坐标中为 unit lower triangular，因此
`det(M_pi)=1`、`det(X_pi)=1`。若 `lambda_j(X_pi)<=beta`，则对每个 `i`

$$
\lambda_i(X_pi)
=\frac1{\prod_{j\ne i}\lambda_j(X_pi)}
\geq\beta^{-(n-1)}.
$$

所以

$$
0\preceq R_pi=I-X_pi/\beta
\preceq(1-\beta^{-n})I.
$$

方向及指数 `n-1`、`n` 均正确。

### `(13)--(14)`

因为 `R_pi` 是 PSD、与 `X_pi` 交换且谱半径严格小于一，

$$
p_{r+1,\beta}(X)-p_{r,\beta}(X)
=\beta^{-1}R^{2r}(I+R)\succeq0.
$$

于是 congruence by `Delta_pi` 保持单调方向，`C_r` 递增；`U_r` 中该项带负号，故
`U_r` 递减。排列空间只有 `n!` 个点，所以极限与期望交换没有测度论缺口；即使改成
一般概率空间，`(14)` 也提供一致支配。

最后，逐特征值使用

$$
X^{-1}-p_{r,\beta}(X)=X^{-1}R^{2r}
$$

以及
`lambda_min(X)^{-1}<=beta^{n-1}`、
`||R||<=1-beta^{-n}`，恰好得到 `(14)`。

**结论：PASS，无 blocker。** 建议仅把原文 `0 < X_pi <= beta I` 排版为
`0 \prec X_pi \preceq beta I`，避免把标量与 Loewner 记号混写。

## 4. Two-step identity `(19)`：通过

`v_i` 是 `A^{1/2}` 的列，因此 `||v_i||^2=A_ii=1`，
`P_i=v_iv_i^T` 是正交 rank-one projection，并且

$$
\sum_iP_i=A,
\qquad \sum_iZ_i=nI-A.
$$

先做 `i`、再做 `j` 后，平方范数对应的乘法顺序确为

$$
(Z_jZ_i)^\top(Z_jZ_i)=Z_iZ_jZ_i,
$$

所以 `(15)` 没有把 chronological order 写反。

再令 `S=sum_i Z_i A Z_i`。直接展开：

$$
S=nA-2A^2+\sum_iP_iAP_i.
$$

而

$$
P_iAP_i=(v_i^\top Av_i)P_i=(A^2)_{ii}P_i,
$$

故最后一项正是 `W`，`(16)` 正确；并且每个
`Z_iAZ_i` 是 `A` 的 congruence，所以 `S>=0`。

所有 ordered pairs 的和为

$$
\sum_{i,j}Z_iZ_jZ_i
=\sum_i Z_i(nI-A)Z_i
=n^2I-nA-S.
$$

去掉 `i=j` 的项时，应减去

$$
\sum_iZ_i^3=\sum_iZ_i=nI-A.
$$

因此

$$
K_{\rm WR,2}=I-A/n-S/n^2,
$$

$$
K_{\rm WOR,2}=I-A/n-S/[n(n-1)],
$$

相减即

$$
K_{\rm WR,2}-K_{\rm WOR,2}
=\frac{S}{n^2(n-1)}
=\frac1{n^2(n-1)}\sum_iZ_iAZ_i\succeq0.
$$

这同时复核了 `(17)--(18)` 的全部系数和 `(19)` 的 Loewner 方向。它比较的是任意固定
初始 energy-coordinate 向量经过前两步后的条件期望；原文没有把它误写成完整 epoch
的可乘性结论。

**结论：PASS，无 blocker。**

## 最终审计判定

唯一需要在主文中实际修改的是 Theorem 3.2 后“对任意 `c>0` 都是 strict
refinement/hierarchy”的措辞。建议加入 `X_pi <= 2c I` 的 refinement 条件，并把
单调 hierarchy 明确绑定到 Lemma 3.3 的 `c=beta`。其余指定公式通过本轮 hostile
audit；按仓库协议，它们仍需独立重证，不能仅凭本文件晋级到 E4/E5。
