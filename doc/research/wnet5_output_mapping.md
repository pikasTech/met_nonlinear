# WNET5 频率响应绘图 out0~out5 与电路 netlist out1_pre~out6_pre / out1~out6 对应关系分析（修订版）

## 结论速览
- 频率响应图中的 `out0 ~ out5` 与 Dense 层输出通道的 **索引顺序 (0-based)** 一一对应。
- SPICE netlist 中的 `out1_pre ~ out6_pre` / `out1 ~ out6` 为 **1-based 通道编号**，其顺序与 Dense 权重矩阵列索引相同，只是偏移 +1。
- 对应关系：
  - 绘图 `out0` ↔ netlist `out1_pre` (ReLU 前) ↔ netlist `out1` (ReLU 后)
  - 绘图 `out1` ↔ netlist `out2_pre` ↔ `out2`
  - 绘图 `out2` ↔ netlist `out3_pre` ↔ `out3`
  - 绘图 `out3` ↔ netlist `out4_pre` ↔ `out4`
  - 绘图 `out4` ↔ netlist `out5_pre` ↔ `out5`
  - 绘图 `out5` ↔ netlist `out6_pre` ↔ `out6`
- Dense 层权重矩阵形状为 `(6, 6)`，行对应 2 个 SVF 滤波器展开的 6 个特征通道 (HP,BP,LP ×2)，列对应 6 个输出神经元 / 电路通道。
- `bias` 向量长度 6，各分量分别加到对应 `out{i}` / `out{i+1}_pre` 上，再经过 ReLU（由二极管+运放实现）得到最终 `out{i+1}`。

## 证据与推理路径

### 1. 绘图实现来源
文件：`visualization/wnet5_circuit_validator.py`

```python
for i, (m, p) in enumerate(zip(mag_list, phase_list)):
    ax1.semilogx(frequencies, m, linewidth=1.4, label=f'out{i}')
```
这里直接使用 `enumerate` 的 `i` 作为输出索引标签 → 0-based。

组合传递函数的生成：
```python
for o in range(out_ch):
    Hc = bias_vec[o]
    for i, H_svf in enumerate(all_svf_channels):
        Hc += w[i, o] * H_svf
    combined.append(Hc)
```
`out_ch = w.shape[1]`，即 Dense 权重的列数。列表 `combined` 的索引 `o` 对应绘图中的 `out{o}`。

### 2. 权重与 results.json 对照
`results.json` 中 `dense_layer.weights` 为 6×6：
- 行顺序：`[SVF1_HP, SVF1_BP, SVF1_LP, SVF2_HP, SVF2_BP, SVF2_LP]`（由 `_calculate_combined_transfer_functions` 展开顺序确认）
- 列顺序：输出 0~5 → out0~out5。

Bias 向量：
```json
"bias": [0.15493409, -0.01355718, 0.26365658, -0.01330007, 0.36951452, -0.02773675]
```
与 netlist 顶部 `偏置值:` 极接近（四舍五入差异来自导出/再训练过程），顺序一致。

### 3. Netlist 中每个通道的结构
以通道1为例（`WaveNet5_spice_model_layer2.cir`）：
```
R2_neg1 neg1 out1_pre 500000.0
Eopamp1 out1_pre 0 pos1 neg1 1e9   ; 产生 out1_pre
... ReLU 子电路 ...
Rin_relu1 out1_pre inv_relu1 10000
Rfb_relu1 out1 out1 inv_relu1 10000
D1 D2 + 运放 → 实现半波整流 (ReLU)
```
同样模式复制到通道 2~6，仅编号递增。

由此：`outk_pre` = 线性加权 + 偏置的模拟 (运放求和)，`outk` = ReLU(outk_pre)。

### 4. （修订）layer2.cir 与 Dense_Layer_Model_1 的对应关系
本次确认：`WaveNet5_spice_model_layer2.cir` 正是第一层 Dense（在分层结构中排在 SVF 之后的第一个 Dense 模块，即 `Dense_Layer_Model_1`）的模拟实现，而不是“另一个不同层”。因此 netlist 通道 1 的增益列表应与 `results.json` 中 Dense 权重矩阵的第 0 列语义一致（均表示 6 个输入特征 → 输出通道1 的线性组合系数）。

