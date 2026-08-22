# Hostile audit：M3 operator Lyapunov 路线

日期：2026-08-21

审计对象：`docs/ITER3_ROUTE_M3_OPERATOR_LYAPUNOV.md`

审计者与原路线作者不同；本文件不构成独立重证或形式化验证。

## 总判定

- **没有发现推翻 M3.1--M3.3、exact-rate PD metric、resolvent certificate 或 Ville
  转换的 P0 blocker。** 核心 Loewner 方向、转置顺序、谱半径用法和条件数系数均通过。
- 找到三个应补入主文的 **P1 假设/论证澄清**：

  1. 自伴正映射仍可有负特征值；所有 operator-norm 步骤必须始终使用
     `rho=max |lambda|`，不能在后续文案中悄悄换成最大代数特征值。
  2. exact metric 的共同 reducing decomposition 应显式写出矩阵空间的 off-diagonal
     blocks；它们可能影响 full spectral radius，但不会破坏 block-diagonal certificate。
  3. `r_A<alpha<1` 的可选性需要明确引用 SPD full-sweep 的严格收缩，例如
     `r_A<=1-det(A)<1`；Ville 结论还应明确 `H` 在运行前固定、epoch permutations 条件独立。

这些是需要修订的量词/桥接说明，不是当前公式的反例。按仓库协议，即使本审计关闭全部
技术 blocker，M3 仍缺独立 reconstruction，不能由本文件单独晋级为 theorem candidate。

## 1. 自伴不等于 Hilbert-space PSD；原文使用方式正确

定义

\[
 \mathcal C(H)=\mathbb E_\pi[P_\pi^\top H P_\pi].
\]

其 Frobenius adjoint 是

\[
 \mathcal C^*(H)=\mathbb E_\pi[P_\pi H P_\pi^\top].
\]

反序恒等式 `P_(pi^rev)=P_pi^T` 和均匀排列分布的反序不变性严格给出
\(\mathcal C^*=\mathcal C\)。因此它在整个实矩阵 Hilbert 空间上自伴，而不只是在 PSD
cone 上自伴。

必须区分两个“正”概念：

- `C` 是 positive/CP map，即 `H>=0 => C(H)>=0`；
- 这**不**推出 Frobenius 二次型 `<H,C(H)>` 对任意不定号 `H` 非负，也不推出
  superoperator 的全部特征值非负。

RPCD 实例确实可以出现负 superoperator 特征值。一个 seed-fixed float64 sanity scan 在
`n=3,4,5,6` 的随机相关矩阵上分别看到约
`-0.1399,-0.1442,-0.1421,-0.1525` 的最小特征值。这只是 E1 检查，但足以说明不能把
`rho(C)` 写成不带绝对值的 `lambda_max(C)` 而不加证明。

复现参数：`random_correlation(n, seed, ridge=0.02)`，每维扫描 seeds `900..929` 并穷举
全部排列；上述四个最小值分别出现在 seeds `915,912,903,900`。运算为 NumPy float64，
未设置“零”容差，因为这里只记录明显负于零的 sanity signal，不作为一般命题证据。

原文 (M3.8) 实际写的是

\[
 \|\mathcal C\|_{F\to F}
 =\max_i|\lambda_i(\mathcal C)|
 =\rho(\mathcal C),
\]

这对有限维自伴算子完全正确，负谱不构成 blocker。后面的
`||C^K||=r_A^K`、resolvent Neumann series 和 finite-time bridge 也都使用这个绝对谱半径，
没有错误地使用最大代数特征值。

此外，positive-map Perron--Frobenius 定理保证 \(+r_A\) 本身有非零 PSD eigenmatrix；
所以即使存在 \(-r_A\)，也不会使文中的 Perron 构造失去正的 spectral-radius
eigenmatrix。

**判定：PASS；建议在 Lemma M3.1 后明确加一句“CP 不排除负 superoperator spectrum”。**

## 2. subunital 与严格谱半径

每个 \(P_\pi\) 是正交投影的乘积，所以

\[
 P_\pi^\top P_\pi\preceq I,
 \qquad \mathcal C(I)\preceq I.
\]

该 Loewner 方向正确。由于 `C` 还自伴，对 Perron matrix \(W\succeq0\) 有

