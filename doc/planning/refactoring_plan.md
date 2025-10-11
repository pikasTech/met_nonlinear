# 循环导入重构方案

## 重构策略：依赖注入 + 接口抽象

### 步骤1：创建项目管理器接口

创建一个协议接口来定义 `ProjectManager` 的必要方法，避免直接依赖具体实现。

```python
# inference/interfaces.py
from typing import Protocol, Any

class ProjectManagerProtocol(Protocol):
    """ProjectManager 协议接口"""
    project_path: str
    project_name: str
    config: Any
    checkpoint_dir: str
```

### 步骤2：修改 ModelLoader 使用依赖注入

```python
# inference/processing/model_loader.py
from typing import Optional, Any, TYPE_CHECKING, Union
from .interfaces import ProjectManagerProtocol

if TYPE_CHECKING:
    from cli import ProjectManager

class ModelLoader:
    def __init__(self, project_path: str, project_manager: Optional[ProjectManagerProtocol] = None):
        self.project_path = project_path
        self.project_name = os.path.basename(project_path)
        self.project_manager = project_manager
        self.model_engine = None
        self.model = None
        self.model_name = None
    
    def initialize_model(self, project_manager: Optional[ProjectManagerProtocol] = None) -> BaseModel:
        # 使用传入的 project_manager 或者类初始化时的 project_manager
        if project_manager is not None:
            self.project_manager = project_manager
        elif self.project_manager is None:
            # 只有在没有传入时才进行延迟导入
            from cli import ProjectManager
            self.project_manager = ProjectManager(self.project_path)
        
        # 其余逻辑保持不变...
```

### 步骤3：修改 InferenceManager 的调用方式

```python
# inference/management/inference_manager.py
class InferenceManager:
    def __init__(self, project_manager):
        self.project = project_manager
        # ... 其他初始化代码
    
    def _get_model_loader(self):
        """获取模型加载器，使用依赖注入"""
        from ..processing.model_loader import ModelLoader
        # 传入 project_manager 避免循环导入
        return ModelLoader(self.project_path, project_manager=self.project)
```

### 步骤4：创建工厂类（可选）

```python
# inference/factory.py
from typing import Optional
from .processing.model_loader import ModelLoader
from .interfaces import ProjectManagerProtocol

class InferenceFactory:
    """推理组件工厂类"""
    
    @staticmethod
    def create_model_loader(project_path: str, project_manager: Optional[ProjectManagerProtocol] = None) -> ModelLoader:
        """创建模型加载器"""
        return ModelLoader(project_path, project_manager=project_manager)
```

## 具体实施步骤

### 1. 创建接口文件

```bash
# 创建 inference/interfaces.py
touch inference/interfaces.py
```

### 2. 修改 model_loader.py

- 移除模块级别的循环导入
- 添加依赖注入支持
- 保持向后兼容性

### 3. 修改调用方的代码

- 在 `inference_manager.py` 中传入 `project_manager`
- 在其他使用 `ModelLoader` 的地方传入依赖

### 4. 测试验证

```python
# 测试脚本
def test_circular_import():
    """测试循环导入是否解决"""
    try:
        import cli
        from inference.processing.model_loader import ModelLoader
        print("✅ 循环导入问题已解决")
        return True
    except ImportError as e:
        print(f"❌ 仍存在循环导入问题: {e}")
        return False

if __name__ == "__main__":
    test_circular_import()
```

## 优势

1. **解决循环导入**：通过依赖注入避免了直接的循环依赖
2. **提高可测试性**：可以轻松注入模拟对象进行测试
3. **降低耦合度**：模块之间的耦合度更低
4. **保持兼容性**：现有代码仍然可以正常工作

## 风险评估

1. **低风险**：主要是重构内部实现，不改变公共接口
2. **可回滚**：如果出现问题，可以快速回滚到当前的延迟导入方案
3. **渐进式**：可以逐步应用到各个模块

## 实施时间表

1. **第一阶段（1-2小时）**：创建接口和修改 `model_loader.py`
2. **第二阶段（1小时）**：修改调用方代码
3. **第三阶段（1小时）**：测试和验证
4. **第四阶段（可选）**：应用到其他模块

## 后续优化建议

1. 考虑将 `ProjectManager` 从 `cli.py` 中提取到独立模块
2. 创建依赖注入容器来管理对象生命周期
3. 使用工厂模式进一步解耦组件创建逻辑