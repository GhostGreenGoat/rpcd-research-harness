# 操作手册

## 查看与领取任务

```text
python -m rpcd_harness list
python -m rpcd_harness show T010-matrix-jensen
python -m rpcd_harness claim T010-matrix-jensen --worker alice --hours 24
```

claim 是 `research/claims/active/` 下的本地 advisory 文件；默认不提交，以减少多分支
冲突。要共享领取状态，可以显式 `git add -f`，或只在团队任务系统中登记。

## 调用 Codex

```text
python -m rpcd_harness run-codex T010-matrix-jensen --worker alice --dry-run
python -m rpcd_harness run-codex T010-matrix-jensen --worker alice
```

每次调用创建唯一 run 目录。先检查 `prompt.md`；真实调用使用 `codex exec --json`，并用
JSON Schema 约束最终消息。可通过 `--codex PATH` 指定 CLI，通过 `--model` 显式选择当前
账号可用模型；不指定时沿用该账号的 Codex 默认配置。

### 两小时深度迭代下限

全局策略在 `research/iteration_policy.json`：每个 worker 的一次完整迭代至少包含
`120` 分钟 Codex 子进程 wall-clock，并约每 `30` 分钟留下一个实质 checkpoint。
两次 pass 之间的空闲时间不计；当前实现不能区分子进程内部的推理、工具等待与 sleep，
所以 wall-clock 不是单独的研究质量证据，必须同时检查 checkpoint、路线与产物。

若一个 pass 提前返回，harness 会把它的结构化结果及同一 output directory 中的产物交给
下一 pass，要求换一条证明/证伪路线或继续攻击尚未关闭的 objection。只有累计 active time
达到下限、至少三条独立 avenue、且失败/压力测试日志满足策略时，才生成最终 `result.json`。
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

## 检查结果与固化 checkpoint

```text
python -m rpcd_harness validate-result runs/T010-matrix-jensen/<run>/result.json
python -m rpcd_harness checkpoint T010-matrix-jensen --run-dir runs/T010-matrix-jensen/<run>
python -m rpcd_harness audit-ledger
```

checkpoint 写入 `research/checkpoints/`，可以提交到 Git。它不复制凭据，也不把某个账号
的 Codex session 当作依赖。

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