\[
 r_A\operatorname{tr}W
 =\langle I,\mathcal C(W)\rangle
 =\langle\mathcal C(I),W\rangle
 \le\operatorname{tr}W,
\]

故 \(r_A\le1\)。但 Theorem M3.5 要选 `r_A<alpha<1`，仅有 subunital 还没有给出严格
小于一。

在本仓库假设 \(A\succ0\) 下，严格性是成立的：Meany/Gram full-sweep bound 给每个排列

\[
 \|P_\pi\|_2^2\le1-\det A<1,
\]

因而

\[
 r_A\le1-\det A<1.
\]

主文其他路线已经有这个 proof candidate，但 M3 文档应在首次要求 `alpha<1` 时显式引用，
或把一般 resolvent 定理先写为任意 `alpha>r_A`，再在 RPCD SPD corollary 中加入
`alpha<1`。

**判定：P1 文案缺口；仓库现有引理可立即关闭，不是核心 blocker。**

## 3. common reducing blocks 与 off-diagonal operator blocks

设 Kraus family \(\{P_\pi\}\) 在转置下封闭。若 \(S\) 对每个 \(P_\pi\) 共同不变，则对
\(v\in S^\perp,s\in S\)，

\[
 \langle P_\pi v,s\rangle
 =\langle v,P_\pi^\top s\rangle=0,
\]

因为 \(P_\pi^\top\) 也属于 family 并保持 \(S\)。故 \(S^\perp\) 同样共同不变；递归分解
确实得到正交 reducing decomposition

\[
 \mathbb R^n=\bigoplus_jV_j,
 \qquad P_\pi=\bigoplus_jP_{\pi,j}.
\]

需要补写的是：superoperator 在矩阵空间上不只有 diagonal blocks。对
\(X\in\operatorname{Hom}(V_k,V_j)\)，相应 block 是

\[
 \mathcal C_{jk}(X)
 =\mathbb E[P_{\pi,j}^\top X P_{\pi,k}].                  \tag{A1}
\]

因此 full \(r_A\) 原则上可能由某个 `j!=k` 的 off-diagonal operator block 决定。原文
没有证明 `r_A=max_j r_j`，但其 exact-metric 论证实际上**不需要**这个等式：

- diagonal restriction \(\mathcal C_{jj}\) 是 full operator 的不变子空间，故
  \(r_j:=\rho(\mathcal C_{jj})\le r_A\)；
- 对 block-diagonal \(H_*=\bigoplus_jG_j\)，所有 off-diagonal 输入块为零，且

  \[
  \mathcal C(H_*)=\bigoplus_j\mathcal C_{jj}(G_j)
  =\bigoplus_jr_jG_j
  \preceq r_AH_*.
  \]

所以 off-diagonal operator blocks 即使支配 \(r_A\)，也只会让右端 rate 更宽，不会破坏
Loewner certificate。事实上可再用 full Perron PSD eigenmatrix 的非零 diagonal block
证明某个 diagonal block 也达到 \(r_A\)，但这不是现有证明所必需。

**判定：PASS；主文应显式展示 (A1)，避免读者误以为忽略了矩阵空间的交叉块。**

## 4. Perron eigenmatrix 的满秩论证

在最小共同不变块 \(V_j\) 上，positive-map PF 给

\[
 G_j\succeq0,\quad G_j\ne0,
 \qquad \mathcal C_{jj}(G_j)=r_jG_j.
\]

若 \(u\in\ker G_j\)，则

\[
 0=u^\top r_jG_ju
 ={1\over n!}\sum_\pi
   (P_{\pi,j}u)^\top G_j(P_{\pi,j}u).
\]

每一项非负，故每一项都为零，即
\(P_{\pi,j}u\in\ker G_j\) 对所有排列成立。因此 \(\ker G_j\) 是共同不变子空间。块的
最小性迫使 kernel 为 `0` 或整个块；后者与 \(G_j\ne0\) 冲突，所以 \(G_j\succ0\)。

这个论证不需要 Perron eigenvalue 简单，也不要求 map primitive；即使 \(r_j=0\) 仍成立。
唯一应写清的是 PF theorem 应用于实 symmetric cone（或先 complexify 再取 Hermitian
eigenmatrix），而不是把“自伴”误当成自动给 PSD eigenvector。

