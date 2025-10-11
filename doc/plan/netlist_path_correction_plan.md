# 网表生成路径修正计划

## 问题概述

当前网表生成存在路径配置错误，导致：
1. 正确的网表（增益值正确）生成到根目录 `data/spice_netlists/`
2. 错误的网表（增益值错误）在项目目录 `projects/WNET5q1h2u6l3/data/spice_netlists/`
3. 路径配置混乱，不同时间生成到不同位置

## 根因分析

### 核心问题
Model对象（如WaveNet5）缺少`project_path`属性，导致WaveNet5SPICEBackend的路径回退逻辑生效，将网表生成到根目录。

### 代码流程分析

1. **InferenceExecutor**（`inference/management/inference_executor.py`）
   - 第68行：创建InferenceProcessor时传递了project_path

2. **InferenceProcessor**（`inference/processing/inference_processor.py`）
   - 第42行：存储了project_path
   - 第59-63行：创建BackendManager时传递了project_path

3. **BackendManager**（`inference/processing/backend_manager.py`）
   - 第39行：存储了project_path
   - 第151行：调用WaveNet5SPICEBackend时使用了正确的output_folder

4. **WaveNet5SPICEBackend**（`inference/wavenet5_spice_backend.py`）
   - 第36-45行：export_model_to_spice中的路径逻辑
   - 当model没有project_path属性时，回退到根目录

5. **WaveNet5模型**（`models/wavenet_models.py`）
   - 第620-659行：__init__方法没有设置project_path属性

## 修改方案

### 方案一：为Model添加project_path属性（推荐）

**优点**：
- 最小化代码改动
- 保持向后兼容
- 逻辑清晰

**缺点**：
- 需要修改模型初始化逻辑

### 方案二：修改WaveNet5SPICEBackend使用传入的output_folder

**优点**：
- 不需要修改模型
- 更简单直接

**缺点**：
- 可能影响其他调用路径

## 详细修改计划（方案一）

### 1. 修改ModelLoader - 为model设置project_path
**文件**：`inference/processing/model_loader.py`
**位置**：第66-71行之间
**修改内容**：
```python
# 获取模型实例
self.model = self.model_engine.model_comp
self.model_name = getattr(self.model, 'model_name', 'Unknown')

# 为模型设置project_path属性（新增）
if hasattr(self.model, '__dict__'):
    self.model.project_path = self.project_path
    logger.info(f'已为模型设置project_path: {self.project_path}')

logger.info(f'模型初始化完成: {self.model_name}')
```

### 2. 修改WaveNet5SPICEBackend - 改进路径逻辑
**文件**：`inference/wavenet5_spice_backend.py`
**位置**：第36-45行
**修改内容**：
```python
def export_model_to_spice(self, model, output_folder=None, layer_configs=None):
    """导出模型为SPICE网表"""
    # 改进路径确定逻辑
    if output_folder is None:
        if hasattr(model, 'project_path') and model.project_path:
            output_folder = os.path.join(model.project_path, 'data', 'spice_netlists')
            logger.info(f"使用model.project_path: {output_folder}")
        else:
            # 警告：使用回退路径
            logger.warning("警告：model缺少project_path属性，使用默认路径")
            output_folder = os.path.join('data', 'spice_netlists')
    
    os.makedirs(output_folder, exist_ok=True)
```

### 3. 修改BackendManager - 确保路径传递正确
**文件**：`inference/processing/backend_manager.py`
**位置**：第148-165行
**修改内容**：
```python
def _create_spice_backend(self) -> InferenceBackend:
    """创建SPICE后端"""
    # 智能路径生成：优先使用项目路径
    output_folder = self._generate_spice_output_path()
    os.makedirs(output_folder, exist_ok=True)
    
    # 确保model有project_path属性
    if hasattr(self.model, '__dict__') and not hasattr(self.model, 'project_path'):
        self.model.project_path = self.project_path
        logger.info(f"为model设置project_path: {self.project_path}")
```

## 详细修改计划（方案二 - 备选）

### 1. 修改WaveNet5SPICEBackend - 强制使用传入的output_folder
**文件**：`inference/wavenet5_spice_backend.py`
**位置**：第36-45行
**修改内容**：
```python
def export_model_to_spice(self, model, output_folder=None, layer_configs=None):
    """导出模型为SPICE网表"""
    # 使用构造函数传入的output_folder或参数指定的output_folder
    if output_folder is None:
        output_folder = self.output_folder  # 使用构造函数中的值
    
    if output_folder is None:
        # 只有在完全没有指定时才使用回退逻辑
        if hasattr(model, 'project_path'):
            output_folder = os.path.join(model.project_path, 'data', 'spice_netlists')
        else:
            output_folder = os.path.join('data', 'spice_netlists')
    
    os.makedirs(output_folder, exist_ok=True)
```

## 测试计划

### 1. 单元测试
- 测试model是否正确设置了project_path属性
- 测试WaveNet5SPICEBackend的路径逻辑

### 2. 集成测试
- 运行推理任务：`python cli.py -i WNET5q1h2u6l3`
- 验证网表生成位置：`projects/WNET5q1h2u6l3/data/spice_netlists/`
- 验证网表内容正确性（增益值）

### 3. 回归测试
- 电阻导出功能：`python cli.py -r WNET5q1h2u6l3`
- BOM生成功能：`python cli.py -r WNET5q1h2u6l3 --bom`
- 验证CSV和BOM数据一致性

## 实施步骤

1. **备份当前代码**
2. **实施方案一的修改**（优先）
3. **运行测试验证**
4. **如果方案一有问题，实施方案二**
5. **更新文档**

## 风险评估

- **低风险**：修改只涉及路径配置，不影响计算逻辑
- **中风险**：可能影响其他使用model的代码路径
- **缓解措施**：充分测试，保留回退逻辑

## 预期收益

1. **网表生成到正确位置**：`projects/{project}/data/spice_netlists/`
2. **路径配置统一**：消除混乱
3. **数据一致性**：CSV、BOM、网表使用相同数据源
4. **验证系统恢复**：可以正确验证网表与CSV的一致性

## 时间估算

- 代码修改：30分钟
- 测试验证：1小时
- 文档更新：30分钟
- **总计**：2小时