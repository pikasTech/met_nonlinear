# 部分层推理功能实施方案

**日期**：2025-01-11  
**作者**：System  
**状态**：实施方案  
**范围**：第一阶段 - 支持从第一层开始的前N层推理

## 概述

本文档详细说明了实现部分层推理功能的具体步骤，包括需要修改的文件列表和每个修改点的说明。

## 文件修改列表

### 1. cli.py
**路径**: `/cli.py`  
**修改类型**: 功能扩展  
**修改点**:
- 在命令行参数解析部分（约第402-410行）添加 `--layers` 参数解析
- 将解析的层数参数传递给 `ProjectManager.run_inference()` 方法
- 参数验证：确保是正整数

**具体修改**:
```python
# 在参数解析部分添加
layers_param = None
if '--layers' in sys.argv:
    idx = sys.argv.index('--layers')
    if idx + 1 < len(sys.argv):
        try:
            layers_param = int(sys.argv[idx + 1])
            if layers_param <= 0:
                logger.error("--layers 参数必须是正整数")
                sys.exit(1)
        except ValueError:
            logger.error("--layers 参数必须是整数")
            sys.exit(1)

# 修改 run_inference 调用
project.run_inference(force=force_mode, quick=quick_inference, layers=layers_param)
```

### 2. ProjectManager.run_inference()
**路径**: `/cli.py` (第247-249行)  
**修改类型**: 接口扩展  
**修改点**:
- 修改方法签名，添加 `layers` 参数
- 将参数传递给 `InferenceManager`

**具体修改**:
```python
def run_inference(self, force=False, quick=False, layers=None):
    """委托给推理管理器"""
    self.inference_manager.run_inference(force=force, quick=quick, layers=layers)
```

### 3. InferenceManager.run_inference()
**路径**: `/inference/management/inference_manager.py` (第73行)  
**修改类型**: 接口扩展  
**修改点**:
- 修改方法签名，添加 `layers` 参数
- 将参数传递给 `InferenceExecutor`
- 在日志中记录层数限制信息

**具体修改**:
```python
def run_inference(self, force=False, quick=False, layers=None):
    """
    运行推理数据生成
    
    参数:
        force: 是否强制重新生成（删除已有数据）
        quick: 是否使用快速模式（只处理最小最大震级）
        layers: 只推理前N层（None表示推理所有层）
    """
    logger.info(f'🔍 推理数据生成项目: {self.project_name}')
    if quick:
        logger.info(f'⚡ 快速推理模式：只处理最小和最大震级数据')
    if layers is not None:
        logger.info(f'🔢 部分层推理模式：只推理前 {layers} 层')
    
    # 保存参数供后续使用
    self.executor.set_layers_limit(layers)
    # ... 其余代码不变
```

### 4. InferenceExecutor
**路径**: `/inference/management/inference_executor.py`  
**修改类型**: 功能扩展  
**修改点**:
- 添加 `set_layers_limit()` 方法
- 在 `_generate_nn_inference()` 方法中传递层参数

**具体修改**:
```python
def __init__(self, ...):
    # ... 现有代码 ...
    self.layers_limit = None

def set_layers_limit(self, layers):
    """设置层数限制"""
    self.layers_limit = layers

def _generate_nn_inference(self, inference_data_dir, input_wave):
    """生成神经网络推理数据"""
    # ... 现有代码 ...
    
    # 在创建processor时传递层数限制
    if self.layers_limit is not None:
        logger.info(f'  设置层数限制: {self.layers_limit}')
    
    # 在推理时传递参数
    processor.infer_and_save(
        input_wave_path=input_wave,
        layer_output_dir=nn_layers_dir,
        use_scaler=True,
        layers=self.layers_limit  # 新增参数
    )
```

### 5. InferenceDataProcessor
**路径**: `/inference/data_processing/data_processor.py`  
**修改类型**: 接口扩展  
**修改点**:
- 修改 `infer_and_save()` 方法，添加 `layers` 参数
- 将参数传递给后端

**具体修改**:
```python
def infer_and_save(self, input_wave_path, output_wave_path=None, 
                  layer_output_dir=None, use_scaler=False, layers=None, **kwargs):
    """
    加载输入数据，进行推理，并保存结果
    
    参数:
        ... 现有参数 ...
        layers: 只推理前N层（None表示推理所有层）
    """
    # ... 现有代码 ...
    
    # 在推理时传递层参数
    if self.processor.backend_type == 'layer_by_layer':
        layer_results = self.processor.backend.infer(
            input_wave_data, 
            use_scaler=use_scaler,
            layers=layers  # 新增参数
        )
```

