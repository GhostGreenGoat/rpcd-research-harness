# 第二轮路线 B：对称化与极值结构

日期：2026-08-20
目标：考察“Kim--Lee--Yun 的置换不变 Hessian 是 RPCD 最坏情形”能否由群平均、
majorization 或局部坐标混合推出。

## 0. 结论摘要与证据状态

本轮没有证明 C001。得到的主要解析结论是：

1. **严格结论（证明草稿，E3）**：RPCD 二阶矩谱半径在 signed permutation
   conjugation 下不变。
2. **严格结论（证明草稿，E3）**：对任意符号向量先 sign-switch、再做全置换
   twirl，所得 equicorrelation 参数落在一个精确区间；区间正端点的唯一饱和者正是
   full-block 的 signed permutation-invariant Hessian。
3. **严格解析反例（E2/E3，待独立复算）**：保持单位对角和同一个
   `lambda_min = 2/5` 的一次轨道中点平均，会把 RPCD rate 从
   `(4521 + 3 sqrt(2321049))/31250` 严格降到 `153/625`。所以极值证明所需的
   “轨道平均使 rate 增大”或 rate 凹性是错误的。
4. **严格几何障碍（证明草稿，E3）**：一般可行 Hessian 不是结构化 signed-block
   Hessian 的凸组合；障碍在 `n=3` 已出现，是 elliptope 与 cut polytope 的差异。
5. **仍可能成立的替代路线**：不要平均 Hessian；应当固定 Hessian 后平均
   Lyapunov 证书，或证明 extremizer 必须饱和某个 signed-correlation 子集。后两种
   操作有严格的局部引理支撑。

这里的 rate 记为

$$
R(A):=\rho(\mathcal M_A),\qquad
\mathcal M_A(X)=\mathbb E_p[T_pXT_p^\top].
$$

转置约定改成 `E[T_p^T X T_p]` 不影响以下谱结论。

## 1. Signed-permutation 等变性

令 `Q` 为置换矩阵或对角符号矩阵，且令

$$
A'=Q^\top A Q,\qquad \mathcal C_Q(X)=Q^\top XQ.
$$

重新标记均匀排列后，每个 epoch 算子满足

$$
T_{A',p}=Q^\top T_{A,p'}Q
$$

其中 `p -> p'` 是排列集合的双射。因此

