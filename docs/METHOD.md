# 方法：从高吞吐探索到可审计数学

## 1. 借鉴的研究循环

Anthropic 的 Riemann zeta 项目没有证明黎曼猜想；它改进了一个与临界线上零点比例有关
的下界。真正值得复用的是研究组织方式：先宽搜大量想法，再把少数有信号的分支做深；
让程序不断检查已知零点和中间恒等式；让不同代理互相审稿；随后做反例搜索、优先权
检索、独立重证，并在可行时形式化。

参考仓库进一步提供了发布纪律：`search_*`、`explore_*` 和 `verify_*` 分离；数值小数
不能冒充定理；只有有限参数陈述、量词说明和 hostile audit 都闭合，结果才进入定理表。

本 harness 把两者合并为下面的循环：

```text
idea fan-out -> cheap falsification -> selected deep proof
     -> finite verifier -> hostile audit -> independent reconstruction
     -> priority audit -> formalization / human review
```

## 2. 证据等级

| 等级 | 名称 | 允许的表述 |
|---|---|---|
| E0 | idea | 未检验思路、类比、可能的引理 |
| E1 | numerical | 浮点实验、优化轨迹、未认证反例候选 |
| E2 | finite-certificate | 明确有限参数、可复现程序、seed/tolerance/margin 完整 |
| E3 | proof-draft | 量词完整的证明草稿；尚未敌对审计 |
| E4 | hostile-audited | 独立审计逐项攻击并关闭全部 blocker |
| E5 | independently-reconstructed | 另一运行从声明重新证明，且与原稿对账 |
| E6 | formalized-or-human-validated | 机器检查或合格人类专家确认 |

E2 不自动推出一般命题。E4/E5 也不自动等于期刊认可；`theorem_candidate` 至少要求
E5，E4 只能保留为 hostile-audited `proof_candidate`。

## 3. 声明状态与晋级门

允许状态：`open_conjecture`、`idea`、`numerical_observation`、
`finite_verified`、`proof_candidate`、`theorem_candidate`、`refuted`、`external_theorem`。

要从 `proof_candidate` 晋级为 `theorem_candidate`，必须同时存在：

1. 完整 finite/general statement 和所有量词、范数、采样语义；
2. 逐步证明稿，每个外部引理有主来源；
3. 独立 `verify_*` 程序覆盖所有可有限检查的恒等式；
4. 不同 run 完成 hostile audit，且 blocker 数为零；
5. 不同 run 独立重证；
6. 文献/优先权审计明确区分“已知技巧”和“新命题”。

这两条证据链必须分开记录：`proof_draft`、`hostile_audit` 和
`independent_reconstruction` 回答“数学上是否成立”；独立的
`domain_expert_spec_review` 先确认 RPCD 问题、量词、范数和形式化规格一致；
`priority_audit` 回答“该命题或常数是否
已知”。`theorem_candidate` 还必须在 claim JSON 的 `gate_evidence` 中为每个 gate 记录
`worker`、`run_id`、对应的已完成 `invocation.json` 和仓库内 artifact 路径；proof、hostile
audit、independent reconstruction 三者必须来自不同 worker 和不同 run，规格审查不能由
原证明 worker 自审，priority audit 也必须与证明 run/worker 分离。模型生成正确证明不构成
priority 证据，检索到相似关键词也不构成数学验证。

反例也有门：必须保存矩阵、生成方法、精度、SPD 裕量、猜想差值和独立复算。浮点负
裕量只叫“反例候选”；要宣布 refuted，应补区间或有理证书，或得到独立高精度确认。

## 4. RPCD 专用攻击面

- `T_pi` 的排列方向或转置写错；
- Euclidean norm、A-energy 和 objective-value 收缩率混用；
- 二阶矩算子的全空间谱半径与固定初值可达子空间混用；
- 单个 epoch 的 Jensen 界被误写成逐轨迹界；
- 正定、单位对角和固定 `lambda_min=sigma` 的量词丢失；
- 浮点优化把接近边界的半正定矩阵误认成 SPD；
- 在小 `n` 的对称性被无依据推广到一般 `n`；
- 同一个代理既提出证明又“独立”审核。

每个 hostile audit 必须逐项覆盖这些风险。