由此 \(H_*=\bigoplus_jG_j\succ0\)，上一节已验证
`C(H_*)<=r_A H_*`。再结合任意 PD subeigenmatrix 都满足 `r_A<=beta(H)`，(M3.13)--
(M3.17) 和 minimum attainment 均成立。

**判定：PASS，无 rank-deficiency blocker。**

## 5. 任意 metric 上界谱半径的方向

令

\[
 \mathcal D_H(X)=H^{-1/2}
 \mathcal C(H^{1/2}XH^{1/2})H^{-1/2}.
\]

这是由 invertible cone congruence 得到的 superoperator similarity，故保持谱并保持 PSD
cone。若 `D_H(I)<=beta I`，取 PF matrix
`W>=0, W!=0, D_H(W)=r_AW`，则

\[
 W\preceq\|W\|_{op}I
 \Longrightarrow
 r_AW\preceq\beta\|W\|_{op}I.
\]

在 \(W\) 的最大特征向量上取二次型恰得 \(r_A\le\beta\)。乘法顺序和 Loewner 方向均
正确。

**判定：PASS。**

## 6. direct spectral finite-time bridge

fresh iid epochs 下，forward covariance map 是
\(X\mapsto\mathbb E[P_\pi XP_\pi^\top]\)。反序封闭使它等于本文的 observable
\(\mathcal C\)，故

\[
 \Sigma_K=\mathcal C^K(y_0y_0^\top).
\]

自伴性给
`||C^K||_(F->F)=r_A^K`，即使有负谱也成立。因此

\[
\begin{aligned}
 \mathbb E\|y_K\|^2
 &=\langle I,\mathcal C^K(y_0y_0^\top)\rangle_F\\
 &\le\|I\|_F r_A^K\|y_0y_0^\top\|_F\\
 &=\sqrt n,r_A^K\|y_0\|^2.
\end{aligned}
\]

`||I||_F=sqrt(n)`、rank-one Frobenius norm 以及 exponent 均正确。它控制
`E||x_K||_A^2`；再用 Jensen 得到 (M3.24) 的 expectation of distance，而不是
`||E x_K||`。

`q<=exp(-mu)` 的两条分支也正确：

\[
 (1-1/n)^n\le e^{-1}\le e^{-\mu},
 \qquad
 (1-\mu/n)^{2n}\le e^{-2\mu}\le e^{-\mu}.
\]

所以 (M3.25) 对“expected squared A-distance 的相对误差 epsilon”系数正确。若改成
`E||x_K||_A <= epsilon ||x_0||_A`，必须重新使用 (M3.24)，所需 log 系数会改变；主文
当前没有混用二者。

**判定：PASS。**

## 7. resolvent metric、条件数与 finite truncation

对 `alpha>r_A=||C||_(F->F)`，

\[
 H_\alpha=\sum_{k\ge0}\alpha^{-k-1}\mathcal C^k(I)
\]

在 Frobenius norm 绝对收敛。负 superoperator eigenvalues 不影响收敛，因为控制量是
绝对谱半径；每一项仍因 map positivity 而 PSD。移位求和严格给出

\[
 \mathcal C(H_\alpha)=\alpha H_\alpha-I.
\]

首项给 \(\lambda_{min}(H_\alpha)\ge1/\alpha\)，而

\[
 \lambda_{max}(H_\alpha)
 \le\|H_\alpha\|_F
 \le{\sqrt n\over\alpha-r_A},
\]

故

\[
 \kappa(H_\alpha)
 \le{\alpha\sqrt n\over\alpha-r_A}.
\]

分母、\(\sqrt n\) 和 \(\alpha\) 因子均正确。这是上界而非 sharp condition number；
主文没有把它写成等式。

当 `r_A=q>0` 时，`q`-resolvent 确实发散，而不仅是 inverse operator 形式上奇异：PF
matrix \(G\succeq0\) 满足 `C(G)=qG`，并且
`<I,G>=tr(G)>0`，所以 `I` 在 `q` eigenspace 上有非零投影。exact-rate 的 block Perron
metric 仍存在，但 resolvent 条件数不能由该极限控制。这个区分正确。

有限和恒等式

\[
 \alpha H_{\alpha,m}-\mathcal C(H_{\alpha,m})
 =I-\alpha^{-m}\mathcal C^m(I)
\]

也正确。因为 `C^m(I)>=0` 且
`||C^m(I)||_F<=sqrt(n)r_A^m`，确有

