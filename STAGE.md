# STAGE - 文献调研阶段管理

## 当前阶段

| 阶段 | 状态 | 开始时间 | 备注 |
|------|------|----------|------|
| STAGE-1 | in_progress | 2026-03-31 | STEP1 文献调研收集 |

## 阶段规划

### STAGE-1: STEP1 文献调研收集
**目标**: 完成 11 个 GAP 的文献调研，识别文献缺口

**角色**: 规划者 (STEP1)

**具体任务**: 参见 [.loop/STEP1.md](./.loop/STEP1.md)

**待处理 mdissue**:
| Issue ID | 主题 | 状态 | 执行者 | 审查者 |
|----------|------|------|--------|--------|
| - | - | - | - | - |

**完成条件**:
- [ ] literature_catalog.md 覆盖所有 P0/P1 方向
- [ ] raw_literature.md 记录所有文献线索
- [ ] GAP文献缺口.md 识别所有缺口

---

### STAGE-2: STEP2 文献分析验证
**目标**: 深度分析已收集文献，验证 GAP 支撑能力

**前置条件**: STAGE-1 完成

**角色**: 执行者 (STEP2)

**具体任务**: 参见 [.loop/STEP2.md](./.loop/STEP2.md)

**待处理 mdissue**:
| Issue ID | 主题 | 状态 | 执行者 | 审查者 |
|----------|------|------|--------|--------|
| - | - | - | - | - |

**完成条件**:
- [ ] verified_literature.md 完成所有 P0 文献分析
- [ ] excluded_literature.md 记录排除文献
- [ ] GAP文献缺口.md 更新缺口等级

---

### STAGE-3: STEP3 GAP 支撑文档生成
**目标**: 生成 GAP 支撑文档和核心文献清单

**前置条件**: STAGE-2 完成

**角色**: 审查者 (STEP3)

**具体任务**: 参见 [.loop/STEP3.md](./.loop/STEP3.md)

**待处理 mdissue**:
| Issue ID | 主题 | 状态 | 执行者 | 审查者 |
|----------|------|------|--------|--------|
| - | - | - | - | - |

**完成条件**:
- [ ] GAP1-GAP11 支撑文档全部生成
- [ ] key_references.md 核心文献清单完成
- [ ] GAP_SUMMARY.md 总体支撑矩阵完成

---

## 角色定义

| 角色 | 职责 | 禁止行为 |
|------|------|----------|
| 规划者 (STEP1) | 更新 STAGE.md、开启/指定 mdissue、审查多轮回复、决定关闭 | 不能执行具体任务 |
| 执行者 (STEP2) | 读取 STAGE.md、按 mdissue 执行、在回复中报告 | 不能关闭 mdissue |
| 审查者 (STEP3) | 审查执行者回复、在 mdissue 中反馈意见 | 不能关闭 mdissue |

## 工作流程

```
规划者(STEP1) ──→ [更新 STAGE.md，开启 mdissue] ──→ 执行者(STEP2)
                                                              │
                                                        [执行并回复 mdissue]
                                                              │
                                                              ▼
                                                        审查者(STEP3)
                                                              │
                                                        [审查并回复 mdissue]
                                                              │
                                                              ▼
                                                    [下一轮]
                                                              │
                                                              ▼
                                              规划者(STEP1)审查回复
                                                              │
                                                        [满意则关闭 mdissue]
                                                              │
                                                    [不满意则继续]
```

## mdissue CLI 命令

```bash
# 查看当前 open 的 issue
bun run C:/Users/liang/.claude/skills/mdissue/scripts/mdissue-cli.ts list --status open

# 查看所有 issue（包括 closed）
bun run C:/Users/liang/.claude/skills/mdissue/scripts/mdissue-cli.ts list --status all

# 获取指定 issue 详情
bun run C:/Users/liang/.claude/skills/mdissue/scripts/mdissue-cli.ts get <id>

# 创建新 issue
bun run C:/Users/liang/.claude/skills/mdissue/scripts/mdissue-cli.ts create -t "标题" -f /tmp/desc.md -k tag1 -k tag2 -k tag3 -k tag4 -k tag5

# 回复 issue
bun run C:/Users/liang/.claude/skills/mdissue/scripts/mdissue-cli.ts reply -i <id> -f /tmp/reply.md

# 关闭 issue
bun run C:/Users/liang/.claude/skills/mdissue/scripts/mdissue-cli.ts close <id>
```

## 规范

1. **执行者** 每个 mdissue 只执行任务并在回复中报告，不能关闭
2. **审查者** 只审查和回复，不关闭 mdissue
3. **规划者** 审查多轮回复后决定是否关闭
4. **禁止** 任何角色在 mdissue 中写"建议优先引用"等推荐建议
