# 第二轮路线 A：保留未访问集合的条件 Lyapunov / Bellman 递推

日期：2026-08-20
对象：一般单位对角 SPD Hessian 上的 RPCD Conjecture 4.1（C001）

## 0. 状态声明

- 本文不给出 C001 的证明。
- 下文的 Bellman 递推、残差递推和 Schur 补恒等式是逐式可检验的**一般代数恒等式**；在完成 hostile audit 前，工程状态仍记为 `proof draft`，不晋级为仓库定理。
- “强一轮 A-energy 界”是通向 C001 的**充分条件**，不是已证结论，也不声称它与 C001 本身等价。
- 本路线与 C010 的区别是：不先把随机三角因子压缩成单个平均矩阵。状态始终保留当前未访问集合 `R`，因而保留随机排列的条件信息。
- 本文不提出新颖性/优先权主张。

## 1. 记号

令

\[
  E(x):=x^\top A x,\qquad g:=Ax,
\]

其中 \(A\in\mathbb S_{++}^n\)、\(A_{ii}=1\)。一轮内，\(R\subseteq[n]\) 表示尚未访问的坐标集合，\(m=|R|\)。若下一坐标为 \(i\in R\)，则

\[
  x^+=U_i x=x-e_i g_i,
  \qquad
  E(x^+)=E(x)-g_i^2.                    \tag{1}
\]

把残差限制到尚未访问的坐标：

\[
  h:=g_R,\qquad B:=A_{RR}.
\]

在 `R` 的局部坐标中，令 \(b_i:=Be_i\)，令 \(J_i\) 删除第 \(i\) 个分量，并定义

\[
  L_{B,i}:=J_i(I-b_i e_i^\top).
\]

则更新后尚未访问部分的残差满足严格恒等式

\[
  h^+_{R\setminus\{i\}}
    =L_{B,i}h.                            \tag{2}
\]

因此，给定当前的 \((x,R)\)，未来 suffix 的演化只需要 \(E(x)\)、\(h=(Ax)_R\) 和主子矩阵 \(B=A_{RR}\)；已经访问过的坐标无须作为额外隐状态保存。

## 2. 全矩阵的精确 remaining-set Bellman 递推

给定任意终端二次型 \(Q\succeq0\)，定义一族 \(n\times n\) 对称矩阵

\[
  P_\varnothing(Q):=Q,
\]

\[
  P_R(Q):=\frac1{|R|}\sum_{i\in R}
       U_i^\top P_{R\setminus\{i\}}(Q)U_i,
  \qquad R\ne\varnothing.                \tag{3}
\]

### Lemma A1（精确条件 Bellman 恒等式；proof draft）

若从状态 \((x,R)\) 开始，之后均匀随机排列 `R` 中的坐标并各更新一次，则

\[
 x^\top P_R(Q)x
 =\mathbb E\!\left[x_{\rm end}^\top Qx_{\rm end}
                    \mid x,R\right].     \tag{4}
\]

特别地，在一轮开始处

\[
 P_{[n]}(Q)=\mathbb E_\pi[T_\pi^\top QT_\pi]
             =:\mathcal M_A^*(Q).         \tag{5}
\]

**推导。** 当 \(R=\varnothing\) 时是定义。对 \(|R|\) 归纳，并对均匀的首个坐标 \(i\in R\) 使用全期望公式，即得到 (3)--(4)。因此

\[
  x_k^\top P_{R_k}(Q)x_k
\]

在一轮内部关于“已揭示前缀”的 filtration 是一个 martingale；它不是逐轨迹单调势函数。

### 条件 Lyapunov 证书形式

不必显式算出精确 \(P_R\)。若能构造解析矩阵族 \(W_R\) 满足

\[
 W_\varnothing=Q,
 \qquad
 \frac1{|R|}\sum_{i\in R}U_i^\top W_{R\setminus\{i\}}U_i
 \preceq W_R,                             \tag{6}
\]

以及

\[
 W_{[n]}\preceq qQ,                       \tag{7}
\]

则 \(\mathcal M_A^*(Q)\preceq qQ\)。这给出一个比固定 `A-energy + scalar Jensen` 更大的证书搜索空间：\(W_R\) 可以依赖未访问集合、主子矩阵 \(A_{RR}\) 以及已访问/未访问块之间的耦合。

## 3. A-energy 的降维残差递推

定义 \(|R|\times|R|\) 矩阵 \(K_R\)；其坐标按 `R` 排列：

\[
 K_\varnothing:=0,
\]

\[
 K_R:=\frac1m\sum_{i\in R}
 \left(e_i e_i^\top
       +L_{B,i}^\top K_{R\setminus\{i\}}L_{B,i}\right).       \tag{8}
\]