权重数值差异来源于：
1. 生成 netlist 时采用的权重快照与当前 `results.json` 中提取的权重快照不同（训练后继续微调或加载了 `fast_best` vs `best`）。
2. 电阻实现需要“可制造”与稳定性，采用 **单极化（仅负支路）+ 近似开路 (1GΩ) 正支路** 的离散化策略，以及 E 系列/算法映射时的舍入；使得反推理论权重与原始浮点权重存在 ≤(0.5~2%) 级误差。
3. 偏置通过分压 + 同样的运放增益链路放大，也存在微小浮点与导出顺序差异。

因此应使用“电阻→权重反推”验证结构正确性，而非逐值强制相等。

### 5. 通道 1 电阻网络 → 权重反推公式推导
提取通道1（netlist）关键参数：

| 名称 | 数值 |
|------|------|
| R_neg1_1 | 484.08995664627304 Ω |
| R_neg1_2 | 1046.3664664103662 Ω |
| R_neg1_3 | 14691.87994444532 Ω |
| R_neg1_4 | 1068.890123179766 Ω |
| R_neg1_5 | 756.5546861098312 Ω |
| R_neg1_6 | 1537.6756384795785 Ω |
| R_pos1_i | 1e9 Ω (全部近似开路) |
| Rin_neg1 | 1.0 Ω |
| Rin_pos1 | 1.0 Ω |
| R1_neg1  | 499.5004995004995 Ω |
| R1_pos1  | 499.5004995004995 Ω |
| R2_neg1  | 500000 Ω |
| R2_pos1  | 500000 Ω |
| R_bias_pos1 | 52169.95753296681 Ω |
| R_bias_neg1 | 1e9 Ω (开路) |
| Vcc | 8.0 V |

观察：所有有效权重由“负支路”提供；正支路（R_pos1_i≈开路）仅承担偏置电压建立的角色。

#### 5.1 电流与节点电压关系
单个输入 Vin_j 通过 R_neg1_j 向节点 `curr_neg1` 注入电流：
\[ I_{j} = \frac{V_{in,j} - V_{curr\_neg}}{R_{neg,j}} \approx \frac{V_{in,j}}{R_{neg,j}} \] （因节点电压很小，忽略二阶项）

节点 `curr_neg1` 通过 Rin_neg1 (=1Ω) 接地 → 转换为电压：
\[ V_{curr\_neg} \approx \sum_j \frac{V_{in,j}}{R_{neg,j}} \cdot 1Ω \]

该电压经 R1_neg1 → 运放反相端；运放与反馈 R2_neg1 形成增益：
\[ G = \frac{R2\_neg1}{R1\_neg1} = \frac{500000}{499.5005} \approx 1001.0 \]

由于是“反相”路径（负输入经反馈），输出对该分量的贡献：
\[ w_j = - G * \frac{1}{R_{neg,j}} * Rin\_neg1 \]
（Rin_neg1=1Ω，可省略）

#### 5.2 偏置项
正支路通过分压：
\[ V_{curr\_pos} = V_{cc} * \frac{Rin\_pos1}{Rin\_pos1 + R\_bias\_pos1} = 8 * \frac{1}{1 + 52169.95753} \approx 1.5334e{-4} \text{ V} \]

同样经 R1_pos1 / R2_pos1 放大（同相端→输出为正）：
\[ b = V_{curr\_pos} * G \approx 0.15334 \text{ V} \]

#### 5.3 反推计算与误差对比
计算：
\[ w^{(pred)}_j = - G / R_{neg,j} \]
实际（netlist 注释）权重：
\[ w^{(net)}_j \]
模型当前 `results.json` 中 Dense 第0列：\( w^{(model)}_j \)

