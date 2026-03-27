# R4: WNET5_EFF2_A1_PS-5_360-07 配置补充

## 任务说明
为 `ex_projects\inference\wnet5-circuit-validation\WNET5_EFF2_A1_PS-5_360-07` 补充 config 配置，包含所有 layer 的配置。

## 模型信息
- **项目路径**: `projects/WNET5_EFF2_A1_PS-5_360-07/`
- **模型类型**: WaveNet5
- **SVF 通道数**: 12
- **Post Dense 通道数**: 14

### 网络层结构
| Layer | 类型 | 通道数 |
|-------|------|--------|
| DIAGIIR | IIR 滤波器 | 12 |
| post_dense_1 | Dense | 14 |
| post_dense_2 | Dense | 14 |
| dense | 输出层 | 1 |

## 创建的配置

### layer1/config.json
```json
{
  "task_info": {
    "task_type": "wnet5-circuit-validation",
    "description": "WNET5电路频率响应理论验证 - Dense层1"
  },
  "model_project_name": "WNET5_EFF2_A1_PS-5_360-07",
  "analysis_layer": 1,
  "frequency_range": {
    "start_freq": 2,
    "stop_freq": 500
  }
}
```
- **analysis_layer**: 1 (对应 post_dense_1)
- **权重通道**: 12→14

### layer2/config.json
```json
{
  "task_info": {
    "task_type": "wnet5-circuit-validation",
    "description": "WNET5电路频率响应理论验证 - Dense层2"
  },
  "model_project_name": "WNET5_EFF2_A1_PS-5_360-07",
  "analysis_layer": 2,
  "frequency_range": {
    "start_freq": 2,
    "stop_freq": 500
  }
}
```
- **analysis_layer**: 2 (对应 post_dense_2)
- **权重通道**: 14→14

### layer4/config.json
```json
{
  "task_info": {
    "task_type": "wnet5-circuit-validation",
    "description": "WNET5电路频率响应理论验证 - Dense层4"
  },
  "model_project_name": "WNET5_EFF2_A1_PS-5_360-07",
  "analysis_layer": 4,
  "frequency_range": {
    "start_freq": 2,
    "stop_freq": 500
  }
}
```
- **analysis_layer**: 4 (对应 dense 输出层)
- **权重通道**: 14→1

**注意**: 该模型只有 2 层 post_dense (post_dense_1, post_dense_2)，没有 post_dense_3，所以没有 layer3。

## 测试结果

### layer1 测试
```
✅ 配置验证通过: wnet5-circuit-validation
✅ 从 JSON 加载 Dense 层 1: kernel=(12, 14), bias=(14,)
✅ WNET5电路验证任务完成
```

### layer2 测试
```
✅ 配置验证通过: wnet5-circuit-validation
✅ 从 JSON 加载 Dense 层 2: kernel=(14, 14), bias=(14,)
[WARNING] SVF通道数 (12) 与权重输入通道数 (14) 不匹配，已循环拓展适配
   原始SVF通道: 12 -> 适配后: 14
✅ WNET5电路验证任务完成
```

### layer4 测试
```
✅ 配置验证通过: wnet5-circuit-validation
✅ 从 JSON 加载 Dense 层 4: kernel=(14, 1), bias=(1,)
[WARNING] SVF通道数 (12) 与权重输入通道数 (14) 不匹配，已循环拓展适配
   原始SVF通道: 12 -> 适配后: 14
✅ WNET5电路验证任务完成
```

## 输出文件
每个 layer 的输出保存在 `ex_projects\inference\wnet5-circuit-validation\WNET5_EFF2_A1_PS-5_360-07\layer{X}\data\` 目录下：

| Layer | 频率响应图 | 分析报告 |
|-------|-----------|---------|
| layer1 | plots/frequency_response.png | reports/analysis_report.json |
| layer2 | plots/frequency_response.png | reports/analysis_report.json |
| layer4 | plots/frequency_response.png | reports/analysis_report.json |

## 结论
所有 layer 配置均已成功创建并通过测试。SVF 通道自动适配功能正常工作，当 SVF 通道数 (12) 与权重通道数 (14) 不匹配时，系统会自动循环拓展适配并输出警告信息。
