# 操作手册

## 先确认目标标签

- `C050`：本仓库当前主目标，即一般维数的有限时间
  `E||x_k||_A <= C exp(-c mu k)||x_0||_A`（`c,C>0` 为通用常数）；复杂度按坐标
  更新计数。
- `C051`：更强的 `K(A)>=c mu A^-1` 一步矩阵充分条件。它推出 `C050`，但当前不知道
  `C050` 是否推出它。
- `C001`：Kim--Lee--Yun 的相关原始渐近协方差率猜想；没有维数一致的 transient
  桥时，不能直接当作 `C050`。
- `C052`：一般 W4 Schur recovery 的单一路线 lemma；它本身既不是 `C051`，也不解决
  `C050`，后面仍缺全深度稳定传播。

开始工作前运行 ledger 与 route 审计，避免把相关但不同的命题混在一起。

## 查看与领取任务

```text
python -m rpcd_harness list
python -m rpcd_harness list --frontier
python -m rpcd_harness show T010-matrix-jensen
python -m rpcd_harness claim T010-matrix-jensen --worker alice --hours 24
python -m rpcd_harness route-list
python -m rpcd_harness route-plan
python -m rpcd_harness route-plan --breadth-snapshot research/breadth_reviews/B001-pre-t143.json
python -m rpcd_harness route-audit
python -m rpcd_harness route-recommend R111-general-w4
python -m rpcd_harness route-breadth path/to/breadth-snapshot.json
python -m rpcd_harness route-import-card runs/<task>/<run>/artifacts/route_card.json --route-id R150-example
python -m rpcd_harness route-review-target R150-example path/to/independent-review.json
python -m rpcd_harness route-import-continuation runs/<task>/<run>/result.json --avenue-index 0
python -m rpcd_harness route-prune R150-example path/to/independent-exact-verdict.json
```

claim 是 `research/claims/active/` 下的本地 advisory 文件；默认不提交，以减少多分支
冲突。要共享领取状态，可以显式 `git add -f`，或只在团队任务系统中登记。

默认 `list` 保留全部历史任务；真正续接当前前沿时优先使用 `list --frontier`，再结合
`route-list` 的 task 映射选择 T140--T144，避免回到已被后续 barrier 取代的旧任务定义。

`route-list` 显示路线层级、状态、方法族和局部 `deepen/scout/suspend` 建议；
`route-plan` 先处理缺失 sealed breadth、方法族与 C051 强证书集中；传入覆盖完整 active
frontier 的 `--breadth-snapshot` 时也把低 `B_eff` 当作扩宽门；首条 Agent-generated
sealed route 激活后必须使用新的 `post_rollout_review`，不能沿用 planning estimate。
通过门后按最深 active frontier 的分数列 depth 候选（并列全部保留），并保护 reviewed
direct-C050 scout 形成 mixed allocation；`route-audit` 检查父层 DAG、重复签名、
sealed-breadth 路线和集中度。建议与
`B_eff` 都只是组合管理信息，不能提升 claim 的证据等级。分支、合并和 first-bad-edge
规则见 `docs/BREADTH_DEPTH_PROTOCOL.md`。在 T143 的 agent-generated statement-only route
真正提交前，`route-audit` 预期以非零状态报告 sealed-breadth blocker；记录并处理该 blocker，
不要把 coordinator 预写的 R140 brief 重标为已经完成的独立 rollout。
checkpoint-resumed run 也不能重标为独立 rollout：card importer 会拒绝它；continuation
importer 仅将其记录为 `independent_breadth_eligible=false` 的 inherited-depth 子节点。
`route-review-target` 和 `route-prune` 也不接受手写 reviewer 名称：review/verdict 及其全部
证据必须位于同一个真实 completed、validated、达到 120 分钟的 standalone reviewer run 的
attested `artifacts/` 树中。九项 canonical attestation 会写入 route provenance；它证明
harness 文件链一致，但不是账号身份的数字签名。

`route-breadth` 读取 `schemas/breadth-snapshot.schema.json` 规定的显式权重和完整相似度矩阵；
相似度必须由 reviewer 按数学 signature 给理由，harness 不用黑箱文本 embedding 猜测。

## 调用 Codex

```text
python -m rpcd_harness run-codex T010-matrix-jensen --worker alice --dry-run
python -m rpcd_harness run-codex T010-matrix-jensen --worker alice
```

