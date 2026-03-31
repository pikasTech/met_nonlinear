# 调研报告：GAP文档审查与AFMAE公式修正

## 基本信息
- 日期：2026-03-31
- 阶段：STEP1 R172
- 覆盖范围：GAP文档编码验证、AFMAE公式一致性修正
- 是否使用子代理：否

## 修正内容

### AFMAE公式一致性修正（关键问题）

**问题描述**：`key_references.md` 中FreDF公式使用L1范数（|...|₁），但源码和GAP10/GAP11使用L2平方范数（|...|²）。

**源码分析** (`src/core/loss_functions.py:189`)：
```python
loss_power_log = tf.square(power_true_log - power_pred_log)
```
源码使用 `tf.square()`，即平方误差（L2范数平方）。

**文档一致性**：
- GAP10: `L^α = α·|F(Ŷ)-F(Y)|² + (1-α)·MSE` ✓
- GAP11: `L^α = α·|F(Ŷ)-F(Y)|² + (1-α)·MSE` ✓
- key_references.md: 原为 `|...|₁`（错误）

**修正操作**：
- 文件：`docs/research/literature/key_references.md`
- 位置：line 131
- 修正：`|F(Ŷ)-F(Y)|₁` → `|F(Ŷ)-F(Y)|²`

## GAP文档编码验证

### 验证方法
使用 `file` 命令检查所有GAP文档编码：
```bash
file docs/research/gap/GAP*.md docs/research/gap/GAP*/*.md
```

### 验证结果

| 文件 | 编码 | 状态 |
|------|------|------|
| GAP_SUMMARY.md | UTF-8 text | ✓ |
| GAP1-GAP11 (所有index.md) | UTF-8 text | ✓ |

**结论**：所有11个GAP文档均为UTF-8编码，中文字符显示正确。R171报告中提到的编码问题实际不存在。

## GAP文档内容审查

### 已审查文档

| GAP | 状态 | 备注 |
|-----|------|------|
| GAP1 | ✓ | 内容正确 |
| GAP2 | ✓ | 内容正确 |
| GAP3 | ✓ | PDF验证状态标注正确 |
| GAP4 | ✓ | 内容正确 |
| GAP5 | ✓ | 内容正确 |
| GAP6 | ✓ | 3个"待下载"条目（IEEE/Sensors Open Access）|
| GAP7 | ✓ | 已在R171前审查 |
| GAP8 | ✓ | 内容正确 |
| GAP9 | ✓ | 已在R171前审查 |
| GAP10 | ✓ | 公式正确（L2平方） |
| GAP11 | ✓ | 公式正确（L2平方） |

### PDF可用性状态

**已下载PDF**：68个arXiv PDF

**无法验证PDF内容**（PDF本身无可读内容）：
- Fasmin_2017_Nonlinear_Electrochemical.pdf
- Lin_2020_effect.pdf（注：DOI已修正为107887）
- Chikishev_2019_Temperature_Amplitude_Frequency.pdf
- Wang_2025_FreDF.pdf（注：公式通过SAMFre验证）

**无法下载PDF**（需机构订阅）：
- Bensmann 2010 (10.1016/j.electacta.2010.02.056)

## 对文档的影响

- `docs/research/literature/key_references.md`：AFMAE公式L1→L2平方修正
- `docs/research/gap/GAP_SUMMARY.md`：无需修改
- `.claude/napkin.md`：记录R172修正日志

## 原始GAP状态摘要

| GAP | 缺口等级 | 状态 |
|-----|---------|------|
| GAP1 | 低 | 温度漂移研究支撑 |
| GAP2 | 低 | 线性度范围研究 |
| GAP3 | 低 | 震级因素研究 |
| GAP4 | 低 | 非线性建模缺失 |
| GAP5 | 低 | 震级因素建模缺失 |
| GAP6 | 低 | 前馈vs反馈量程限制 |
| GAP7 | 无 | 前馈利用非线性区 |
| GAP8 | 无 | 频率相关补偿优势 |
| GAP9 | 无 | 计算效率优势 |
| GAP10 | 无 | AFMAE vs 纯MAE |
| GAP11 | 无 | AFMAE vs 其他频域损失 |
