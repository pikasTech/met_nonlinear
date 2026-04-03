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
  - 更新 `xxx_analyze.md` 文件后，要同步更新 `docs\research\literature\analyze\index.md` 中的汇总信息、摘要和链接索引
  - 所有文件均要用中文编写，发现非中文内容必须翻译成中文

- 规划要求
  - 每个论文对应一个 mdissue
  - 保持打开的 mdissue 在 8 个左右
    - 如果少于 8 个，应该积极发现新的问题和任务，已经分析的论文也可以复查
      - 复查任务必须重新打开已经关闭的 issue 或者创建新的 issue
    - 如果多于 8 个，则不开启新的 issue，集中解决当前的 issue，但是也不能为了减少数量而草率关闭 issue，必须等审查者完全满意才关闭

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
  - 禁止使用 `bash` 或者 `shell` 等工具编辑文件，这极易造成编码错误
    - 禁止使用 `echo`、`printf`、`cat` 等命令通过重定向 (`>` / `>>`) 创建或编辑文件
      - 这些命令创建的文件编码不可控，极易产生乱码
      - 应当使用 `edit`、`patch`、`write` 等专用的文件编辑工具
    - 发现乱码的文件则全量 `read` 后直接 `write` 全文进行恢复