### 6. LayerByLayerBackend
**路径**: `/inference/backends/layered_backend.py`  
**修改类型**: 核心功能实现  
**修改点**:
- 修改 `infer()` 方法签名，添加 `layers` 参数
- 实现层数限制逻辑
- 更新日志和元数据

**具体修改**:
```python
def infer(self, input_wave_data: Union[str, WaveData], use_scaler=False, layers=None) -> List[WaveData]:
    """
    对输入波形进行分层推理
    
    参数:
        input_wave_data: 输入波形数据对象或波形文件路径
        use_scaler: 是否使用缩放器
        layers: 只推理前N层（None表示推理所有层）
    
    返回:
        List[WaveData]: 包含每一层推理结果的波形数据对象列表
    """
    # ... 现有验证代码 ...
    
    layered_models = self.model.get_layered_models()
    total_layers = len(layered_models)
    
    # 确定要推理的层数
    if layers is not None:
        num_layers_to_infer = min(layers, total_layers)
        if layers > total_layers:
            logger.warning(f'请求推理 {layers} 层，但模型只有 {total_layers} 层。将推理所有 {total_layers} 层。')
    else:
        num_layers_to_infer = total_layers
    
    logger.info(f'将推理前 {num_layers_to_infer}/{total_layers} 层')
    
    # ... 准备批数据代码 ...
    
    layer_results = []
    for layer_idx in range(num_layers_to_infer):  # 修改循环范围
        logger.info(f'正在处理第 {layer_idx + 1}/{num_layers_to_infer} 层（共 {total_layers} 层）')
        
        # ... 层推理逻辑 ...
        
        # 更新元数据
        layer_output.add_user_metadata('layer_index', layer_idx)
        layer_output.add_user_metadata('total_layers_in_model', total_layers)
        layer_output.add_user_metadata('layers_inferred', num_layers_to_infer)
        
        # ... 其余代码 ...
    
    return layer_results
```

### 7. 后端管理器验证（可选）
**路径**: `/inference/processing/backend_manager.py`  
**修改类型**: 验证逻辑  
**修改点**:
- 确保其他后端不受影响
- 添加参数验证

## 测试计划

### 单元测试
1. 测试参数解析的各种情况：
   - 正常情况：`--layers 2`
   - 边界情况：`--layers 0`（应报错）
   - 非法输入：`--layers abc`（应报错）
   - 超出范围：`--layers 100`（应警告并使用实际层数）

2. 测试接口传递：
   - 确保参数正确传递到各个层级
   - 验证不指定参数时的向后兼容性

3. 测试推理结果：
   - 验证只推理指定层数
   - 检查输出文件和元数据

### 集成测试
1. 完整命令行测试：
```bash
# 推理前2层
python cli.py -i --layers 2 WNET5q0.5h2u6l4

# 结合快速模式
python cli.py -i -q --layers 3 WNET5q0.5h2u6l4

# 不指定层数（向后兼容）
python cli.py -i WNET5q0.5h2u6l4
```

2. 输出验证：
   - 检查生成的文件数量
   - 验证元数据中的层信息
   - 确认日志输出正确

## 实施时间表

| 阶段 | 任务 | 预计时间 |
|------|------|----------|
| 1 | 修改 cli.py 参数解析 | 2小时 |
| 2 | 扩展各层接口 | 3小时 |
| 3 | 实现 LayerByLayerBackend 核心逻辑 | 4小时 |
| 4 | 编写和运行测试 | 3小时 |
| 5 | 文档更新 | 1小时 |
| **总计** | | **13小时** |

## 注意事项

1. **错误处理**：所有新增的参数都需要适当的验证和错误处理
2. **日志记录**：在关键位置添加清晰的日志，便于调试
3. **元数据**：确保输出文件包含足够的元数据，标识部分层推理的信息
4. **向后兼容**：不指定 `--layers` 参数时，系统行为应与现有版本完全一致
5. **文档更新**：完成实现后，需要更新用户文档和 README

## 后续扩展

本实施方案为第一阶段，后续可以考虑：
- 支持推理中间层（如第2-4层）
- 支持非连续层推理（如第1,3,5层）
- 添加层推理的可视化工具
- 性能优化，避免不必要的层加载