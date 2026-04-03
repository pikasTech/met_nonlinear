## 任务

下载 GAP 文档中引用的文献 PDF，并转换为 Markdown 格式保存到本地。

## 核心原则

- **只处理 GAP 文档中明确引用并附有下载链接的文献**
- PDF 保存到 `docs/research/papers/` 目录
- Markdown 转换后保存到 `docs/research/papers_md/` 目录
- 转换后的 markdown 必须保留原论文的标题、作者、摘要、主要内容结构
- 使用 paper-fetch skill 获取 arXiv 论文；使用其他方式获取 DOI 论文
- 不要尝试获取无法访问的论文（如付费期刊），遇到这种情况标记为"需手动获取"并跳过
- **本步骤只做下载和转换，不做分析和整理**

## 输入文件

docs/research/gap/GAP*/index.md（所有 GAP 文档中的引用链接）
docs/research/literature/verified_literature.md（已验证文献清单）

## 流程

### A. 收集文献链接

- 遍历 `docs/research/gap/` 下所有 GAP 目录的 index.md
- 从每个 index.md 的"下载链接"列提取所有 URL
- 去重后生成完整的文献 URL 清单
- 同时记录每篇文献的标题、作者、年份信息

### B. 下载文献 PDF

- 创建目录 `docs/research/papers/` 用于存放 PDF
- 按以下方式下载：
  - **arXiv 论文**：使用 paper-fetch skill，arXiv ID 从 URL 中提取（如 `2505.04245` 从 `https://arxiv.org/abs/2505.04245`）
  - **DOI 论文**：尝试直接访问 DOI 链接下载（如 `https://doi.org/10.1016/j.measurement.2020.107518`）
  - **其他链接**：使用 wget 或 curl 下载
- PDF 文件命名格式：`{第一作者}{年份}_{标题关键词}.pdf`
- 已存在的 PDF 不重复下载（检查文件是否存在）

### C. 转换为 Markdown

- 创建目录 `docs/research/papers_md/` 用于存放转换后的 markdown
- 使用 pdftotext 或类似工具将 PDF 转为纯文本
- 整理文本结构：标题、作者、摘要、正文章节
- markdown 文件命名格式：`{第一作者}{年份}_{标题关键词}.md`
- 已存在的 markdown 不重复转换

### D. 记录状态

- 维护 `docs/research/papers/PAPER_LIST.md` 记录已下载的论文清单
- 记录每篇论文的：标题、作者、年份、来源URL、下载状态、转换状态

## 输出文件

- `docs/research/papers/` - PDF 文件目录
- `docs/research/papers_md/` - Markdown 文件目录
- `docs/research/papers/PAPER_LIST.md` - 论文清单

## 禁止行为

- 禁止下载 GAP 文档中未引用的论文
- 禁止尝试破解付费期刊或版权受限的内容
- 禁止修改原始 PDF 文件
- 禁止在转换过程中添加个人解读或评论
- **禁止使用 `echo`、`printf`、`cat` 等命令通过重定向创建或编辑文件，这极易产生乱码**
  - 应当使用 `edit`、`patch`、`write` 等专用文件编辑工具
