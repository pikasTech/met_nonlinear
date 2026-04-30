# 论文 AI 原理示意图绘制规范

本文档记录当前论文中使用 AI 绘制机理类 bitmap 示意图的长期经验，适用于 `docs/paper/latex/main.tex` 中需要表达物理机理、结构先验、部署原理或算法流程的插图。

## 适用边界

- 适合用 AI 生成的图：物理机理示意图、算法原理图、结构先验图、硬件部署流程图、带少量标注的二维说明图。
- 更适合用代码生成的图：定量曲线、柱状图、箱线图、雷达图、数据对比图、需要精确坐标或可重复数值绘制的图。
- AI 图必须作为论文资产落到 `docs/paper/assets/`，再由对应的 `ex_projects/plot/single/**/config.json` 或 `ex_projects/plot/multi/**/config.json` 读入并输出到自身 `data/` 目录，避免旧 figure pipeline 覆盖或丢失。

## 生成前判断

- 先全文读取 `docs/paper/latex/main.tex`，确认图要服务的上下文，而不是只按局部段落补图。
- 若已有结构图，新的机理图应避免重复画完整设备结构；应只保留解释机理所需的最小结构元素。
- 论文中“机理图”应放在对应物理公式或控制方程附近，而不是放在 Introduction 中作为概念装饰。
- 图应回答一个明确问题：例如“哪些物理化学因素导致频率响应漂移”，而不是只画正常工作过程。

## 提示词原则

- 明确要求二维、白底、黑色线条、简单上色、少量标注，避免 3D、照片感、复杂装置或装饰风。
- 参考已有图风格时，应明确写出“匹配已有电化学反应腔结构示意图风格：白底、黑色轮廓、浅青色电解液填充、简洁标签”。
- 对于机理图，应在提示词中列出必须体现的“原因 -> 参数变化 -> 观测现象”链条。
- 对于 MET 非线性机理图，推荐链条为：
  - 膜片大挠度导致等效刚度 `k(A)` 上升，并使固有频率 `η(A)` 漂移；
  - 流体惯性与水动力阻力变化导致阻尼 `ζ(A)` 改变；
  - 浓度极化和离子输运非均匀导致局部通量变化；
  - Butler--Volmer 电极反应非线性导致灵敏度 `S(A)` 漂移；
  - 上述因素共同改变局部传递函数 `H(s; A)`，最终表现为频率响应曲线右移和增益变化。

## 迭代判定标准

- 第一版若只是普通工作流程图，应继续迭代，直到图中明确体现“导致现象的关键因素”。
- 若图重复已有结构图，应继续简化结构，只保留服务机理解释的局部结构。
- 若图把电化学反应画成完整原电池，应要求只保留局部电极反应示意，避免和传感器结构含义冲突。
- 若图中英文标注过多，应减少到关键短语；复杂解释放入正文和 caption。
- 最终验收包括：图像可读、正文位置合理、`python cli.py ep ex_projects/plot/.../<figure_project>` 可重复生成、LaTeX 编译通过。

## 密集流程图的简化策略

当 AI 生成的算法流程图在单栏或双栏版面中显得过小、过密时，优先改为代码生成的简化 schematic，而不是继续放大原图。稳定做法是先保留正文真正需要的主链路，再删除次要装饰和重复信息：

- 每张原理图只回答一个核心问题，例如“AFMAE 如何从波形误差转为幅频响应误差”或“LUT 如何把 KAN 激活的在线求值变为查表”。
- 子图数量优先控制为两段式结构：第一段解释关键变换路径，第二段解释训练或部署中的取舍；不要把公式推导、矩阵索引、硬件图标和性能结论都塞入同一画面。
- 每个框只保留短语或核心符号，长公式留给正文 equation；例如图中写 `uniform LUT`、`v_0,\ldots,v_{Q-1}`，正文再给出完整采样公式。
- 曲线小图只承担“形状提示”作用，能去掉坐标轴、图例和多余刻度时应去掉，避免在缩放后的 PDF 中变成不可读细节。
- 对于并列路径，应突出主差异词：如 `one table read` 与 `two reads + blend`、`MAE pointwise` 与 `AFMAE response`；辅助说明放入 caption 或正文段落。
- 对于嵌入式验证流程图，应把主链路压缩为“导出一次”和“两个目标验证”：上半部分说明训练项目导出同一份 C 实现，下半部分并列展示 QEMU 数值一致性和目标板吞吐/内存验证；逐文件产物、归一化公式、串口包级步骤和硬件装饰图标放到正文或省略。
- `.raw.json` 应记录简化焦点和被省略的次要内容，使后续维护者知道删减是有意设计，而不是信息遗漏。

## 项目落地方式

1. 使用 `imagegen` 生成图像，保留默认生成目录中的原始图。
2. 将选定版本复制到 `docs/paper/assets/<figure_name>_ai.png`。
3. 创建或更新 `ex_projects/plot/single/<figure_name>/config.json`，把资产路径写入 `paper_figure.source_path` 或等价绘图配置。
4. 渲染后在 ex_project 的 `data/` 目录同步写入 `.raw.json`，记录来源、图类型和关键表达元素。
5. 执行：

```bash
python cli.py ep ex_projects/plot/single/<figure_name>
```

6. 编译验证：

```bash
python C:/Users/lyon/.agents/skills/latex/scripts/latex-cli.py build --workdir c:/work/met_nonlinear_master/docs/paper/latex --tex main.tex --engine xelatex --passes 2
```

当图已从 AI 资产改为代码生成的简化 schematic 时，项目落地方式调整为：在 `ex_projects/plot/` 中保留可运行的 figure project，由 `python cli.py ep ...` 刷新 PNG 和 `.raw.json`；`main.tex` 只引用对应 ex_project `data/` 下的稳定产物，不直接引用 `docs/paper/assets/`。

## 当前 canonical 示例

- MET 非线性机理图资产：`docs/paper/assets/fig_14_met_nonlinear_mechanism_ai.png`
- 论文引用图：`ex_projects/plot/single/fig_14_met_nonlinear_mechanism/data/fig_14_met_nonlinear_mechanism.png`
- 生成入口：`python cli.py ep ex_projects/plot/single/fig_14_met_nonlinear_mechanism`
- 正文位置：`docs/paper/latex/main.tex` 中 `eq:nonlinear_mechanism_terms` 附近
- AFMAE 简化原理图相关面板：`ex_projects/plot/single/fig_03_loss_ablation_1_maeafmae` 和同组 loss-ablation ex_projects，用于展示 MAE/AFMAE 训练对比。
- LUT 简化部署图：`ex_projects/plot/multi/fig_15_lut_lookup_principles`，用于展示“离线采样成表”和“在线 nearest / linear 查表取舍”两条主链路。
- 板端验证简化流程图：`ex_projects/plot/multi/fig_17_board_inference_validation_workflow`，用于展示“trained Wiener-KAN project -> C export package -> embedded C inference kernel”和“QEMU / STM32F405 两条验证路径”。
