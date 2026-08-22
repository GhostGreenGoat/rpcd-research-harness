# RPCD 第三轮：矩阵不等式与 finite-time Lyapunov 综合

日期：2026-08-21

> **第四轮更新：** 本文中的强一步猜想 C026 与边界目标 `S_C>=2I` 后来被一个全有理
> `n=8` 反例精确推翻；归约公式本身仍有效。请以
> `docs/ITER4_T080_BOUNDARY_KERNEL_INEQUALITY.md` 的证据状态为准。原始 RPCD 协方差谱率
> 猜想和所求复杂度阶并未因此被反驳。

## 结论先行

本轮没有证明一般维数的

\[
 O\!\left({n\over\mu}\log{1\over\varepsilon}\right)
\]

坐标更新复杂度，也没有反驳它。实质推进有四点：

1. 把最干净的充分条件单独登记为强一步猜想 C026；超过 11.2 万次固定谱隙/边界评估
   没有找到反例，但它仍只是 `open_conjecture / E1`。
2. 把最危险的 \(\mu\downarrow0\) 区域严格归约成奇异相关矩阵上的有限 Schur-complement
   不等式 \(S_C\succeq2I\)。这比继续搜索极小 \(\mu\) 更接近解析核心。
3. 构造了一个从 Gram determinant 单调上升到精确 Bellman 解的矩阵证书层级
   \(H_0\preceq H_1\preceq\cdots\preceq H_{n-1}=K\)，并得到第一层闭式。
4. 证明草稿表明，对 RPCD 的反序封闭算子，谱率 \(r\le q\) 与“存在某个正定二次
   Lyapunov metric at rate \(q\)”等价。强一步猜想只是把这个 metric 固定成 `A-energy`；
   允许 metric 适应 Hessian 后，真正新增的 finite-time 难点是条件数。

所有新的一般结论仍处于 `E3 proof draft` 或更低等级；没有 Lean 形式化，也没有晋级为
theorem candidate。

## 1. 正确的参数与目标

对未归一化 \(Q\succ0\)，令

\[
 D=\operatorname{Diag}(Q),\qquad
 A=D^{-1/2}QD^{-1/2},\qquad
 \mu=\lambda_{\min}(A).
\]

下面的 \(\mu\) 都指这个尺度不变的参数。若坚持使用
`mu_raw=lambda_min(Q)`，只能由

\[
 \mu\ge {\mu_{\rm raw}\over\max_iQ_{ii}}
\]

把目标写成 \(O(n\max_iQ_{ii}/\mu_{\rm raw})\)。

令

\[
 q_{n,\mu}=\max\{(1-1/n)^n,(1-\mu/n)^{2n}\}.
\]

若能证明

\[
 \mathbb E_\pi[T_\pi^\top AT_\pi]\preceq q_{n,\mu}A,       \tag{S1}
\]

则每个 epoch 条件收缩，因而

\[
 \mathbb E\|x_K\|_A^2\le q_{n,\mu}^K\|x_0\|_A^2,
 \qquad
 \mathbb E\|x_K\|_A\le q_{n,\mu}^{K/2}\|x_0\|_A.          \tag{S2}
\]

小 \(\mu\) 时 \(q\le e^{-2\mu}\)，所以 (S2) 正好给出目标坐标复杂度。若只追求复杂度
阶而不追求 ICML 猜想的 sharp 常数，证明

\[
 \mathbb E[T_\pi^\top AT_\pi]\preceq(1-c\mu)A             \tag{S3}
\]

对某个 universal \(c>0\) 已经足够。这是后续证明不应忘记的放松空间。

## 2. 强一步不等式的反例攻击与边界归约

### 2.1 全固定谱隙壳层参数化

每个 `diag(A)=1, lambda_min(A)=mu<1` 都可唯一写成

\[
 A_\mu=\mu I+(1-\mu)C,
 \qquad C\succeq0,quad C_{ii}=1,quad\lambda_{\min}(C)=0.  \tag{S4}
\]

因此搜索奇异 Gram matrices `C=VV^T` 并不是只看一个特殊子类，而是在连续意义上参数化
固定 \(\mu\) 可行壳层。subset DP 用 \(2^n\) 个状态精确求 float64 的
`E[T^T A T]`，并与 \(n!\) 穷举在 \(n\le7\) 上交叉核对。