每次调用创建唯一 run 目录。先检查 `prompt.md`；真实调用使用 `codex exec --json`，并用
JSON Schema 约束最终消息。可通过 `--codex PATH` 指定 CLI，通过 `--model` 显式选择当前
账号可用模型；不指定时沿用该账号的 Codex 默认配置。harness 显式使用
密封 card 阶段的 `--sandbox read-only` 和专用 Structured Output schema，由 CLI 的 `-o`
把 card 交给 harness；因此 card 不依赖 sandbox 文件 ACL。锁卡后的研究阶段改用
`--sandbox workspace-write` 写证明工件，两个阶段都不授予 `danger-full-access`。

### Sealed breadth、continuation 与 critic

- `continuation_depth` 读取任务 `inputs` 中声明的继承材料，沿已有 blocker 深挖；
- `sealed_breadth` 的第一阶段只在独立 staged directory 中看到
  `context_policy.allowlist`，必须先把可证伪的 route card 作为专用 Structured Output
  返回；harness 校验、保存为 `route_card.json` 并记录 SHA-256 后，下一阶段才回到仓库
  根目录读取声明过的历史；
- `critic_validation` 用不同 worker 独立复算候选的声明、有限验证与目标迁移。

`T143-sealed-finite-time-breadth` 绑定仓库内官方四方法族 fanout；不得用 standalone
`run-codex` 绕过 manifest。正式 reference run 已完成，curated 数学材料位于
`research/iteration7/p1_sealed_breadth/`。只有 covariance 卡保持为存活的 direct-C050
候选；exchangeable 卡的锁定引理已被精确反驳，另外两张锁定卡退化为 C051-strength。
需要重放或在另一账号建立完整依赖时仍使用：

```text
python -m rpcd_harness show T143-sealed-finite-time-breadth
python -m rpcd_harness fanout T143-sealed-finite-time-breadth --manifest research/fanouts/T143-initial-breadth.json --max-parallel 4 --dry-run
python -m rpcd_harness fanout T143-sealed-finite-time-breadth --manifest research/fanouts/T143-initial-breadth.json --max-parallel 4
```

`--dry-run` 只生成 prompt、task snapshot 和 invocation；它不会实际启动 Codex、创建运行时
sealed workspace、锁定 agent 生成的 route card 或运行验证器。`T144` 是不同-run hostile
audit，应优先选择 covariance rollout 并攻击 `C(I-C(I)) >= mu C(I)` / reachable-polar
edge。完整 `runs/` 不进 Git，因此 fresh clone 仍显示 dependency blocked；先导入经审计的
`pack --include-runs` bundle 或重跑 T143。curated handoff 不足以重建九件套 run
attestation，也不能用 `--allow-unmet-dependencies` 绕过正常审计顺序。

T144 有真实 `invocation.iteration_complete=true`、`validation.valid=true` 和 `result.json`
后，使用不同 worker 并行运行 T145 fresh reconstruction 与 T146 novelty audit；不要把
T144 hostile audit 重新命名为“独立重证”，也不要用证明正确性代替 priority 检索：

```text
python -m rpcd_harness run-codex T145-fresh-reconstruct-audited-route --worker fresh-reproducer
python -m rpcd_harness run-codex T146-novelty-audit-audited-route --worker priority-librarian
python -m rpcd_harness run-codex T147-formal-exact-human-handoff --worker formal-handoff
```

这三个任务的 `inputs` 只含稳定的仓库文件；harness 会把最新 validated dependency result
路径注入 prompt。不要手工添加尚不存在的 `runs/<task>/<run>/result.json` 占位符。T147
直接依赖 T144、T145、T146 并分别记录 correctness 与 novelty verdict：有限 exact PASS
只证明其声明的有限事实，准备好 Lean 文件不等于 kernel proof，模型自审也不等于人类专家
确认；因此 T147 的 Agent 输出封顶 E5，E6 只能由后续真实 kernel/合格专家 ledger gate
触发。任一路线引理失败只关闭该路线；除非证书否定带全部量词的 canonical G-FT，C050 仍为
open conjecture。

staged directory 只是减少意外读取历史的机制，**不是 OS sandbox**。同一用户权限下的进程
仍可能主动访问父目录、网络或本机其他文件。只运行可信 agent/代码，不要把凭据安全寄托在
context staging 上。

### 独立 fanout