这里 \(K_{R\setminus\{i\}}\) 使用主子矩阵
\(A_{R\setminus\{i\},R\setminus\{i\}}\) 定义。

### Lemma A2（剩余 sweep 的精确能量降幅；proof draft）

对任意当前状态 \((x,R)\)，

\[
 \mathbb E[E(x_{\rm end})\mid x,R]
 =E(x)-h^\top K_Rh.                       \tag{9}
\]

**证明。** 若首先选择 \(i\)，(1) 给出即时降幅 \(h_i^2\)，(2) 给出 suffix 的输入残差 \(L_{B,i}h\)。对 suffix 使用归纳假设并对 \(i\) 平均，右端恰为 (8)。

因此

\[
 V_R(x):=E(x)-(Ax)_R^\top K_R(Ax)_R       \tag{10}
\]

是 `Q=A` 时 (4) 的降维版本，并满足

\[
 V_R(x)=\frac1{|R|}\sum_{i\in R}
          V_{R\setminus\{i\}}(U_ix).      \tag{11}
\]

这就是本路线的精确条件 Lyapunov：它显式记住 `R`，而不是只记住一轮起点处的 \(A\)-energy。

## 4. 与随机三角因子的精确等价

对主问题 \(B=A_{RR}\) 和 `R` 的一个排列 \(\pi\)，令 \(M_{R,\pi}\) 是相应的置换下三角 Gauss--Seidel 因子。沿该固定 suffix，每一步的选中残差组成向量

\[
 r=M_{R,\pi}^{-1}h.
\]

由 (1)，总能量降幅是 \(\|r\|_2^2\)。所以

\[
 \text{fixed-suffix decrease}
 =h^\top(M_{R,\pi}M_{R,\pi}^\top)^{-1}h. \tag{12}
\]

结合 (9)，对所有 \(h\) 比较二次型得到

\[
 \boxed{
 K_R=\mathbb E_{\pi\in\mathfrak S(R)}
       [(M_{R,\pi}M_{R,\pi}^\top)^{-1}].
 }                                                       \tag{13}
\]

因此 C010 的 Jensen 下界只是

\[
 K_{[n]}\succeq
 \left(\mathbb E_\pi[M_\pi M_\pi^\top]\right)^{-1}
 =(A+S)^{-1}.                             \tag{14}
\]

递推 (8) 则精确保留了 Jensen 在 (14) 中丢掉的逆矩阵波动和所有条件主子问题。C011 只阻断 (14) 后的裸标量比较，不阻断 (8)。

## 5. 通向 C001 的明确矩阵目标

记

\[
 q(A):=\max\left\{(1-1/n)^n,
                    (1-\sigma/n)^{2n}\right\},
 \qquad \sigma=\lambda_{\min}(A).
\]

由 (9)，在完整一轮起点 \(h=Ax\) 时

\[
 \mathcal M_A^*(A)
 =\mathbb E[T_\pi^\top AT_\pi]
 =A-AK_{[n]}A.                            \tag{15}
\]

故以下两式严格等价：

\[
 \mathcal M_A^*(A)\preceq q(A)A,         \tag{16}
\]

\[
 \boxed{
 K_{[n]}\succeq(1-q(A))A^{-1}.
 }                                                       \tag{17}
\]

(16) 是“一轮统一 A-energy 收缩”；它通过正映射迭代和有限维范数等价推出
\(\rho(\mathcal M_A)\le q(A)\)，因而足以证明 C001。反方向未建立：C001 的谱半径结论一般不要求 `A` 本身就是满足 (16) 的一步 Lyapunov 矩阵。

更灵活的版本是利用 (3)：寻找某个 \(Q\succ0\) 及其 subset-dependent 上包络 (6)，使 (7) 对 \(q=q(A)\) 成立。它可以在 (17) 过强时仍然成功。

## 6. Schur 补揭示的精确“顺序损失”

递推 (8) 的困难可用一个 rank-one 恒等式精确定位。固定 \(i\in R\)，把它排在局部坐标第一位，并写

\[
 B=\begin{pmatrix}1&b^\top\\ b&C\end{pmatrix},
 \quad c=C^{-1}b,
 \quad s=1-b^\top C^{-1}b,
 \quad r=1-s.
\]

这里 \(s>0\) 是 Schur 补。令 \(L=[-b\ I]\)，并定义“先更新 \(i\)，然后把其余坐标精确解完”的理想降幅矩阵

\[
 G_i:=e_i e_i^\top+L^\top C^{-1}L.
\]

### Lemma A3（rank-one 顺序损失；proof draft）

直接使用分块逆公式可得

