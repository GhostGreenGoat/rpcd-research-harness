# 第二轮路线 C：hostile audit

审计对象：`docs/ITER2_ROUTE_C_PROJECTION_ALGEBRA.md`
日期：2026-08-20
审计角色：独立于路线 C 推导的检查 run

## 1. 总体结论

**结论：核心数学结论通过本轮 hostile audit；未找到反例或方向错误。**

- blocker（结论错误）：**0**。
- proof-completeness blocker：**1 个可局部修复的缺失证明**——原文直接断言 determinant 极值 (11)，但没有写出极值论证。该断言为真，下文给出补丁证明。
- minor clarification：**3 个**——需要明确 covariance 算子所用范数空间、补足 degree-3 inclusion--exclusion 的全集分类、避免 `W_i` 与列矩阵 `W_pi` 记号重载。
- 经采用本文给出的局部修正后，Theorem 3.1、4.1、4.2 仍可保持 `E3 proof draft`；本审计不是独立重证门，也不自动把它们晋级为 theorem candidate。

逐项结论如下：

| 检查项 | 结论 | 严重度 |
|---|---|---|
| defect telescoping 与 determinant 因子分解 | 正确 | pass |
| determinant 到谱范数的方向 | 正确 | pass |
| `C_A` 的谱半径/算子范数链 | 正确；事实上排列反转使 `C_A` 对称，仍应注明范数空间 | minor clarification |
| `lambda_i >= sigma, sum lambda_i=n` 下的 determinant 下界 | 结论正确，原稿缺少证明 | proof-completeness blocker |
| `n=2` 推论 | 正确 | pass |
| high-`sigma` 推论和 `tau_n` 唯一性 | 正确 | pass |
| degree-3 inclusion--exclusion | 公式和反例矩阵均正确 | minor clarification |

## 2. Defect determinant 的独立核对

固定排列，记

\[
 P_k=Z_{\pi_k}\cdots Z_{\pi_1},
 \qquad P_0=I,
 \qquad Q_i=v_iv_i^\top=I-Z_i.
\]

由于 `Z_i` 是对称幂等投影，

\[
\begin{aligned}
 P_{k-1}^\top P_{k-1}-P_k^\top P_k
 &=P_{k-1}^\top(I-Z_{\pi_k}^\top Z_{\pi_k})P_{k-1}\\
 &=P_{k-1}^\top Q_{\pi_k}P_{k-1}\\
 &=w_kw_k^\top,
\end{aligned}                                               \tag{A1}
\]

其中 \(w_k=P_{k-1}^\top v_{\pi_k}\)。从 `k=1` 到 `n` 望远镜求和，严格得到

\[
 I-P_\pi^\top P_\pi=\sum_{k=1}^n w_kw_k^\top.              \tag{A2}
\]

### 2.1 三角因子的方向

展开

\[
 w_k=Z_{\pi_1}\cdots Z_{\pi_{k-1}}v_{\pi_k}.
\]

每乘一个 \(Z_{\pi_j}=I-v_{\pi_j}v_{\pi_j}^\top\)，只会减去一个属于
\(\operatorname{span}\{v_{\pi_1},\ldots,v_{\pi_{k-1}}\}\) 的向量；因此

\[
 w_k=v_{\pi_k}+\sum_{j<k}r_{jk}v_{\pi_j}.                  \tag{A3}
\]

若列矩阵记为 \(\mathsf W_\pi=[w_1\ \cdots\ w_n]\)，则

\[
 \mathsf W_\pi=V_\pi R_\pi,
\]

且 \(R_\pi\) 的第 `k` 列只在行 `1,...,k` 非零、对角元为 1；所以它确为**单位上三角矩阵**。原文的三角方向正确。

因为 `A` 正定，\(V_\pi\) 可逆；单位三角 \(R_\pi\) 也可逆。故 (A2) 右端正定，而不仅是半正定，并且

\[
\begin{aligned}
 \det(I-P_\pi^\top P_\pi)
 &=\det(\mathsf W_\pi\mathsf W_\pi^\top)\\
 &=\det(V_\pi V_\pi^\top)\\
 &=\det(V^\top V)=\det A.                                 \tag{A4}
\end{aligned}
\]

### 2.2 从 determinant 到 norm 的方向

设 \(s_1\ge\cdots\ge s_n\ge0\) 是 \(P_\pi\) 的奇异值。投影乘积是 contraction，故 \(s_j\le1\)；由 (A2) 正定，还有 \(s_j<1\)。于是

\[
 \det A=\prod_{j=1}^n(1-s_j^2).
\]

其中 \(1-s_1^2\) 是最小因子，而其余因子均不超过 1，因此

\[
 \det A\le1-s_1^2.
\]

所以

\[
 \|P_\pi\|_2^2=s_1^2\le1-\det A.                          \tag{A5}
\]