\[
 \mathcal C^m(I)\preceq\sqrt n r_A^m I.
\]

所以 (M3.38) 足以使 residual PSD。主文宜把“PSD + Frobenius norm bound 推出 Loewner
bound”这一中间句写出。

naive regularization (M3.39) 也通过：

\[
 \alpha(H+\eta I)-\mathcal C(H+\eta I)
 \succeq(\alpha-r)H-(1-\alpha)\eta I,
\]

给出的 \(\eta\) 条件方向正确。

**判定：PASS；仅需补严格收缩来源和 finite-sum 的中间 Loewner 句。**

## 8. Ville all-time 转换

若 \(H\succ0\) 是运行前固定的确定性 metric，且每个 epoch 的排列在给定过去后仍独立
均匀，则

\[
 \mathbb E[\|y_{K+1}\|_H^2\mid\mathcal F_K]
 \le\alpha\|y_K\|_H^2.
\]

对 \(\alpha>0\)，

\[
 S_K=\alpha^{-K}\|y_K\|_H^2
\]

是非负 supermartingale。Ville 给

\[
 \Pr\left\{\sup_{K\ge0}S_K>{S_0\over\delta}\right\}\le\delta.
\]

利用
`lambda_min(H)||y||^2 <= ||y||_H^2 <= lambda_max(H)||y||^2`，得到

\[
 \|x_K\|_A^2
 \le{\kappa(H)\over\delta}\alpha^K\|x_0\|_A^2
\]

对所有 \(K\) 同时成立，概率至少 \(1-\delta\)。\(\kappa\)、\(1/\delta\) 和 exponent
均正确；这不是把单时刻 Markov bound 错误地做 union bound。

必要限定：若 `H` 是看过同一条 RPCD 轨迹后自适应挑选的随机 SDP 解，上述条件期望和
Ville 不能原样使用；必须 sample split，或证明 metric 是 predictable 并重新构造
supermartingale。主文讨论的是固定 \(A\) 后预先构造的 `H`，所以公式本身成立，但应把
这一点写进定理假设。`alpha=0` 的单独处理也正确。

**判定：PASS with P1 assumption clarification。**

## 9. 条件 mixing 引理

(M3.40) 被正确标成条件引理，而不是从 irreducibility 自动推出的 quantitative theorem。
在 `tr(G)=1`、`C(G)=rG` 下，代入即得

\[
 \left(\sum_{k=0}^{m-1}r^k\right)G\succeq\gamma I.
\]

又有 \(\lambda_{max}(G)\le\operatorname{tr}G=1\)，故

\[
 \kappa(G)\le {\sum_{k=0}^{m-1}r^k\over\gamma}\le {m\over\gamma}.
\]

正确。必须保持当前措辞：定性 irreducibility 本身不给 uniform
`gamma(n,mu)`，尤其接近 reducible 的 family 可能使条件数爆炸。

**判定：PASS。**

## 10. Blocker 清单与建议修订

### P0 blocker

无。

### P1：应在晋级前修改

1. 在 Lemma M3.1 后明确：positive/CP 不表示 superoperator PSD；后续 `r_A` 始终是
   最大绝对特征值。可以保留一个小型负谱回归测试，防止未来把 `rho` 改成 `lambda_max`。
2. 在 Theorem M3.3 中加入 matrix-space blocks (A1)，并说明只需
   `r_j<=r_A`，不需要假设 off-diagonal blocks 不支配 full rate。
3. 在 Theorem M3.5 前引用 `r_A<=1-det(A)<1`，关闭 `alpha<1` 的存在性。
4. 在 Ville 命题中显式要求：`H` 预先固定、初值固定或适当条件化、每个 epoch fresh
   conditional-uniform permutation。

### P2：可读性增强

1. 在 (M3.38) 前补写 `C^m(I)>=0`，解释 Frobenius norm 如何变成 Loewner bound。
2. PF 应用注明是在 real symmetric PSD cone 上，或通过 complexification/Hermitian cone。
3. 明确区分 (M3.25) 的 squared-distance tolerance 与 (M3.24) 的 expected-distance
   tolerance。

完成这些局部修改后，本审计没有留下数学 blocker；仍然开放的是主文已承认的两个核心
问题：一般 C001 rate 本身，以及 exact-rate metric 在等号边界的 uniform condition number。
