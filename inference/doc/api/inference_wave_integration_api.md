# 推理Wave集成API设计文档

## 概述

本文档描述了推理功能集成Wave数据源的API设计，基于简化直接查找策略的实现。

## 核心修改

### 1. InferenceManager._find_input_file() 简化

```python
def _find_input_file(self) -> str:
    """
    查找推理输入文件
    只查找 data/wave_output/dataset_{TYPE}_output_original.wave
        
    Returns:
        str: wave文件路径
        
    Raises:
        FileNotFoundError: 文件不存在时报错并提示使用 -w 生成
    """
    # 构建目标文件路径
    wave_output_dir = os.path.join(self.project_path, "data", "wave_output")
    dataset_type = self.config.dataset_type
    target_file = f"dataset_{dataset_type}_output_original.wave"
    target_path = os.path.join(wave_output_dir, target_file)
    
    # 检查文件是否存在
    if os.path.exists(target_path):
        relative_path = os.path.relpath(target_path, self.project_path)
        self.logger.info(f"找到推理输入文件: {relative_path}")
        print(f"✓ 使用wave文件: {relative_path}")
        return target_path
    
    # 文件不存在，生成详细错误信息
    project_name = os.path.basename(self.project_path)
    error_msg = f"未找到推理输入文件: {target_file}\n"
    
    if not os.path.exists(wave_output_dir):
        error_msg += f"\nwave输出目录不存在: {wave_output_dir}\n"
    else:
        wave_files = [f for f in os.listdir(wave_output_dir) if f.endswith('.wave')]
        if wave_files:
            error_msg += f"\nwave输出目录中找到以下文件:\n"
            for f in wave_files:
                error_msg += f"  - {f}\n"
            error_msg += f"\n但需要的是: {target_file}\n"
    
    error_msg += f"\n请先运行以下命令生成wave数据:\n"
    error_msg += f"  python cli.py -w {project_name}\n"
    
    raise FileNotFoundError(error_msg)
```

### 2. 调用处修改

```python
# run_inference 方法
def run_inference(self, force: bool = False):
    """运行推理"""
    try:
        input_wave = self._find_input_file()  # 删除参数
    except FileNotFoundError as e:
        print(f"\n❌ 推理失败")
        print(str(e))
        return

# _generate_inference_data 方法
def _generate_inference_data(self, data_dir: str):
    """生成推理数据"""
    input_wave = self._find_input_file()  # 删除参数
    # ... 继续处理
```

### 3. 删除的配置项

以下配置项不再需要：
- `inference_input_path` - 不再支持自定义输入路径
- `inference_auto_detect` - 始终使用固定路径
- `inference_use_output` - 始终使用output_original

## 配置示例

### 默认配置（自动使用output_original）

```json
{
    "dataset_type": "MET",
    "inference_auto_detect": true,
    "inference_use_output": true
}
```

### 使用input文件

```json
{
    "dataset_type": "MET", 
    "inference_auto_detect": true,
    "inference_use_output": false
}
```

### 使用传统方式

```json
{
    "dataset_type": "MET",
    "inference_auto_detect": false,
    "inference_input_path": "inference/temp/dataset_input.wave"
}
```

## 命令行使用

```bash
# 基础使用（自动检测）
python cli.py -i PROJECT_NAME

# 强制重新推理
python cli.py -i PROJECT_NAME -f

# 指定输入文件（覆盖自动检测）
python cli.py -i PROJECT_NAME --input custom.wave
```

## 错误处理

### 场景1：Wave文件未生成

```
错误：未找到推理输入文件
建议：请先运行 python cli.py -w PROJECT_NAME 生成wave数据
```

### 场景2：数据集类型不匹配

```
警告：期望文件 dataset_MET_output_original.wave 不存在
找到以下wave文件：
  - dataset_AliasSimu_output_original.wave
建议：检查config.json中的dataset_type配置
```

### 场景3：回退到默认路径

```
信息：类型化wave文件不存在，尝试默认路径
使用文件：inference/temp/dataset_input.wave
```

## 测试要点

1. **自动检测测试**
   - 存在类型化文件时的行为
   - 不存在类型化文件时的回退
   
2. **配置测试**
   - inference_use_output的切换
   - inference_auto_detect的开关
   
3. **错误场景测试**
   - 无任何wave文件
   - 类型不匹配
   - 权限问题

4. **向后兼容测试**
   - 旧项目的推理功能
   - 显式指定路径的行为

## 实现优先级

1. **P0 - 核心功能**
   - 文件查找逻辑
   - 基本错误处理
   
2. **P1 - 用户体验**
   - 清晰的提示信息
   - 有用的错误建议
   
3. **P2 - 高级功能**
   - 配置文件支持
   - 命令行参数扩展