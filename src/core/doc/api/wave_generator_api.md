# Wave Generator API 文档

## 概述

Wave Generator API 提供了从数据集生成波形文件的功能。该 API 设计为最大限度地重用现有的数据集加载和处理逻辑，同时提供简洁的编程接口。

## 核心类

### DatasetWaveGenerator

波形数据生成器类，负责从项目配置中加载数据集并生成波形文件。

#### 构造函数

```python
DatasetWaveGenerator(project_manager)
```

**参数：**
- `project_manager` (ProjectManager): 项目管理器实例

**示例：**
```python
from cli import ProjectManager
from core.wave_generator import DatasetWaveGenerator

project = ProjectManager('projects/my_project')
generator = DatasetWaveGenerator(project)
```

#### 方法

##### `generate_wave_data(output_folder=None, compress=True, force=False)`

生成波形数据文件。

**参数：**
- `output_folder` (str, optional): 输出目录路径。如果为 None，则使用项目目录下的 `wave_output` 文件夹
- `compress` (bool, default=True): 是否压缩波形文件
- `force` (bool, default=False): 是否强制覆盖已存在的文件

**返回值：**
- `Dict[str, Any]`: 包含生成结果的字典

**返回值结构：**
```python
{
    'project_name': str,           # 项目名称
    'dataset_type': str,           # 数据集类型 ('MET', 'PE', 'Alias', 'AliasSimu')
    'output_folder': str,          # 输出目录路径
    'compress': bool,              # 是否压缩
    'files': {                     # 生成的文件路径
        'input': str,              # 输入波形文件路径
        'output_original': str     # 原始输出波形文件路径
    },
    'dataset_info': {              # 数据集信息
        'magn_list': List[float],  # 震级列表
        'freq_list': List[float],  # 频率列表
        'magn_num': int,           # 震级数量
        'freq_num': int,           # 频率数量
        'fs': float,               # 采样率
        'time_clipped_s': float,   # 时间截取长度
        'type': str                # 数据集类型
    }
}
```

**异常：**
- `ValueError`: 配置错误或数据集加载失败
- `FileNotFoundError`: 数据文件不存在
- `PermissionError`: 输出目录权限不足
- `FileExistsError`: 输出目录包含已存在的文件且 force=False

**示例：**
```python
# 基本使用
result = generator.generate_wave_data()

# 自定义输出目录
result = generator.generate_wave_data(output_folder='/path/to/output')

# 不压缩文件
result = generator.generate_wave_data(compress=False)

# 强制覆盖已存在的文件
result = generator.generate_wave_data(force=True)

# 访问生成的文件
print(f"Input file: {result['files']['input']}")
print(f"Output file: {result['files']['output_original']}")
```

## ProjectManager 扩展

### `generate_wave_data(output_folder=None, compress=True, force=False)`

在 ProjectManager 类中添加的便捷方法，内部创建 DatasetWaveGenerator 实例并调用其方法。

**参数和返回值：** 与 `DatasetWaveGenerator.generate_wave_data()` 相同

**示例：**
```python
from cli import ProjectManager

project = ProjectManager('projects/my_project')
result = project.generate_wave_data()
```

## 命令行接口

### 基本命令

```bash
python cli.py -w PROJECT_NAME
```

### 命令行参数

- `-w`: 启用波形生成模式
- `--output DIRECTORY`: 指定输出目录
- `--no-compress`: 禁用文件压缩
- `-f` 或 `--force`: 强制覆盖已存在的文件
- `-all`: 处理所有项目
- `--debug`: 显示详细错误信息

### 命令行示例

```bash
# 生成单个项目的波形数据
python cli.py -w WNET5q1h2u6l3

# 指定输出目录
python cli.py -w WNET5q1h2u6l3 --output /path/to/custom/output

# 禁用压缩
python cli.py -w WNET5q1h2u6l3 --no-compress

# 强制覆盖已存在的文件
python cli.py -w WNET5q1h2u6l3 -f

# 批量处理匹配的项目
python cli.py -w WNET5* -f

# 处理所有项目
python cli.py -w -all
```

## 支持的数据集类型

