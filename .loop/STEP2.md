## 任务

对 STEP1 收集的文献线索进行深度阅读、分析和理论提取，形成系统性的理论综述。

## 核心原则

- **所有 `docs/research/literature/` 目录下的文档必须使用中文编写**
- 深度阅读优先于数量扩充，宁可少读几篇也要确保理解准确
- 同一主题的文献，优先阅读经典论文和高引用论文
- 对冲突理论或相反结论必须明确标注，不得静默合并
- STEP2 只做理论分析和提取，不要再次大规模扩展新文献检索
- 没有找到原文或无法获取全文时，不得写入 `verified_literature.md`
- STEP2 有评判权，但没有推荐权；职责是判定文献质量、理论可靠性和与论文的相关度
- 鼓励使用子代理并行分析不同主题或不同理论方向的文献，但最终必须统一收敛为一份系统性分析报告

## 输入文件

.loop/PRINCIPLE.md
docs/research/literature/literature_catalog.md
docs/research/literature/raw_literature.md
docs/research/literature/verified_literature.md
docs/IDEA.md

## 流程

- 读取 `docs/research/literature/raw_literature.md` 中新增或待分析条目
- 将本轮分析过程写入 `docs/research/literature/{YYYYMMDD}/` 下的分析报告，至少记录：分析对象、分析深度、核心发现、理论提取、待核实事项、影响到的文档
- 分析报告优先按 `.loop/REPORT_TEMPLATE.md` 中"分析报告模板"编写，保证不同轮次结构一致
- 通过全文阅读、PDF 下载、单位图书馆等渠道获取文献完整内容
- 对以下内容进行深度分析：
  - 核心方法/理论的基本原理
  - 关键公式和数学推导
  - 实验设置和评估指标
  - 与其他方法的对比
  - 优点和局限性
- 按主题对文献进行分类整理：
  - Wiener 模型理论
  - KAN 网络
  - 频域损失函数
  - 深度学习漂移补偿
  - 神经网络架构效率对比
- 提取可直接支撑论文声称的理论依据
- 识别文献中的研究空白和机会
- 如分析结果改变了整体判断，更新 `docs/research/literature/SUMMARY.md`：补充新理论发现、修正原有理解、删除过时结论
- 将条目按以下规则移动：
  - 全文已获取且理论内容已分析 -> `docs/research/literature/verified_literature.md`
  - 无法获取全文/理论不可靠/明显不相关 -> `docs/research/literature/excluded_literature.md`
  - 仍缺关键信息 -> 留在 `docs/research/literature/raw_literature.md` 并保留简短待办
- 更新时优先改现有条目，不要把同一文献在三个文件里重复写成长篇全文
- 对 `docs/research/literature/verified_literature.md` 中的文献，尽量补齐以下字段：
  - 核心贡献
  - 关键方法/理论
  - 主要结论
  - 与论文的相关点
  - 可引用的具体内容
- 每个进入 `docs/research/literature/verified_literature.md` 的文献都必须有理论分析记录；没有分析记录就不能通过
- 如果证据不足，只能维持 `pending` 或转入 `excluded`，不能为了推进节奏放行
- 若本轮更新了 `verified_literature.md`、`excluded_literature.md`、`SUMMARY.md` 等汇总文档，必须补充对应分析报告路径引用

## 理论提取重点

### Wiener 模型理论

- Wiener 系统的定义：线性动态系统 + 非线性静态增益
- 辨识方法：脉冲响应法、频率响应法、非线性最小二乘法
- 与 Hammerstein 模型的区别和联系
- 在电化学传感器中的应用

### KAN 网络理论

- Kolmogorov-Arnold 表示定理
- B-spline 基函数的选择
- 与 MLP 的结构差异
- 计算效率的理论分析

### AFMAE 损失函数

- 频域分析基础（FFT、功率谱）
- 频域损失的数学定义
- 与时域 MAE 的关系和区别
- 在时间序列预测中的优势

### 深度学习漂移补偿

- 现有方法的分类和总结
- 主流评估指标
- 数据集构建方法
- 研究空白分析

### MEASUREMENT 实验测量

- 传感器频率响应测量标准方法
- 非线性校准的实验设计流程
- 信号采集与预处理规范
- 数据集划分策略（训练/验证/测试）
- 测量不确定度分析

### 传感器非线性补偿

- 电化学传感器非线性建模方法
- 温度漂移补偿的传统方法
- 前馈补偿 vs 反馈补偿的比较
- 深度学习在传感器补偿中的应用
- 补偿效果评估指标（谐波失真、信噪比等）

## 输出文件

- `docs/research/literature/verified_literature.md`
- `docs/research/literature/excluded_literature.md`
- `docs/research/literature/{YYYYMMDD}/` 下的分析报告
- `docs/research/literature/SUMMARY.md`（如分析结果改变当前理论认知）

## 禁止行为

- 禁止仅凭标题/摘要就认定文献有效
- 禁止删除重复条目的来源痕迹；应保留去重依据
- 禁止把"可能相关"但未深度阅读的文献直接升级为高相关度
- 禁止修改 `docs/research/literature/raw_literature.md`
- 禁止输出"建议优先引用""必须引用"等推荐建议
