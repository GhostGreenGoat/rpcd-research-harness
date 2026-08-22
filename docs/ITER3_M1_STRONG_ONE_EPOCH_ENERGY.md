# M1：强一轮 A-energy 不等式与有限时 RPCD 目标

日期：2026-08-21

## 状态边界

本文研究下面这个比 C001 更强的充分条件，但**没有证明它**：

小谱隙 Schur 归约和两极点--六边形 exact certificate 已另经
`docs/ITER3_AUDIT_M1_BOUNDARY.md` hostile audit；强一步一般命题本身仍只是开放猜想。

\[
 \mathbb E_\pi[T_\pi^\top A T_\pi]\preceq q_{n,\mu}A,
 \qquad
 q_{n,\mu}:=\max\left\{(1-1/n)^n,(1-\mu/n)^{2n}\right\},       \tag{M1}
\]

其中 \(A\succ0\)、\(A_{ii}=1\)、\(\mu=\lambda_{\min}(A)\)，且每个 epoch 独立抽取
一个均匀随机排列。下文的搜索是 float64 E1 数值证据；未找到反例不是证明。

若新问题从一般 \(Q\succ0\) 开始，必须先做 coordinate normalization。令

\[
 D=\operatorname{Diag}(Q_{11},\ldots,Q_{nn}),\qquad
 A=D^{-1/2}QD^{-1/2},\qquad z=D^{1/2}x.                       \tag{0}
\]

则 exact coordinate descent 在 \(z\) 上正是本文的 unit-diagonal 模型，且
\(x^\top Qx=z^\top Az\)。复杂度参数应是
\(\mu=\lambda_{\min}(D^{-1/2}QD^{-1/2})\)，不能只用未经归一化的
\(\lambda_{\min}(Q)\)：缩放 \(Q\mapsto cQ\) 不改变 exact CD 轨迹，却会任意缩放后者。

## 1. 为什么 M1 正好对应强有限时结论

记 \(\|x\|_A^2=x^\top Ax\)。若 (M1) 成立，则对 epoch filtration 有

\[
 \mathbb E[\|x_{k+1}\|_A^2\mid x_k]
 \le q_{n,\mu}\|x_k\|_A^2.
\]

反复使用全期望公式得到无额外前因子的界

\[
 \boxed{\mathbb E\|x_K\|_A^2\le q_{n,\mu}^K\|x_0\|_A^2},       \tag{1}
\]

以及由 Jensen/Cauchy--Schwarz 得到用户所要求的“距离的期望”界

\[
 \boxed{\mathbb E\|x_K\|_A
 \le q_{n,\mu}^{K/2}\|x_0\|_A}.                              \tag{2}
\]

这比 \(\|\mathbb E x_K\|_A\) 强；后者可能因不同轨迹互相抵消而很小，即使每条轨迹
仍离最优点很远。

固定时刻的 Markov 界为

\[
 \Pr\{\|x_K\|_A\ge\varepsilon\|x_0\|_A\}
 \le {q_{n,\mu}^K\over\varepsilon^2}.                         \tag{3}
\]

在小 \(\mu\) 分支，

\[
 -\log q_{n,\mu}
 =-2n\log(1-\mu/n)\ge2\mu.
\]

因此为使 (2) 不超过 \(\varepsilon\|x_0\|_A\)，取

\[
 K\ge {1\over\mu}\log {1\over\varepsilon}
\]

个 epoch 足够。每个 epoch 是 \(n\) 次坐标更新，故得到目标阶

\[
 N=nK=O\!\left({n\over\mu}\log {1\over\varepsilon}\right).  \tag{4}
\]

Euclidean 距离由
\(\mu\|x\|_2^2\le\|x\|_A^2\le\lambda_{\max}(A)\|x\|_2^2\)
转换；平方距离界多一个 \(\kappa(A)=\lambda_{\max}(A)/\mu\) 前因子，距离界多一个
\(\sqrt{\kappa(A)}\) 前因子。

## 2. 只有 C001 谱半径时，有限时能推出什么

在 energy 坐标 \(y=A^{1/2}x\) 中，令

