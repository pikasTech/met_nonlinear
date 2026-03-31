## 总目标

为每一个下载下来的文献，分析其对 `docs\IDEA.md` 的 `## 第二稿声称的贡献 3月29修订` 的支撑作用

## 具体要求

- 每个论文的分析要求
  - 论文的基本信息（标题、作者、发表时间、会议/期刊）
  - 论文的核心内容摘要
  - 论文与 `docs\IDEA.md` 中每个声称贡献的关联分析
    - 批判性支持 （GAP 支持）
      - 论文做了XXX （和 IDEA 的研究内容相关）
      - 论文没有做XXX （批判凸显 IDEA 的 GAP）
    - 直接支持
      - 论文证明了XXX
      - 论文为 XXX 方法的选择/XXX 架构的选择/XXX 提供了理论支持/思路启发
  - 引用要求
    - 必须精确引用到论文 markdown 的行号
    - 必须摘录关键的原文段落

- 输入要求
  - `docs\research\literature\markdown\xxx.md` 论文 markdown 文件

- 输出要求
  - 分析结果输出到 `docs\research\literature\analyze` 目录下
  - 命名为 `xxx_analyze.md`，其中 `xxx` 和输入文件名保持一致
  - `docs\research\literature\analyze\index.md` 中对所有分析结果进行汇总和链接索引

- 禁止行为
  - 禁止修改 `docs\research\literature\markdown\xxx.md` 的原文
  - 禁止模糊引用，必须精确到行号和段落
  - 禁止无根据的关联分析，必须有明确的论文内容支撑分析