$$
\mathcal M_{A'}=\mathcal C_Q\,\mathcal M_A\,\mathcal C_Q^{-1},
\qquad R(A')=R(A).
$$

这说明 sign switching 和坐标重标号是完全合法的 gauge 变换。但这只比较一个
群轨道上的点，并不比较轨道的凸平均。

## 2. Signed twirl 的精确区间与唯一正端饱和者

设 `A` 为单位对角 SPD，且 `lambda_min(A) >= sigma`。对
`s in {+1,-1}^n` 令 `D_s=Diag(s)`，定义全置换 twirl

$$
\operatorname{Tw}_s(A)
:=\frac1{n!}\sum_{P\in S_n}P^\top D_sAD_sP.
$$

### 定理 B.1（signed-twirl 饱和定理）

有

$$
\operatorname{Tw}_s(A)=(1-\alpha_s)I+\alpha_s\mathbf1\mathbf1^\top,
\qquad
\alpha_s=\frac{s^\top As-n}{n(n-1)},
$$

并且

$$
-\frac{1-\sigma}{n-1}\leq \alpha_s\leq 1-\sigma.
$$

若 `sigma < 1`，则正端点等号

$$
\alpha_s=1-\sigma
$$

成立当且仅当

$$
A=\sigma I+(1-\sigma)ss^\top.
$$

也就是说，Kim--Lee--Yun 的 full-block signed permutation-invariant 矩阵，恰好是
“signed total correlation”耗尽全部谱预算的唯一矩阵。

### 证明

置换共轭的不动子空间是 `span{I, 11^T}`。twirl 保持对角为一，所有非对角元变成
它们的平均，因此

$$
\alpha_s
=\frac{\mathbf1^\top D_sAD_s\mathbf1-n}{n(n-1)}
=\frac{s^\top As-n}{n(n-1)}.
$$

下界来自 `A >= sigma I`：

$$
s^\top As\geq \sigma\|s\|^2=\sigma n.
$$

另一方面，`tr(A)=n` 且所有特征值至少为 `sigma`，所以

$$
\lambda_{\max}(A)\leq n-(n-1)\sigma.
$$

因而

$$
s^\top As\leq n\lambda_{\max}(A)
\leq n\bigl(n-(n-1)\sigma\bigr),
$$

这给出 `alpha_s <= 1-sigma`。

若上端等号成立，则两个上界都必须取等：`s/sqrt(n)` 是最大特征向量，最大特征值为
`n-(n-1)sigma`，其余 `n-1` 个特征值全为 `sigma`。因此

$$
A=\sigma I+
\bigl(n-(n-1)\sigma-\sigma\bigr)\frac{ss^\top}{n}
=\sigma I+(1-\sigma)ss^\top.
$$

逆向代入立即成立。证毕。

### 能推出什么，不能推出什么

该定理给出了一个真正的极值统计量，但尚未给出

$$
R(A)\leq F(\alpha_s)
$$

之类的桥梁。特别地，`Tw_s(A)` 的最小特征值通常大于 `lambda_min(A)`，而且
`A -> M_A` 是非线性的；所以不能把上述几何极值直接提升为 RPCD rate 极值。

## 3. 轨道平均所需凹性的最小定参数反例

取 `n=3`、`sigma=2/5`、`q=3/5`，并令

$$
A=
\begin{pmatrix}
1&-q&-q\\
-q&1&q\\
-q&q&1
\end{pmatrix}
=\frac25I+\frac35ss^\top,
\qquad s=(1,-1,-1)^\top.
$$

令 `P` 交换前两个坐标，并取轨道中点

$$
B=\frac12(A+P^\top AP)
=
\begin{pmatrix}
1&-q&0\\
-q&1&0\\
0&0&1
\end{pmatrix}.
$$

两者都严格正定，而且

$$
\operatorname{spec}(A)=\left\{\frac25,\frac25,\frac{11}{5}\right\},
\qquad
\operatorname{spec}(B)=\left\{\frac25,1,\frac85\right\}.
$$

所以这一步平均**没有改变最小特征值**。

对 `B`，第三坐标与前两维解耦；一 epoch 的非零部分就是二维 RPCD。二维相关参数为
`q` 时可直接算得

$$
R(B)=\frac{q^2+q^4}{2}=\frac{153}{625}.
$$

对 `A`，sign-switch 后是三维正 equicorrelation 矩阵。穷举六个排列并做精确有理
特征多项式运算，`E[T_p tensor T_p]` 的特征多项式（忽略正的常数因子）为

$$
\begin{aligned}
&(125z-33)(125z+3)^2
(78125z^2-22605z-36)\\
&\qquad\cdot(9765625z^2-1177500z-286137)^2.
\end{aligned}
$$

逐个比较这些实根，Perron 根是

$$
R(A)=\frac{4521+3\sqrt{2321049}}{31250}
\approx 0.2909278976.
$$

而

$$
R(B)=\frac{153}{625}=0.2448.
$$

严格不等式只需注意

$$
9\cdot2321049-3129^2=11098800>0,
$$

故 `3 sqrt(2321049) > 3129`，即 `R(A)>153/625`。

由于 `R(P^TAP)=R(A)`，我们得到

$$
R\!\left(\frac{A+P^\top AP}{2}\right)
<\frac{R(A)+R(P^\top AP)}2.
$$

### 该反例关闭的路线

它严格否定了以下自然命题：

- `R` 在置换轨道的凸包上是凹函数；
- 每次相邻坐标的 Robin-Hood averaging 都使 RPCD 变慢；
- 可以通过不断平均坐标 profile，把一般矩阵推到置换不变矩阵，同时保持或增大 rate。

它**不是** C001 的反例。事实上 `A` 与 `B` 都属于论文已经控制的 signed/block
结构族；这里只是说明该结构族内部的 rate 也不是由“对称度越高越坏”这一单调原则
排列的。这也解释了论文为什么必须对所有 block size `2 <= k <= n` 取最大，而不能只
保留 full block。

## 4. 凸包路线的 cut-polytope 障碍

固定 `sigma in (0,1)`。任意满足 `A >= sigma I` 的单位对角矩阵可唯一写成

$$
A=\sigma I+(1-\sigma)C,
\qquad C\succeq0,\quad \operatorname{diag}(C)=\mathbf1.
$$

也就是说，归一化可行域是相关矩阵 elliptope。

Kim--Lee--Yun 的 signed block 矩阵归一化后形如

$$
C=\operatorname{diag}(ss^\top,I).
$$

每个这样的 `C` 都是 sign rank-one 矩阵 `vv^T` 的凸组合：固定 active block 的相对
符号，令 inactive signs 独立取 Rademacher 平均即可。反过来，full block 已包含所有
`vv^T`。所以整个结构族的凸包恰好是 cut polytope

$$
\operatorname{CUT}_n=\operatorname{conv}\{vv^\top:v\in\{\pm1\}^n\}.
$$

但在 `n=3`，矩阵

$$
C_\triangle=
\begin{pmatrix}
1&-1/2&-1/2\\
-1/2&1&-1/2\\
-1/2&-1/2&1
\end{pmatrix}
$$

有特征值 `{0,3/2,3/2}`，故属于 elliptope。另一方面，对任意 sign vector `v`，

$$
v_1v_2+v_1v_3+v_2v_3\in\{-1,3\}.
$$

所以 cut polytope 中任何点的三个非对角元之和至少为 `-1`，而
`C_triangle` 的该和为 `-3/2`。因此

$$
C_\triangle\notin\operatorname{CUT}_3.
$$

甚至 `C_triangle` 是 elliptope 的极点：若它是两个相关矩阵的平均，则它的核向量
`1` 必须同时属于两个 PSD 矩阵的核；单位对角加上三个行和为零的方程唯一强制所有
非对角元等于 `-1/2`。

所以即使未来证明 `R(A)` 在整个可行域上凸，最多也只能把极值问题推到 elliptope 的
全部极点；仍不能只检查 signed rank-one/block 极点。高秩、带 cycle frustration 的
极点必须另行排除。

## 5. 可保留的替代局部命题

### 5.1 饱和簇会自动产生部分置换对称性（严格结论）

令 `S` 是大小为 `k` 的坐标子集，`s in {+1,-1}^k`。定义

$$
\alpha_{S,s}
=\frac{s^\top A_{SS}s-k}{k(k-1)}.
$$

把定理 B.1 的迹与 Rayleigh 商证明应用到主子矩阵，得到

$$
\alpha_{S,s}\leq1-\sigma.
$$

若取等，则

$$
A_{SS}=\sigma I_k+(1-\sigma)ss^\top.
$$

更重要的是，令 `G=A-sigma I >= 0`。对任何 `y perpendicular s`，上述等号给出
`y^T G_SS y=0`。PSD 矩阵满足 `x^T Gx=0 => Gx=0`，故整个 cross block 必须满足

$$
A_{S,S^c}=s c^\top
$$

对某个向量 `c`。sign-switch 后，`S` 中所有坐标不仅内部 equicorrelated，而且对外部
具有完全相同的 profile；Hessian 自动具有一个 `S_k` 自同构群。

这给出一个具体的解析归纳目标：证明任何 RPCD extremizer 必须饱和某个
`alpha_{S,s}`；一旦做到，就可以把该簇压缩为较小的部分置换不变问题。当前尚未证明
“extremizer 必须饱和”。

### 5.2 应平均证书，而不是平均 Hessian（严格结论）

若一个固定 Hessian `A` 的 signed-permutation 自同构群为 `G`，且存在
`X > 0` 满足 Lyapunov/Collatz 上界

$$
\mathcal M_A(X)\preceq rX,
$$

则把 `X` 在自同构群上平均，

$$
\bar X=\frac1{|G|}\sum_{Q\in G}Q^\top XQ,
$$

仍有 `bar X > 0` 和

$$
\mathcal M_A(\bar X)\preceq r\bar X.
$$

证明只是利用第一节的等变性、线性和 Loewner 序。这个平均是合法的，因为始终固定
同一个 `A`；第三节反例不适用。

因此更可靠的 symmetry harness 是：

1. 从候选 extremizer 的自同构群求 commutant；
2. 只在该低维 commutant 内搜索/证明 Lyapunov 证书；
3. 对部分对称族逐块比较证书，而不是平均输入 Hessian。

### 5.3 尚未证明、但值得单独攻击的命题

以下均保持为 E0 候选：

- **Gauge-first/frustration 命题**：先选择 sign gauge 最大化 `s^TAs`；证明负 cycle
  frustration 不会增加 RPCD rate。结构化最坏族全部是 balanced signed graphs，而
  第四节缺失的高秩极点首先表现为 frustration。
- **极点消除命题**：若 `C` 是 rank 大于一的 elliptope 极点，则构造一个 signed
  block Hessian，其 RPCD rate 不小于 `sigma I+(1-sigma)C`。
- **饱和簇 KKT 命题**：全局 extremizer 必须使某个 `alpha_{S,s}=1-sigma`；随后使用
  5.1 的模块结构归纳。
- **谱半径凸性命题**：本轮反例否定的是凹性，不是否定凸性。即使凸性成立，仍必须
  配合“高秩 elliptope 极点不最坏”的新引理，不能跳过第四节障碍。

## 6. 本路线的决策

第二轮不应继续投入“对 Hessian 做全群平均并寻找 Jensen 方向”。该方法的关键凹性在
最小的定参数例子中已经严格失败。

建议保留并进入下一轮的两条子路线是：

1. **饱和簇/模块归纳**：先证明 extremizer 的 signed-correlation saturation，再利用
   自动出现的部分置换对称性降维；
2. **对称 Lyapunov 证书**：在每个部分不变族的 commutant 中建立
   `M_A(X) <= rX`，并攻击非对称方向是否能违反同一个证书。

主要外部问题来源：Donghwa Kim, Jaewook Lee, Chulhee Yun,
[*Provable Benefit of Random Permutations over Uniform Sampling in Stochastic Coordinate
Descent*](https://arxiv.org/abs/2505.23152), ICML 2025。论文自身把一般 Hessian 情形列为
Conjecture 4.1，并在结构类中保留所有 block size；本文件没有改变该公开状态。
