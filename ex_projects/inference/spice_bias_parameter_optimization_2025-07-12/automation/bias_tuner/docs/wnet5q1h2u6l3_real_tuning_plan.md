# WNET5q1h2u6l3 实际微调执行计划

## 📋 计划概述

**目标项目**: WNET5q1h2u6l3
**执行日期**: 2025-07-13
**执行类型**: 首次实际测试（从Mock转向Real）
**主要目标**: 验证微调器实际调用cli.py的功能，优化WaveNet5模型的偏置误差

## 🔍 当前状态分析

### 微调器系统状态

**✅ 已完成组件**:
- 核心架构：分析器、补偿器、执行器、配置管理器
- Mock测试：6次模拟测试，最新测试显示98.1%改善率
- 策略支持：同相位、缩放、自适应、保守四种策略
- 严格验证：零容错路径验证系统
- 配置系统：集中化配置管理

**🔧 关键配置**:
```python
EXECUTION_CONFIG = {
    "inference_timeout": 600,        # 10分钟超时
    "analysis_timeout": 300,         # 5分钟分析超时
    "layer_delay": 2.0,             # 层间延迟2秒
}
```

### WNET5q1h2u6l3项目状态

**📊 当前偏置配置**:
- **Layer 1**: [0.005323, 0.002278, 0.005201, 0.014258, 0.003152, 0.003255]
- **Layer 2**: [0.002181, 0.001301, 0.000932, 0.007533, 0.000669, 0.001903]  
- **Layer 3**: [0.007174, 0.000358, -0.001310, -0.003717, 0.000912, 0.000241]
- **Layer 4**: [0.110052]

**🔍 错误分析现状** (2025-07-13 10:04:02):
- **Layer 1**: mean_error: 4.11e-08, rms_error: 0.0173 ✅ (极小误差)
- **Layer 2**: mean_error: 0.00416, rms_error: 0.0335 ⚠️ (中等误差)
- **Layer 3**: mean_error: 0.00405, rms_error: 0.0335 ⚠️ (中等误差)
- **Layer 4**: mean_error: 0.00148, rms_error: 0.0216 ⚠️ (小误差)
- **Layer 5**: mean_error: -4.827, rms_error: 4.879 🔴 (严重误差)

**🎯 主要问题**: Layer 5的巨大偏置误差（-4.827），但配置中缺少Layer 5的补偿设置

## 📋 执行计划

### Phase 1: 预执行验证 (预计2分钟)

**🔒 严格路径验证**:
```bash
python test_strict_validation.py
```

**验证项目**:
- [x] 项目目录存在性
- [x] 关键文件完整性（config.json, error_analysis.json等）
- [x] JSON格式验证
- [x] 项目名匹配验证

**预期结果**: 所有验证通过，确认学术诚信保护

### Phase 2: 基线测试执行 (预计10分钟)

**🎯 目标**: 验证实际调用cli.py的基本功能

**执行命令**:
```python
from pathlib import Path
from tuner import BiasTuner, CompensationStrategy

# 创建微调器
project_path = Path("/mnt/f/Work/met_nonlinear_worktrees/met_nonlinear_master/projects/WNET5q1h2u6l3")
tuner = BiasTuner(
    project_path,
    strategy=CompensationStrategy.SAME_PHASE,
    python_env="conda run --no-capture-output -n tf26 python",
    dry_run=False
)

# 执行基线测量
baseline = tuner.run_baseline_measurement()
```

**关键监控点**:
- subprocess调用是否成功
- conda环境是否正确
- cli.py是否正常执行
- 错误分析文件是否正确生成
- 执行时间是否在预期范围

### Phase 3: 单层微调测试 (预计15分钟)

**🎯 目标**: 测试单层补偿功能

**执行策略**: 选择Layer 2进行微调（中等误差，安全测试）

**执行命令**:
```python
# 微调Layer 2
results = tuner.tune_sequential(
    layer_order=[2],
    scale_factors={2: 0.8}  # 80%补偿，保守策略
)
```

**预期改善目标**:
- Layer 2: 从 0.00416 → < 0.002 (50%以上改善)

### Phase 4: 多层序列微调测试 (预计30分钟)

**🎯 目标**: 测试多层序列微调功能

**执行策略**: Layer 2 → Layer 3 → Layer 4 序列微调

**执行命令**:
```python
# 序列微调
results = tuner.tune_sequential(
    layer_order=[2, 3, 4],
    scale_factors={2: 0.8, 3: 0.8, 4: 0.5}  # 递减策略
)
```

**预期改善目标**:
- Layer 2: 50%以上改善
- Layer 3: 40%以上改善  
- Layer 4: 30%以上改善

### Phase 5: Layer 5 特殊处理测试 (预计20分钟)

**🎯 目标**: 处理Layer 5的严重偏置问题

**⚠️ 风险分析**: Layer 5误差极大(-4.827)，需要特殊策略

**执行策略**: 
1. 首先分析Layer 5配置缺失原因
2. 手动添加Layer 5补偿配置
3. 使用保守策略进行微调

