# RPCD Research Harness

这是一个面向 **Random-Permutation Coordinate Descent (RPCD)** 开放问题的可移植研究
工程。它不宣称已经解决 RPCD 猜想；它把“提出思路、数值筛选、有限维证书、证明草稿、
敌对审计、独立重证和形式化”拆成可复现、可交接的任务。

当前主目标是机器可读声明 [`C050`](research/claims/C050-finite-time-expected-distance.json)：
对单位对角 SPD 矩阵 `A`，令 `mu=lambda_min(A)`，每个 epoch 独立重抽均匀随机排列，
希望存在与维数无关的数值常数 `c,C>0`，使所有初值和所有 epoch 数 `k>=0` 满足

```text
E ||x_k||_A <= C exp(-c mu k) ||x_0||_A.
```

一个 epoch 有 `n` 次坐标更新，所以这正是期望距离意义下的
`O((n/mu) log(1/epsilon))` 目标；它不是较弱的 `||E x_k||_A`。`C050` 的一般
`n>=7` 情形仍开放。[`C051`](research/claims/C051-strong-k-sufficient-certificate.json)
记录更强的 `K(A)>=c mu A^-1` 一步矩阵充分条件；`C051 => C050`，反向并不知道。

Kim–Lee–Yun (ICML 2025) Conjecture 4.1 仍以 [`C001`](research/claims/C001-rpcd-conjecture.json)
保留为相关的原始渐近协方差率猜想：

```text
rho(mathcal M_A) <= max((1 - 1/n)^n, (1 - mu/n)^(2n)).
```

它本身不是当前有限时间强期望距离陈述；现有桥接会带入维数相关的 transient/prefactor。
因此文档和任务不得把 `C001`、`C050`、`C051` 当成等价命题。截至
[`docs/SOURCES.md`](docs/SOURCES.md) 记录的公开检索，`C001` 也没有一般证明或认证反例，
仍保持 `OPEN_CONJECTURE` 并等待后续 literature audit 复查。当前 harness 版本为 `0.3.0`。

