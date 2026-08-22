# RPCD 第二轮解析迭代：综合结论与下一步

日期：2026-08-20

## 结论先行

C001 仍未解决，也没有发现反例。第二轮的实质进展不是扩大数值搜索，而是把证明空间
拆成四种不同机制，并得到一个部分参数区间的解析证明、两个精确递推/修正恒等式，以及
两个能排除错误证明路线的解析障碍。

目前最强的正面结论是

\[
\rho(\mathcal M_A)
\le 1-\det A
\le 1-\sigma^{n-1}\bigl(n-(n-1)\sigma\bigr).                 \tag{S1}
\]

它推出：

1. C001 对 `n=2`、全部 `sigma in (0,1]` 成立；
2. 对每个 `n>=2`，C001 在 `sigma>=tau_n` 的显式高谱隙区域成立，其中 `tau_n` 由

   \[
   \tau_n^{n-1}(n-(n-1)\tau_n)
   =1-(1-1/n)^n
   \]

   唯一确定。

这里第一步 `||P_pi||^2<=1-det A` 是经典 Meany/Gram-determinant 界；本工程给出了当前
方形单位 frame 情形的自包含证明。将它接到 RPCD covariance map 并提取上述参数区间，
现记为 C023、E4 本地 hostile-audited proof candidate；仍需独立重证、优先权审计和形式化，
不能称为最终定理。

## 四条路线的结果

| 路线 | 本轮得到的解析对象 | 它解决了什么 | 尚缺什么 |
|---|---|---|---|
| A：remaining-set Bellman | 精确的 `P_R(Q)`、残差 `K_R` 递推及累计 Schur rank-one 顺序损失 | 保留前缀与未访问集合的条件信息；把强一轮目标化为 `K_[n] >= (1-q)A^-1` | 控制坏方向随 principal-submatrix 删除链的去对齐，或构造真正依赖 `R` 的矩阵 Lyapunov 证书 |
| B：对称与极值 | signed twirl 的精确区间/饱和者；固定 `sigma` 的轨道中点反例；cut-polytope 障碍 | 严格关闭“平均 Hessian 会使 RPCD 更慢”的朴素凹性路线 | 证明 extremizer 必须出现饱和 signed cluster，或在固定 Hessian 的自同构群内平均证书 |
| C：投影代数 | 两步无放回 PSD 修正；Gram-defect determinant；部分参数区间证明 | 得到 (S1)，覆盖 `n=2` 与高 `sigma`；定位第三阶 pinching 项 | 对 RPCD 特殊 tensor projections 控制第三阶及更高阶 pinching moments |
| D：order-poset | `M^-1` 的 increasing-path 展开和 `E[(MM^T)^-1]` 的双路径 poset 公式 | 把 `n!` 枚举换成局部线性扩张计数，并保持一个显式平方表示 | 构造不破坏 PSD 的有限 path-feature/SOS 截断；不能按交替符号逐项截断 |

## 两个跨路线核心恒等式

### 1. Jensen 的遗漏项被精确识别

令 `X_pi=M_pi M_pi^T`、`Y=E[X_pi]`、`Delta_pi=X_pi-Y`，则

\[
E[X_\pi^{-1}]
=Y^{-1}+Y^{-1}E[\Delta_\pi X_\pi^{-1}\Delta_\pi]Y^{-1}.       \tag{S2}
\]

裸 Jensen 丢掉的不是抽象误差，而是一个明确的 PSD variance correction。以
`beta=(n+tr(A^2))/2` 为 canonical scale，可用全局 inverse polynomial minorant 构造
单调收紧的有限 moment hierarchy。该层级已经通过一次 hostile audit；其一般瓶颈是
如何只用 `n`、`sigma` 和 PSD 约束统一控制低阶 precedence moments。

在旧的 C011 路线障碍矩阵上，二级 polynomial correction 的 float64 上界为
`0.815327...`，低于 C001 目标 `0.816343...`；这只是 E2 信号，说明该层级能修复旧
Jensen 缺口，不是一般证明。

### 2. 前两步无放回严格保留一个 PSD 增益

在 energy coordinates 中，若 `Z_i` 是坐标更新对应的正交投影，则两次独立有放回和
两次均匀无放回更新的平方范数矩阵满足

\[
K_{\rm WR,2}-K_{\rm WOR,2}
=\frac1{n^2(n-1)}\sum_i Z_iAZ_i\succeq0.                    \tag{S3}
\]

在 covariance tensor 空间还有等价的有限总体修正

\[
R^2-C_2=\frac{R(I-R)}{n-1}\succeq0.                         \tag{S4}
\]

这严格证明了任意初始向量的前两次 distinct-coordinate 更新不劣于两次有放回更新。
它不能直接按 pair 相乘成完整 epoch，因为前缀状态与剩余坐标集相关；路线 A 正是为保留
这种相关性而设计。

## 被关闭或降级的证明路线

1. **裸 Jensen 标量化**：C011 已表明其常数可以比 C001 目标松；需要 (S2) 的 variance
   correction，不能继续只优化同一个一阶矩。
2. **对 Hessian 做轨道平均**：`n=3,sigma=2/5` 的精确例子保持同一最小特征值，却使
   RPCD rate 从约 `0.290928` 降到 `0.2448`。因此所需的凹性/单调对称化方向错误。
3. **结构族凸包覆盖可行域**：signed block 族的凸包只是 cut polytope，而一般相关矩阵
   位于更大的 elliptope；高秩 frustration 极点不能被凸组合论证自动排除。
4. **把二步修正当成 commuting falling factorial 继续乘**：第三阶出现一般无固定
   Loewner 符号的 pinching correction。
5. **只用 `(m,sigma,c_m)` 的标量 Bellman 归纳**：它把所有 rank-one 坏方向当成完全
   对齐，所得常数远弱于 C001。

## 下一轮优先级

1. `T070`：从干净环境独立重证 (S1)，完成 Meany 来源和高-`sigma` 推论的优先权审计；
   这是当前最接近可晋级结果的分支。
2. `T055`：用 route A 的 exact remaining-set recursion 构造矩阵值 `W_R`，优先尝试把
   (S3) 做成条件版本。
3. `T050`：推导 `C_{2,beta}` 的精确 precedence-moment 公式，并寻求 uniform Loewner
   bound；旧 C011 例子说明二级已经有足够常数余量。
4. `T075`：放弃平均 Hessian，转攻 extremizer 的 saturated signed cluster/KKT 命题。
5. `T060`：仅在保留平方结构的前提下尝试 path-feature SOS；避免交替路径的逐项估计。
6. `T130`：待 `T070` 独立重证通过后，把 Gram-defect 与 `n=2` 推论作为第一块 Lean
   形式化目标；它比直接形式化完整 C001 更小、更可审计。

## 状态边界

- C001：`open_conjecture`，状态不变。
- C020、C022、C023：已有 proof draft 和本地 hostile audit；尚无独立重证。
- C021、C024、C025：proof draft / exact counterexample draft，仍待独立审计或重证。
- 本轮新增程序只验证有限矩阵恒等式和回归性质；任何 float64 结果都没有被提升为一般
  数学结论。