\[
 P_\pi=A^{1/2}T_\pi A^{-1/2},\qquad
 \mathcal C=\mathbb E_\pi[P_\pi\otimes P_\pi].
\]

均匀全排列平均满足 \(\mathcal C^*=\mathcal C\)：一个 word 的转置恰对应反序排列。
所以 C001 的 \(\rho(\mathcal C)\le q\) 不受 Jordan 或 nonnormal 前因子影响，并给出
\(\|\mathcal C^K\|_{F\to F}\le q^K\)。若
\(\Sigma_0=y_0y_0^\top\)，则

\[
\begin{aligned}
 \mathbb E\|x_K\|_A^2
 &=\langle I,\mathcal C^K(\Sigma_0)\rangle_F\\
 &\le \|I\|_F\,q^K\|\Sigma_0\|_F\\
 &=\boxed{\sqrt n\,q^K\|x_0\|_A^2}.                         \tag{5}
\end{aligned}
\]

因此

\[
 \mathbb E\|x_K\|_A\le n^{1/4}q^{K/2}\|x_0\|_A,            \tag{6}
\]

且失败概率至多 \(\sqrt n q^K/\varepsilon^2\)。这里显式
\(\sqrt n\) 来自 \(\|I\|_F\)，不是未控制的渐近常数。对一般非自伴正映射，仅知道
谱半径并不足以得到 (5)；本问题能写出 (5) 的关键是全排列的反序对称性。

(M1) 因而严格有价值：它把 (5) 的 \(\sqrt n\) 和 (6) 的 \(n^{1/4}\) 都去掉；但
C001 本身并不逻辑蕴含 \(A\) 就是这样的一步 Lyapunov 矩阵。

## 3. 精确评估方法

没有枚举 \(n!\) 个排列。对 \(R\subseteq[n]\) 定义

\[
 F_\varnothing=A,
 \qquad
 F_R={1\over |R|}\sum_{i\in R}U_i^\top F_{R\setminus\{i\}}U_i. \tag{7}
\]

则 \(F_{[n]}=\mathbb E[T_\pi^\top A T_\pi]\)。一次评估只需 \(2^n\) 个 subset
状态；搜索目标是

\[
 g(A):=\lambda_{\max}(A^{-1/2}F_{[n]}A^{-1/2})-q_{n,\mu}.      \tag{8}
\]

在 seed `20260825` 的独立交叉检查中，(7) 与穷举排列实现对
\(n=3,\ldots,7\) 的最大 entrywise 差依次为
`1.04e-17, 6.94e-17, 4.16e-17, 9.71e-17, 3.61e-16`。

固定 \(\mu<1\) 的搜索参数化事实上覆盖整个可行壳层：

\[
 C={A-\mu I\over1-\mu}\succeq0,
 \quad C_{ii}=1,
 \quad\lambda_{\min}(C)=0,
 \quad A=\mu I+(1-\mu)C.                                    \tag{9}
\]

所以可以写 \(C=VV^\top\)，其中 \(V\) 的每一行是单位向量，且
`rank(V)<=n-1`。随机 low-rank Gram 并不是额外限制；它是固定最小特征值相关矩阵的
边界参数化。有限采样当然仍不覆盖连续参数空间。

## 4. 数值搜索结果

主搜索覆盖：

- \(n=3,\ldots,8\)；
- \(\mu\in\{0.001,0.003,0.01,0.03,0.1,0.25,0.5,0.8\}\)；
- signed rank-one、随机 boundary Gram、rank-two frustrated circle、cut mixtures；
- row-sphere 局部优化；seed `20260821`。

主搜索记录 `54,054` 次目标评估，所有 gap 都非正。最接近者是

```text
n=8, mu=0.001
energy rate = 0.9979064808812682
target      = 0.9980018739066953
gap         = -9.539302542704853e-05
family      = boundary_gram_r2
```

随后用 seed `20260823` 在 \(n=8,\mu=10^{-5}\) 上额外进行了 `15,001` 次低谱隙
搜索；再用 seed `20260824` 对最佳 rank-three Gram 做 `10,500` 次 tangent greedy
refinement。最终最接近记录为