## 快速开始

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install -c constraints.txt -e .
python -m unittest discover -s tests -v
python scripts/verify_rpcd_identities.py
python -m rpcd_harness list --frontier
python -m rpcd_harness route-list
python -m rpcd_harness route-plan
python -m rpcd_harness route-plan --breadth-snapshot research/breadth_reviews/B001-pre-t143.json
python -m rpcd_harness route-audit
# after a reviewer fills every pair in a breadth snapshot:
python -m rpcd_harness route-breadth path/to/breadth-snapshot.json
# controlled registry transitions after a run:
python -m rpcd_harness route-import-card runs/<task>/<run>/artifacts/route_card.json --route-id R150-example
python -m rpcd_harness route-review-target R150-example runs/<review-task>/<review-run>/artifacts/review.json
python -m rpcd_harness route-import-continuation runs/<task>/<run>/result.json --avenue-index 0
python -m rpcd_harness route-prune R150-example runs/<review-task>/<review-run>/artifacts/prune-verdict.json
```

在 Linux/macOS 上用 `source .venv/bin/activate` 激活环境。只做本地数学验证需要
Python；要让 harness 调度 agent，还需安装并在当前账号登录
[Codex CLI](https://developers.openai.com/codex/cli/)，先确认 `codex --version` 可用。
公开基线使用 Python 3.12.13、NumPy 2.3.5 和 SymPy 1.14.0；精确依赖约束见
[`constraints.txt`](constraints.txt)。

## Agent 从当前进展继续

新 agent 不需要重放聊天记录。完成安装和测试后，按顺序读取：

1. [`research/problem.md`](research/problem.md)：规范化、目标量和记号；
2. [`research/iteration7/p1_sealed_breadth/README.md`](research/iteration7/p1_sealed_breadth/README.md)：
   最新四路密封宽搜、导入判定和下一审计目标；
3. [`research/iteration6/PORTABLE_HANDOFF.md`](research/iteration6/PORTABLE_HANDOFF.md)：继承型解析路线的最短交接入口；
4. [`docs/ITER6_MATRIX_INEQUALITY_SYNTHESIS.md`](docs/ITER6_MATRIX_INEQUALITY_SYNTHESIS.md)：最新解析结论与严格范围；
5. [`docs/ITER5_FAILURE_MAP_AND_ROUTES.md`](docs/ITER5_FAILURE_MAP_AND_ROUTES.md)：不要重复的失败路线；
6. [`research/claims/`](research/claims/)：机器可读声明、证据等级与未决 objection；
7. [`research/routes/`](research/routes/) 与
   [`docs/BREADTH_DEPTH_PROTOCOL.md`](docs/BREADTH_DEPTH_PROTOCOL.md)：当前路线 DAG、组合决策和
   `B_eff` 口径。

当前三个继承型最小解析目标仍是：一般 `W4` 的四点路径/不等权星形/带符号环，cycle-cut
框架中的 adapted off-diagonal arc covariance，以及边界低谱层的完整 Loewner
shorting。T143 的四路 sealed-breadth reference run 已完成：一条 direct-C050 covariance
路线待审，一条 exchangeable 锁定引理被精确反驳，两条锁定边退化为 C051-strength；其中
polynomial-moment 结果还因改写 immutable `falsifier` 被 importer 拒绝。任何新结论都应先写入
独立任务目录，再通过 hostile audit 和独立重证。

`route-list` 显示 `L0--L3` 节点、状态和局部 `deepen/scout/suspend` 建议；`route-plan`
先执行全局宽度与强证书集中门，再列出并列的最深候选，不会假造唯一赢家；`route-audit`
检查父层 DAG、重复签名、sealed-breadth 存在性以及方法族/目标证书集中度。路线分数只是资源分配
指标，不会提高数学证据等级。T143 已产生三个受控 DAG 导入：R150 与 R180 为
`proposed/unreviewed`，R160 因自报精确反例而 `suspended`；R170 导入被一致性门拒绝。
因此当前 `route-audit` 仍会以非零状态诚实报告“尚无 active agent-generated
statement-only sealed-breadth route”和 C051 证书集中；这是等待独立 target review 的组合
blocker，不是声称 DAG 已损坏。显式 reviewer 估计
[`B001-pre-t143`](research/breadth_reviews/B001-pre-t143.json) 给出当前有效宽度 `B_eff=1.2`：
R140 仅是 proposed coordinator precommit，不计入 active frontier；三条已实现路线都共享
C051 风险。该数值是资源
配置诊断，T143 的 Agent card 进入 `proposed/unreviewed` 后须先由不同 worker 做 RPCD
target-fidelity review；激活后必须用 `kind=post_rollout_review` 的新 snapshot 重评。
把最新、覆盖全部 active-frontier 节点的 reviewer snapshot 传给
`route-plan --breadth-snapshot ...` 后，低于 policy 阈值的 `B_eff` 也会成为显式扩宽门；
旧 snapshot 若漏掉新激活路线或仍是 `planning_estimate` 会被拒绝，而不会静默沿用。
通过宽度门后，planner 会同时保护 reviewed direct-C050 scout，避免它被静态高分的
C051 充分条件路线饿死。

`list --frontier` 只显示挂在当前 route DAG 上的 T140--T144；不带选项的 `list` 仍保留
早期任务，供复现历史分支和失败证书使用，不能据其 `ready` 字样判断当前研究优先级。

运行一个自包含任务（会使用当前机器、当前账号自己的 Codex 登录）：

```powershell
python -m rpcd_harness claim T020-exact-small-n --worker account-a
python -m rpcd_harness run-codex T020-exact-small-n --worker account-a --dry-run
python -m rpcd_harness run-codex T020-exact-small-n --worker account-a
```

`--dry-run` 会先生成完整 prompt 和命令，不消耗模型额度。真实运行产生的事件流、最终
结构化结果和文件哈希放在 `runs/<task>/<run-id>/`。

## 路线组合、fanout 与可信验证

任务可以选择三种研究模式：

- `continuation_depth`：读取声明中列出的继承材料，沿一个已定位的 blocker 深挖；
- `sealed_breadth`：第一阶段只把 allowlist 文件复制到单独工作目录，先生成并锁定
  `route_card.json` 的 SHA-256，随后才揭示声明过的历史；
- `critic_validation`：由不同 worker 对候选声明、有限检查和目标迁移做敌对复算。

[`T143`](research/tasks/T143-sealed-finite-time-breadth.json) 的正式 reference fanout 已分别尝试
covariance block powers、exchangeable-pair coupling、noncommutative moments 和 adaptive
Lyapunov duality；结果与证据上限见
[`iteration7 handoff`](research/iteration7/p1_sealed_breadth/README.md)。只有 covariance 锁定卡
仍是存活的 direct-C050 候选。T144 应优先敌对审计该路线的 reachable two-epoch warm edge。
因为完整 `runs/` 不进 Git，fresh clone 上 [`T144`](research/tasks/T144-audit-sealed-finite-time-route.json)
仍会保持 dependency blocked；需要导入经审计的 `--include-runs` bundle 或重新运行 T143，不能
用 curated handoff 冒充九件套 attestation。

T144 真正产生 harness-validated run 后，后续门分成两条互不替代的支线：
[`T145`](research/tasks/T145-fresh-reconstruct-audited-route.json) 从冻结声明重新证明，回答
“数学是否成立”；[`T146`](research/tasks/T146-novelty-audit-audited-route.json) 核验主来源和
优先权，回答“是否已知”。二者都通过后，[`T147`](research/tasks/T147-formal-exact-human-handoff.json)
才整理形式化、精确有限证书和人类专家核验包。hostile audit 不等于独立重证，正确证明也不
自动等于新结果；这些任务通过 dependency result 自动读取已验证 run，不把易失的
`runs/...` 路径写进静态 `inputs`。

可以用 `schemas/fanout.schema.json` 编写至少两个、worker 和 `method_family` 均不同的
rollout，然后先 dry-run：

```powershell
python -m rpcd_harness fanout T143-sealed-finite-time-breadth `
  --manifest research/fanouts/T143-initial-breadth.json --max-parallel 4 --dry-run
python -m rpcd_harness fanout T143-sealed-finite-time-breadth `
  --manifest research/fanouts/T143-initial-breadth.json --max-parallel 4
