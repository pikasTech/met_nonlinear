# WaveNet5效率优化实验计划 - 基于E05的参数精简优化

## 1. 背景分析

### E05配置性能基准
- 别名抑制率(ASR): 90.3%
- 总参数量: 8,641
- 参数效率: 10.45 ASR/千参数

### E05配置详解
```json
{
    "epoch_train": 30000,
    "step_per_epoch": 1,
    "learning_rate": 0.02,
    "use_model": "WaveNet5",
    "dataset_type": "Alias",
    "data_path": "data/ALIA",
    "kernal_units": 6,  // IIR滤波器数量
    "use_best_val_weights": true,
    "auto_lr_decay_steps": 1000,
    "model_subcfg": {
        "init_center_freqs": [8, 25, 50, 85, 120, 180],  // 6个中心频率
        "init_quality_factors": [1.5, 2.0, 2.5, 3.0, 4.0, 5.0],  // 6个Q值
        "post_dense": true,
        "post_dense_activation": "relu",
        "post_dense_units": 16,
        "post_dense_layers": 3,
        "use_dense_bias": true
    },
    "target_sweep": 0,
    "use_predict_features": true
}
```

### 关键配置参数说明
1. **kernal_units**: IIR滤波器数量，必须与init_center_freqs和init_quality_factors的长度一致
2. **init_center_freqs**: 每个IIR滤波器的中心频率(Hz)
3. **init_quality_factors**: 每个IIR滤波器的Q值(品质因数)
4. **post_dense_layers**: Dense层的层数
5. **post_dense_units**: 每个Dense层的单元数
6. **use_dense_bias**: 是否在Dense层使用偏置项

## 2. 优化目标

- **主要目标**: 降低总参数量至5000以下
- **性能约束**: 保持ASR ≥ 80%
- **优化方法**: 仅通过修改config.json实现，不改动任何代码

## 3. 参数量估算公式

基于E05的实际参数量(8,641)，推算各部分参数：
- IIR滤波器部分: 约1,000-2,000参数
- Dense层部分: 约6,641-7,641参数
  - 第1层: input_dim × 16 + 16 (bias)
  - 第2层: 16 × 16 + 16 = 272
  - 第3层: 16 × output_dim + output_dim

## 4. 优化实验方案（6个核心实验）

基于控制变量原则，每个实验仅修改E05基线的一个或相关的参数组。

### 实验1: 减少Dense层数（保守方案）
- **名称**: EFF_A1
- **预计参数量**: ~7,000
- **修改内容**: 将Dense层从3层减少到2层
- **配置修改**:
  ```json
  "post_dense_layers": 2  // 原值: 3
  ```

**预期情况分析**:
- **情况A (轻微影响)**: ASR 85-90%，参数效率提升20% → 结论：减少一层是可行的优化
- **情况B (性能保持)**: ASR 88-92%，参数效率提升25% → 结论：E05存在冗余，2层足够
- **情况C (显著下降)**: ASR 75-85% → 结论：3层是必要的最小深度
- **情况D (崩溃)**: ASR <75% → 结论：网络深度对任务至关重要

### 实验2: 减少Dense单元数（中等方案）
- **名称**: EFF_A2  
- **预计参数量**: ~5,500
- **修改内容**: 将每个Dense层的单元数从16减少到8
- **配置修改**:
  ```json
  "post_dense_units": 8  // 原值: 16
  ```

**预期情况分析**:
- **情况A (影响可接受)**: ASR 82-88%，参数效率提升40% → 结论：宽度可以适度减少
- **情况B (性能下降)**: ASR 75-82% → 结论：16单元是性能和效率的平衡点
- **情况C (严重退化)**: ASR <75% → 结论：非线性建模能力严重不足
- **情况D (意外稳定)**: ASR >88% → 结论：E05过度参数化，8单元已足够

### 实验3: 4个IIR滤波器（频率优化）
- **名称**: EFF_B1
- **预计参数量**: ~6,500
- **修改内容**: 将IIR滤波器从6个减少到4个
- **配置修改**:
  ```json
  "kernal_units": 4,
  "model_subcfg": {
      "init_center_freqs": [15, 40, 80, 140],
      "init_quality_factors": [2.0, 2.5, 3.0, 3.5]
  }
  ```