`fanout` 从 `schemas/fanout.schema.json` 描述的 manifest 启动至少两个 rollout。rollout ID、
worker 和 method family 必须各自唯一。例如先保存：

```json
{
  "schema_version": "1.0",
  "task_id": "T143-sealed-finite-time-breadth",
  "rollouts": [
    {
      "rollout_id": "block-power",
      "worker": "scout-block-power",
      "method_family": "covariance-block-power",
      "context_mode": "statement_only",
      "route_ids": ["R100-l0-finite-time"],
      "objective": "Seek a finite block-power contraction with a uniform transient bound.",
      "required_controls": [
        "one exactly tractable commuting family",
        "one near-singular noncommuting family"
      ]
    },
    {
      "rollout_id": "reachable-cone",
      "worker": "scout-reachable-cone",
      "method_family": "reachable-cone-gauge",
      "context_mode": "statement_only",
      "route_ids": ["R100-l0-finite-time"],
      "objective": "Characterize and contract the cone reachable from rank-one initial covariances.",
      "required_controls": [
        "one rank-one reachable initial covariance",
        "one full-space versus reachable-cone separation test"
      ]
    }
  ]
}
```

然后运行：

```text
python -m rpcd_harness fanout T143-sealed-finite-time-breadth --manifest fanout-T143.json --max-parallel 2 --dry-run
python -m rpcd_harness fanout T143-sealed-finite-time-breadth --manifest fanout-T143.json --max-parallel 2
```

manifest 必须位于仓库内，ensemble 中只保存 repo-relative 路径和 manifest SHA-256。不带
`--rollout-id` 时运行完整 manifest，ensemble 写 `complete=true`；其中某个 rollout 失败
仍会保留其他记录，但 downstream 的 complete-fanout dependency 不会接受失败记录。

跨账号执行时，在每个干净 clone 上从同一个 commit 和 manifest 运行一个或几个 shard；
`--rollout-id` 可重复，显式选择得到的 ensemble 一律写 `complete=false`：

```text
python -m rpcd_harness fanout T143-sealed-finite-time-breadth \
  --manifest research/fanouts/T143-initial-breadth.json \
  --rollout-id t143-covariance-block-powers
python -m rpcd_harness pack T143-sealed-finite-time-breadth \
  --out bundles/account-a-T143.zip --include-runs
```

协调账号对每个包先运行 `verify-bundle`，再把它们 `unpack` 到同一个基线 clone。run ID 和
ensemble ID 必须保持唯一，项目文件必须来自同一 commit。然后合并全部 shard：

```text
python -m rpcd_harness fanout-merge T143-sealed-finite-time-breadth \
  --manifest research/fanouts/T143-initial-breadth.json \
  --shard runs/T143-sealed-finite-time-breadth/ensembles/<account-a>/ensemble.json \
  --shard runs/T143-sealed-finite-time-breadth/ensembles/<account-b>/ensemble.json
```

`fanout-merge` 要求 shard 为 non-dry、`complete=false`，并重验 task、manifest 路径/hash、
rollout 元数据、run invocation completion、`validation.valid`、result 身份、canonical task
snapshot、artifact manifest、trusted verifier reports 与 artifact/log trees 的九项
attestation。重复 rollout/run、缺失覆盖、failed record、错误 manifest 或篡改都会拒绝；合并
输出按原 manifest 顺序覆盖全部 rollout 并写 `complete=true`。
它不会自动切换账号，也不会证明不同提示必然产生思想独立性。并行任务共享同一个仓库，
所以持久写入必须留在各自 run artifact 目录，之后再审计合并。

### 两小时深度迭代下限

全局策略在 `research/iteration_policy.json`：每个 worker 的一次完整迭代至少包含
`120` 分钟 Codex 子进程 wall-clock，并约每 `30` 分钟留下一个实质 checkpoint。
两次 pass 之间的空闲时间不计；当前实现不能区分子进程内部的推理、工具等待与 sleep，
所以 wall-clock 不是单独的研究质量证据，必须同时检查 checkpoint、路线与产物。

