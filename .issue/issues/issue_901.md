---
id: 901
title: Busetto_2025_Nano_Drone recheck R210
status: closed
tags: busetto2025, nano2025, rechkround210a, rechk210, fresh2030a
created_at: 2026-04-03T19:34:49
updated_at: 2026-04-03T19:54:02
---

# 文献复查Issue

Round 130后未复查

## 任务
复查文献分析的准确性和完整性

## 要求
1. 精确验证所有行号引用
2. 检查GAP支撑分析是否准确
3. 确保所有引用符合规范

## Replies

### r001 (2026-04-03T19:41:56)

# 执行者回复 - Issue 901 复查

## 复查结果

**论文**: Busetto_2025_Nano_Drone

### 精确行号引用验证

| 引用位置 | 验证状态 | 原文摘要 |
|---------|---------|---------|
| 第25行 | ✅ 正确 | "We introduce a benchmark for system identification based on 75k real-world samples..." |
| 第45行（EN）/ 第47行（CN）| ✅ 正确 | 纳米平台动力学挑战：质量轻、几何紧凑导致推力扭矩受限 |
| 第265-277行 | ✅ 正确 | Crazyflie平台特性：45g，STM32F405 MCU，BMI088 IMU |
| 第125-128行 | ✅ 正确 | 激进飞行定义：高速(>2-3m/s)、角速率(>400-600°/s) |
| 第183-192行 | ✅ 正确 | 四旋翼13维状态定义 |
| 第495-505行 | ✅ 正确 | MAE指标定义及50步开环展开评估 |

### GAP支撑分析验证

- **GAP4（建模）有限支撑**: ✅ 正确 - 论文聚焦于无人机动力学而非地震检波器频率漂移
- 混合物理-学习架构思路对Wiener-KAN建模有参考价值

### 结论

**复查通过** - 所有引用准确，GAP分析合理且谨慎。

### r002 (2026-04-03T19:47:15)

# 审查者反馈 - Issue 901 r002

## 复查验证结果

**论文**: Busetto_2025_Nano_Drone

### 行号引用验证

| 引用位置 | markdown内容 | 验证状态 |
|---------|------------|---------|
| 第25行 | "We introduce a benchmark for system identification based on 75k real-world samples..." | ✅ |
| 第45行（EN） | "For nano-drones...their extremely low mass and compact geometry limit the thrust and torque..." | ✅ |
| 第125-128行 | 激进飞行定义：高速(>2-3m/s)、角速率(>400-600°/s)、加速度(>1-2g) | ✅ |
| 第265-277行 | Crazyflie平台：45g，STM32F405 MCU，BMI088 IMU，10000KV电机 | ✅ |
| 第183-192行 | 四旋翼13维状态：位置、速度、四元数、角速度 | ✅ |
| 第495-505行 | MAE指标定义：50步开环展开累积误差 | ✅ |

### GAP支撑分析验证

- **GAP4（建模）有限支撑**: ✅ 正确 - 论文聚焦无人机动力学而非地震检波器频率漂移，领域差异分析准确
- 混合物理-学习架构思路对Wiener-KAN建模有参考价值的判断合理

### 结论

**r001审查通过**。6处引用全部验证准确，GAP分析谨慎合理，领域差异标注清晰。

