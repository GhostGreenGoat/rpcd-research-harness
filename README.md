# RPCD Research Harness

这是一个面向 **Random-Permutation Coordinate Descent (RPCD)** 开放问题的可移植研究
工程。它不宣称已经解决 RPCD 猜想；它把“提出思路、数值筛选、有限维证书、证明草稿、
敌对审计、独立重证和形式化”拆成可复现、可交接的任务。

主目标是 Kim–Lee–Yun (ICML 2025) 的 Conjecture 4.1。对单位对角的正定矩阵
`A`，令 `sigma = lambda_min(A)`；一次 epoch 使用独立均匀随机排列更新所有坐标。
猜想声称其平方范数的渐近 epoch 收缩率不超过

```text
max((1 - 1/n)^n, (1 - sigma/n)^(2n)).
```

截至本仓库初始化日（2026-08-19）的公开检索只找到结构化 Hessian 类上的证明和一般
情形的数值证据，没有找到 Conjecture 4.1 的一般证明或反例。因此这里将它保持为
`OPEN_CONJECTURE`，并要求后续 literature audit 定期复查。

## 快速开始

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install -c constraints.txt -e .
python -m unittest discover -s tests -v
python scripts/verify_rpcd_identities.py
python -m rpcd_harness list
```

在 Linux/macOS 上用 `source .venv/bin/activate` 激活环境。只做本地数学验证需要
Python；要让 harness 调度 agent，还需安装并在当前账号登录
[Codex CLI](https://developers.openai.com/codex/cli/)，先确认 `codex --version` 可用。
公开基线使用 Python 3.12.13、NumPy 2.3.5 和 SymPy 1.14.0；精确依赖约束见
[`constraints.txt`](constraints.txt)。

## Agent 从当前进展继续

新 agent 不需要重放聊天记录。完成安装和测试后，按顺序读取：

1. [`research/problem.md`](research/problem.md)：规范化、目标量和记号；
2. [`research/iteration6/PORTABLE_HANDOFF.md`](research/iteration6/PORTABLE_HANDOFF.md)：当前最短交接入口；
3. [`docs/ITER6_MATRIX_INEQUALITY_SYNTHESIS.md`](docs/ITER6_MATRIX_INEQUALITY_SYNTHESIS.md)：最新解析结论与严格范围；
4. [`docs/ITER5_FAILURE_MAP_AND_ROUTES.md`](docs/ITER5_FAILURE_MAP_AND_ROUTES.md)：不要重复的失败路线；
5. [`research/claims/`](research/claims/)：机器可读声明、证据等级与未决 objection。

当前三个最小解析目标是：一般 `W4` 的四点路径/不等权星形/带符号环，cycle-cut
框架中的 adapted off-diagonal arc covariance，以及边界低谱层的完整 Loewner
shorting。任何新结论都应先写入独立任务目录，再通过 hostile audit 和独立重证。

运行一个自包含任务（会使用当前机器、当前账号自己的 Codex 登录）：

```powershell
python -m rpcd_harness claim T020-exact-small-n --worker account-a
python -m rpcd_harness run-codex T020-exact-small-n --worker account-a --dry-run
python -m rpcd_harness run-codex T020-exact-small-n --worker account-a
```

`--dry-run` 会先生成完整 prompt 和命令，不消耗模型额度。真实运行产生的事件流、最终
结构化结果和文件哈希放在 `runs/<task>/<run-id>/`。

默认每个 worker 的完整研究迭代有 **120 分钟 Codex 子进程 wall-clock 下限**。提前结束的 pass 会由
harness 自动续跑；pass 之间的空闲不计时，但当前实现无法从运行中的子进程时间里识别 sleep/等待。
因此每轮还要求定期 checkpoint、至少三条不同
路线，以及失败或敌对压力测试的可复核记录。策略文件
[`research/iteration_policy.json`](research/iteration_policy.json) 会随 portable bundle
一起迁移，真实子进程时长由 `invocation.json` 记录，而不是依赖模型自报。

## 跨账号运行

账号之间只交换 Git 仓库、任务包和检查点，**不交换 Codex session、cookie、API key、
`auth.json` 或 `.codex/`**。每个账号在自己的环境中登录，然后：

```powershell
python -m rpcd_harness pack T030-counterexample-search --out bundles/T030.zip --include-runs
python -m rpcd_harness verify-bundle bundles/T030.zip
python -m rpcd_harness unpack bundles/T030.zip --dest path/to/clean/clone
```

`--include-runs` 只加入所选 task 的 run，但其中可能包含 prompt、事件流、stderr 和工具
输出；把这种 bundle 发给第三方前仍须人工审计，公共仓库默认不提交 `runs/` 或 `bundles/`。

推荐协作单位是一个 Git 分支或一个 zip 工作包。任务 ID 和 run ID 都是稳定的；结果不
依赖某个聊天线程 ID，因此额度用尽后可在另一账号的新会话中继续。详见
[`docs/PORTABILITY.md`](docs/PORTABILITY.md)。

## 研究轨道

- `T001`：文献与优先权审计，确认问题是否仍开放。
- `T010`：矩阵 Jensen 候选界的逐行代数证明。
- `T015`：把“原始 Jensen 标量界不足以推出主猜想”的浮点见证升级为区间/有理证书。
- `T020`：小维 `n!` 精确排列枚举、公式回归测试和证书生成。
- `T030`：按原论文参数化搜索一般 SPD 反例。
- `T040`：批量提出证明架构，并用机器实验快速淘汰。
- `T050`：用有限 resolvent moments 严格补回裸 Jensen 丢失的 variance correction。
- `T055`：在“当前状态 + 未访问集合”上构造条件 Lyapunov/Bellman 证书。
- `T060`：把随机排列逆矩阵写成 order-poset path squares，并尝试保正的 SOS 截断。
- `T070`：独立重证 Gram-determinant 部分定理并做优先权审计。
- `T075`：研究 extremizer 是否必须出现饱和 signed-correlation cluster。
- `T080`：低谱隙边界不等式 `S_C >= 2I`；第四轮已给出精确反例并关闭该目标。
- `T085`：压缩第二及更高 Schur-loss moments，构造可闭合的 remaining-set 矩阵证书。
- `T090`：敌对审计适应性 Lyapunov metric、resolvent 条件数和 time-uniform 尾界。
- `T095`：证明或反驳全局尖锐候选 `K(A) >= (mu/2) A^{-1}`，并并行研究边界候选
  `K_0 >= (3/2) P_ker`；任一正的全局常数都达到目标复杂度阶。
- `T100`：对候选证明做 hostile audit 和反例攻击。
- `T110`：不看原推导，从声明和引理独立重证。
- `T120`：在前述门全部通过后才尝试形式化。
- `T130`：把 Gram-defect 与 `n=2` 部分定理作为更小的 Lean 形式化目标。
- `T140`：从四点路径、frustrated cycle 和不等权星形继续一般 `W4` Schur 恢复。
- `T141`：证明 cycle-cut half-memory 框架中的 adapted arc covariance 界。
- `T142`：证明边界低谱层的完整 Loewner shorting，而不是仅做 compression。

研究方法、证据等级与晋级门见 [`docs/METHOD.md`](docs/METHOD.md)，数学定义见
[`research/problem.md`](research/problem.md)，操作手册见 [`docs/RUNBOOK.md`](docs/RUNBOOK.md)。

## 重要边界

- “搜索了很多矩阵而没找到反例”仍是数值证据，不是证明。
- 浮点 `n!` 枚举是高价值的有限维回归测试，但不是任意 `n` 的定理。
- 当前的 matrix-Jensen 路线作为 `C010` 候选命题管理；只有 hostile audit 和独立重证
  都闭合后，才可升级为 theorem candidate。
- 已找到一个 `n=4` 有限见证，表明 C010 的原始标量常数可能比 C001 目标更松；这不是
  RPCD 反例，而是要求下一阶段保留更多排列结构的路线障碍。
- 本工程不会自动轮换账号或搬运认证状态；它提供的是合规的、凭据无关的工作交接层。

第二轮解析迭代已经得到一个一般上界
`rho <= 1 - sigma^(n-1) (n-(n-1)sigma)`，从而覆盖 `n=2` 的全部参数和一般维数的显式
高-`sigma` 区域；它仍是待独立重证和优先权审计的 proof candidate。其余路线、精确
恒等式、已关闭的错误证明方向和下一轮排序见
[`docs/ITER2_SYNTHESIS.md`](docs/ITER2_SYNTHESIS.md)。C001 的一般低-`sigma` 情形仍保持开放。

第三轮集中攻击强一步矩阵不等式。它把 `mu -> 0` 的最危险区域归约为奇异相关矩阵上的
`S_C >= 2I`，构造了单调 determinant-tail Bellman 证书层级，并证明草稿性地建立了
谱率与适应性正定 Lyapunov metric 的等价关系。完整状态、精确两极点--六边形证书和
下一步见 [`docs/ITER3_MATRIX_INEQUALITY_SYNTHESIS.md`](docs/ITER3_MATRIX_INEQUALITY_SYNTHESIS.md)。
一般目标复杂度仍未解决。

第四轮已经用一个全有理的 `n=8` 两极点--单纯形环矩阵精确反驳 `S_C >= 2I`，并在
`mu=1/100` 给出正定的强一轮固定 `A-energy` 反例。56 个对称类别、全部 `8!` 排列和
独立的 `2^8` Bellman 递推得到同一分数。这个结果**不反驳**原始协方差谱率猜想 C001；
它只淘汰了一个更强的充分条件。进一步的解析族证明边界常数不能大于 `3/2`；另一组
signed-rank-one 正定矩阵则证明全局一步常数不能大于 `1/2`。两者控制不同谱方向，互不
矛盾。目前最强存活目标是 `K(A) >= (mu/2) A^{-1}`；若成立，它直接给出期望平方
`A`-距离的 `2n/mu` 更新常数，以及期望 `A`-距离的 `4n/mu` 更新常数。任意固定正常数
都仍足以给出 `O((n/mu) log(1/epsilon))`，所以矩阵不等式路线已转入 `T095`，而非被放弃。
该 half-constant 已对所有 `n<=4` 的一般矩阵、以及任意维 signed-rank-one 正定族证明；
一般矩阵从 `n=5` 起仍开放。
总览见 [`docs/ITER4_MATRIX_INEQUALITY_SYNTHESIS.md`](docs/ITER4_MATRIX_INEQUALITY_SYNTHESIS.md)；细节见
[`docs/ITER4_T080_BOUNDARY_KERNEL_INEQUALITY.md`](docs/ITER4_T080_BOUNDARY_KERNEL_INEQUALITY.md)
、[`docs/ITER4_AUDIT_T080_POLE_SIMPLEX_ASYMPTOTIC.md`](docs/ITER4_AUDIT_T080_POLE_SIMPLEX_ASYMPTOTIC.md)
与 [`docs/ITER4_AUDIT_GLOBAL_HALF_SHARPNESS.md`](docs/ITER4_AUDIT_GLOBAL_HALF_SHARPNESS.md)。

第六轮把 weighted third-prefix 不等式推进为内部 E4 证明候选，因此一般维数已有
`O(n^2/mu log(1/epsilon))` 的期望距离有限时间界，并在 `n<=6` 证明了目标阶
`O(n/mu log(1/epsilon))`。此外，目标阶结论已覆盖“至多两个特征值低于 1”以及
常对角、秩至多 3 的等方低谱子空间等全维谱区域。一般 `n>=7` 仍开放；下一个明确
层级是 `W4` 的方向性 Schur 恢复；这一层已在任意 signed matching、全维 weighted
三点路径和全维等权星形上闭合，但一般重叠/不等权结构仍未解决。总览与跨账号入口分别见
[`docs/ITER6_MATRIX_INEQUALITY_SYNTHESIS.md`](docs/ITER6_MATRIX_INEQUALITY_SYNTHESIS.md)
和 [`research/iteration6/PORTABLE_HANDOFF.md`](research/iteration6/PORTABLE_HANDOFF.md)。

检索范围、来源版本和复用依据集中记录在 [`docs/SOURCES.md`](docs/SOURCES.md)。

代码与仓库内原创文档以 [MIT License](LICENSE) 发布；第三方资料只保留来源链接和复现元数据。