若一个 pass 提前返回，harness 会把它的结构化结果及同一 output directory 中的产物交给
下一 pass，要求换一条证明/证伪路线或继续攻击尚未关闭的 objection。只有累计 active time
达到下限且失败/压力测试日志满足策略时，才生成最终 `result.json`。传统任务要求三条 avenue；
`continuation_depth` 可专注一个已登记 route，critic 至少需要两个独立攻击，而 sealed breadth
的宽度来自 fanout 中彼此不同的 rollout。
每个 pass 的 prompt、事件流、stderr 和结果均保留在 run 目录，因此额度中断时不会丢失，
可随 bundle 移交给另一账号继续。`invocation.json` 中的 harness-owned timing 是时长证据；
模型自报时长不作为证据。

## 本地数学验证

```text
python scripts/verify_rpcd_identities.py
python scripts/search_rpcd_counterexample.py --n 4 --samples 100 --seed 7
python -m unittest discover -s tests -v
```

反例搜索输出负 margin 时先标记 candidate，再提高精度、重新参数化和独立复算。

### Task-declared trusted verifiers

任务 JSON 可以声明 `verifiers`，例如：

```json
{
  "name": "exact finite identity",
  "command": ["{python}", "scripts/verify_rpcd_identities.py"],
  "mode": "exact",
  "timeout_seconds": 120,
  "expected_exit_code": 0,
  "when": "both"
}
```

`when` 可设为 `preflight`、`final` 或 `both`，缺省为 `final`。普通任务的 preflight 在
首个研究 pass 前执行；sealed-breadth 任务先生成并锁定 route card，再揭示并执行 preflight，
所以旧脚本名不会污染密封宽搜。preflight 失败会在消耗两小时研究预算前停止；`both` 在最终
交付时再次执行。harness 以 argv、`shell=False` 执行这些仓库所有者信任的命令；shell
launcher/control operator、越界路径和未知 placeholder 会被拒绝。stdout/stderr 保存在
`runs/.../verifiers/`，阶段记录分别为 `trusted_verifiers.preflight.json` 和
`trusted_verifiers.json`；失败会使本次 invocation 不完整。

`{python}` 只允许作为完整的第一个 argv 元素，并展开为运行 harness 的当前 Python
解释器，避免依赖某台机器的绝对路径或 Windows App Execution Alias。

这不是敌意代码隔离层：Python/Sage/Lean 或仓库内程序仍以当前用户权限运行。先审查任务和
验证器源码，再执行来自他人的分支或 bundle。`exact` 只表示该命令设计为精确有限检查；
PASS 不会把数值证据变成一般定理，也不会自动提升 claim 等级。

## 检查结果与固化 checkpoint

```text
python -m rpcd_harness validate-result runs/T010-matrix-jensen/<run>/result.json
python -m rpcd_harness checkpoint T010-matrix-jensen --run-dir runs/T010-matrix-jensen/<run>
python -m rpcd_harness audit-ledger
```

checkpoint 写入 `research/checkpoints/`，可以提交到 Git。它不复制凭据，也不把某个账号
的 Codex session 当作依赖。

若额度中断，先连同源 run 一起迁移 checkpoint，然后在另一账号创建新的 continuation run：

```text
python -m rpcd_harness run-codex T010-matrix-jensen --worker account-b \
  --resume-from-checkpoint research/checkpoints/T010-matrix-jensen--<source-run>.json
```

resume 只接受未完成、非 dry 的源 run；会重验 checkpoint 的全文件哈希闭包、task/run 身份、
task snapshot、repository source snapshot 和最后一个可用 phase result/validation。旧 artifact
经哈希核对后复制到新 run，源 active time 不计入新 run；新 worker 必须重新完成完整 120 分钟。
若源任务是 sealed breadth，必须已经锁定 route card；续跑直接进入 post-reveal depth，
`resume_lineage.independence=false`、`eligible_for_fanout=false`，不能进入 sealed breadth 统计或
complete fanout。详见 `docs/PORTABILITY.md`。

## 导出与导入

```text
python -m rpcd_harness pack T010-matrix-jensen --out bundles/T010.zip --include-runs
python -m rpcd_harness verify-bundle bundles/T010.zip
python -m rpcd_harness unpack bundles/T010.zip --dest ../rpcd-on-account-b
```

带 `--include-runs` 的包只包含所选 task 的 runs，但 prompt、JSONL、stderr 和工具输出
仍可能包含绝对路径或用户提供的敏感文本。对外发送前必须人工复核；不要把 runs bundle
直接提交到公共 Git 仓库。

`unpack` 默认拒绝覆盖内容不同的现有文件；只有明确传 `--force` 才覆盖。应优先解到
干净目录，再用 Git 比较。
