# Hostile audit：Iteration 3 路线 M2 remaining-set matrix Lyapunov

日期：2026-08-21
被审计文件：`docs/ITER3_ROUTE_M2_REMAINING_SET_MATRIX_LYAPUNOV.md`
审计者：独立于 M2 推导的 M3/literature run

## 0. 审计结论

**结论：PASS，未发现 blocker。**

本审计从 local residual recursion 重新推导了以下各项，没有把 M2 文档中的证明当作前提：

| 项目 | 结论 | 证据 |
|---|---:|---|
| `D_i` leverage identity (M2.5)--(M2.7) | PASS | block inverse 的 exact rank-one 计算 |
| `H_0<=H_1` | PASS | 对每个首坐标分别成立的 Loewner 分解，不只是在平均后成立 |
| `H_r` 单调且 `H_(m-1)=K` | PASS | Bellman positivity + 对维数/深度的双重归纳 |
| `H_1` 闭式 (M2.14) | PASS | 三个求和项逐项精确消去 |
| `W_R^(r)` 与 finite-time 推论 | PASS | exact conditional energy matrix + congruence + tower property |
| `J_2` 闭式与 (M2.27) | PASS | 直接 residual recursion；另行重证两步 WOR `<=` WR |
| fixed-basis closure obstruction | PASS（按文中限定的含义） | Bellman image 确实产生 `J_B` 与下一 Schur moment `R_B` |
| simple-null / rank-one 两个渐近障碍 | PASS | resolvent expansion、Loewner squeeze、显式特征值极限 |
| `m=3, mu=1/5` rational barrier | PASS | 独立 exact rational arithmetic |

这不是 C001 或强一轮 `A`-energy 猜想的证明。它只确认 M2 所声称的 certificate hierarchy、
finite-time per-instance consequence 和路线障碍在其量词范围内成立。数值 regression 仍只算 E2；
一般结论来自下面的代数重建。

## 1. Local Schur defect 与 leverage identity

把被选坐标 `i` 放在第一位，写

\[
 B=\begin{pmatrix}1&b^\top\\b&C\end{pmatrix},
 \qquad c=C^{-1}b,
 \qquad s=1-b^\top C^{-1}b={1\over G_{ii}},
 \qquad G=B^{-1}.
\]

分块逆公式给

\[
 Ge_i={1\over s}\begin{pmatrix}1\\-c\end{pmatrix},
 \qquad
 (G-I)e_i={1\over s}\begin{pmatrix}1-s\\-c\end{pmatrix}.  \tag{A2.1}
\]

而 route A 的 Schur defect 是

\[
 D_i={1\over s}
 \begin{pmatrix}1-s\\-c\end{pmatrix}
 \begin{pmatrix}1-s\\-c\end{pmatrix}^{\!\top}.
\]

代入 (A2.1) 立即得到

\[
 \boxed{D_i=s_i(G-I)e_ie_i^\top(G-I)},
 \qquad s_i={1\over G_{ii}},                               \tag{A2.2}
\]

以及

\[
 \boxed{\overline D_B={1\over m}(G-I)S_B(G-I)}.            \tag{A2.3}
\]

`D_i` 相对 `G` 的唯一非零广义特征值为

\[
\begin{aligned}
 s_i e_i^\top(G-I)G^{-1}(G-I)e_i
 &=s_i e_i^\top(G-2I+B)e_i\\
 &=s_i(G_{ii}-1)=1-s_i,                                    \tag{A2.4}
\end{aligned}
\]

这里用了 `B_ii=1`。Schur complement 给 `0<s_i<=1`；若 `B>=mu I`，则
`G_ii<=1/mu`，故 `s_i>=mu`。所以

\[
 D_i\preceq(1-s_i)G\preceq(1-\mu)G.                       \tag{A2.5}
\]

**Verdict：** (M2.5)--(M2.7) 全部通过。

