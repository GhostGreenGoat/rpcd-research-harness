# 第三轮路线 M3：自伴 covariance operator 与适应性 Lyapunov 度量

日期：2026-08-21
对象：一般单位对角 SPD 二次函数上的 RPCD；C001 / Conjecture 4.1

## 0. 状态与结论先行

- 本文**没有证明** C001 的核心谱半径估计

  \[
  r_A:=\rho(\mathcal M_A)\le q_{n,\mu},\qquad
  q_{n,\mu}:=\max\{(1-1/n)^n,(1-\mu/n)^{2n}\}.
  \]

- 下文标为 `E3 proof draft` 的命题随后通过了
  `docs/ITER3_AUDIT_M3_OPERATOR_LYAPUNOV.md` hostile audit；仍未完成 E5 独立重证。
- M3 的主要正面结论是：对 RPCD 这个反序封闭的随机矩阵族，

  \[
  r_A\le q
  \quad\Longleftrightarrow\quad
  \exists Q_L\succ0:\ \mathcal M_A^*(Q_L)\preceq qQ_L.       \tag{M3.1}
  \]

  所以 C001 与“存在一个适应 Hessian 的正定二次 Lyapunov 度量”是等价的；强一步
  `A`-energy 命题只是在 (M3.1) 中固定选择 `Q_L=A`，因而确实更强。
- (M3.1) 的存在性不自动给出 `Q_L` 相对 `A` 的条件数。可量化的 canonical 构造是

  \[
  H_\alpha=(\alpha I-\mathcal C_A)^{-1}(I),\qquad \alpha>r_A,
  \]

  它满足

  \[
  \mathcal C_A(H_\alpha)=\alpha H_\alpha-I,qquad
  \kappa(H_\alpha)\le {\alpha\sqrt n\over \alpha-r_A}.       \tag{M3.2}
  \]

  代价是速率从 `r_A` 放慢到任意 `alpha>r_A`。在等号边界 `r_A=q`，exact-rate 度量存在，
  但其统一条件数仍是本路线的主要瓶颈。
- 全排列平均还有一个无需构造固定度量的直接 finite-time 推论：

  \[
  \mathbb E\|x_K\|_A^2\le \sqrt n\,r_A^K\|x_0\|_A^2.        \tag{M3.3}
  \]

  这与 `ITER3_M1_STRONG_ONE_EPOCH_ENERGY.md` 第 2 节的独立推导一致。若 C001 成立，
  (M3.3) 已给出 expectation of squared distance，而不是 distance of the expected iterate。

## 1. Energy coordinates 中的反序自伴性

令 `diag(A)=1`、`A succ 0`，并定义

\[
 v_i=A^{1/2}e_i,\qquad Z_i=I-v_iv_i^\top.
\]

因为 `||v_i||^2=A_ii=1`，每个 `Z_i` 都是正交投影。若

\[
 U_i=I-e_ie_i^\top A,
 \qquad T_\pi=U_{\pi_n}\cdots U_{\pi_1},
\]

则在 `y=A^(1/2)x` 坐标中

\[
 P_\pi=A^{1/2}T_\pi A^{-1/2}
      =Z_{\pi_n}\cdots Z_{\pi_1}.                           \tag{M3.4}
\]

定义 observable covariance operator

\[
 \mathcal C_A(H):=\mathbb E_\pi[P_\pi^\top H P_\pi].       \tag{M3.5}
\]

若 `pi^rev=(pi_n,...,pi_1)`，则

\[
 P_{\pi^{\rm rev}}=P_\pi^\top.                             \tag{M3.6}
\]

均匀分布在反序下不变，所以 (M3.5) 也等于

\[
 \mathbb E_\pi[P_\pi H P_\pi^\top].
\]

### Lemma M3.1（E3 proof draft：自伴、正、subunital）

`C_A` 在 Frobenius 内积下自伴，保持 PSD cone，并且

\[
 \mathcal C_A(I)\preceq I.                                  \tag{M3.7}
\]

因此其全部特征值为实数，而且

\[
 \|\mathcal C_A\|_{F\to F}=\rho(\mathcal C_A)=:r_A.        \tag{M3.8}
\]

**证明草稿。** (M3.6) 把 `C_A` 的 Frobenius adjoint 中的每个 word 配对回另一个等概率
word。正性来自 Kraus 形式。每个 `P_pi` 是正交投影的乘积，故 `P_pi^T P_pi<=I`，平均后
得到 (M3.7)。有限维自伴算子的 operator norm 等于最大绝对特征值，即谱半径。`square`