**预期情况分析**:
- **情况A (频率充分)**: ASR 85-90% → 结论：4个滤波器能覆盖主要频率特征
- **情况B (轻微退化)**: ASR 80-85% → 结论：某些频率细节丢失但整体可接受
- **情况C (明显不足)**: ASR 70-80% → 结论：6个滤波器是必要的频率分辨率
- **情况D (频率关键)**: ASR <70% → 结论：IIR滤波器数量是性能瓶颈

### 实验4: 4 IIR + 3层8单元（平衡优化）
- **名称**: EFF_C1
- **预计参数量**: ~4,200
- **修改内容**: 同时减少IIR滤波器和Dense单元数
- **配置修改**:
  ```json
  "kernal_units": 4,
  "model_subcfg": {
      "init_center_freqs": [15, 40, 80, 140],
      "init_quality_factors": [2.0, 2.5, 3.0, 3.5],
      "post_dense_units": 8
  }
  ```

**预期情况分析**:
- **情况A (协同优化)**: ASR 80-85% → 结论：平衡削减是可行的策略
- **情况B (勉强达标)**: ASR 78-82% → 结论：接近80%目标，可以接受
- **情况C (双重影响)**: ASR 70-78% → 结论：同时削减两部分影响过大
- **情况D (超预期)**: ASR >85% → 结论：找到了更优的参数配比

### 实验5: 4 IIR + 2层12单元（结构重组）
- **名称**: EFF_C2
- **预计参数量**: ~4,500
- **修改内容**: 减少层数但增加宽度
- **配置修改**:
  ```json
  "kernal_units": 4,
  "model_subcfg": {
      "init_center_freqs": [15, 40, 80, 140],
      "init_quality_factors": [2.0, 2.5, 3.0, 3.5],
      "post_dense_layers": 2,
      "post_dense_units": 12
  }
  ```

**预期情况分析**:
- **情况A (结构优化)**: ASR 82-88% → 结论：浅而宽的结构更高效
- **情况B (性能相当)**: ASR 78-82% → 结论：深度和宽度可以互换
- **情况C (深度重要)**: ASR <78% → 结论：3层深度不可替代
- **情况D (意外发现)**: ASR >88% → 结论：找到了更优的网络结构

### 实验6: 3 IIR + 1层32单元（极简架构）
- **名称**: EFF_D1
- **预计参数量**: ~3,000
- **修改内容**: 激进的结构简化
- **配置修改**:
  ```json
  "kernal_units": 3,
  "model_subcfg": {
      "init_center_freqs": [20, 60, 120],
      "init_quality_factors": [2.5, 3.5, 4.5],
      "post_dense_layers": 1,
      "post_dense_units": 32
  }
  ```

**预期情况分析**:
- **情况A (极简有效)**: ASR 75-82% → 结论：单层宽网络可以达到目标
- **情况B (勉强及格)**: ASR 70-75% → 结论：接近性能下限
- **情况C (结构崩溃)**: ASR <70% → 结论：过度简化导致性能崩溃
- **情况D (惊喜)**: ASR >82% → 结论：发现了极高效的架构

## 5. 实验执行策略

### 实验优先级

#### 第一批次（高优先级）
1. **EFF_A1** - 减少Dense层数（最保守，验证可行性）
2. **EFF_A2** - 减少Dense单元数（中等风险，潜力大）
3. **EFF_B1** - 4个IIR滤波器（验证频率敏感性）

#### 第二批次（根据第一批结果决定）
4. **EFF_C1** - 4 IIR + 8单元（如果A2和B1都有效）
5. **EFF_C2** - 结构重组（如果需要新思路）

#### 第三批次（可选）
6. **EFF_D1** - 极简架构（仅在前面都成功时尝试）

### 决策树

```
如果 EFF_A1 ASR > 85%:
    → 继续 EFF_A2
    如果 EFF_A2 ASR > 82%:
        → 层数和单元数都可减少
        → 执行 EFF_C1 验证组合效果
    否则:
        → 单元数是瓶颈
        → 执行 EFF_B1 探索其他方向
否则:
    → 层数是关键
    → 直接执行 EFF_B1 和 EFF_C2
```