主搜索及低谱隙/边界专项搜索共超过 11.2 万次评估，覆盖
\(n=3,\ldots,8\)、signed/cut/frustrated/low-rank Gram 和局部球面优化，没有发现 (S1)
的浮点反例。最接近样本都在 \(\mu\downarrow0\) 的低秩边界。这些是 E1 路线选择证据，
不是对 (S1) 的证明。

### 2.2 小谱隙的一阶核心

固定奇异相关矩阵 \(C\)，令

\[
 K_0(C)=\mathbb E_\pi[(M_\pi(C)M_\pi(C)^\top)^{-1}].
\]

按 \(\mathcal N=\ker C\)、\(\mathcal R=\mathcal N^\perp\) 分块，并定义

\[
 S_C=(K_0)_{NN}-(K_0)_{NR}(K_0)_{RR}^{-1}(K_0)_{RN}.       \tag{S5}
\]

block perturbation proof draft 给出

\[
 r_E(A_\mu)=1-\mu\lambda_{\min}(S_C)+o(\mu),              \tag{S6}
\]

而 \(q_{n,\mu}=1-2\mu+O(\mu^2)\)。所以边界上的 sharp 核心是

\[
 \boxed{S_C\succeq2I\quad\text{on }\ker C.}               \tag{S7}
\]

若 (S7) 对某个 \(C\) 严格失败，该射线在充分小正 \(\mu\) 下会给出 (S1) 的解析反例；
若严格成立，该固定射线在充分小 \(\mu\) 下安全。等号必须继续看二阶。

Schur 判据还把 (S7) 等价地改写成更直接的随机三角求解不等式

\[
 \boxed{
 K_0(C)\succeq2P_{\ker C}
 \quad\Longleftrightarrow\quad
 \mathbb E_\pi\|M_\pi(C)^{-1}z\|^2
 \ge2\|P_{\ker C}z\|^2\quad(\forall z).
 }                                                         \tag{S7a}
\]

这为下一步提供了比抽象 perturbation 更具体的证明入口：研究随机顺序三角求解对 Gram
依赖方向的平均 coercivity。

直接搜索 (S7) 的最小值从 `n=3` 的约 `2.33333` 下降到 `n=8` 的约 `2.05207`，显示常数
2 即使成立也可能随维数渐近取到。

### 2.3 当前最危险族已从浮点升级为 exact certificate

`n=8` 的危险候选是两个重复 pole 加一个 latitude hexagon，取
\(a=4/\sqrt{21}\) 时 `rank(C)=3`。利用 \(S_2\times D_6\) 分解，并在
\(\mathbb Q(\sqrt{21})\) 上枚举所有 `8!` 个三角求解，得到

\[
 \lambda_{\min}(S_C)
 =\frac{54099374095982388041}{26363285800809721344}
 =2+\frac{1372802494362945353}{26363285800809721344}>2.    \tag{S8}
\]

所以这个最接近的候选不是隐藏的反例。式 (S8) 只认证一个有限对称族，不能推广成 (S7)。

## 3. Remaining-set 矩阵证书层级

对一个 `m x m` principal problem \(B\)，令精确剩余 sweep 降幅矩阵为 \(K(B)\)。本轮
定义

\[
 H_0(B)=\det(B)B^{-1},
\]

\[
 H_{r+1}(B)=\frac1m\sum_i
 \left(e_ie_i^\top+L_i^\top H_r(B_{-i,-i})L_i\right).      \tag{S9}
\]

证明草稿得到单调层级

\[
 \boxed{H_0(B)\preceq H_1(B)\preceq\cdots
 \preceq H_{m-1}(B)=K(B).}                                \tag{S10}
\]

因此每揭示一个真实坐标并对子问题使用 determinant tail，证书都不会变弱；最后恢复精确
Bellman 解。若 \(G=B^{-1}\)、\(d=\det B\)，第一层还有闭式

\[
 H_1(B)=\frac1m\left[
 d\operatorname{tr}(G)G-d(G-I)^2+I-d\operatorname{Diag}(\operatorname{diag}G)
 \right].                                                  \tag{S11}
\]

对应

\[
 c_r(A)=\lambda_{\min}(A^{1/2}H_r(A)A^{1/2})
\]

给出真正的 finite-time strong-expectation 界

\[
 \mathbb E\|x_K\|_A^2\le(1-c_r)^K\|x_0\|_A^2.            \tag{S12}
\]

但第一层仍不够：在结构族 `n=3, mu=1/5` 上

\[
 c_1={547\over1875}
 <1-(14/15)^6.
\]

