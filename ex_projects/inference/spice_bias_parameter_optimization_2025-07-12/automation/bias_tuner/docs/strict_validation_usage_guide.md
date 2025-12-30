# 严格偏置验证系统使用指南

## 🔒 核心安全原则

**零容错模式**：严格、单一地校验JSON文件，**禁止任何容错机制**，避免读取错误文件造成极其严重的毁灭性的学术不端问题。

## 📋 系统概述

严格偏置验证系统是为保护学术诚信而设计的零容错路径验证工具，确保：

- ✅ **精确路径验证** - 仅接受精确路径匹配
- ✅ **FAIL FAST机制** - 任何验证失败立即终止
- ✅ **学术诚信保护** - 防止读取错误文件
- ❌ **禁止容错机制** - 无模糊匹配、自动发现
- ❌ **禁止错误恢复** - 无fallback或修复机制

## 🏗️ 系统架构

### 核心组件

```
严格验证系统/
├── utils/path_validator.py      # 零容错路径验证核心
├── core/strict_executor.py      # 严格执行器
├── cli/strict_bias_tuner_cli.py # 零容错CLI工具
├── exceptions.py                # 学术诚信保护异常
└── test_strict_validation.py    # 独立验证测试
```

### 验证流程

```
1. 项目路径严格验证
   ├── 项目目录存在性检查
   ├── 必需文件精确路径验证
   └── 路径权限验证

2. JSON文件完整性验证
   ├── JSON格式严格解析
   ├── 必需键结构验证
   └── 项目名一致性验证

3. 学术诚信保护检查
   ├── 文件内容匹配验证
   ├── 项目标识符验证
   └── 执行准备状态确认
```

## 📁 必需文件清单

基于WNET5q1h2u6l3项目结构，系统验证以下关键文件：

| 文件类型 | 精确路径 | 验证要求 |
|---------|----------|----------|
| **主配置** | `projects/{PROJECT}/config.json` | 🔴 强制验证 |
| **错误分析** | `projects/{PROJECT}/data/inference/error_analysis.json` | 🔴 强制验证 |
| **推理元数据** | `projects/{PROJECT}/data/inference/inference_metadata.json` | 🔴 强制验证 |
| **模型信息** | `projects/{PROJECT}/data/model_info.json` | 🔴 强制验证 |

### 配置文件结构要求

**config.json** 必需结构：
```json
{
    "inference_config": {
        "bias_compensation": {
            "enabled": true,
            "layer_bias_adjustments": {
                "1": [0.005323, 0.002278, ...],
                "2": [0.002181, 0.001301, ...],
                "3": [0.007174, 0.000358, ...],
                "4": [0.110052]
            }
        }
    },
    "use_model": "WaveNet5"
}
```

## 🛠️ 使用方法

### 1. 独立验证测试

```bash
# 运行独立验证测试脚本
python test_strict_validation.py
```

**输出示例：**
```
🔒 [测试] INFO: ======================================================================
🔒 [测试] INFO: 🔒 开始严格验证测试: WNET5q1h2u6l3
🔒 [测试] INFO: ======================================================================
🔒 [测试] INFO: ✅ 项目目录存在: /path/to/projects/WNET5q1h2u6l3
🔒 [测试] INFO: ✅ config 文件存在: .../config.json
🔒 [测试] INFO: ✅ error_analysis 文件存在: .../error_analysis.json
🔒 [测试] INFO: ✅ inference_metadata 文件存在: .../inference_metadata.json
🔒 [测试] INFO: ✅ model_info 文件存在: .../model_info.json
🔒 [测试] INFO: ✅ 阶段1: 路径验证通过
🔒 [测试] INFO: ✅ 阶段2: JSON完整性验证通过
🔒 [测试] INFO: 📊 偏置补偿已启用，配置层数: 4
🔒 [测试] INFO: 🎉 严格验证测试完全成功！
```

### 2. CLI工具使用（待修复导入问题）

```bash
# 仅验证模式
python cli/strict_bias_tuner_cli.py WNET5q1h2u6l3 \
    --root /path/to/project/root \
    --validate-only

# 执行模式（Mock）
python cli/strict_bias_tuner_cli.py WNET5q1h2u6l3 \
    --root /path/to/project/root \
    --execute --mock

# 执行模式（实际调用cli.py）
python cli/strict_bias_tuner_cli.py WNET5q1h2u6l3 \
    --root /path/to/project/root \
    --execute
```

### 3. Python API使用

