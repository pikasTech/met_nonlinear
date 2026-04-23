# 论文 LUT 插值部署评估方法说明

## 写作定位

本文档用于沉淀 Wiener-KAN 在 MCU 侧不同导出实现方式的比较方法。它既是仓库内的长期参考文档，也是后续撰写论文部署补充实验时可直接展开的中文中间稿。

本文档只描述比较目标、对象定义、执行流程、正式指标与写作边界，不记录一次性的串口日志或图像截图。

## 实验目的

当前 Wiener-KAN 的 MCU 导出存在三个彼此冲突的目标：

1. 数值一致性：C 推理尽量逼近 TensorFlow 参考路径；
2. 板端时延：`KEIL-SPEED (ms/point)` 尽量低；
3. 存储代价：Flash / RAM 尽量小。

LUT 近似、LUT 插值与非 LUT 精确路径分别对这三个目标施加不同影响，因此需要一个稳定的专题评估方法，而不是只报告单一实现的最好数字。

## 比较对象

长期上，LUT 插值专题评估必须满足“同一训练模型、不同导出实现”的语义约束。也就是说，以下对象必须共用：

- 同一个 `model_project_name`
- 同一份 `weights_file`
- 同一段 validation 选窗

当前稳定的三种实现变体为：

1. **LUT 最近邻**
   - `use_lut = true`
   - `lut_interpolation = false`
2. **LUT + 一阶线性插值**
   - `use_lut = true`
   - `lut_interpolation = true`
3. **非 LUT 精确路径**
   - `use_lut = false`

因此，这个专题实验衡量的是“同一模型的部署实现取舍”，而不是“不同训练模型谁更好”。

## 实验设计

### 固定训练模型

当前专题实验固定 Wiener-KAN canonical project：

- `projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4`

围绕这一个训练项目创建多个 `qemu-c-inference` EP，仅修改 `generation_config`。

### 统一评估字段

当前最稳定、最适合进入论文正文的字段包括：

- `QEMU-MAE`
- `KEIL-MAE`
- `KEIL-SPEED (ms/point)`
- Flash
- RAM

如果需要补充解释实现代价来源，可以进一步读取 `build_output_<target>.txt` 中的 `Code` / `RO-data` / `RW-data` / `ZI-data`。

### 结论判据

该专题实验不应试图寻找“单一绝对最优实现”，而应回答：

1. 哪一种实现提供最低延迟；
2. 哪一种实现提供最高数值一致性；
3. 哪一种实现提供最低 Flash / RAM；
4. 哪一种实现更适合作为正文主部署结果，哪一种应作为补充分析或 future work。

## 正式执行流程

当前稳定工作流如下：

1. 基于同一个训练 project 创建多个 `qemu-c-inference` EP；
2. 对每个 EP 运行：
   - `python cli.py ep "ex_projects/inference/qemu-c-inference/TASK_NAME"`
   - `python cli.py ep keil-bench "ex_projects/inference/qemu-c-inference/TASK_NAME"`
3. 从每个 EP 中读取：
   - `data/benchmark_summary.json`
   - `data/keil_benchmark_summary.json`
   - `keil_project/MDK-ARM/output/build_output_<target>.txt`
4. 统一整理为同一张比较表；
5. 在论文中按“精度 / 速度 / 资源”三列 trade-off 写法展开。

## 指标口径

### 数值一致性

对于任一实现变体 $v$，定义：

$$
E_{\mathrm{QEMU}}^{(v)}
=
\frac{1}{N}\sum_{i=1}^{N}
\left|
\hat{y}^{(v,\mathrm{QEMU})}_i
-
\hat{y}^{(\mathrm{TF})}_i
\right|
$$

$$
E_{\mathrm{KEIL}}^{(v)}
=
\frac{1}{N}\sum_{i=1}^{N}
\left|
\hat{y}^{(v,\mathrm{KEIL})}_i
-
\hat{y}^{(\mathrm{TF})}_i
\right|
$$

即当前 `QEMU-MAE` 与 `KEIL-MAE` 都是“导出 C 推理相对 TensorFlow 参考路径的聚合一致性误差”。

### 板端时延

单位点时延定义固定为：

$$
S_{\mathrm{KEIL}}^{(v)}
=
\frac{\mathrm{wall\_time\_per\_iter\_ms}}
\mathrm{record\_count} \cdot \mathrm{seq\_len}
$$

也就是当前 `KEIL-SPEED (ms/point)` 的稳定口径。

### 资源占用

当前 Flash / RAM 定义为：

$$
\mathrm{Flash} = \mathrm{Code} + \mathrm{RO\text{-}data}
$$

$$
\mathrm{RAM} = \mathrm{RW\text{-}data} + \mathrm{ZI\text{-}data}
$$

## 写作建议

论文中推荐按如下逻辑组织该专题结果：

1. 最近邻 LUT 往往提供最低时延，但误差可能偏大；
2. `LUT + interpolation` 适合写成“在保持 LUT 存储框架的前提下，用有限速度代价换取明显更好的数值一致性”；
3. `No LUT exact` 适合写成“精确参考上界”或“实现取舍边界”，而不是直接写成正文默认部署实现；
4. 如果某种实现明显牺牲其中一个维度，应把它写成 trade-off，而不是单向优点。

## 写作边界

当前章节应避免以下写法：

- 把 LUT 插值实验写成训练模型精度横评；
- 在比较中混入不同训练权重或不同 validation 选窗；
- 只报告最快路径，不报告其 `KEIL-MAE` 代价；
- 只报告最精确路径，不报告其 `KEIL-SPEED` 或 Flash 代价。

## 相关文档

- [paper_edge_inference_evaluation_method.md](paper_edge_inference_evaluation_method.md)
- [edge_device_emulation.md](edge_device_emulation.md)
- [metrics.md](metrics.md)