```

不带 `--rollout-id` 时，fanout 运行 manifest 全集并写 `complete=true`。跨账号分摊时，每个
账号从同一 commit 和同一个仓库内 manifest 只运行分配给自己的 rollout；`--rollout-id`
可重复，但任何显式选择产生的都是 `complete=false` shard：

```powershell
python -m rpcd_harness fanout T143-sealed-finite-time-breadth `
  --manifest research/fanouts/T143-initial-breadth.json `
  --rollout-id t143-covariance-block-powers
```

各账号用 `pack --include-runs` 传递 task-scoped bundle。协调账号验证并导入这些 bundle 后，
显式列出每个 shard 的 `ensemble.json`：

```powershell
python -m rpcd_harness fanout-merge T143-sealed-finite-time-breadth `
  --manifest research/fanouts/T143-initial-breadth.json `
  --shard runs/T143-sealed-finite-time-breadth/ensembles/<account-a>/ensemble.json `
  --shard runs/T143-sealed-finite-time-breadth/ensembles/<account-b>/ensemble.json
```

merge 会重验相同 task 和 manifest SHA-256、每个非 dry completed run 的 task snapshot、
invocation、validation、result、artifact manifest、trusted verifier reports 及 artifact/log
tree 的九项 attestation，并拒绝重复、缺失、失败或事后篡改；只有覆盖 manifest 全部
rollout 的输出才写 `complete=true`。`fanout` 不会自动切换 GitHub/Codex 账号，也不能仅凭
worker 名称保证思想独立。