这里的 positive/CP 是保持 PSD cone，不表示 superoperator 本身在 Frobenius Hilbert
空间上 PSD；其谱可以包含负特征值。因此全文的 `r_A` 始终是
`max_i |lambda_i(C_A)|`，不是未经证明的最大代数特征值。

原坐标的 observable map

\[
 \mathcal M_A^*(Q):=\mathbb E_\pi[T_\pi^\top Q T_\pi]
\]

与 (M3.5) 满足

\[
 Q=A^{1/2}HA^{1/2}
 \quad\Longrightarrow\quad
 \mathcal M_A^*(Q)=A^{1/2}\mathcal C_A(H)A^{1/2}.           \tag{M3.9}
\]

因此 `C_A` 与 `M_A^*` 相似；`M_A^*` 又是 forward covariance map `M_A` 的 Frobenius
adjoint，三者谱半径相同，都是 (M3.8) 中的 `r_A`。

故 `Q` 相对 `A` 的广义条件数正好是

\[
 \kappa_A(Q):=
 {\lambda_{\max}(A^{-1/2}QA^{-1/2})
  \over\lambda_{\min}(A^{-1/2}QA^{-1/2})}
 =\kappa(H).                                                \tag{M3.10}
\]

Kim--Lee--Yun 的 Lemma 2.3 与 Appendix A.1 已经利用同一个 energy similarity 和
complementary/reverse permutation pairing 证明 RPCD matrix operator 可对角化。本文不把
Lemma M3.1 的基础对称化本身作为新颖性主张；新增用途是 exact Lyapunov attainment、显式
finite-time prefactor 和 resolvent conditioning。

## 2. 谱半径与正定 Lyapunov metric 的等价性

对 `H succ 0` 定义

\[
 \beta_A(H):=\lambda_{\max}\!\left(
 H^{-1/2}\mathcal C_A(H)H^{-1/2}\right).                   \tag{M3.11}
\]

于是 `C_A(H)<=beta_A(H)H`。

### Lemma M3.2（E3 proof draft：任何证书都上界谱半径）

对每个 `H succ 0`，

\[
 r_A\le\beta_A(H).                                         \tag{M3.12}
\]

**证明草稿。** 令

\[
 \mathcal D_H(X)=H^{-1/2}\mathcal C_A(H^{1/2}XH^{1/2})H^{-1/2}.
\]

它与 `C_A` 相似、保持 PSD cone，且 `D_H(I)<=beta_A(H)I`。有限维 positive-map
Perron--Frobenius 定理给出 `W>=0`、`W!=0`，满足
`D_H(W)=r_A W`。由 `W<=||W||_op I` 和正性，

\[
 r_AW=\mathcal D_H(W)
 \preceq\|W\|_{\rm op}\mathcal D_H(I)
 \preceq\beta_A(H)\|W\|_{\rm op}I.
\]

在 `W` 的最大特征向量上取二次型，得到 `r_A<=beta_A(H)`。`square`

对一般 positive map，通常只能保证任意 `alpha>r` 存在正定 subeigenmatrix；RPCD 的
Kraus family 还有额外的 transpose closure，使最优值在 `alpha=r` 也能取到。

### Theorem candidate M3.3（E3 proof draft：exact-rate PD metric 存在）

对 (M3.5) 的 RPCD operator，总存在 `H_* succ 0` 使

\[
 \boxed{\mathcal C_A(H_*)\preceq r_AH_*.}                   \tag{M3.13}
\]

因此

\[
 \boxed{r_A=\min_{H\succ0}\beta_A(H).}                     \tag{M3.14}
\]

**证明草稿。** Kraus family `{P_pi}` 因 (M3.6) 在转置下封闭。把 `R^n` 递归分解为这族
矩阵的最小共同不变子空间。若 `S` 对所有 `P_pi` 不变，它也对所有 `P_pi^T` 不变，故
`S^perp` 同样不变；所以这是一个正交 reducing decomposition，所有 `P_pi` 同时成为
block diagonal。

在每个最小块 `V_j` 上，令 `C_j` 为相应的 CP map，`r_j=rho(C_j)`。有限维 positive-map
Perron--Frobenius 定理给出非零 `G_j>=0`，满足

\[
 \mathcal C_j(G_j)=r_jG_j.                                  \tag{M3.15}
\]

事实上 `G_j` 必须正定。若 `u in ker(G_j)`，则

