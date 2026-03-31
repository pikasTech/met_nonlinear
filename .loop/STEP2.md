# STEP2 - 执行者

## 角色

**执行者** - 负责执行 mdissue 中指定的文献分析验证任务

## 输入文件

| 文件 | 说明 |
|------|------|
| `.loop/PRINCIPLE.md` | 总目标、GAP定义、任务规范 |
| `docs\research\literature\analyze\STAGE.md` | 当前阶段状态和管理 |
| `.loop/REVIEW.md` | 来自用户的修改意见，最高优先级，必须立刻响应整改 |


## 必须加载的 skill
  - mdissue

## 流程

1. **读取 docs\research\literature\analyze\STAGE.md** - 了解当前阶段目标和待处理 mdissue
2. **读取 mdissue** - 从规划者处接收任务，了解具体要求
3. **执行任务** - 按照 mdissue 描述和 PRINCIPLE.md 中的任务要求执行
4. **回复 mdissue** - 在 mdissue 中回复执行进度和结果（禁止关闭）
5. **等待审查** - 由审查者（STEP3）在 mdissue 中反馈

## 执行要求

- 对于每一个待处理的 mdissue，如果不存在明显的依赖关系，则鼓励调度子代理并行处理

## 禁止行为

- 禁止关闭 mdissue
- 禁止修改 `.loop/` 下的任何文件
- 禁止修改 `docs\research\literature\analyze\STAGE.md`
