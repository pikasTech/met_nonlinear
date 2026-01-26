# 单元测试说明文档

## 测试框架概述

本项目使用Python的标准`unittest`框架进行单元测试，测试用例组织如下：

- `run_tests.py`: 项目根目录下的测试启动模块
- `testcase/`: 存放所有测试用例的文件夹
- `testcase/test_config.py`: 测试配置和通用工具
- `testcase/test_*.py`: 各个模块的具体测试用例
- `testcase/test_data/`: 测试数据存放目录

## 运行测试

### 运行所有测试

```bash
python run_tests.py
```

### 运行特定测试模块

```bash
python run_tests.py test_data_processing
```

### 增加详细输出

```bash
python run_tests.py -v
```

## 添加新的测试用例

1. 在`testcase/`目录下创建新的测试文件，命名为`test_<模块名>.py`
2. 从`test_config.py`中导入`BaseTestCase`
3. 创建继承自`BaseTestCase`的测试类
4. 实现测试方法，方法名必须以`test_`开头

示例:

```python
# testcase/test_new_module.py
from testcase.test_config import BaseTestCase

class TestNewModule(BaseTestCase):
    def test_new_function(self):
        # 测试代码
        self.assertEqual(1 + 1, 2)
```

## 测试数据

测试数据应放在`testcase/test_data/`目录中，可以在测试中使用`TEST_DATA_DIR`常量访问此目录：

```python
from testcase.test_config import TEST_DATA_DIR
import os

# 访问测试数据文件
test_file_path = os.path.join(TEST_DATA_DIR, 'test_file.csv')
```