```text
n=8, mu ~= 1e-5
energy rate = 0.9999794794667142
target      = 0.9999800001875032
gap         = -5.207207890434162e-07
(1-energy rate)/mu ~= 2.05205333
```

该负 margin 在 float64 下不是反例，也不是一般证明。它显示最危险区域确实是
\(\mu\downarrow0\)，而且 M1 比 C001 更值得直接做解析审计。

## 5. 搜索提示出的可解析边界族

局部候选在 signed symmetry 后非常接近以下三维 Gram 族：两个重复的 pole 和一个规则
六边形 latitude ring。令

\[
 v_1=v_2=e_3,
\]

\[
 v_{2+j}=\left(
 \sqrt{1-a^2}\cos{2\pi j\over6},
 \sqrt{1-a^2}\sin{2\pi j\over6},
 a\right),\qquad j=0,\ldots,5,                              \tag{10}
\]

并令

\[
 C(a)_{ij}=v_i^\top v_j,
 \qquad A(\mu,a)=\mu I+(1-\mu)C(a).                          \tag{11}
\]

网格搜索在 \(a\approx0.873\) 附近最慢；简单的精确参数
\(a=4/\sqrt{21}\) 给出 `rank(C)=3`，三个非零特征值为

\[
 {5\over7},\quad {5\over7},\quad {46\over7}.                \tag{12}
\]

在 \(\mu=10^{-5}\) 的 float64 评估中，其小谱隙损失系数约为 `2.05204`，仍在目标
一阶系数 `2` 的安全一侧，但已经很接近。该族有
\(S_2\times D_6\) 自同构，可把 (7) 的证书/反例问题按 orbit 和不可约表示降维；这是
本轮最具体的下一解析目标。不能从这些小数宣称一阶系数的精确值。

### 5.1 小 \(\mu\) 极限可化成一个有限 Schur-complement 引理

搜索还给出一个比继续扫小数更明确的解析目标。固定任意奇异相关矩阵
\(C\succeq0\)、\(C_{ii}=1\)，并令

\[
 A_\mu=\mu I+(1-\mu)C.
\]

对排列三角因子定义

\[
 K_0(C):=\mathbb E_\pi
 \left[(M_\pi(C)M_\pi(C)^\top)^{-1}\right].                 \tag{15}
\]

即使 \(C\) 奇异，\(M_\pi(C)\) 仍是 unit triangular，故 (15) 有定义且
\(K_0(C)\succ0\)。以下是一个尚待独立审计的 perturbation proof draft。

将空间正交分解为
\(\mathcal N=\ker C\) 与 \(\mathcal R=\mathcal N^\perp\)，并把 \(K_0\) 写成 block
矩阵。定义

\[
 S_C=(K_0)_{\mathcal NN}
 -(K_0)_{\mathcal NR}(K_0)_{\mathcal RR}^{-1}
  (K_0)_{\mathcal RN}.                                      \tag{16}
\]

由精确 energy identity，强一步 generalized rate 等于

\[
 r_E(A_\mu)
 =1-\lambda_{\min}\!\left(A_\mu^{1/2}K(A_\mu)A_\mu^{1/2}\right), \tag{17}
\]

其中 \(K(A_\mu)\to K_0(C)\)。在
\(\mathcal N\oplus\mathcal R\) 分块后，(17) 中被减矩阵的三个主尺度分别是

\[
 \mu(K_0)_{\mathcal NN},\qquad
 \sqrt\mu(K_0)_{\mathcal NR}C_{\mathcal R}^{1/2},\qquad
 C_{\mathcal R}^{1/2}(K_0)_{\mathcal RR}C_{\mathcal R}^{1/2}.
\]

消去具有正定常数阶极限的 \(\mathcal R\) block，标准 Schur-complement perturbation
给出

\[
 \boxed{
 r_E(A_\mu)=1-\mu\lambda_{\min}(S_C)+o(\mu).
 }                                                          \tag{18}
\]

另一方面

\[
 q_{n,\mu}=(1-\mu/n)^{2n}=1-2\mu+O(\mu^2)
 \qquad(\mu\downarrow0).                                   \tag{19}
\]

所以 M1 在最危险边界的一阶必要条件被压缩成