\[
 0=u^\top\mathcal C_j(G_j)u
  ={1\over n!}\sum_\pi\|G_j^{1/2}P_{\pi,j}u\|^2,
\]

从而 `ker(G_j)` 对块内所有 Kraus 矩阵共同不变；块的最小性排除非平凡 kernel。
又因 `C_j` 是 `C_A` 在一个不变矩阵子空间上的限制，`r_j<=r_A`。取

\[
 H_*:=\bigoplus_j G_j\succ0
\]

便有

\[
 \mathcal C_A(H_*)=\bigoplus_j r_jG_j
 \preceq r_A\bigoplus_jG_j.
\]

结合 Lemma M3.2 即得 (M3.14)。`square`

矩阵空间还包含 off-diagonal blocks

\[
 \operatorname{Hom}(V_k,V_j),\qquad
 X\longmapsto\mathbb E[P_{\pi,j}^\top X P_{\pi,k}].
\]

它们可能影响 full spectral radius；上面的证明没有假设
`r_A=max_j r_j`。所需的只有每个 diagonal restriction 的 `r_j<=r_A`，而 block-diagonal
`H_*` 的 off-diagonal 输入块为零，所以这些交叉 operator blocks 不破坏 (M3.13)。

这里用到的外部基础是：Evans--Høegh-Krohn (1978) Theorem 2.5 给任意有限维 positive map
一个 PSD Perron eigenvector，Theorem 2.3 给 irreducible 情形 strictly positive Perron
eigenvector；Farenick (1996) Theorem 2 把 Kraus 矩阵无共同非平凡不变子空间与 CP map
irreducibility 联系起来。上面的 kernel 论证把所需特例直接写了出来。

### Corollary M3.4（E3 proof draft：C001 的等价 Lyapunov 形式）

对任意 `q>=0`，

\[
 r_A\le q
 \quad\Longleftrightarrow\quad
 \exists H\succ0:\ \mathcal C_A(H)\preceq qH              \tag{M3.16}
\]

\[
 \quad\Longleftrightarrow\quad
 \exists Q_L\succ0:\ \mathcal M_A^*(Q_L)\preceq qQ_L.     \tag{M3.17}
\]

第一方向用 Theorem M3.3，反方向用 Lemma M3.2；(M3.17) 来自 (M3.9)。因此固定 `A` 的
certificate search 可以写成 SDP feasibility：

\[
 I\preceq H\preceq tI,\qquad \mathcal C_A(H)\preceq qH,     \tag{M3.18}
\]

并最小化 `t`。这在逻辑上没有绕开 C001：对所有 `A` 解析地证明 (M3.18) 可行，正好与
证明谱半径界同样困难。它的价值在于把“强制 `H=I`”放宽为可适应矩阵几何的证书。

## 3. 任意正定 metric 给出的 finite-time 与高概率结论

若 `C_A(H)<=alpha H`，其中 `H` 在运行前由固定 Hessian 预先确定，且每个 epoch 在给定
过去后仍 fresh、条件均匀独立重排，则

\[
 \mathbb E[\|y_K\|_H^2]\le
 \alpha^K\|y_0\|_H^2.                                     \tag{M3.19}
\]

由范数等价和 Jensen，

\[
 \boxed{
 \mathbb E\|x_K\|_A^2
 \le\kappa(H)\alpha^K\|x_0\|_A^2,
 }                                                          \tag{M3.20}
\]

\[
 \boxed{
 \mathbb E\|x_K\|_A
 \le\sqrt{\kappa(H)}\,\alpha^{K/2}\|x_0\|_A.
 }                                                          \tag{M3.21}
\]

(M3.21) 是 expectation of distance，不是较弱的 `||E x_K||_A`。

此外

\[
 S_K:=\alpha^{-K}\|y_K\|_H^2
\]

是非负 supermartingale。Ville 不等式给出：以至少 `1-delta` 的概率，对所有 `K>=0`
同时有

\[
 \boxed{
 \|x_K\|_A^2
 \le {\kappa(H)\over\delta}\alpha^K\|x_0\|_A^2.
 }                                                          \tag{M3.22}
\]

这是 time-uniform high-probability certificate；若 `alpha=0`，则一步期望为零意味着误差
几乎处处归零，单独处理即可。

### 不构造 `H` 的直接 spectral-to-finite-time bridge

由自伴性，若 `Sigma_0=y_0y_0^T`，则

