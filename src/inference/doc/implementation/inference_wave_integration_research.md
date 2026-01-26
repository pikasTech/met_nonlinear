# 推理功能集成Wave数据源调研报告

## 调研背景

当前推理功能（`cli.py -i`）默认读取 `inference/temp/dataset_input.wave` 文件，但随着新增的wave数据生成功能（`-w`），我们可以生成包含数据集类型标识的wave文件，如 `dataset_MET_output_original.wave`。本调研旨在探索如何让推理功能默认使用这些更具语义化的wave文件。

## 现状分析

### 1. 当前推理数据流

```
推理流程：
1. InferenceManager._find_input_file() 查找输入文件
2. 默认查找路径：inference/temp/dataset_input.wave
3. InferenceProcessor 加载wave文件并进行推理
4. 结果保存到 data/inference/ 目录
```

### 2. 新生成的Wave文件特点

- **位置**: `projects/{PROJECT_NAME}/data/wave_output/`
- **命名规则**: `dataset_{TYPE}_{input|output_original}.wave`
- **数据集类型**: MET、PE、Alias、AliasSimu
- **包含元数据**: 数据集信息、采样率、频率列表等

### 3. 技术优势

1. **文件名语义化**: 包含数据集类型，易于识别
2. **数据完整性**: 包含完整的元数据信息
3. **统一生成**: 通过 `-w` 参数统一生成，确保一致性
4. **多种选择**: 同时生成input和output_original，提供灵活性

## 设计方案

### 方案一：简化直接查找策略（推荐）

**核心思想**: 直接查找固定路径的wave文件，不提供回退机制。

**实现要点**:

1. **固定查找路径**
   ```python
   # InferenceManager._find_input_file() 简化为
   wave_output_dir = os.path.join(self.project_path, "data", "wave_output")
   dataset_type = self.config.dataset_type
   target_file = f"dataset_{dataset_type}_output_original.wave"
   target_path = os.path.join(wave_output_dir, target_file)
   
   if not os.path.exists(target_path):
       raise FileNotFoundError(f"请先运行: python cli.py -w {project_name}")
   ```

2. **删除参数和配置**
   - 删除 `default_path` 参数
   - 删除 `inference_input_path` 配置
   - 不支持自定义输入路径

3. **清晰的错误提示**
   - 文件不存在时直接报错
   - 提示用户运行 `-w` 命令
   - 列出目录中已有的wave文件

**优点**:
- 实现极其简单，只需修改一个方法
- 逻辑清晰，没有复杂的回退和配置
- 强制统一的数据流程
- 错误信息明确

**缺点**:
- 破坏性变更，不兼容旧项目
- 必须先生成wave数据
- 灵活性降低

### 方案二：推理数据源抽象层

**核心思想**: 创建统一的推理数据源接口，支持多种数据来源。

**实现要点**:

1. **创建数据源接口**
   ```python
   class InferenceDataSource(ABC):
       @abstractmethod
       def get_input_data(self) -> WaveData:
           pass
       
       @abstractmethod
       def get_metadata(self) -> Dict:
           pass
   
   class WaveFileDataSource(InferenceDataSource):
       """从wave文件读取数据"""
       
   class DatasetDataSource(InferenceDataSource):
       """从数据集直接生成数据"""
       
   class WaveOutputDataSource(InferenceDataSource):
       """从wave_output目录读取类型化文件"""
   ```

2. **数据源工厂**
   ```python
   class DataSourceFactory:
       @staticmethod
       def create_source(config, project_path) -> InferenceDataSource:
           if config.inference_source == "wave_output":
               return WaveOutputDataSource(project_path, config.dataset_type)
           elif config.inference_source == "dataset":
               return DatasetDataSource(project_path)
           else:
               return WaveFileDataSource(config.inference_input_path)
   ```

3. **集成到InferenceManager**
   ```python
   def run_inference(self):
       data_source = DataSourceFactory.create_source(self.config, self.project_path)
       input_data = data_source.get_input_data()
       # 继续推理流程...
   ```

**优点**:
- 架构清晰，易于扩展
- 支持多种数据源
- 测试友好

**缺点**:
- 需要较大重构
- 增加了系统复杂度

### 方案三：自动Wave生成与缓存机制

**核心思想**: 推理时自动检查并生成所需的wave文件。

**实现要点**:

1. **推理前检查**
   ```python
   def _ensure_wave_files(self):
       wave_output_dir = os.path.join(self.project_path, "data", "wave_output")
       expected_file = f"dataset_{self.config.dataset_type}_output_original.wave"
       
       if not os.path.exists(os.path.join(wave_output_dir, expected_file)):
           # 自动调用wave生成功能
           self.project_manager.generate_wave_data()
   ```

2. **缓存机制**
   - 检查wave文件的时间戳
   - 与模型权重文件对比，判断是否需要重新生成
   - 支持force参数强制重新生成

3. **配置控制**
   ```json
   {
       "inference_auto_generate_wave": true,
       "inference_wave_cache_ttl": 3600  // 缓存有效期（秒）
   }
   ```

**优点**:
- 用户无需手动生成wave文件
- 始终使用最新数据
- 减少存储冗余

**缺点**:
- 首次推理时间较长
- 可能产生不必要的重复生成

## 方案对比

| 特性 | 方案一 | 方案二 | 方案三 |
|------|--------|--------|--------|
| 实现复杂度 | 极低 | 高 | 中 |
| 向后兼容性 | 无 | 良好 | 优秀 |
| 扩展性 | 差 | 优秀 | 良好 |
| 用户体验 | 良好 | 良好 | 优秀 |
| 维护成本 | 极低 | 高 | 中 |

## 建议实施计划

### 推荐方案：方案一（简化直接查找策略）

**理由**：
1. 实现最简单，只需修改一个方法
2. 逻辑最清晰，没有复杂的配置和回退
3. 强制规范化的数据流程
4. 错误提示明确，用户知道该做什么

### 实施步骤

1. **修改 _find_input_file 方法**
   - 删除 `default_path` 参数
   - 直接查找 `dataset_{TYPE}_output_original.wave`
   - 文件不存在时抛出详细错误

2. **更新所有调用处**
   - `run_inference` 方法中删除参数
   - `_generate_inference_data` 方法中删除参数
   - 添加异常处理和错误提示

3. **清理配置**
   - 删除 `inference_input_path` 配置项
   - 删除相关的默认值和文档

### 示例使用流程

```bash
# 1. 生成wave数据
python cli.py -w WNET5q1h2u6l3

# 2. 运行推理（自动使用生成的wave文件）
python cli.py -i WNET5q1h2u6l3

# 输出示例：
# ✓ 找到推理输入文件: projects/WNET5q1h2u6l3/data/wave_output/dataset_MET_output_original.wave
# 开始神经网络推理...
```

## 未来扩展

1. **支持多种输入模式**
   - 原始输入推理：使用 `dataset_*_input.wave`
   - 输出恢复推理：使用 `dataset_*_output_original.wave`
   - 自定义输入推理：指定任意wave文件

2. **推理结果对比**
   - 自动对比不同输入模式的推理结果
   - 生成对比报告

3. **批量推理优化**
   - 缓存已加载的wave文件
   - 并行处理多个项目

## 结论

通过扩展现有的文件查找机制，我们可以以最小的改动实现推理功能与新的wave数据生成功能的集成。这种方案既保持了系统的简洁性，又提供了良好的用户体验，是当前最适合的实施方案。