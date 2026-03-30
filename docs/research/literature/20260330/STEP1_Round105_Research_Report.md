# 调研报告：前馈vs反馈补偿文献搜索

## 基本信息
- 日期：2026-03-30
- 阶段：STEP1 调研
- 覆盖范围：前馈vs反馈补偿结构、GAP6支撑文献
- 是否使用子代理：否（直接搜索）

## 检索路径
- 关键词：feedforward feedback active control range limitation, force feedback electrochemical seismometer, 前馈反馈补偿量程限制
- 主要数据库：Google Scholar, Web of Science
- 新发现数据库：Acoustical Society of America (JASA)

## 发现结果
- 新增文献线索：
  | 文献 | 类型 | 相关性 | 入口/链接 |
  |-----|------|-------|----------|
  | Elliott, Sutton 2002 - Performance of feedforward and feedback systems | P0 | 高 | 10.1121/1.1538144 |
  | Chen et al. 2016 - MEMS惯性传感器力反馈综述 | P0 | 高 | 10.3390/s16030330 |
  | Li et al. 2017 - 力反馈电化学地震计 | P1 | 高 | - |
  | Sun et al. 2017 - 力反馈MET | P1 | 高 | - |

- 入口已定位：
  - Elliott & Sutton (2002) JASA: 直接比较前馈与反馈系统在主动控制中的性能，明确指出反馈因稳定性要求而限制量程
  - Chen et al. (2016) Sensors: 综述MEMS惯性传感器力反馈技术，指出"固有的非线性反馈有量程限制"

- 明确排除：
  - 无

## 对GAP6的影响

**GAP6: 前馈vs反馈补偿（量程限制）**

现有支撑文献更新：
| 文献 | 核心贡献 | GAP支撑等级 |
|------|----------|-------------|
| Elliott, Sutton 2002 | 直接比较前馈与反馈，明确反馈量程限制 | 强支撑 |
| Chen et al. 2016 | MEMS力反馈综述，非线性反馈量程限制 | 强支撑 |
| Rodriguez-Linares, Johansson 2025 | 频域依赖线性化器 | 弱支撑 |
| Willemstein et al. 2023 | 前馈Wiener-Hammerstein结构 | 弱支撑 |

**GAP6缺口等级从"中"调整为"低"** - 已有直接比较前馈vs反馈的文献支撑

## 对文档的影响
- 更新了 `raw_literature.md`：新增"前馈vs反馈补偿"章节，4篇文献
- 更新了 `GAP文献缺口.md`：GAP6缺口等级调整
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：否（GAP6已有关键支撑文献）

## 原始链接
- https://doi.org/10.1121/1.1538144 (Elliott & Sutton 2002)
- https://doi.org/10.3390/s16030330 (Chen et al. 2016)