\[
\begin{aligned}
 \mathbb E\|y_K\|^2
 &=\langle I,\mathcal C_A^K(\Sigma_0)\rangle_F\\
 &=\langle\mathcal C_A^K(I),\Sigma_0\rangle_F\\
 &\le\|\mathcal C_A^K(I)\|_F\|\Sigma_0\|_F\\
 &\le\sqrt n\,r_A^K\|y_0\|^2.
\end{aligned}                                               \tag{M3.23}
\]

所以得到 (M3.3) 以及

\[
 \mathbb E\|x_K\|_A\le n^{1/4}r_A^{K/2}\|x_0\|_A.        \tag{M3.24}
\]

若 C001 成立，由 `q_(n,mu)<=exp(-mu)`，平方 `A`-distance 的相对误差 `epsilon` 可由

\[
 K\ge {1\over\mu}\left(\tfrac12\log n+\log{1\over\epsilon}\right)
                                                                    \tag{M3.25}
\]

个 epoch 保证。即 coordinate updates 为

\[
 O\!\left({n\over\mu}(\log n+\log(1/\epsilon))\right).     \tag{M3.26}
\]

它只比无 prefactor 的 conjectured finite-time 目标多一个 additive `log n` warm-up。
Euclidean squared distance 还可写成

\[
 \mathbb E\|x_K\|_2^2
 \le\sqrt n\,\kappa(A)r_A^K\|x_0\|_2^2,                   \tag{M3.27}
\]

其中 `lambda_max(A)<=n-(n-1)mu`。

## 4. Resolvent Lyapunov metric：显式条件数

### Theorem candidate M3.5（E3 proof draft：canonical resolvent certificate）

由 C023 的 full-sweep Gram bound，SPD 情形满足

\[
 r_A\le1-\det A<1.
\]

取任意 `r_A<alpha<1`，定义

\[
 H_\alpha
 :=\sum_{k=0}^\infty\alpha^{-k-1}\mathcal C_A^k(I)
 =(\alpha I-\mathcal C_A)^{-1}(I).                          \tag{M3.28}
\]

则级数在 Frobenius norm 中收敛，每一项 PSD，而且

\[
 H_\alpha\succeq\alpha^{-1}I,                              \tag{M3.29}
\]

\[
 \boxed{\mathcal C_A(H_\alpha)=\alpha H_\alpha-I
 \prec\alpha H_\alpha,}                                   \tag{M3.30}
\]

\[
 \boxed{\kappa(H_\alpha)
 \le {\alpha\sqrt n\over\alpha-r_A}.}                     \tag{M3.31}
\]

**证明草稿。** Lemma M3.1 给

\[
 \|\mathcal C_A^k(I)\|_F\le r_A^k\|I\|_F=\sqrt n\,r_A^k,
\]

所以 (M3.28) 收敛且

\[
 \lambda_{\max}(H_\alpha)\le\|H_\alpha\|_F
 \le{\sqrt n\over\alpha-r_A}.
\]

首项给 (M3.29)；移位求和给 (M3.30)，两条特征值界给 (M3.31)。`square`

令 `Q_(L,alpha)=A^(1/2)H_alpha A^(1/2)`，则 (M3.9)--(M3.10) 给

\[
 \mathcal M_A^*(Q_{L,\alpha})\prec\alpha Q_{L,\alpha},
 \qquad
 \kappa_A(Q_{L,\alpha})\le{\alpha\sqrt n\over\alpha-r_A}.
                                                                    \tag{M3.32}
\]

### 条件于 C001 的统一选择

若 `r_A<=q=q_(n,mu)`，取

\[
 \alpha={1+q\over2}.
\]

则

\[
 \kappa(H_\alpha)\le{2\sqrt n\over1-q},
 \qquad
 \alpha^K\le\exp[-K(1-q)/2].                              \tag{M3.33}
\]

又因

\[
 q\le e^{-\mu},\qquad
 1-q\ge1-e^{-\mu}\ge(1-e^{-1})\mu,                        \tag{M3.34}
\]

(M3.20) 的平方 `A`-distance 相对误差 `epsilon` 由下面的充分条件保证：

\[
 K\ge {2\over(1-e^{-1})\mu}
 \log\!{2\sqrt n\over(1-e^{-1})\mu\epsilon}.             \tag{M3.35}
\]

这个 resolvent bound 多出 `log(n/mu)`，所以对固定时刻 expectation，直接的 (M3.23)
更紧。它的额外价值是提供一个显式、满秩、可验证的 metric，以及 (M3.22) 的 time-uniform
高概率控制。