原稿的 inequality direction 正确。一个容易发生但原稿没有犯的错误，是把乘积与最小因子的比较方向反写。

## 3. Covariance 算子的范数检查

单个 \(P_\pi\otimes P_\pi\) 通常不是对称矩阵，但完整排列平均
\(\mathcal C_A\) **是对称的**。因为每个 \(W_i=Z_i\otimes Z_i\) 对称，且排列集合在反转下封闭，

\[
\begin{aligned}
 \mathcal C_A^\top
 &=\frac1{n!}\sum_\pi
   W_{\pi_1}\cdots W_{\pi_n}\\
 &=\mathcal C_A.                                           \tag{A6}
\end{aligned}
\]

所以这里甚至有 \(\rho(\mathcal C_A)=\|\mathcal C_A\|_2\)。不过原稿只使用较弱的
\(\rho(C)\le\|C\|_2\)，该不等式对任何方阵都成立；即使没有观察到上述反转对称性，推导仍然有效。

这里应明确：\(\|\cdot\|_2\) 是 \(\mathbb R^{n^2}\) 上的 Euclidean induced norm；等价地，是矩阵空间 \(\mathbb R^{n\times n}\) 配备 Frobenius norm 后的算子范数。对任何方阵，包括非正规、非对称方阵，均有

\[
 \rho(C)\le\|C\|_2.                                       \tag{A7}
\]

另外，

\[
 \|P\otimes P\|_2=\|P\|_2^2.                             \tag{A8}
\]

因此

\[
\begin{aligned}
 \rho(\mathcal M_A)
 &=\rho(\mathcal C_A)\\
 &\le\|\mathcal C_A\|_2\\
 &\le\frac1{n!}\sum_\pi\|P_\pi\otimes P_\pi\|_2\\
 &\le1-\det A.                                             \tag{A8a}
\end{aligned}
\]

第一行只使用 (1) 的 similarity，未声称 similarity 保持 Euclidean norm。后三行全部在 projection coordinates 的同一个 Frobenius/Euclidean 空间中进行。因此不存在跨相似变换误用 Euclidean norm 的问题；同时，`C_A` 的自伴性来自完整排列的反转配对，而不是来自单个 word。

**建议修正。** 在路线 C 的 (10) 前增加一句：

> All norms in (10) are induced Euclidean norms on the vectorized/Frobenius covariance space. Moreover, the full permutation average `C_A` is self-adjoint by reversal symmetry; the displayed argument only needs the general inequality `rho(C_A) <= ||C_A||_2`.

## 4. Determinant 下界的极值审计

原稿 (11) 的结论正确，但“product is minimized ...”只有断言，没有证明。这是当前稿件唯一的 proof-completeness blocker。

### 修正证明 1：两变量质量转移

考虑任意两个都严格大于 \(\sigma\) 的特征值 \(a\le b\)。在保持和不变的前提下，取
\(0<\delta\le a-\sigma\)，则

\[
 (a-\delta)(b+\delta)-ab
 =\delta(a-b)-\delta^2\le0.                \tag{A9}
\]

所以把较小者一直降到 \(\sigma\)、把相同质量加到较大者，不会增大乘积。反复应用后，至多一个特征值大于 \(\sigma\)。由总和为 `n`，极小配置必为

\[
 (\sigma,\ldots,\sigma,n-(n-1)\sigma),
\]

从而

\[
 \det A=\prod_i\lambda_i
 \ge\sigma^{n-1}\bigl(n-(n-1)\sigma\bigr).                \tag{A10}
\]

这里最后一个分量至少为 \(\sigma\)，因为 \(\sigma\le1\)。

### 修正证明 2：凹函数极点论证

也可指出 \(\sum_i\log\lambda_i\) 是可行多面体

\[
 \{\lambda:\lambda_i\ge\sigma,\ \sum_i\lambda_i=n\}
\]

上的凹函数，最小值可在极点取得；每个极点恰有 `n-1` 个 lower-bound constraints 活跃。这给出同一配置。建议正文采用质量转移证明，因为它同时给出等号条件且不依赖读者补全“凹函数最小值在某个极点达到”的论证。

原文给出的

\[
 A_\sigma=\sigma I+(1-\sigma)\mathbf1\mathbf1^\top
\]

确有单位对角，特征值为 \(\sigma\)（重数 `n-1`）和
\(n-(n-1)\sigma\)，所以 sharpness 声明正确。

## 5. `n=2` 与 high-`sigma` 推论

### 5.1 `n=2`

由 (A10)，

\[
 1-d_2(\sigma)
 =1-\sigma(2-\sigma)
 =(1-\sigma)^2.                             \tag{A11}
\]

对 \(0<\sigma\le1\)，两边非负且

