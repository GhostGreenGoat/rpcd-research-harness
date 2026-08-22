# 跨账号与跨机器交接

## 原则

可移植性的单位是文件，不是聊天会话：

- Git 保存代码、任务、数学声明和小型证书；
- `research/routes/` 保存可机器审计的路线 DAG、签名、父层和组合决策；sealed route card
  另存 SHA-256，防止揭示历史后回写成已有路线；
- `pack` 生成带 SHA-256 manifest 的完整工作包；
- `runs/` 保存某次 Codex 调用的 prompt、JSONL 事件、结构化结果和产物哈希；
- checkpoint 只引用内容哈希和相对路径，不引用账号或 session ID。

严禁提交或打包 `.codex/`、`auth.json`、cookie、API key 和 `.env*`。每个账号必须在其
自己的系统上完成登录。本工程不会自动切换账号，也不会尝试绕过服务限额。

当前主目标是 `C050` 有限时间期望距离；`C051` 是更强充分条件，`C001` 是相关原始
渐近猜想。跨账号 handoff 必须保留 claim ID，不能只写“RPCD 猜想”，否则下一账号可能
在不同目标上继续。

## 推荐流程

1. 账号 A 从干净 Git commit 创建分支 `work/T020-account-a`，先运行
   `python -m rpcd_harness route-audit` 和完整测试。若 T143 仍未执行，route audit 会按设计
   以非零状态报告缺少 agent-generated sealed breadth；把它记录为 portfolio blocker，不能
   用 coordinator brief 冒充通过。
2. `python -m rpcd_harness claim T020-exact-small-n --worker account-a` 创建带过期时间的 advisory claim。
3. 运行任务；让 task-declared preflight verifier 先剪枝、final verifier 再验收，然后用
   `checkpoint` 固化相对路径和哈希。
4. 提交代码、研究文档、route 决策和 checkpoint；原始大日志可用
   `pack --include-runs` 单独传输。
5. 账号 B 拉取同一 commit，先运行 `verify-bundle`、`route-audit` 和验证器，再领取下游
   审计任务。
6. 合并时按 task/run/route ID 合并，不覆盖另一个账号的 run。冲突意味着需要人工比较，而
不是选择“最后写入者”。

带 `--include-runs` 的包只收集所选 task 的 run，但 run 中的 prompt、JSONL、stderr 和
工具输出仍可能含绝对路径或敏感文本。跨账号发送前人工审计，公共仓库不提交 `runs/`。

## Sealed context、fanout 与验证器边界

`sealed_breadth` 会把 allowlist 复制到仓库外的临时 staged directory，让第一阶段先写
不可变 route card，随后才揭示声明过的历史；放在仓库外也避免自动继承仓库祖先
`AGENTS.md`。这是防止探索路线过早同化的**研究方法控制**，不是 OS 访问控制：Codex/验证
进程仍以当前用户权限运行，理论上可访问其他目录、网络或本机资源。不要用它处理不可信
代码，也不要把本机凭据放进仓库后指望 staged context 隐藏。

`fanout` 在一台机器上并行启动多个 lineage 清楚的 rollout，但所有 rollout 使用这台机器
当前的 Codex 登录和共享文件系统；它不是账号轮换器。要跨账号分摊额度，每个账号必须从
同一个 Git commit 和同一个 repo-relative manifest 开始，以可重复的 `--rollout-id` 只运行
分配给自己的 rollout。显式选择产生 `complete=false` shard；不带选择器的完整 fanout 才
直接写 `complete=true`。不要复制 session、cookie、`.codex/` 或 `auth.json`。

每个账号用 `pack TASK --include-runs` 创建 task-scoped bundle。协调账号依次
`verify-bundle`，再把包导入同一个干净 clone；若两个包对同一路径给出不同内容，必须停下
人工核对，不能用 `--force` 覆盖。所有 shard 到位后运行：