若已经知道严格谱 slack `r_A<q`，可直接取 `alpha=q`，得到 exact target rate 和

\[
 \kappa(H_q)\le{q\sqrt n\over q-r_A}.                       \tag{M3.36}
\]

当 `r_A=q` 时 resolvent 在 `q` 发散；Theorem M3.3 仍保证某个 exact-rate `H_* succ 0`
存在，但 (M3.31) 不再提供条件数。这精确区分了“证书存在性”和“uniformly useful
finite-time certificate”。

### 有限 resolvent sum 与 naive PSD regularization

有限和

\[
 H_{\alpha,m}:=\sum_{k=0}^{m-1}\alpha^{-k-1}\mathcal C_A^k(I)
\]

满足

\[
 \alpha H_{\alpha,m}-\mathcal C_A(H_{\alpha,m})
 =I-\alpha^{-m}\mathcal C_A^m(I).                           \tag{M3.37}
\]

因为 `C_A^m(I)>=0` 且
`||C_A^m(I)||_F<=sqrt(n)r_A^m`，先有 Loewner 界
`C_A^m(I)<=sqrt(n)r_A^m I`。所以只要

\[
 \sqrt n(r_A/\alpha)^m\le1,                                \tag{M3.38}
\]

它就是一个有限可检查证书。这给出一种 finite-horizon / polynomial harness，而不必显式
求解无限级数。

另一方面，若 `C_A(H)<=rH`，简单加 `eta I` 并不保持 rate `r`。利用 (M3.7)，对
`r<alpha<1`，充分条件是

\[
 \eta\le{(\alpha-r)\lambda_{\min}(H)\over1-\alpha},        \tag{M3.39}
\]

此时 `C_A(H+eta I)<=alpha(H+eta I)`。若起始 Perron matrix 奇异，这个粗 regularization
在 kernel 上失效；resolvent 构造则始终安全。RPCD 的 transpose closure 允许用
Theorem M3.3 的 block Perron 直和避免奇异性，但仍没有 condition-number estimate。

## 5. 条件数瓶颈的定量版本

在一个 irreducible block 上，把 Perron matrix `G` 归一化为 `tr(G)=1`。若能证明某个
`m,gamma>0` 满足

\[
 \sum_{k=0}^{m-1}\mathcal C^k(X)
 \succeq\gamma\operatorname{tr}(X)I
 \quad\text{对所有 }X\succeq0,                             \tag{M3.40}
\]

则由 `C(G)=rG` 得

\[
 \left(\sum_{k=0}^{m-1}r^k\right)G\succeq\gamma I,
\]

从而

\[
 \kappa(G)\le{\sum_{k=0}^{m-1}r^k\over\gamma}
 \le{m\over\gamma}.                                       \tag{M3.41}
\]

这只是一个**条件引理**，不是已建立的 RPCD uniform bound。Farenick 的 irreducibility
criterion 是定性的；当前没有从 `n` 与 `mu` 推出可用 `gamma(n,mu)`。接近 reducible 的
Kraus families 中 Perron metric 可能高度病态，这正是不能从“`H_*` 存在”跳到目标
finite-time constant 的原因。

一个可证伪的下一目标是：在所有最小 reducing blocks 上证明 (M3.40)，并使
`log(m/gamma)=O(log n+log(1/mu))`，或直接证明 SDP (M3.18) 在 `q=q_(n,mu)` 处存在
`t=poly(n,1/mu)`。即使成功，它仍需与 C001 的核心 rate 证明配合；它本身不证明
`r_A<=q_(n,mu)`。

## 6. 一手文献审计与优先权边界

以下只列原论文/出版社页面；“未发现”不是完整优先权证明。