### 执行步骤

1. **批量创建实验目录**
   ```bash
   # 第一批次
   for exp in EFF_A1 EFF_A2 EFF_B1; do
       mkdir -p projects/WNET5_$exp
       cp projects/WNET5_RealAlias_E05/config.json projects/WNET5_$exp/
   done
   ```

2. **配置文件生成脚本**
   ```python
   # generate_eff_configs.py
   import json
   import os
   
   # 读取E05基准配置
   with open('projects/WNET5_RealAlias_E05/config.json', 'r') as f:
       base_config = json.load(f)
   
   # 实验配置定义
   experiments = {
       'EFF_A1': {
           'model_subcfg': {'post_dense_layers': 2}
       },
       'EFF_A2': {
           'model_subcfg': {'post_dense_units': 8}
       },
       'EFF_B1': {
           'kernal_units': 4,
           'model_subcfg': {
               'init_center_freqs': [15, 40, 80, 140],
               'init_quality_factors': [2.0, 2.5, 3.0, 3.5]
           }
       }
   }
   
   # 生成配置文件
   for exp_name, changes in experiments.items():
       config = base_config.copy()
       # 深度更新配置
       for key, value in changes.items():
           if key == 'model_subcfg':
               config['model_subcfg'].update(value)
           else:
               config[key] = value
       
       # 保存配置
       output_path = f'projects/WNET5_{exp_name}/config.json'
       with open(output_path, 'w') as f:
           json.dump(config, f, indent=4)
   ```

3. **运行第一批实验**
   ```bash
   python cli.py -p WNET5_EFF_A1
   python cli.py -p WNET5_EFF_A2  
   python cli.py -p WNET5_EFF_B1
   ```

4. **结果跟踪表格**
   
   | 实验 | 参数量 | ASR(%) | 效率 | 决策 |
   |------|--------|---------|------|------|
   | E05 | 8,641 | 90.3 | 10.45 | 基准 |
   | EFF_A1 | ~7,000 | - | - | - |
   | EFF_A2 | ~5,500 | - | - | - |
   | EFF_B1 | ~6,500 | - | - | - |

## 6. 成功标准与风险控制

### 量化成功标准
- **突破性成功**: ASR ≥ 85%，参数量 < 4,000，效率 > 20 ASR/千参数
- **显著成功**: ASR ≥ 82%，参数量 < 5,000，效率 > 16 ASR/千参数
- **达标成功**: ASR ≥ 80%，参数量 < 6,000，效率 > 13 ASR/千参数
- **可接受**: ASR ≥ 78%，参数量 < 7,000，效率 > 11 ASR/千参数

### 风险控制措施

1. **渐进式实验**
   - 从保守方案开始，根据结果决定是否继续
   - 设置ASR=78%为硬性下限，低于此值立即停止

2. **早停策略**
   - 如果第一批次全部失败（ASR<80%），重新评估目标
   - 如果找到ASR>85%且参数<5000的配置，可提前结束

3. **回退方案**
   - 保留所有中间结果，可以选择次优但稳定的配置
   - 如果极简方案失败，选择最佳的效率/性能平衡点

### 项目交付标准

#### 最低交付要求
- 至少一个配置达到 ASR ≥ 80%
- 参数量相比E05减少至少30%
- 完整的实验报告和分析

#### 理想交付成果
- 找到ASR ≥ 82%且参数量 < 5,000的配置
- 参数效率提升50%以上
- 明确的参数-性能权衡曲线

## 7. 预期成果与后续计划

### 预期关键发现
1. **参数效率曲线**: 确定ASR与参数量的关系
2. **架构洞察**: 理解WaveNet5在低参数区的表现
3. **优化边界**: 找到当前架构的效率极限

### 后续优化方向
- 如果成功达到目标，可以考虑：
  - 知识蒸馏进一步压缩
  - 结构化剪枝精确控制参数
  - 量化感知训练减少精度损失

- 如果未达到目标，需要：
  - 重新评估80% ASR的合理性
  - 考虑架构级别的创新
  - 探索其他效率优化技术