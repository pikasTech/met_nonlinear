# 批量实验运行器使用指南

## 功能概述

`batch_run_experiments.py` 是一个强大的批量实验运行工具，支持：
- 📊 串行/并行运行多个实验
- 📄 自动保存stdout/stderr日志
- ⏱️ 实时显示运行状态和进度
- 📋 生成运行总结报告

## 快速使用

### 1. 运行Phase2高优先级实验
```bash
# 运行最有希望的两个实验
python documentation/20250706-wnet5_efficiency_optimization/batch_run_experiments.py --phase2-high

# 或者手动指定
python documentation/20250706-wnet5_efficiency_optimization/batch_run_experiments.py WNET5_EFF2_A1 WNET5_EFF2_B1
```

### 2. 运行所有Phase2实验
```bash
# 串行运行（避免资源竞争）
python documentation/20250706-wnet5_efficiency_optimization/batch_run_experiments.py --phase2

# 并行运行（最多2个同时）
python documentation/20250706-wnet5_efficiency_optimization/batch_run_experiments.py --phase2 --mode parallel --max-parallel 2

# 🚀 并行运行所有6个实验（一键启动）
python documentation/20250706-wnet5_efficiency_optimization/batch_run_experiments.py --phase2-parallel
```

### 3. 自定义实验列表
```bash
# 运行特定的实验
python documentation/20250706-wnet5_efficiency_optimization/batch_run_experiments.py \
    WNET5_EFF2_A1 WNET5_EFF2_B1 WNET5_EFF2_C1
```

## 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `projects` | 要运行的项目名称列表 | `WNET5_EFF2_A1 WNET5_EFF2_A2` |
| `--mode` | 运行模式：serial或parallel | `--mode parallel` |
| `--max-parallel` | 并行模式下最大同时运行数（默认6） | `--max-parallel 3` |
| `--log-dir` | 日志保存目录 | `--log-dir experiment_logs` |
| `--phase1` | 运行所有Phase1实验 | `--phase1` |
| `--phase2` | 运行所有Phase2实验 | `--phase2` |
| `--phase2-high` | 仅运行Phase2高优先级实验 | `--phase2-high` |
| `--phase2-parallel` | 🚀 并行运行所有6个Phase2实验 | `--phase2-parallel` |

## 日志结构

```
logs/
├── WNET5_EFF2_A1/
│   ├── stdout_20250107_120000.log    # 标准输出
│   └── stderr_20250107_120000.log    # 错误输出
├── WNET5_EFF2_A2/
│   ├── stdout_20250107_120100.log
│   └── stderr_20250107_120100.log
└── summary_20250107_130000.json      # 运行总结
```

## 运行示例

### 示例1：串行运行Phase2高优先级
```bash
$ python batch_run_experiments.py --phase2-high

🔬 WaveNet5批量实验运行器
============================================================
📋 实验列表: WNET5_EFF2_A1, WNET5_EFF2_A2
🔄 运行模式: serial
📂 日志目录: /home/ubuntu/met_nonlinear/logs

准备运行 2 个实验，是否继续? (y/n): y

============================================================
🚀 启动实验: WNET5_EFF2_A1
============================================================
📂 工作目录: /home/ubuntu/met_nonlinear
📋 命令: python cli.py -p WNET5_EFF2_A1
📄 标准输出: logs/WNET5_EFF2_A1/stdout_20250107_120000.log
📄 错误输出: logs/WNET5_EFF2_A1/stderr_20250107_120000.log
✅ 进程已启动 (PID: 12345)

⏳ 等待 WNET5_EFF2_A1 完成...
⏱️  运行时间: 1800秒
✅ WNET5_EFF2_A1 完成 (返回码: 0, 耗时: 1800秒)
📊 日志大小: stdout=125,432字节, stderr=0字节
```

### 示例2：并行运行多个实验
```bash
$ python batch_run_experiments.py WNET5_EFF2_A1 WNET5_EFF2_A2 WNET5_EFF2_B1 --mode parallel --max-parallel 2

🔄 并行模式: 最多同时运行 2 个实验
[同时运行EFF2_A1和EFF2_A2，完成后再运行EFF2_B1]
```

### 示例3：一键并行运行所有Phase2实验
```bash
$ python batch_run_experiments.py --phase2-parallel

🔬 WaveNet5批量实验运行器
============================================================
📋 实验列表: WNET5_EFF2_A1, WNET5_EFF2_A2, WNET5_EFF2_B1, WNET5_EFF2_B2, WNET5_EFF2_C1, WNET5_EFF2_C2
🔄 运行模式: parallel
🔢 最大并行数: 6
📂 日志目录: /home/ubuntu/met_nonlinear/logs

准备运行 6 个实验，是否继续? (y/n): y

🔄 并行模式: 最多同时运行 6 个实验
[6个实验同时运行，充分利用计算资源]
```

## 查看日志

### 实时查看日志
```bash
# 查看标准输出
tail -f logs/WNET5_EFF2_A1/stdout_*.log

# 查看错误输出
tail -f logs/WNET5_EFF2_A1/stderr_*.log
```

### 查看运行总结
```bash
cat logs/summary_*.json
```

## 高级用法

### 1. 后台运行
```bash
# 使用nohup后台运行
nohup python batch_run_experiments.py --phase2 > batch_run.log 2>&1 &

# 查看运行状态
tail -f batch_run.log
```

### 2. 筛选失败的实验重新运行
```bash
# 假设EFF2_B1和EFF2_C1失败了
python batch_run_experiments.py WNET5_EFF2_B1 WNET5_EFF2_C1
```

### 3. 自定义日志目录
```bash
# 为不同批次使用不同的日志目录
python batch_run_experiments.py --phase2 --log-dir logs_phase2_round1
```

## 注意事项

1. **资源考虑**：
   - 并行运行会占用更多GPU/CPU资源
   - 默认支持6个并行任务，根据硬件配置调整`--max-parallel`
   - 如果GPU显存不足，建议降低并行数量

2. **日志空间**：长时间运行的实验会产生大量日志，确保有足够磁盘空间

3. **中断恢复**：如果批量运行中断，可以查看日志确定哪些实验未完成，然后重新运行

4. **结果分析**：运行完成后，使用`analyze_efficiency_results.py`分析实验结果

5. **性能优化**：
   - 使用`--phase2-parallel`可以充分利用多GPU环境
   - 6个实验并行运行可以显著减少总体等待时间

## 推荐工作流程

1. **第一步**：运行高优先级实验
   ```bash
   python batch_run_experiments.py --phase2-high
   ```

2. **第二步**：分析结果
   ```bash
   python documentation/20250706-wnet5_efficiency_optimization/analyze_efficiency_results.py
   ```

3. **第三步**：根据结果决定是否运行其他实验
   ```bash
   # 如果需要更多数据点
   python batch_run_experiments.py WNET5_EFF2_B1 WNET5_EFF2_B2
   ```

---

**提示**：第一次使用建议先用单个实验测试，确保环境配置正确。