\[
 \boxed{\lambda_{\min}(S_C)\ge2
 \quad\text{对每个奇异 unit-diagonal }C\succeq0.}          \tag{20}
\]

若某个固定 \(C\) 的左端严格大于 2，则 M1 对该射线上的所有充分小正 \(\mu\) 成立；
若找到小于 2 的 \(C\)，它会产生一族解析 M1 反例候选。等号情形必须继续算二阶项。

这个 Schur 条件还有一个更简洁的全空间等价形式。令

\[
 P_{\mathcal N}\text{ 为 }\ker C\text{ 的正交投影}.
\]

由于 \((K_0)_{RR}\succ0\)，对 block matrix 使用 Schur-complement 判据得到

\[
 \boxed{
 S_C\succeq2I_{\mathcal N}
 \quad\Longleftrightarrow\quad
 K_0(C)\succeq2P_{\mathcal N}.
 }                                                          \tag{20b}
\]

等价地，对任意 \(z\in\mathbb R^n\)，sharp 边界引理可以写成随机三角求解的 coercivity：

\[
 \boxed{
 \mathbb E_\pi\|M_\pi(C)^{-1}z\|_2^2
 \ge2\|P_{\ker C}z\|_2^2.
 }                                                          \tag{20c}
\]

式 (20c) 比 block 记号更适合直接证明：它允许使用随机顺序、反序配对和 Gram dependency
向量；同时它仍完整保留了 kernel--range coupling，不能被误换成较弱的
`P_N K_0 P_N >= 2P_N`。

对 (10) 的 \(a=4/\sqrt{21}\) 族，直接枚举 (15) 后得到

```text
lambda_min(S_C) = 2.0520725111709694   (float64 E1)
```

与有限 \(\mu\) 搜索的 `2.05204...` 一致。这把下一步从“继续把 mu 调小”变成了清楚的
有限矩阵不等式 (20)。

### 5.2 危险对称族的一阶系数已有精确证书

式 (10) 在 `a=4/sqrt(21)` 时具有 \(S_2\times D_6\) 对称性。把
\(\ker C\) 分解成 pole difference、hexagon 的二/三次谐波和 trivial null block，
并对最后一块消去唯一的 trivial range direction，(16) 的四个不同特征值可以用
\(\mathbb Q(\sqrt{21})\) 上的 `8!` 次有限枚举精确计算。

其中最小值来自 pole-difference 向量 \(e_1-e_2\)，为

\[
 \boxed{
 \lambda_{\min}(S_C)
 =\frac{54099374095982388041}{26363285800809721344}
 =2+\frac{1372802494362945353}{26363285800809721344}>2.
 }                                                          \tag{20a}
\]

其余三个不可约块的精确系数为

\[
 \frac{11509555074695071519}{5021578247773280256},\qquad
 \frac{11515509191657071019}{5021578247773280256},
\]

\[
 \frac{488055383208183036561913190226544088459}
 {230204206472163556575595297474813648896},
\]

也都严格大于 2。验证器只使用 `fractions.Fraction` 和
\((u+v\sqrt{21})(s+t\sqrt{21})\) 的精确乘法，没有浮点特征值判定。因此 (20a) 是该
**单个有限对称族**的 E3 exact certificate，而不是一般 (20) 的证明。它严格关闭了
当前最危险数值候选“其实略低于 2，只是 float64 没看出来”的可能性。

随后用 seed `20260826` 直接对 (20) 做了 `33,406` 次边界系数评估，不再引入极小
\(\mu\) 的条件数。没有找到小于 2 的样本；各维最小记录为：

| n | 最小 `lambda_min(S_C)` | family / rank |
|---:|---:|---|
| 3 | 2.3333333326 | cut mixture / 1 |
| 4 | 2.2017652805 | two-pole ring / 2 |
| 5 | 2.1164403811 | local Gram / 3 |
| 6 | 2.0844593594 | local Gram / 3 |
| 7 | 2.0651617622 | local Gram / 3 |
| 8 | 2.0520726273 | local Gram / 3 |

