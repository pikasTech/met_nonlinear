## 总目标

为每一个下载下来的文献，分析其对 `docs\IDEA.md` 的 `## 第二稿声称的贡献 3月29修订` 的支撑作用

## 具体要求

- 每个论文的分析要求
  - 论文的基本信息（标题、作者、发表时间、会议/期刊）
  - 论文的核心内容摘要
  - 论文与 `docs\IDEA.md` 中每个声称贡献的关联分析
    - 批判性支持 （GAP 支持）
      - 论文做了什么 （和 IDEA 的研究内容相关）
      - 论文没有做什么/没有做好什么 （批判凸显 IDEA 的 GAP）
    - 直接支持
      - 论文证明了什么
      - 论文为 XXX 方法的选择/XXX 架构的选择/XXX 提供了理论支持/思路启发
  - 引用要求
    - 必须精确引用到论文 markdown 的行号
    - 必须摘录关键的原文段落
  
- 规划要求
  - 每个论文对应一个 mdissue

- 输入要求
  - `docs\research\literature\markdown\xxx.md` 论文 markdown 文件
    - 必须分析**全部的**个markdown文件，均要生成 `xxx_analyze.md` 分析报告，不得遗漏

- 输出要求
  - 分析结果输出到 `docs\research\literature\analyze` 目录下
  - 命名为 `xxx_analyze.md`，其中 `xxx` 和输入文件名保持一致
  - `docs\research\literature\analyze\index.md` 中对所有分析结果进行汇总和链接索引

- 审查要求
  - 行号引用必须准确，行号引用有任何错误都是 P0 级别的错误
  - 只要审查者还提出了任何修改意见，规划者都不得关闭 mdissue，必须继续修改，直到审查者完全满意为止
  - 如果当前没有明确待处理的论文，规划者应当开始复查已经关闭的 mdissue，发现任何问题都必须重新打开 mdissue 进行修改，直到完全满足审查者的要求为止

- 禁止行为
  - 禁止修改 `docs\research\literature\markdown\xxx.md` 的原文
  - 禁止模糊引用，必须精确到行号和段落
  - 禁止无根据的关联分析，必须有明确的论文内容支撑分析
  - 禁止跳过 `docs\research\literature\markdown\xxx.md` 里面的论文，必须全部分析
  - 禁止在一个 mdissue 中分析多篇论文，避免注意力分散