```python
from utils.path_validator import StrictPathValidator, StrictPathChecker

# 创建严格验证器
validator = StrictPathValidator(
    project_name="WNET5q1h2u6l3",
    project_root="/path/to/project/root"
)

# 创建检查器
checker = StrictPathChecker(validator)

# 执行验证
try:
    success = checker.pre_execution_check()
    if success:
        print("✅ 严格验证通过")
        validated_paths = validator.get_validated_paths()
    else:
        print("❌ 严格验证失败")
except Exception as e:
    print(f"❌ 验证异常: {e}")
```

## ⚠️ 安全保护机制

### 1. 零容错验证

- **精确匹配**: 文件路径必须完全匹配，不允许近似
- **立即失败**: 任何验证错误立即终止执行
- **无自动修复**: 不提供任何路径猜测或自动发现

### 2. 学术诚信保护

```python
# 项目名严格匹配验证
if data["project_name"] != self.project_name:
    raise ValueError(
        f"项目名不匹配\n"
        f"期望: {self.project_name}\n"
        f"实际: {data['project_name']}\n"
        f"严格验证失败 - 学术不端风险阻止"
    )
```

### 3. 异常处理层次

```
AcademicIntegrityError (学术诚信保护)
├── StrictValidationError (严格验证错误)
│   ├── PathValidationError (路径验证错误)
│   ├── ConfigLoadError (配置加载错误)
│   ├── ErrorAnalysisLoadError (错误分析加载错误)
│   └── ExecutionStateError (执行状态错误)
└── PathSecurityError (路径安全错误)
    └── ProjectDiscoveryError (项目发现错误)
```

## 🔧 cli.py集成

### subprocess调用方式

严格执行器通过subprocess调用cli.py，**无需修改cli.py**：

```python
# 构建严格的cli.py调用命令
cmd = [
    "conda", "run", "--no-capture-output", "-n", "tf26",
    "python", "cli.py", "-a", self.project_name
]

# 执行命令 - 严格模式
result = subprocess.run(
    cmd,
    cwd=work_dir,
    capture_output=True,
    text=True,
    timeout=300  # 5分钟超时
)
```

### 环境要求

- **Python环境**: conda tf26环境
- **工作目录**: 项目根目录
- **调用参数**: `-a {PROJECT_NAME}` 用于分析模式

## 📊 验证报告示例

### 成功案例
```
======================================================================
🔒 严格验证报告: WNET5q1h2u6l3
======================================================================
✅ 项目路径验证: 通过
✅ JSON文件完整性: 通过
✅ 结构一致性验证: 通过
✅ 学术诚信检查: 通过

🔒 严格验证状态: 全部通过
🔒 执行准备状态: 就绪
======================================================================
```

### 失败案例
```
======================================================================
🔒 严格验证报告: WNET5q1h2u6l3
======================================================================
❌ 严格验证状态: 失败
❌ 执行准备状态: 被阻止
⚠️  学术不端风险规避
======================================================================
```

## 🚨 常见错误及解决

### 1. 文件不存在错误

```
FileNotFoundError: 必需文件不存在: /path/to/config.json
文件类型: config
严格验证失败 - 学术不端风险阻止
```

**解决方案**: 确保所有必需文件存在于精确路径

### 2. JSON格式错误

```
ValueError: JSON格式错误: /path/to/config.json
错误详情: Expecting ',' delimiter: line 10 column 5
严格验证失败 - 学术不端风险阻止
```

**解决方案**: 修复JSON格式错误

### 3. 项目名不匹配

```
ValueError: 项目名不匹配
期望: WNET5q1h2u6l3
实际: WNET5q1h2u6l4
严格验证失败 - 学术不端风险阻止
```

**解决方案**: 确保项目名完全匹配

## 📈 性能特点

- **快速验证**: 平均验证时间 < 1秒
- **内存效率**: 最小内存占用，仅加载必要文件
- **零延迟**: FAIL FAST机制避免不必要的处理
- **完全隔离**: 不影响cli.py现有功能

## 🔐 安全保证

1. **防止文件混淆**: 严格项目名验证
2. **防止路径错误**: 精确路径匹配
3. **防止格式错误**: JSON完整性验证
4. **防止执行错误**: 预验证机制
5. **学术诚信保护**: 全流程安全机制

---

**⚠️ 重要提醒**: 此系统专为学术诚信保护设计，任何验证失败都会立即终止操作。请确保所有文件路径和内容准确无误后再使用。