最小值随维数向 2 靠近，说明 (20) 即使为真也很可能是 asymptotically sharp，不能期待
一个与 \(n\) 无关的正余量。subset recursion 对 \(K_0\) 的实现用 seed `20260827` 与
\(n!\) 穷举在 \(n=3,\ldots,7\) 交叉核对，最大 entrywise 差从 `0` 到
`2.36e-14`。这些仍然只是 E1 有限搜索。

## 6. 与现有进展的关系

1. **C023 已经给出真正的有限时部分结论。** Meany/Gram bound 对每个排列逐路径给出

   \[
   \|T_\pi x\|_A^2\le(1-\det A)\|x\|_A^2.                  \tag{13}
   \]

   因而任意排列序列均满足
   \(\|x_K\|_A\le(1-\det A)^{K/2}\|x_0\|_A\)。结合
   \(\det A\ge\mu^{n-1}(n-(n-1)\mu)\)，得到显式有限时界；它覆盖全部
   \(n=2\) 和一般维数的高 \(\mu\) 区域，但低 \(\mu\) 时随维数指数退化，达不到 (4)。

2. **C010 已经是一个无 prefactor 的有限时框架，但常数不够。** 已有 Jensen 候选给出
   \(\mathbb E[T^\top AT]\preceq r_{MJ}(A)A\)，所以 (1)--(3) 对
   \(q=r_{MJ}\) 成立；C011 表明不能普遍证明 \(r_{MJ}\le q_{n,\mu}\)。

   它仍给出一个全参数的显式 benchmark。令
   \(\bar L=n-(n-1)\mu\)，则 \(\lambda_{\max}(A)\le\bar L\)，并且

   \[
   \theta\le {1\over3}\max\left\{
      {(1-\mu)^2\over\mu},{(\bar L-1)^2\over\bar L}
   \right\}+{\bar L-1\over6\mu}=:B_{n,\mu}.                 \tag{21}
   \]

   第一项来自
   \(A^{-1/2}(A-I)^2A^{-1/2}\) 的特征值
   \((\lambda-1)^2/\lambda\)；第二项使用
   \(((A-I)^2)_{ii}=(A^2)_{ii}-1\le\bar L-1\)。于是
   \(r_{MJ}\le B/(1+B)\)，给出
   \(O(n/\mu\log(1/\varepsilon))\) 个 epoch、即
   \(O(n^2/\mu\log(1/\varepsilon))\) 次坐标更新。它距离目标还差一个 \(n\) 因子。

3. **C020 是对 M1 最直接的加强。** 若某一级 resolvent-moment upper matrix
   \(U_r\preceq q_{n,\mu}A\)，就立即得到 (1)--(4)。旧 C011 witness 上 level two 已在
   float64 下越过目标，但一般 uniform moment bound 尚缺。

4. **C021 给出 M1 的精确等价目标：**

   \[
   K_{[n]}\succeq(1-q_{n,\mu})A^{-1}.                       \tag{14}
   \]

   当前缺口正是控制随机 principal-submatrix 删除链中 Schur 坏方向的去对齐。

## 7. 可复现文件

- `scripts/search_strong_one_epoch_energy.py`
- `scripts/refine_strong_one_epoch_boundary.py`
- `scripts/search_m1_boundary_coefficient.py`
- `scripts/certify_m1_two_pole_hexagon.py`
- `research/evidence/M1_STRONG_ENERGY_SEARCH_2026_08_21.json`
- `research/evidence/M1_N8_LOW_MU_SEARCH_2026_08_21.json`
- `research/evidence/M1_BOUNDARY_REFINEMENT_2026_08_21.json`
- `research/evidence/M1_BOUNDARY_COEFFICIENT_SEARCH_2026_08_21.json`
- `research/evidence/M1_TWO_POLE_HEXAGON_EXACT_2026_08_21.json`

下一步应优先对 (10)--(11) 做 symmetry reduction 并求
\(\mu\downarrow0\) 的精确一阶系数；同时继续尝试证明一般 (14)。若这个低维族的精确
系数掉到 2 以下，它将给出 M1 的解析反例候选；若能证明统一不小于 2，则会揭示 M1
在最危险边界附近所需要的 sharp local lemma。