1. **Kim, Lee, Yun (ICML 2025).**
   [PMLR 原文与 PDF](https://proceedings.mlr.press/v267/kim25x.html)。Definition 2.1 定义
   `sigma=lambda_min(D^-1 A)`；在 unit-diagonal 归一化后就是 `lambda_min(A)`。
   Lemma 2.3 与 Appendix A.1 通过 energy similarity 及 complementary permutation pairing
   证明 RPCD matrix operator 可对角化；Conjecture 4.1 给出本文的 `q_(n,mu)` 渐近
   expected squared Euclidean norm rate。原文 Eq. (7) 把二次 convergence measure 写成
   operator power iteration。此次定向审阅没有在文中找到 (M3.13)--(M3.14)、resolvent
   condition bound (M3.31)，或显式 `sqrt(n)` finite-time coefficient (M3.23)。因此这些只可
   称为本 harness deduction，尚不可主张论文层面的新颖性。

2. **Evans--Høegh-Krohn (1978).**
   [期刊 DOI](https://doi.org/10.1112/jlms/s2-17.2.345)。Theorem 2.3 是有限维
   irreducible positive map 的 strictly positive Perron eigenvector / simple spectral-radius
   结果；Theorem 2.5 给一般 positive map 一个非零 PSD spectral-radius eigenvector。
   这是 Theorem M3.3 的 Perron 基础，故 Perron 部分不应声明为新。

3. **Farenick (1996).**
   [AMS 原文 PDF](https://community.ams.org/journals/proc/1996-124-11/S0002-9939-96-03441-7/S0002-9939-96-03441-7.pdf)，
   [DOI](https://doi.org/10.1090/S0002-9939-96-03441-7)。Theorem 2：对 full matrix
   algebra 上的 Kraus map，irreducibility 等价于 Kraus 矩阵没有共同非平凡不变子空间。
   本文利用 RPCD Kraus family 的 transpose closure 把 reducible 情形正交分块，再逐块应用
   该思想。

4. **Agaskar, Wang, Lu (GlobalSIP 2014).**
   [作者稿](https://dash.harvard.edu/server/api/core/bitstreams/7312037d-8b4a-6bd4-e053-0100007fdf3b/content)，
   [DOI](https://doi.org/10.1109/GlobalSIP.2014.7032145)。Proposition 1 对 iid randomized
   Kaczmarz 给出 exact MSE lifting
   `vec(I)^T R_A(p)^N vec(z_0z_0^T)`，其中
   `R_A(p)=sum_i p_i(P_i^perp tensor P_i^perp)`。这是 covariance lifting 的直接先例，
   但不是每 epoch 无放回随机排列，也不给 C001 rate 或 adapted metric condition number。

5. **Recht--R\'e (COLT 2012)**
   [PMLR 原文](https://proceedings.mlr.press/v23/recht12.html) 把无放回投影/最小二乘比较联系到
   noncommutative AM--GM；**Lai--Lim (ICML 2020)**
   [PMLR 原文](https://proceedings.mlr.press/v119/lai20a.html) 证明一般 conjecture 从 `n=5`
   起为假。它们说明不能把 generic noncommutative product inequality 当作 RPCD 黑箱；
   RPCD 的 rank-one frame、完整 sweep 与反序自伴性仍是额外结构。

6. **Bai, Wang, Wu (LAA 2021).**
   [期刊 DOI/摘要](https://doi.org/10.1016/j.laa.2020.10.028) 对 randomized
   Gauss--Seidel 推导 exact mean-squared residual closed form；其 sampling 是逐步 random scan，
   不是每 epoch fresh permutation，故不能直接提供 (M3.1) 的 uniform `q_(n,mu)`。

7. **Han--Xie (2024 preprint).**
   [arXiv:2410.01140](https://arxiv.org/abs/2410.01140) Theorem 3.2 / Corollary 3.3 用
   `max_pi ||T_pi A^dagger A||` 给 reshuffling Kaczmarz 的逐路径 linear rate。它证明一般
   收敛，但使用 worst-permutation norm；没有利用平均 covariance spectral radius，因而
   不给这里 conjectured sharp RPCD rate。

## 7. M3 的最终边界

M3 已经关闭的是逻辑桥，而不是 C001 的数值常数：

1. 全排列反序使 energy covariance operator 真正自伴，消除了 Jordan/nonnormal 暂态。
2. 对 RPCD，`spectral rate <=q` 与某个 PD quadratic Lyapunov certificate at rate `q`
   等价；exact rate `r_A` 可以取到。
3. 任意 `alpha>r_A` 都有显式 resolvent certificate，条件数至多
   `alpha sqrt(n)/(alpha-r_A)`，并给 expectation-of-distance 与 time-uniform
   high-probability bounds。
4. 单独知道 C001 已足够得到带 `sqrt(n)` 前因子的有限时 expected squared `A`-distance
   bound；强 `A`-energy 的意义是去掉此前因子，而不是建立 finite-time 收敛所必需。
5. 仍未解决两件核心事：(a) 对一般 `A` 证明 `r_A<=q_(n,mu)`；(b) 在可能的等号边界
   控制 exact-rate metric 的 `kappa_A(Q_L)`。前者就是原 open conjecture，后者是 M3 新暴露的
   finite-time conditioning 问题。