| 数据集类型 | 描述 | 配置参数 |
|-----------|------|----------|
| MET | 电化学传感器数据 | `dataset_type: "MET"` |
| PE | 压电传感器仿真数据 | `dataset_type: "PE"` |
| Alias | 真实混叠失真数据 | `dataset_type: "Alias"` |
| AliasSimu | 仿真混叠失真数据 | `dataset_type: "AliasSimu"` |

## 文件命名规则

生成的波形文件使用以下命名规则：
- 输入文件：`dataset_{TYPE}_input.wave`
- 输出文件：`dataset_{TYPE}_output_original.wave`

其中 `{TYPE}` 是数据集类型（MET、PE、Alias、AliasSimu）。

## 错误处理

### 自定义异常

```python
class WaveGenerationError(Exception):
    \"\"\"波形生成相关错误\"\"\"
    pass

class DatasetLoadError(WaveGenerationError):
    \"\"\"数据集加载错误\"\"\"
    pass

class OutputFolderError(WaveGenerationError):
    \"\"\"输出目录错误\"\"\"
    pass
```

### 常见错误及解决方法

1. **FileNotFoundError**: 数据文件不存在
   - 检查项目配置中的 `data_path` 是否正确
   - 确认环境变量 `MET_DATA_BASE` 已设置

2. **PermissionError**: 输出目录权限不足
   - 检查输出目录的写入权限
   - 使用有权限的目录作为输出路径

3. **FileExistsError**: 输出目录包含已存在的文件
   - 使用 `force=True` 参数强制覆盖
   - 或者选择其他输出目录

4. **ValueError**: 配置错误
   - 检查项目配置文件是否有效
   - 确认数据集类型配置正确

## 性能优化

### 批量处理

对于多个项目的批量处理，推荐使用以下模式：

```python
from cli import ProjectManager

def batch_generate_wave_data(project_names, **kwargs):
    \"\"\"批量生成波形数据\"\"\"
    results = []
    failed_projects = []
    
    for project_name in project_names:
        try:
            project_path = f'projects/{project_name}'
            project = ProjectManager(project_path)
            result = project.generate_wave_data(**kwargs)
            results.append(result)
            print(f\"✅ {project_name}: Success\")
        except Exception as e:
            failed_projects.append((project_name, str(e)))
            print(f\"❌ {project_name}: {e}\")
    
    return results, failed_projects

# 使用示例
project_names = ['project1', 'project2', 'project3']
results, failed = batch_generate_wave_data(project_names, force=True)
```

### 缓存机制

API 内部实现了数据集缓存机制，相同配置的数据集会被缓存以提高性能。

## 日志记录

API 提供详细的日志记录功能：

```python
import logging

# 配置日志级别
logging.basicConfig(level=logging.INFO)

# 生成波形数据时会输出详细日志
generator = DatasetWaveGenerator(project)
result = generator.generate_wave_data()
```

日志信息包括：
- 数据集加载状态
- 文件生成进度
- 错误和警告信息
- 性能统计信息

## 测试

### 单元测试

```python
import unittest
from core.wave_generator import DatasetWaveGenerator
from cli import ProjectManager

class TestWaveGenerator(unittest.TestCase):
    def test_basic_generation(self):
        project = ProjectManager('projects/test_project')
        generator = DatasetWaveGenerator(project)
        result = generator.generate_wave_data()
        
        self.assertIn('files', result)
        self.assertIn('dataset_info', result)
```

### 集成测试

```python
def test_end_to_end_generation():
    \"\"\"端到端测试\"\"\"
    project = ProjectManager('projects/test_project')
    result = project.generate_wave_data()
    
    # 验证文件是否生成
    assert os.path.exists(result['files']['input'])
    assert os.path.exists(result['files']['output_original'])
```

## 版本兼容性

该 API 与以下版本兼容：
- Python 3.7+
- TensorFlow 2.6+
- calibration_analyzer 库

## 更新日志

### v1.0.0 (2025-07-09)
- 初始版本发布
- 支持所有数据集类型的波形生成
- 提供命令行和编程接口
- 完整的错误处理和日志记录