## 2. `H_0<=H_1`、单调性与最终 exactness

### 2.1 `H_0<=K` 的依赖已满足

对孤立 local problem `B`，任意 residual `h` 可由状态 `x=B^{-1}h` 实现，其当前能量是
`h^T B^-1 h`。route C 的逐排列 Gram-defect bound 给

\[
 \|P_\pi y\|^2\le(1-\det B)\|y\|^2.
\]

因此每个排列的能量降幅至少是

\[
 \det(B)h^\top B^{-1}h.
\]

平均后得到

\[
 K(B)\succeq\det(B)B^{-1}=H_0(B).                          \tag{A2.6}
\]

该步骤正确地使用了 `B` 仍是 unit-diagonal SPD principal problem；没有把奇异极限当作
SPD 结论。

### 2.2 第一次 Bellman lift 逐坐标优于 `H_0`

令

\[
 d=\det B,\qquad \delta_i=\det C_i,
 \qquad d=s_i\delta_i.
\]

由 Hadamard inequality，`0<delta_i<=1`。再由

\[
 L_i^\top C_i^{-1}L_i=G-e_ie_i^\top-D_i
\]

可逐个 `i` 得到

\[
\begin{aligned}
 &e_ie_i^\top+\delta_iL_i^\top C_i^{-1}L_i-dG\\
 &\quad=\delta_i\bigl((1-s_i)G-D_i\bigr)
       +(1-\delta_i)e_ie_i^\top\succeq0.                  \tag{A2.7}
\end{aligned}
\]

两个 PSD 项的符号分别由 (A2.5) 与 `delta_i<=1` 保证。因此这是比“平均后 PSD”更强的
termwise statement；平均即得 `H_1(B)>=H_0(B)`。

### 2.3 全层级单调且有限深度 exact

对 `r>=1`，即时项抵消后

\[
 H_{r+1}(B)-H_r(B)
 ={1\over m}\sum_i L_i^\top
 \bigl(H_r(C_i)-H_{r-1}(C_i)\bigr)L_i.                    \tag{A2.8}
\]

所以 (A2.7) 是深度归纳的 base case，而 congruence 与平均保持 Loewner order。对维数再归纳：
当 `r=m-1` 时，每个 size `m-1` child 已在深度 `m-2` 等于其 exact `K(C_i)`，故

\[
 H_{m-1}(B)
 ={1\over m}\sum_i(e_ie_i^\top+L_i^\top K(C_i)L_i)
 =K(B).                                                     \tag{A2.9}
\]

因此

\[
 H_0\preceq H_1\preceq\cdots\preceq H_{m-1}=K             \tag{A2.10}
\]

成立。`m=1` 时统一设 `H_r([1])=[1]` 正好是归纳边界。

**Verdict：** Theorem candidate M2.2 通过；没有循环使用待证单调性。

## 3. `H_1` 闭式

利用

\[
 H_1(B)={1\over m}\sum_i
 \left[\delta_iG-\delta_iD_i+(1-\delta_i)e_ie_i^\top\right], \tag{A2.11}
\]

以及 `delta_i=d/s_i=dG_ii`，三个和分别是

\[
 \sum_i\delta_i=d\operatorname{tr}G,                       \tag{A2.12}
\]

\[
 \sum_i\delta_iD_i
 =\sum_i d(G-I)e_ie_i^\top(G-I)=d(G-I)^2,                  \tag{A2.13}
\]

\[
 \sum_i(1-\delta_i)e_ie_i^\top
 =I-d\operatorname{Diag}(\operatorname{diag}G).            \tag{A2.14}
\]

代回即为

\[
 \boxed{
 H_1(B)={1\over m}\left[
 d\operatorname{tr}(G)G-d(G-I)^2+I
 -d\operatorname{Diag}(\operatorname{diag}G)
 \right].}                                                 \tag{A2.15}
\]

