# 日志过滤系统使用指南

## 功能概述

新的日志过滤系统解决了批量SPICE仿真时产生过多终端日志的问题。系统特点：

- **完整记录**：所有日志都保存在文件中
- **智能过滤**：终端只显示重要信息
- **可配置**：通过YAML配置文件控制过滤规则

## 配置文件

配置文件：`logging_filter.yaml`

### 主要配置项

```yaml
# 模块级别过滤
module_filters:
  spicelib: ERROR           # 只显示ERROR及以上
  tensorflow: WARNING       # 只显示WARNING及以上
  matplotlib: WARNING       # 只显示WARNING及以上
  h5py: ERROR              # 只显示ERROR及以上

# 强制显示关键词（无论级别）
always_show_keywords:
  - "错误"
  - "失败" 
  - "项目"
  - "完成"
  - "成功"

# 强制隐藏关键词
always_hide_keywords:
  - "Creating converter from"
  - "Using fontManager instance"
  - "matplotlib data path"
```

## 过滤效果对比

### 过滤前（原始输出）
```
RunTask #1:: Starting simulation 1: temp/spice_output/tmp0.net
RunTask #1:Simulation Successful. Time elapsed: 00.0120 secs
RunTask #1:Simulation Finished. Calling...dummy_callback(rawfile, logfile)
RunTask #1:Callback Finished. Time elapsed: 00.0000 secs
File contains 7 traces, reading 7.
RunTask #1:: Starting simulation 2: temp/spice_output/tmp1.net
... (大量重复信息)
```

### 过滤后（终端输出）
```
❌ spicelib.RunTask - ERROR - 这是一个ERROR级别的消息，应该显示
⚠️  tensorflow - WARNING - 这是TensorFlow的警告消息  
✅ cli - INFO - 推理完成
❌ cli - ERROR - 这是项目错误，应该显示
```

## 使用方法

### 1. 基本使用
```bash
# 使用wrapper自动加载过滤配置
./cli -i WNET5q0.5h2u6l4
```

### 2. 自定义配置
修改 `logging_filter.yaml` 后重新运行即可。

### 3. 临时禁用过滤
如果需要看到所有日志，可以临时重命名配置文件：
```bash
mv logging_filter.yaml logging_filter.yaml.bak
./cli -i WNET5q0.5h2u6l4
mv logging_filter.yaml.bak logging_filter.yaml
```

## 配置详解

### 日志级别（从低到高）
- `DEBUG` - 调试信息
- `INFO` - 一般信息  
- `WARNING` - 警告
- `ERROR` - 错误
- `CRITICAL` - 严重错误

### 模块过滤示例

```yaml
module_filters:
  # 完全隐藏spicelib的INFO和WARNING
  spicelib: ERROR
  
  # 显示tensorflow的WARNING和ERROR  
  tensorflow: WARNING
  
  # 保持项目模块的所有INFO消息
  cli: INFO
  inference.manager: INFO
```

### 关键词过滤

**always_show_keywords**: 包含这些词的消息总是显示
- 适用于重要状态消息："完成"、"成功"、"失败"

**always_hide_keywords**: 包含这些词的消息总是隐藏  
- 适用于过于详细的库内部信息

## 故障排除

### 问题：某些重要消息被过滤了
**解决**：在 `always_show_keywords` 中添加相关关键词

### 问题：仍有太多详细日志
**解决**：提高相关模块的过滤级别（INFO→WARNING→ERROR）

### 问题：YAML文件格式错误
**解决**：检查缩进和语法，或删除配置文件使用默认规则

## 性能影响

- **几乎无影响**：过滤只影响终端显示，不影响程序执行
- **日志完整性**：所有信息仍完整保存在日志文件中
- **实时响应**：重要错误和警告立即显示

## 日志文件位置

完整日志始终保存在：
```
logs/{项目名}_{任务类型}_{时间戳}.log
```

例如：
```
logs/WNET5q0.5h2u6l4_inference_20250711_011406.log
```