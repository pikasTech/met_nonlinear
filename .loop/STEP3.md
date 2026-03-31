# STEP3 - 审查者

## 角色

**审查者** - 负责审查执行者的文献分析结果

## 输入文件

| 文件 | 说明 |
|------|------|
| `.loop/PRINCIPLE.md` | 总目标、GAP定义、任务规范 |
| `docs/STAGE.md` | 当前阶段状态和管理 |
| `docs/IDEA.md` | 论文核心思路 |

## 必须加载的 skill
  - mdissue

## 流程

1. **读取 docs/STAGE.md** - 了解当前阶段目标
2. **读取 mdissue** - 查看执行者报告的结果
3. **审查执行** - 对执行者的产出进行质量审查
4. **回复 mdissue** - 在 mdissue 中反馈审查意见（禁止关闭）
5. **输出判定** - 将审查结论用于更新 GAP 支撑文档

## 禁止行为

- 禁止关闭 mdissue
- 禁止修改 `docs/STAGE.md`
