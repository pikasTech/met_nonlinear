# R1 任务报告

## 任务

纯叙事角度的 MN 主文子图调整建议。

## 判断前提

- 只看文章叙事效率，不考虑技术实现难度、图形重绘成本和已有配置限制。
- 目标不是把更多 Supplement 图搬回 main，而是让主文的因果链和阅读节奏更顺。
- 优先原则是“一张图只回答同一层级的问题”，避免一张图同时承担对象介绍、方法细节、结果证明和部署流程四种不同功能。

## 总结结论

最值得动的只有两处：

1. 把机理图并回主文第一张器件图。
2. 把 local transfer slices 并回方法图，而不是并到结果图。

如果只做这两处调整，主文叙事会明显更顺；其余 Supplement 图大多更适合继续留在补充材料中。

## 具体建议

### 1. 第一张主图改成“对象 + 非线性来源”一体图

当前最自然的主线起点，不应该只是器件结构和读出电路，还应该直接把“为什么这个传感器会出现幅值相关非线性”交代清楚。

推荐把以下内容收束到同一张主图：

- MET structure
- readout circuit
- nonlinear mechanism schematic
- 如版面允许，可加入一个最小化的代表性幅值相关频响现象作为问题引子

这样第一张图就能连续回答三个问题：

- 研究对象是什么
- 信号怎么被读出来
- 非线性问题为什么会出现

叙事收益是，读者从器件到问题的过渡会更自然，不会出现“先介绍对象，后面再突然补一张机理图”的割裂感。

### 2. 方法图不应只是框图，要把物理先验来源并进去

当前方法图如果只展示 Wiener-KAN 框架，读者知道模型长什么样，但不够直观地理解“为什么前端是 Wiener local prior，而不是任意黑箱前端”。

从叙事角度，最应该并入方法图的是：

- local transfer slices

推荐的表达方式是：

- 左侧给 Wiener-KAN framework
- 右侧给 magnitude-conditioned local transfer slices
- 如需要进一步强化物理动机，可少量借用 parallel Wiener principle schematic 的原理性 panel，但不要把结果性拟合 panel 一起带回 main

这样方法图不再只是在讲“结构是什么”，而是在讲“结构为什么这样设计”。这会明显增强方法章节的说服力。

### 3. 主结果图尽量不要再塞新子图

主结果图应该只负责证明方法有效，不要再混入方法解释或部署流程。

因此建议：

- main compensation result 图保持基本稳定
- 不把 local transfer slices、LUT principle 或 workflow panel 塞进主结果图

理由是这些信息层级不同，会削弱“结果证明”本身的冲击力。

### 4. Horizontal summary 更应该做减法，不应该继续加子图

横向总结图当前容易承载过多信息。纯叙事上，它最适合做“横评摘要”，不适合再兼做训练过程和部署流程摘要。

建议优先保留：

- frequency drift
- sensitivity drift
- linearity
- 一个综合摘要 panel（如 radar 或 compact summary）

建议优先移出：

- convergence curve
- 若部署单独成图，则 throughput 也可从 summary 中拿掉

这样横评图的功能会更单纯：只服务于“主文核心结果的跨模型比较”。

### 5. 部署图只保留“结果型”子图回 main

部署章节在主文中只需要证明两件事：

- 可以落到板端
- 精度/速度/资源占用的代价是可接受的

因此如果要把部署内容放回主文，只建议保留：

- embedded performance panel
- LUT trade-off panel

而以下内容更适合留在 Supplement：

- export workflow
- validate workflow
- 详细导出链路说明

这样主文部署图是在证明“可行”，而不是解释“怎么做出来”。

### 6. 下列图整体上更适合留在 Supplement

从叙事角色看，以下图都偏补充论证，而不是主线证据：

- hyperparameter sensitivity
- LUT lookup principles
- KAN single-neuron toy example
- parallel Wiener equivalent 的结果型 panel
- 任何重复承载已有主结论的流程图或细分表格

这些图可以增强完整性，但不适合占用 main 的有限 display items。

## 推荐的主文图序思路

如果只按叙事组织主文，推荐的 display item 主线可以是：

1. 对象与问题来源图：structure + readout + mechanism
2. 问题存在图：nonlinear frequency response / amplitude-dependent drift
3. 方法图：framework + local transfer prior
4. 主补偿结果图
5. main benchmark table
6. horizontal summary figure（压缩后版本）
7. ablation overview table
8. deployment result figure 或 figure/table 合并项

这个顺序对应的故事线是：

- 先说明对象和问题从哪里来
- 再说明问题确实存在
- 然后说明方法为什么这样设计
- 再证明方法有效
- 最后证明横评成立和部署可行

## 一句话建议

如果只能做两处子图调整，就做下面两件事：

1. 机理图并回第一张器件图。
2. local transfer slices 并回方法图。

这是纯叙事角度下收益最高、最能改善主文阅读流的两处调整。