任务 JSON 还可以声明仓库所有者信任的 `verifiers`。`when` 可取 `preflight`、`final`
或 `both`（默认 `final`）：普通任务在研究前先做便宜剪枝；sealed 任务先锁 route card，
再运行 preflight，避免验证器名称锚定独立构思；`both` 会在交付前复跑。harness 使用 argv、
`shell=False`、路径检查和 timeout，并分别写出结构化记录与哈希日志。这里的“trusted”很
重要：它限制 shell 注入面，但不是运行敌意代码的沙箱；PASS 也只支持其实际检查的有限
声明，不会自动晋级数学结论。

sealed 阶段使用仓库外的临时 working directory，避免 Codex 自动继承仓库祖先
`AGENTS.md`；其中只复制 allowlist，并不写入 denylist 名称。它仍只是降低误读既有历史的
概率，**不是操作系统安全边界**：同一用户权限下的进程仍可主动访问其他目录、网络或本机
资源，所以只应运行可信 agent/代码，且凭据必须留在仓库和 bundle 之外。

默认每个 worker 的完整研究迭代有 **120 分钟 Codex 子进程 wall-clock 下限**。提前结束的 pass 会由
harness 自动续跑；pass 之间的空闲不计时，但当前实现无法从运行中的子进程时间里识别 sleep/等待。
因此每轮还要求定期 checkpoint 和失败或敌对压力测试的可复核记录。传统任务仍要求一轮内
至少三条 avenue；`continuation_depth` 允许把整轮深挖集中到一个真实 route，
`critic_validation` 要求至少两个独立攻击，而 sealed 搜索宽度由多个独立 rollout 形成，
不靠同一 Agent 虚构三条相似路线。策略文件
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

对一个已 checkpoint 的未完成 run，可在新账号中开启带可审计 lineage 的深度续跑：

```powershell
python -m rpcd_harness run-codex T030-counterexample-search --worker account-b `
  --resume-from-checkpoint research/checkpoints/T030-counterexample-search--<source-run>.json
```

这会校验源 run 与源码快照并复制已哈希 artifacts，但不会恢复 session、继承旧 active time，
也不会把续跑计作新的 sealed breadth/fanout 样本；新 run 仍须完成完整 120 分钟。

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
- `T140`：从四点路径、frustrated cycle 和不等权星形继续一般 `W4` Schur 恢复；它只可
  报告路线命题 `C052`，即使 W4 成功，仍需全深度稳定传播才能到 `C051`，再由 `C051`
  推出 `C050`。
- `T141`：证明 cycle-cut half-memory 框架中的 adapted arc covariance 界。
- `T142`：证明边界低谱层的完整 Loewner shorting，而不是仅做 compression。
- `T143`：statement-only sealed breadth；正式四路 reference run 已完成，curated 结果见
  `research/iteration7/p1_sealed_breadth/`；fresh clone 需完整 bundle 或重跑才能满足下游机器依赖。
- `T144`：对 covariance sealed 候选做独立敌对审计；优先攻击 reachable warm/polar edge，
  不把 R160 的局部反例误报为 C050 反例。
- `T145`：基于真实 validated T144 result 锁定一份 fresh proof，再与原路线逐步对账。
- `T146`：独立做 primary-source novelty/priority audit，不把正确性与新颖性混为一谈。
- `T147`：汇总正确性和优先权门，生成 formal/exact/human-review handoff；Agent 运行
  本身封顶 E5，只有随后实际 kernel proof 或合格专家确认才允许 ledger 晋级 E6。

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
- route score、fanout 数量和 sealed card 哈希都是研究过程证据，不是命题正确性的证据。
- staged context、argv 验证器和 bundle 过滤都不是敌意代码的 OS sandbox；公开或执行前仍需
  人工检查仓库所有代码与产物。

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
