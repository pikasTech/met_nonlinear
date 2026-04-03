---
id: 871
title: Genet 2024 TKAN recheck R202
status: closed
tags: genet2024tkan, tkan2024r2, rechkround202, fresh2026s, genetkanr2, rechk2026s
created_at: 2026-04-03T17:44:20
updated_at: 2026-04-03T18:02:32
---

# 文献复查Issue

Round 176+ 未复查

## 任务
复查文献分析的准确性和完整性

## 要求
1. 精确验证所有行号引用
2. 检查GAP支撑分析是否准确
3. 确保所有引用符合规范

## Replies

### r001 (2026-04-03T17:53:46)

## 执行者回复 - Issue 871 (Genet_2024_TKAN) r001

### 复查验证结果

**总体状态**: 5 PASS, 0 FAIL ✅

### 行号引用验证结果

| 引用位置 | 验证结果 |
|---------|---------|
| 第113行 | ✅ "The integration of an LSTM cell combined with the RKAN enables the capture of complex nonlinearities with learnable activation functions of RKAN..." |
| 第134-135行 | ✅ RNN隐藏状态更新公式：h_t = f(W_hh·h_{t-1} + W_hx·x_t + b_h) |
| 第142-143行 | ✅ RKAN输入组合公式：s_{l,t} = W_{l,tilde{x}}·x_t + W_{l,tilde{h}}·tilde{h}_{l,t-1} |
| 第331行 | ✅ "TKAN stands out with longer time steps, with an R-squared value at least 25% higher than that of GRU" |
| 第357行 | ✅ "This stability in the TKAN model's learning process..." |

### GAP支撑分析验证

- 无直接GAP支撑 - 论文聚焦于金融市场时间序列预测，未涉及频率域分析或Wiener系统建模

### 结论

所有行号引用准确，GAP支撑分析合理。analyze文件通过复查验证。

### r002 (2026-04-03T18:00:31)

## 审查意见 - Issue 871 (Genet_2024_TKAN)

### 抽样验证结果

对执行者报告的引用进行抽样验证：

- 第113行: ✅ "The integration of an LSTM cell combined with the RKAN enables the capture of complex nonlinearities..."
- 第134-135行: ✅ RNN隐藏状态更新公式
- 第142-143行: ✅ RKAN输入组合公式
- 第331行: ✅ "TKAN stands out with longer time steps, with an R-squared value at least 25% higher than that of GRU"
- 第357行: ✅ "This stability in the TKAN model's learning process..."

### GAP支撑分析

- 评估为"无直接GAP支撑"准确反映了论文聚焦于金融市场时间序列预测

**结论**：analyze 文件通过审查，5处引用验证准确。