```text
python -m rpcd_harness fanout-merge TASK \
  --manifest research/fanouts/<manifest>.json \
  --shard runs/TASK/ensembles/<shard-a>/ensemble.json \
  --shard runs/TASK/ensembles/<shard-b>/ensemble.json
```

merger 要求所有 shard 具有相同 task、source manifest 相对路径和 SHA-256；逐个重验
non-dry completed run 的 canonical task snapshot、invocation、validation、result、artifact
manifest、trusted verifier reports 与 artifact/log trees 的九项 attestation，
并拒绝重复 rollout/run、缺少 manifest rollout、failed record、错误 hash 或篡改。只有
全覆盖输出为 `complete=true`，才能满足 `complete_validated_fanout` dependency 或作为后续
route import 的 canonical ensemble lineage。

task-declared trusted verifiers 使用 argv、`shell=False`、路径检查和 timeout，并保存独立
stdout/stderr。`when=preflight|final|both` 控制早期剪枝与终局验收；sealed 路线只在 card
锁定后才暴露并运行 preflight。这些限制降低命令拼接风险，但验证器仍是以用户权限运行的
仓库代码，不是敌意代码 sandbox。从陌生分支或 bundle 恢复后，先人工审查 task JSON 和
verifier 源码，再执行。验证器 PASS 不会自动改变 claim 的证据等级。

`T143-sealed-finite-time-breadth` 当前只是 ready 的 sealed-breadth 任务；仓库内 route
节点和 sealed brief 不代表该 rollout 已运行。`T144` 在 T143 产生可迁移候选前保持
blocked。跨账号交接时应一并记录 route-card hash、是否已揭示历史、首个 bad edge 和
仍未满足的 dependency。

## 额度耗尽时

不要依赖 `codex exec resume` 才能续做。当前 run 应在结束前或定期写出：

- 已证到哪一步；
- 失败路线；
- 生成的引理/反例候选；
- 运行命令与 seed；
- 下一步最小任务；
- 所有产物哈希。

先在账号 A 固化源 run，并把 checkpoint、它引用的源 run（通常通过
`pack --include-runs`）以及同一源码快照交给账号 B：

```text
python -m rpcd_harness checkpoint TASK --run-dir runs/TASK/<source-run>
python -m rpcd_harness run-codex TASK --worker account-b \
  --resume-from-checkpoint research/checkpoints/TASK--<source-run>.json
```

第二条命令创建新的 run，不恢复 Codex session。harness 会验证 checkpoint 对源 run 当前
文件集合的完整 SHA-256 覆盖、task/run 身份、task snapshot、repository source snapshot 和
上一 phase result/validation；已完成 run、dry-run、篡改/增删文件或源码漂移均拒绝。经验证
的旧 artifacts 会复制到新 output directory，prompt 会读取上一 phase 结果和这些副本。

源 run 的 active time 只写进 lineage 作为历史，不给新 run 抵扣；账号 B 仍须从 0 重新满足
完整 120 分钟下限。这样会损失不可见的对话状态，但保留可审核的科学状态；这是有意设计的。

若上一账号运行的是 sealed breadth，还应传递锁定后的 route card 与 hash。新账号可以
继续 post-reveal 深挖，但不能把新摘要覆盖成“独立 statement-only 发现”；若要获得真正
独立的 breadth 样本，应重新开一个新的 rollout ID 和 sealed phase。
带 `resume_lineage` 的 invocation 会明确写入 `independence=false` 和
`eligible_for_fanout=false`：`route-import-card` 拒绝把它导入为 sealed breadth，
而 `route-import-continuation` 只把它登记为同一分支的 inherited depth。

## 中央仓库并发注意

Git claim 只是 advisory lock。在离线 clone 中两人可能同时领取同一任务；合并时保留
两个 run，它们反而可以作为独立复现。真正需要互斥的写操作应由分支/PR 或外部任务
系统协调，而不要把账号凭据放进 harness。