\[
 1-\sigma\le(1-\sigma/2)^2
\]

（差为 \(\sigma^2/4\)），平方后得到

\[
 (1-\sigma)^2\le(1-\sigma/2)^4.            \tag{A12}
\]

后者是 C001 maximum 的第二项，因此 Theorem 4.1 正确；无须判断此处究竟是哪一分支取得 maximum。

### 5.2 high-`sigma`

令

\[
 d_n(\sigma)=\sigma^{n-1}(n-(n-1)\sigma).
\]

对 `n>=2`，

\[
 d_n'(\sigma)
 =n(n-1)\sigma^{n-2}(1-\sigma)>0
 \quad(0<\sigma<1).                        \tag{A13}
\]

又有 \(d_n(0)=0,d_n(1)=1\)，而

\[
 0<1-(1-1/n)^n<1.
\]

故 (13) 确有唯一 \(\tau_n\in(0,1)\)。当 \(\sigma\ge\tau_n\) 时，

\[
 \rho(\mathcal M_A)
 \le1-d_n(\sigma)
 \le(1-1/n)^n,
\]

而 C001 的右端是包含该项的 maximum。Theorem 4.2 的量词、单调方向和 endpoint 均正确。

## 6. Degree-3 inclusion--exclusion 审计

令原始三次 word 总和为

\[
 D^3=\sum_{i,j,k}W_kW_jW_i.
\]

三个相等事件的贡献分别为

\[
\begin{array}{c|c}
 i=j & \sum_{i,k}W_kW_i^2=D^2,\\
 j=k & \sum_{i,j}W_j^2W_i=D^2,\\
 i=k & \sum_{i,j}W_iW_jW_i=K.
\end{array}
\]

任意两个相等事件的交集和三个事件的交集都对应 \(i=j=k\)，贡献均为 \(D\)。普通 inclusion--exclusion 只是在 word 的指标集合上计数，不要求这些矩阵交换。因此

\[
\begin{aligned}
 \sum_{i,j,k\ {m distinct}}W_kW_jW_i
 &=D^3-(D^2+D^2+K)+(D+D+D)-D\\
 &=D^3-2D^2+2D-K.                          \tag{A14}
\end{aligned}
\]

原稿 (4)--(5) 正确。建议在正文补上最后的 `+3D-D`，避免目前“two copies of `D^2-D` ...”的简写让读者怀疑 all-equal words 是否被重复处理。

### 6.1 不定号例子的独立复算

对原稿中的 rank-one projections `P,Q`，

\[
 D^2-K=PQ+QP-PQP-QPQ.
\]

利用 \(PQP=c^2P\)、\(QPQ=c^2Q\)，得到

\[
 D^2-K
 =cs^2\begin{pmatrix}c&s\\s&-c\end{pmatrix}.             \tag{A15}
\]

括号内矩阵的特征值是 `+1,-1`，所以 (A15) 的特征值确为
\(\pm cs^2\)。这里 `c,s>0`，故 correction 严格不定号。把零投影作为第三个投影不会改变 `D` 或 `K`，所以作为一般 projection algebra 的 degree-3 barrier 是有效的；原稿也已正确声明它不是 RPCD 特殊 tensor family 的反例。

## 7. 必须修改与建议修改

### 必须修改后才可称“完整 E3 proof draft”

1. 在 (11) 后加入 (A9)--(A10) 的 determinant 极值证明。当前结论正确，但缺失的极值步骤是 Theorem 4.1/4.2 的共同依赖。

### 建议修改

1. 在 (10) 明确使用 vectorized covariance/Frobenius 空间上的 induced Euclidean norm，并说明 `C_A` 无需对称。
2. 在 degree-3 计数中显式写出 `-(2D^2+K)+3D-D`。
3. 将 Theorem 3.1 中的列矩阵 `W_pi` 改名为 `mathsf W_pi` 或其他符号，避免与 covariance projection `W_i=Z_i tensor Z_i` 重载。
4. 在 (8) 到 (9) 之间明确写一句：由单位三角因子和 `V` 可逆，defect 是正定的，故所有 \(s_j<1\)。

## 8. 最终判定

在补上 determinant 极值证明后，本审计未发现会推翻以下结论的 blocker：

- \(\det(I-P_\pi^\top P_\pi)=\det A\)；
- \(\|P_\pi\|_2^2\le1-\det A\)；
- \(\rho(\mathcal M_A)\le1-d_n(\sigma)\)；
- C001 对 `n=2` 的全部参数成立；
- C001 对任意 `n>=2`、\(\sigma\ge\tau_n\) 成立；
- degree 3 出现无通用 Loewner 符号的 pinching correction。

这些仍是本工程中的 proof-draft / hostile-audited-local 结果，不包含优先权审计、独立重证或 Lean 检查。
