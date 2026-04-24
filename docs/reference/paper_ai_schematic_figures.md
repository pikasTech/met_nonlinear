# 论文 AI 原理示意图绘制规范

本文档记录当前论文中使用 AI 绘制机理类 bitmap 示意图的长期经验，适用于 `docs/paper/latex/main.tex` 中需要表达物理机理、结构先验、部署原理或算法流程的插图。

## 适用边界

- 适合用 AI 生成的图：物理机理示意图、算法原理图、结构先验图、硬件部署流程图、带少量标注的二维说明图。
- 更适合用代码生成的图：定量曲线、柱状图、箱线图、雷达图、数据对比图、需要精确坐标或可重复数值绘制的图。
- AI 图必须作为论文资产落到 `docs/paper/assets/`，再由 `docs/paper/src/paper_pipeline.py` 复制到 `docs/paper/figures/`，避免后续生成流程覆盖或丢失。

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
- 最终验收包括：图像可读、正文位置合理、`gen_data.py` 不会覆盖、LaTeX 编译通过。

## 项目落地方式

1. 使用 `imagegen` 生成图像，保留默认生成目录中的原始图。
2. 将选定版本复制到 `docs/paper/assets/<figure_name>_ai.png`。
3. 在 `docs/paper/src/paper_pipeline.py` 中写入复制逻辑，把 assets 中的图复制到 `docs/paper/figures/<figure_name>.png`。
4. 同步写入 `.raw.json`，记录来源、图类型和关键表达元素。
5. 执行：

```bash
python docs/paper/gen_data.py
```

6. 编译验证：

```bash
python C:/Users/lyon/.agents/skills/latex/scripts/latex-cli.py build --workdir c:/work/met_nonlinear_master/docs/paper/latex --tex main.tex --engine xelatex --passes 2
```

## 当前 canonical 示例

- MET 非线性机理图资产：`docs/paper/assets/fig_14_met_nonlinear_mechanism_ai.png`
- 论文引用图：`docs/paper/figures/fig_14_met_nonlinear_mechanism.png`
- 生成流水线：`docs/paper/src/paper_pipeline.py` 中的 `make_mechanism_schematic()`
- 正文位置：`docs/paper/latex/main.tex` 中 `eq:nonlinear_mechanism_terms` 附近