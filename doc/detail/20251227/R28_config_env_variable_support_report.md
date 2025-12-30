# R28 配置路径环境变量支持修改报告

## 任务目标

让 `ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1\config.json` 中的 `compare_with_experiment` 路径支持环境变量 `${MET_DATA_BASE}` 格式，以便在不同机器上运行。

## 修改内容

### 1. 添加环境变量替换函数

**文件**: `visualization/wnet5_circuit_validator.py`

**新增函数** (第24-29行):
```python
def _expand_env_vars(path: str) -> str:
    """展开路径中的环境变量，支持 ${VAR_NAME} 和 $VAR_NAME 格式"""
    if not path:
        return path
    expanded = os.path.expandvars(path)
    return Path(expanded).as_posix() if '/' in expanded or '\\' in expanded else expanded
```

### 2. 修改路径字段读取逻辑

**文件**: `visualization/wnet5_circuit_validator.py`

**修改位置**: `__init__` 方法 (第56-66行)

**修改前**:
```python
self.experiment_path = config.get('compare_with_experiment')
...
self.exp_data_dir = self.experiment_comparison.get('experiment_data_dir')
self.selftest_file = self.experiment_comparison.get('selftest_file')
```

**修改后**:
```python
# 支持环境变量替换，如 ${MET_DATA_BASE}/data/xxx.xlsx
self.experiment_path = _expand_env_vars(config.get('compare_with_experiment'))
...
# 支持环境变量替换
self.exp_data_dir = _expand_env_vars(self.experiment_comparison.get('experiment_data_dir'))
self.selftest_file = _expand_env_vars(self.experiment_comparison.get('selftest_file'))
```

### 3. 更新配置文件

**文件**: `ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1\config.json`

**修改前**:
```json
"compare_with_experiment": "F:\\BaiduSyncdisk\\data\\SVF-NET-CIRCUIT\\20251201-SVFNET-Dense1-3层.xlsx"
```

**修改后**:
```json
"compare_with_experiment": "${MET_DATA_BASE}/data/SVF-NET-CIRCUIT/20251201-SVFNET-Dense1-3层.xlsx"
```

## 支持的路径字段

以下配置文件中的路径字段现在支持环境变量替换：

| 字段 | 位置 | 说明 |
|------|------|------|
| `compare_with_experiment` | 顶层 | 旧的单文件对比配置（向后兼容） |
| `experiment_data_dir` | `experiment_comparison` | 实验数据目录（C05新增） |
| `selftest_file` | `experiment_comparison` | 自测试文件路径（C05新增） |

## 使用方法

### Windows
```cmd
set MET_DATA_BASE=F:\BaiduSyncdisk
python cli.py ep ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1
```

### Linux/Mac
```bash
export MET_DATA_BASE=/home/user/BaiduSyncdisk
python cli.py ep ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer1
```

### 配置文件示例
```json
{
  "compare_with_experiment": "${MET_DATA_BASE}/data/SVF-NET-CIRCUIT/20251201-SVFNET-Dense1-3层.xlsx",
  "experiment_comparison": {
    "experiment_data_dir": "${MET_DATA_BASE}/data/experiment",
    "selftest_file": "${MET_DATA_BASE}/data/selftest.xlsx"
  }
}
```

## 向后兼容性

- 如果路径中不包含环境变量格式，函数直接返回原路径
- 如果环境变量未设置，`os.path.expandvars()` 会保持原样返回（如 `${MET_DATA_BASE}` 不变）
- 旧的硬编码路径配置仍然正常工作

## 修改文件清单

| 文件 | 修改类型 |
|------|----------|
| `visualization/wnet5_circuit_validator.py` | 添加函数 + 修改3处路径读取 |
| `ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1\config.json` | 更新路径格式 |

## 验证建议

1. 设置环境变量后运行:
   ```cmd
   set MET_DATA_BASE=F:\BaiduSyncdisk
   python cli.py ep ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1
   ```
2. 验证日志中显示的 `experiment_path` 已正确展开
3. 验证程序能正常读取实验数据文件