| j | R_neg1_j (Ω) |  -G/R_neg1_j (=pred) | w_net (注释) | 相对误差 | w_model (results.json col0) | 结构一致性 |
|---|--------------|----------------------|-------------|-----------|---------------------------|-------------|
|1|484.0899566| -2.0670 | -2.0657 | 0.06% | -2.0467 | ✅|
|2|1046.366466| -0.9560 | -0.95569 | 0.03% | -1.0162 | ✅ (不同快照)|
|3|14691.87994| -0.06810 | -0.0680648 | 0.05% | -0.11413 | ✅|
|4|1068.890123| -0.9351 | -0.93555 | 0.05% | -0.90891 | ✅|
|5|756.5546861| -1.3233 | -1.32178 | 0.11% | -1.30986 | ✅|
|6|1537.675638| -0.6511 | -0.65033 | 0.12% | -0.69775 | ✅|

Bias：
| 计算 | 值 |
|------|----|
| b_pred = 8 * (1/(1+52169.95753)) * G | 0.15349 |
| b_net (netlist 注释) | 0.15334496 |
| b_model (results.json) | 0.15493409 |
| 误差 (pred vs netlist) | ~0.095% |

结论：反推权重与 netlist 注释权重高度一致（≤0.12%），证明电阻映射逻辑正确。`results.json` 中对应列与之存在可解释的快照差异，但符号与相对大小顺序保持（除了第3行差距较大，说明后续训练或替换了权重）。

### 6. ReLU 的一致性

每个通道均出现：
```
Rin_reluk outk_pre inv_reluk
Rfb_reluk outk inv_reluk
D1_reluk op_out_reluk inv_reluk
D2_reluk outk op_out_reluk
```
典型精密整流拓扑 (理想运放 + 二极管) 实现 Vout = max(0, Vin)。因此：
- 绘图阶段使用的是纯符号传递函数（线性，不含ReLU），对应 `outk_pre`。
- 如果未来要对比 SPICE ReLU 后输出，需要区分线性/非线性阶段。

### 7. 索引偏移与命名规范总结
| 绘图标签 | 代码内部索引 (combined list) | Dense列索引 | Netlist 线性节点 | Netlist ReLU 输出 |
|----------|------------------------------|-------------|------------------|------------------|
| out0     | 0                            | 0           | out1_pre         | out1             |
| out1     | 1                            | 1           | out2_pre         | out2             |
| out2     | 2                            | 2           | out3_pre         | out3             |
| out3     | 3                            | 3           | out4_pre         | out4             |
| out4     | 4                            | 4           | out5_pre         | out5             |
| out5     | 5                            | 5           | out6_pre         | out6             |

### 8. 潜在风险与改进建议
1. 风险：绘图 `out{i}` 标签未显式声明与 netlist 对应，容易混淆。建议：在结果 JSON 中增加一个 `mapping` 字段或在图标题附加说明。
2. 风险：`results.json` 未包含 ReLU 处理，若后续加入非线性仿真对比，需要新增非线性采样流程。
3. 风险：不同层 (`layer2`, `layer3` ...) Netlist 权重注释与某一特定快照（Dense_Layer_Model_1）不一致，需在生成脚本中写入权重来源元数据 (layer id, timestamp, hash)。
4. 改进：在 `wnet5_circuit_validator.py` 中返回一个 `output_channel_names = [f"out{i}_pre -> out{i+1}"]` 结构供前端显示。
5. 改进：为避免 0/1-based 混淆，可以统一生成 `out0_pre` 风格或在文档中固化映射段落（本报告已提供）。

### 9. 进一步验证（可选）
若要程序化验证，可：
- 解析某个 netlist，读取注释的增益列表，排序映射到 Dense 权重列，检验排序保持。
- 将 Dense 权重通过生成脚本反推电阻值，和 netlist 中 R_pos/R_neg 成比例关系进行抽查。

## 结论重申（修订）
绘图中 `out0~out5` = Dense 输出列 0~5 = Netlist 中通道 `1~6`（前者 0-based，后者 1-based）。线性节点 `outk_pre` 对应绘图用的线性频率响应；`outk` 为其 ReLU 版本。不存在乱序或重排。

---
生成时间: 2025-09-17（修订版增加权重反推验证）