**Verdict：** (M2.14) 通过。关键 cancellation (A2.13) 不需要交换性以外的额外假设；
`G-I` 本身对所有项相同。

## 4. `W_R^(r)` 与 finite-time 推论

对当前 remaining set `R`，令 `B=A_RR`、`h=A_R,:x`。exact conditional terminal-energy
matrix 是

\[
 W_R^{\rm exact}=A-A_{:,R}K(B)A_{R,:},                     \tag{A2.16}
\]

因为

\[
 \mathbb E[E(x_{\rm end})\mid x,R]
 =x^\top Ax-h^\top K(B)h.
\]

由 `H_r(B)<=K(B)`，

\[
 W_R^{(r)}-W_R^{\rm exact}
 =A_{:,R}(K(B)-H_r(B))A_{R,:}\succeq0,                    \tag{A2.17}
\]

故 (M2.16) 的方向正确。事实上还可补出文中未显式写出的 Bellman equality：

\[
 W_R^{(r+1)}={1\over|R|}\sum_{i\in R}
 U_i^\top W_{R\setminus\{i\}}^{(r)}U_i,                  \tag{A2.18}
\]

它由 `E(U_i x)=E(x)-h_i^2` 和 `h^+=L_i h` 对所有 `x` 比较二次型得到。

在完整 epoch，

\[
 \mathbb E[T_\pi^\top AT_\pi]
 =A-AK(A)A\preceq A-AH_r(A)A.                             \tag{A2.19}
\]

令 `G_r=A^(1/2)H_r(A)A^(1/2)`、`c_r=lambda_min(G_r)`。因为 exact terminal-energy
matrix PSD，且 `0<=H_r<=K`，有 `0<c_r<=1`。因此

\[
 A-AH_rA=A^{1/2}(I-G_r)A^{1/2}
 \preceq(1-c_r)A.                                         \tag{A2.20}
\]

fresh epochs 下对当前 iterate 条件化，再迭代 tower property，得到

\[
 \mathbb E\|x_k\|_A^2\le(1-c_r)^k\|x_0\|_A^2.            \tag{A2.21}
\]

Jensen 给 expected distance 界 `(1-c_r)^(k/2)`；平方相对误差的 epoch complexity 是
`O(c_r^-1 log(1/epsilon))`，乘每 epoch 的 `n` 次更新即为 M2.21。又因
`H_r>=det(A)A^-1`，确有 `c_r>=det(A)`。

**Verdict：** (M2.15)--(M2.21) 通过。它们控制的是 expectation of squared distance / distance，
不是 distance of the expected iterate。

## 5. Prefix hierarchy 与 `J_2` 公式

`J_t(B)` 是前 `t` 个 distinct coordinates 的 exact expected decrease；均匀排列的
`t+1` prefix 删除首坐标后，suffix 正是 child 上的均匀 `t` prefix，所以递推正确。
每条轨迹多走一步只会再减去一个 residual square，故

\[
 0=J_0\preceq J_1\preceq\cdots\preceq J_m=K.              \tag{A2.22}
\]

第一层是 `J_1=I/m`。第二层直接给

\[
 J_2={I\over m}+{1\over m(m-1)}\sum_iL_i^\top L_i.         \tag{A2.23}
\]

逐 entry 求和：对角 `k` 收到 `m-1` 个 child identity 项和
`||(B_-k,k)||^2=(B^2)_kk-1`；非对角 `(k,l)` 只收到首坐标为 `k` 或 `l` 的两个
`-B_kl`。因此

\[
 \sum_iL_i^\top L_i
 =mI-2B+\operatorname{Diag}(\operatorname{diag}B^2),       \tag{A2.24}
\]

代回得到

\[
 \boxed{
 J_2(B)={(2m-1)I-2B+
 \operatorname{Diag}(\operatorname{diag}B^2)\over m(m-1)}.
 }                                                          \tag{A2.25}
\]