第二层开始出现新的 Schur-loss moment，`B^{-1}, I, bar(D)` 的有限基不闭合。现在最具体
的代数瓶颈不再是“找 Lyapunov 函数”，而是找到一个保留 leverage 和 child spectral
floor 的 PSD moment compression。

## 4. 允许适应性 metric 后的算子结论

在 energy coordinates 中，令

\[
 \mathcal C_A(H)=\mathbb E[P_\pi^\top H P_\pi].
\]

反序排列对应转置 word，所以 \(\mathcal C_A\) 在 Frobenius 内积下自伴。由 transpose-
closed Kraus family 的共同 reducing blocks 和逐块 Perron matrix，证明草稿得到

\[
 \boxed{
 r_A\le q
 \Longleftrightarrow
 \exists H\succ0:\ \mathcal C_A(H)\preceq qH.
 }                                                         \tag{S13}
\]

这说明强一步 (S1) 的风险边界：它固定 `H=I`，但 C001 只要求某个适应性 `H`。即使 (S1)
最终被反例否定，矩阵 Lyapunov 路线仍然存活。

任取 \(\alpha>r_A\)，canonical resolvent

\[
 H_\alpha=(\alpha I-\mathcal C_A)^{-1}(I)
\]

满足

\[
 \mathcal C_A(H_\alpha)=\alpha H_\alpha-I,
 \qquad
 \kappa(H_\alpha)\le{\alpha\sqrt n\over\alpha-r_A}.       \tag{S14}
\]

它给 expectation of squared distance、expectation of distance 和 Ville time-uniform high-
probability 界。exact-rate metric 在 \(r_A\) 处存在，但当 \(r_A=q\) 时仍缺 uniform
condition-number bound。

此外，自伴性直接给

\[
 \mathbb E\|x_K\|_A^2\le\sqrt n\,r_A^K\|x_0\|_A^2.       \tag{S15}
\]

因此只要将来证明原 C001，新的 finite-time 目标自动得到一个带 additive `log n` warm-up
的版本；强一步 (S1) 的额外价值是去掉 \(\sqrt n\) 前因子，而不是 finite-time bridge 的
唯一可能性。

## 5. 本轮明确关闭的错误捷径

1. “搜索十万次无反例”等于证明：错误；最危险 margin 正在随 \(n\) 靠近零。
2. 只压缩 \(K_0\) 到 `ker(C)`：不够；与 `range(C)` 的 \(\sqrt\mu\) coupling 会在一阶
   通过 Schur complement 回流。
3. 平均 Schur rank-one losses 必然得到 `1/m`：错误；简单零模态时它们渐近完全对齐。
4. `B^{-1}, I, bar(D)` 三个矩阵形成 Bellman 封闭基：错误；下一步产生二阶 child
   Schur moment。
5. exact-rate PD Lyapunov metric 存在就自动给 finite-time 常数：错误；还必须控制 metric
   条件数。

## 6. 下一轮优先级

1. `T080`：证明或反驳边界不等式 (S7)。优先利用 reverse-paired triangular solves、
   Schur complement 的变分表示，以及 nullity/rank 分解。
2. `T085`：压缩第二 Schur-loss moment，使 (S10) 在少数层内给出
   \(c_r(A)\ge c\mu\)。为了用户的复杂度目标，常数 `c>0` 已经够，不必先追 sharp `q`。
3. `T090`：独立 hostile-audit (S13)--(S15)，尤其检查 off-diagonal operator blocks、
   exact-rate metric 的满秩性和 Ville 转换。
4. 对 (S7) 的等号/近等号序列研究 \(n\to\infty\) 构型；这比继续扩大无结构随机搜索更
   可能揭示 sharp 证明或反例。

## 7. 状态边界

| 对象 | 当前状态 | 本轮后能否声称解决目标 |
|---|---|---|
| C026 强一步 A-energy | open conjecture / E1 | 否 |
| C029 小谱隙 Schur 归约 | proof candidate / E4 hostile-audited | 否；给出 sharp 子问题 |
| 两极点-六边形族 (S8) | finite exact certificate | 只关闭一个候选族 |
| C027 determinant-tail hierarchy | proof candidate / E4 hostile-audited | 否；给出单调 finite-time 证书族 |
| C028 adapted Lyapunov | proof candidate / E4 hostile-audited | 条件于谱率可给 finite-time 界 |
| 一般 \(O(n/\mu\log(1/\varepsilon))\) | open | 否 |