**执行步骤**:
```python
# 1. 手动添加Layer 5配置
config_manager = tuner.config_manager
current_config = config_manager.get_current_config()
current_config["inference_config"]["bias_compensation"]["layer_bias_adjustments"]["5"] = [-2.4]  # 50%补偿

# 2. 保守微调
results = tuner.tune_sequential(
    layer_order=[5],
    scale_factors={5: 0.5}  # 50%补偿，保守策略
)
```

## 🎯 预期场景与应对方案

### 场景1: 完全成功 (概率: 60%)

**特征**:
- 所有调用成功执行
- cli.py正常运行
- 错误分析文件正确生成
- 偏置误差显著改善

**预期结果**:
- Layer 2-4: 30-50%误差改善
- Layer 5: 至少50%误差改善
- 整体系统稳定性良好

**后续行动**: 生成完整报告，准备生产部署

### 场景2: 部分成功 (概率: 25%)

**特征**:
- 基本调用功能正常
- 部分层微调成功，部分层效果不佳
- 可能出现收敛问题

**可能问题**:
- Layer 5补偿策略需要调整
- 某些层的补偿系数不合适
- 层间相互影响导致收敛困难

**应对策略**:
```python
# 调整补偿策略
tuner.strategy = CompensationStrategy.ADAPTIVE
# 降低补偿系数
scale_factors = {layer: 0.3 for layer in [2, 3, 4, 5]}
```

### 场景3: 调用失败 (概率: 10%)

**特征**:
- subprocess调用失败
- conda环境问题
- cli.py执行错误

**可能原因**:
- conda环境tf26不可用
- Python路径问题
- 权限问题
- 依赖库缺失

**应对策略**:
```python
# 1. 检查conda环境
import subprocess
result = subprocess.run(["conda", "env", "list"], capture_output=True, text=True)
print(result.stdout)

# 2. 测试直接调用
result = subprocess.run([
    "conda", "run", "--no-capture-output", "-n", "tf26", 
    "python", "--version"
], capture_output=True, text=True)

# 3. 回退到mock模式调试
tuner_debug = BiasTuner(project_path, dry_run=True)
```

### 场景4: 配置冲突 (概率: 5%)

**特征**:
- 现有偏置配置与微调器冲突
- JSON格式问题
- 权限或文件锁定问题

**应对策略**:
```python
# 1. 备份原始配置
config_manager.backup_config()

# 2. 重置为基线配置
config_manager.reset_to_baseline()

# 3. 逐步应用补偿
```

## 📊 成功指标

### 技术指标

**🎯 关键性能指标**:
- **执行成功率**: > 90%
- **Layer 2-4改善率**: > 30%
- **Layer 5改善率**: > 50%
- **整体误差改善**: > 40%

**⏱️ 性能指标**:
- **单次cli调用**: < 5分钟
- **完整微调流程**: < 60分钟
- **内存使用**: < 4GB
- **无崩溃执行**: 100%

### 质量指标

**🔒 稳定性指标**:
- 配置文件完整性保持
- 无数据丢失或损坏
- 可重复执行
- 回滚机制有效

**📈 改善效果**:
- RMS误差整体下降
- 最大误差控制在合理范围
- 层间误差平衡改善

## 🛠️ 监控与调试

### 实时监控

**📝 日志监控**:
```python
# 设置详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 监控关键节点
logger.info("开始微调执行")
logger.info(f"当前补偿配置: {compensation_config}")
logger.info(f"执行命令: {cmd}")
```

**📊 进度跟踪**:
- 每层微调开始/结束时间
- 误差改善情况
- subprocess返回状态
- 文件生成状态

### 调试工具

**🔧 调试命令**:
```bash
# 1. 手动测试cli调用
conda run --no-capture-output -n tf26 python cli.py -a WNET5q1h2u6l3

# 2. 检查项目状态
python test_strict_validation.py

# 3. 查看详细日志
tail -f logs/simulation_*/cli.log
```

## 📋 执行检查清单

### 预执行检查

- [ ] conda环境tf26可用
- [ ] WNET5q1h2u6l3项目完整
- [ ] 严格验证通过
- [ ] 备份原始配置
- [ ] 磁盘空间充足（>1GB）
- [ ] 网络连接稳定

### 执行中监控

- [ ] subprocess调用状态
- [ ] cli.py执行进度
- [ ] 错误分析文件生成
- [ ] 内存使用情况
- [ ] 执行时间控制

### 执行后验证

- [ ] 所有预期文件生成
- [ ] 配置文件更新正确
- [ ] 误差改善符合预期
- [ ] 无数据丢失或损坏
- [ ] 生成完整执行报告

## 🚨 风险控制

### 数据安全

**🔒 备份策略**:
- 执行前自动备份config.json
- 保留原始错误分析文件
- 生成回滚脚本

**🛡️ 失败保护**:
- 30秒无响应自动终止
- 异常情况自动回滚
- 完整错误日志记录

### 学术诚信保护

**✅ 严格验证**:
- 零容错路径验证
- 项目名精确匹配
- 文件完整性检查
- 执行状态严格控制

---

**⚠️ 重要提醒**: 这是首次实际测试，所有操作都将被详细记录。如遇任何异常情况，立即停止执行并分析原因。确保学术诚信和数据安全始终是第一优先级。