### 独立重证 (M2.27)

在 energy coordinates 令 `Z_i=I-v_iv_i^T`，并令 `S=sum_i Z_i`。两步 iid
with-replacement 与 ordered-distinct without-replacement 的 remaining-energy matrices 之差为

\[
\begin{aligned}
 R_{\rm WR}-R_{\rm WOR}
 &= {mS-\sum_iZ_iSZ_i\over m^2(m-1)}\\
 &= {\sum_iZ_i(mI-S)Z_i\over m^2(m-1)}\succeq0,            \tag{A2.26}
\end{aligned}
\]

因为 `mI-S=sum_i(I-Z_i)>=0`。另一方面，一步 RCD 条件能量收缩至多
`1-mu/m`，所以两步 WR remaining energy 至多是 `(1-mu/m)^2` 倍初始能量。
WOR 不大于 WR，转回 residual coordinates 即得

\[
 J_2(B)\succeq\left[1-(1-\mu/m)^2\right]B^{-1}.            \tag{A2.27}
\]

在 full dimension `m=n`，其系数约为 `2mu/n`，所以 epoch 数是 `O(n/mu)`，总更新数
`O(n^2/mu)`；M2 对这一路径的复杂度判断正确。

**Verdict：** (M2.23)--(M2.27) 通过。

## 6. Closure 与方向性障碍

### 6.1 固定 basis 的 Bellman image

由 `D_i=G-e_ie_i^T-L_i^TC_i^-1L_i`，

\[
 {1\over m}\sum_iL_i^\top C_i^{-1}L_i
 =G-\overline D_B-{I\over m}.                              \tag{A2.28}
\]

(A2.24) 给出 M2.29；把 child ansatz
`a C_i^-1+bI-c bar(D)_Ci` 代入 Bellman recursion，恰好得到 M2.31。新对象

\[
 \mathcal R_B={1\over m}\sum_iL_i^\top\overline D_{C_i}L_i
\]

依赖 codimension-one children 的 inverse diagonals，不能由 (A2.2)--(A2.3) **代数恒等地**
压回原三个 basis elements。M2 正确地只称其为 closure obstruction，并明确没有证明
不存在更聪明的 inequality/compression。

### 6.2 simple-null 几何

固定 unit-diagonal PSD `C`，假设其零空间由单位向量 `u` 张成且所有 `u_i!=0`。对

\[
 B_\mu=\mu I+(1-\mu)C
\]

在固定 `C,m`、`mu->0` 时，operator norm 意义下

\[
 G_\mu=\mu^{-1}uu^\top+O(1),
 \qquad s_i={\mu\over u_i^2}+O(\mu^2).                    \tag{A2.29}
\]

代入 leverage identity 得

\[
 D_i=\mu^{-1}uu^\top+O(1)=G_\mu+O(1).                     \tag{A2.30}
\]

因此 `mu u^T bar(D)u ->1`。另一方面 (A2.5) 给 `bar(D)<=G`，所以

\[
 B_\mu^{1/2}\overline D B_\mu^{1/2}\preceq I.
\]

用 `B_mu^(1/2)u=sqrt(mu)u` 取 Rayleigh quotient，再由上界 squeeze，得到 M2.33 的
`lambda_max ->1`。原文省略了最后这个 squeeze，但结论正确。

regular-simplex correlation matrix 的 off-diagonal 是 `-1/(m-1)`，确实具有 simple null
vector `1/sqrt(m) * 1`，所以是合法显式例子。

### 6.3 signed rank-one 几何

对

\[
 B_\mu=\mu I+(1-\mu)11^\top,
\]

`G` 在 `1^perp` 上的特征值为 `1/mu`，且

\[
 G_{ii}={m-1\over m\mu}
 +{1\over m[m-(m-1)\mu]}.
\]

由于 `S_B=sI`，normalized `bar(D)` 在最小特征子空间上的特征值是

