# 跨账号与跨机器交接

## 原则

可移植性的单位是文件，不是聊天会话：

- Git 保存代码、任务、数学声明和小型证书；
- `pack` 生成带 SHA-256 manifest 的完整工作包；
- `runs/` 保存某次 Codex 调用的 prompt、JSONL 事件、结构化结果和产物哈希；
- checkpoint 只引用内容哈希和相对路径，不引用账号或 session ID。

严禁提交或打包 `.codex/`、`auth.json`、cookie、API key 和 `.env*`。每个账号必须在其
自己的系统上完成登录。本工程不会自动切换账号，也不会尝试绕过服务限额。

## 推荐流程

1. 账号 A 从干净 Git commit 创建分支 `work/T020-account-a`。
2. `python -m rpcd_harness claim T020-exact-small-n --worker account-a` 创建带过期时间的 advisory claim。
3. 运行任务，执行验证器，再用 `checkpoint` 固化相对路径和哈希。
4. 提交代码、研究文档和 checkpoint；原始大日志可用 `pack --include-runs` 单独传输。
5. 账号 B 拉取同一 commit，先运行 `verify-bundle`/验证器，再领取下游审计任务。
6. 合并时按 task/run ID 合并，不覆盖另一个账号的 run。冲突意味着需要人工比较，而
不是选择“最后写入者”。

带 `--include-runs` 的包只收集所选 task 的 run，但 run 中的 prompt、JSONL、stderr 和
工具输出仍可能含绝对路径或敏感文本。跨账号发送前人工审计，公共仓库不提交 `runs/`。

## 额度耗尽时

不要依赖 `codex exec resume` 才能续做。当前 run 应在结束前或定期写出：

- 已证到哪一步；
- 失败路线；
- 生成的引理/反例候选；
- 运行命令与 seed；
- 下一步最小任务；
- 所有产物哈希。

另一账号用同一个 task JSON、上一个 checkpoint 和结果文档开启全新 run。这样会损失
不可见的对话状态，但保留可审核的科学状态；这是有意设计的。

## 中央仓库并发注意

Git claim 只是 advisory lock。在离线 clone 中两人可能同时领取同一任务；合并时保留
两个 run，它们反而可以作为独立复现。真正需要互斥的写操作应由分支/PR 或外部任务
系统协调，而不要把账号凭据放进 harness。