\[
 \boxed{
 B^{-1}-G_i
 =D_i
 :=\frac1s
   \begin{pmatrix}r\\-c\end{pmatrix}
   \begin{pmatrix}r\\-c\end{pmatrix}^{\!\top}
 \succeq0.
 }                                                       \tag{18}
\]

而且 \(D_i\) 相对于 \(B^{-1}\) 的唯一非零广义特征值为 \(r=1-s\)。由于 \(B\succeq\sigma I\)，

\[
 s=\frac1{(B^{-1})_{ii}}\ge\sigma,
 \qquad
 D_i\preceq(1-\sigma)B^{-1}.             \tag{19}
\]

这给出一个有解释力的分解：即使 suffix 被理想地精确求解，“坐标 \(i\) 必须先更新一次且不能回访”也会留下 rank-one 顺序损失 \(D_i\)。RPCD 的改进必须来自不同 \(i\) 的这些 rank-one 坏方向在随机删除过程中不能持续对齐。

另一个等价的精确记账式如下。令

\[
 Z_R(h):=h^\top B^{-1}h,
 \qquad
 \overline D_B:=\frac1m\sum_{i\in R}D_i
\]

（每个 \(D_i\) 嵌回 `R` 的共同局部坐标）。由 (18)，

\[
 \mathbb E_i[Z_{R\setminus\{i\}}(L_{B,i}h)]
 =Z_R(h)-\frac1m\|h\|_2^2-h^\top\overline D_Bh.          \tag{20}
\]

其中 \(\|h\|^2/m\) 正是该步的条件期望能量降幅。由完整起点
\(Z_{[n]}(Ax)=E(x)\) 向后迭代到 \(Z_\varnothing=0\)，得到

\[
 \boxed{
 \mathbb E[E(x_{\rm end})]
 =\mathbb E\sum_{k=0}^{n-1}
 h_{R_k}^\top\overline D_{A_{R_kR_k}}h_{R_k}.
 }                                                       \tag{21}
\]

所以“一轮后剩余的能量”恰好是沿随机删除链累计的 Schur 顺序损失；(21) 不是估计，而是恒等式。

## 7. 明确瓶颈：标量归纳会丢掉坏方向的去对齐

假设尝试仅用

\[
 K_{R\setminus\{i\}}\succeq c_{m-1}C^{-1}
\]

做标量归纳。将 (18) 代入 (8) 可得所需的关键比较

\[
 (c_{m-1}-c_m)B^{-1}
 +\frac{1-c_{m-1}}m I
 -\frac{c_{m-1}}m\sum_{i\in R}D_i
 \succeq0.                               \tag{22}
\]

仅逐项使用 (19) 会把所有 rank-one 坏方向当作完全对齐。具体地，它只能认证递推系数

\[
 c_m^{\rm crude}
 :=\sigma c_{m-1}+\frac\sigma m(1-c_{m-1}),              \tag{23}
\]

即 `K_R\succeq c_m^{\rm crude}B^{-1}`。这是随 `m` 快速恶化的粗界，远达不到 (17) 需要的
\(c_n=1-q(A)\)。因此下面这条做法被标为解析障碍：

> 只保存 `m`、`sigma` 和一个标量系数 `c_m`，再逐个上界 `D_i`，无法利用随机排列中坏方向随 principal submatrix 改变而去对齐的机制。

本路线下一步应直接攻击下面二者之一，而不是回到裸 Jensen：

1. 证明沿随机删除链的累计损失 (21) 不超过 \(q(A)E(x)\)；证明必须同时控制 \(D_i\) 的方向和下一状态 \(L_{B,i}h\)。
2. 构造真正依赖 `R` 的矩阵上包络 \(W_R\)，例如包含未访问残差块和跨块项，使 (6)--(7) 闭合。

一个最小、可证伪的 bottleneck lemma 是强 A-energy 命题 (17)。若它失败，remaining-set Bellman 路线仍可通过一般 \(Q\ne A\) 的 (6)--(7) 继续；若它成立，则立即推出 C001。

## 8. 本轮结论

1. 得到了精确的 subset Bellman 递推 (3) 和低维残差递推 (8)，不再把一轮随机排列压成单个平均 Gram 矩阵。
2. 证明草稿显示 \(K_R\) 与随机三角因子逆 Gram 的期望完全相同，见 (13)；C010 是它的一次 Jensen 松弛。
3. 把本路线通向 C001 的强目标压缩成单个矩阵不等式 (17)。
4. 得到了 rank-one Schur 顺序损失 (18) 及累计损失恒等式 (21)。它们解释了裸标量归纳为什么太松，也指出需要控制的真正对象是坏方向在随机 principal-submatrix 链上的去对齐。
5. 尚未关闭 (17) 或构造出满足 (6)--(7) 的显式 \(W_R\)，因此 C001 状态不变，仍为 open conjecture。