\[
 \theta_\mu={s\over m}{(1-\mu)^2\over\mu}
 \longrightarrow{1\over m-1}.                             \tag{A2.31}
\]

每个 principal child 仍为同型矩阵且最小特征值仍是 `mu`，所以文中对两类几何的对照
成立。

**Verdict：** Section 5--6 的障碍结论通过；它们没有被错误提升成 universal impossibility。

## 7. Exact rational barrier

对 `m=3, mu=1/5`，

\[
 B={1\over5}I+{4\over5}11^\top
\]

在 `1^perp` 上 `G` 的特征值是 `5`，并且

\[
 \det B={13\over125},\qquad
 \operatorname{tr}G={135\over13},\qquad
 G_{ii}={45\over13}.
\]

把这些 exact fractions 代入 (A2.15)，在该子空间得到

\[
 \lambda(B^{1/2}H_1B^{1/2})={547\over1875}.                \tag{A2.32}
\]

`span(1)` 上的值更大，所以这是 `c_1(B)`。目标降幅及差值为

\[
 1-\left({14\over15}\right)^6={3861089\over11390625},      \tag{A2.33}
\]

\[
 \left[1-\left({14\over15}\right)^6\right]
 -{547\over1875}
 ={538064\over11390625}>0.                                 \tag{A2.34}
\]

**Verdict：** M2.34--M2.36 通过。它只否定 depth-one determinant-tail certificate 足以达到
target，不否定 exact `K` 或强一轮命题；原文量词正确。

## 8. Blockers 与 nonblockers

### Blockers

**无。** 在指定审计范围内没有发现错误公式、Loewner 方向反转、隐藏的随机独立性假设，
或把有限数值结果提升成一般定理的情况。

### Nonblockers / 建议澄清

1. `J_t` 最好显式限定 `0<=t<=m`，并补 `J_0(empty)=0`；当前递推在所用范围内有唯一自然
   解释，不影响任何结论。
2. 对 `W_R^(r)` 最好补写 terminal convention `W_empty=A` 以及 Bellman equality (A2.18)。
   当前 conditional upper bound 和 finite-time 推论本身已经正确。
3. 在 (M2.27) 前最好明确 local principal matrix 由 interlacing 满足 `B>=mu I`；原文早先
   使用了这一事实，但 Section 4 可再提醒一次。
4. Section 6 的 `O(1)` 应注明是在固定 `C,m` 下的 operator-norm bound；从 lower Rayleigh
   limit 得到 `lambda_max ->1` 时应补 `bar(D)<=G` 的上界 squeeze。
5. `c_r in (0,1]` 可在 finite-time 公式前显式写出。它由 `0<H_r<=K` 和 exact terminal
   energy PSD 自动成立，不是额外假设。

这些都是呈现/边界定义问题，不改变 theorem candidate M2.2、closed form、finite-time bound
或障碍结论。

## 9. 可复现有限检查（E2，不是证明）

审计脚本：`scripts/audit_m2_bellman.py`

命令：

```powershell
python scripts/audit_m2_bellman.py
```

设置：

- NumPy float64；
- seed `20260821`；
- `m=2,...,6`，共 150 个随机 unit-diagonal SPD Gram matrices；
- assertion tolerance `5e-10`；
- 另用 Python `Fraction` exact arithmetic 检查 rational barrier。

输出：

```text
max_leverage_residual       = 1.474376176702208e-13
max_H1_residual             = 7.216449660063518e-15
max_J2_residual             = 2.220446049250313e-16
max_final_H_minus_K         = 0.0
max_epoch_identity_residual = 3.0531133177191805e-16
min_monotonicity_eigenvalue = 2.1337890801320647e-4
barrier_coefficient         = 547/1875
barrier_gap                 = 538064/11390625
```

这些检查只用于发现实现/转置/索引错误；PASS 结论依赖 Sections 1--7 的 exact algebra。
