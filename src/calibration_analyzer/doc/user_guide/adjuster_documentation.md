# Adjuster.py 快速上手指南

## 概述

`adjuster.py` 是一个简单而强大的 Python GUI 库，让你用几行代码就能创建专业的参数调节界面。经过模块化重构，现在具有更好的代码组织和扩展性。

### 🚀 重构升级 (2025年5月)

- **模块化架构**: 将原来的1288行单文件拆分为5个清晰的模块
- **100%向后兼容**: 现有代码无需任何修改
- **更好的维护性**: 功能分离，便于开发和调试
- **团队协作**: 支持多人并行开发不同模块

### 📁 模块结构

```
adjuster.py              # 主API接口 (兼容层)
├── adjuster_utils.py    # 工具函数和辅助类
├── adjuster_widgets.py  # UI控件类
├── adjuster_plots.py    # 绘图功能  
└── adjuster_core.py     # 核心Panel类
```

## 5分钟快速入门

### 最简单的例子

```python
from adjuster import Panel

# 1. 定义你的参数
params = {
    "frequency": 1000.0,        # 数值调节器
    "enable": True,             # 复选框  
    "output_file@filepath": "", # 文件选择器
    "start@button": False       # 按钮
}

# 2. 创建界面
panel = Panel(params, name="我的第一个界面")

# 3. 运行
panel.mainloop()
```

就这么简单！你已经有了一个完整的参数调节界面。

### ✨ 重构后的新特性亮点

```python
# 🔧 现在支持模块化导入（可选）
from adjuster_widgets import Adjuster    # 只导入需要的控件
from adjuster_utils import format_value  # 只导入需要的工具

# 🚀 性能优化：按需加载，减少内存占用
# 🛠️ 更好维护：代码按功能模块化组织  
# 👥 团队协作：多人可并行开发不同模块
# 📦 向后兼容：现有代码完全不需要修改！
```

### 📊 重构前后对比

| 方面 | 重构前 | 重构后 | 改进 |
|------|--------|--------|------|
| **文件结构** | 单个1288行文件 | 5个模块化文件 | ✅ 结构清晰 |
| **代码维护** | 难以定位和修改 | 按功能分离 | ✅ 易于维护 |  
| **团队协作** | 多人冲突频繁 | 模块独立开发 | ✅ 并行开发 |
| **功能扩展** | 修改风险大 | 模块内扩展 | ✅ 安全扩展 |
| **导入性能** | 全量加载 | 按需导入 | ✅ 内存优化 |
| **代码复用** | 难以复用 | 模块独立复用 | ✅ 高复用性 |
| **API兼容** | N/A | 100%兼容 | ✅ 无缝升级 |

## 核心概念

### 1. 一切都是字典
- 用普通字典定义界面
- 键名就是参数名
- 值就是默认值
- 特殊后缀控制组件类型

### 2. 自动类型识别
```python
params = {
    "number": 123.4,           # 自动识别为数值调节器
    "text": "hello",           # 自动识别为文本框
    "flag": True,              # 自动识别为复选框
    "file@filepath": "",       # 强制为文件选择器
    "action@button": False     # 强制为按钮
}
```

### 3. 自动保存加载
界面会自动保存你的设置到 `.data/` 文件夹，下次打开自动恢复。

### 4. 灵活的导入方式

重构后的adjuster支持多种导入方式：

```python
# 方式1: 统一导入 (推荐，保持兼容性)
from adjuster import Panel, Adjuster, TextField, format_value

# 方式2: 星号导入 (全部导入)
from adjuster import *

# 方式3: 模块化导入 (按需导入，减少内存)
from adjuster_widgets import Adjuster, TextField    # 只导入控件
from adjuster_utils import format_value             # 只导入工具函数
from adjuster_core import Panel                     # 只导入核心类

# 方式4: 完整模块导入
import adjuster
panel = adjuster.Panel(params)
```

**建议**: 现有项目继续使用方式1，新项目可考虑方式3实现按需导入。

### 🔧 模块化开发示例

下面展示如何利用模块化架构开发自定义功能：

```python
# 示例：创建自定义的数据处理工具
from adjuster_core import Panel                    # 核心面板
from adjuster_widgets import Adjuster, TextField   # 需要的控件
from adjuster_utils import format_value            # 工具函数
from adjuster_plots import Plotter                 # 绘图功能

class DataProcessor:
    def __init__(self):
        # 只导入需要的模块，节省内存
        self.setup_ui()
    
    def setup_ui(self):
        params = {
            "threshold": 0.5,           # 使用Adjuster控件
            "input_file@filepath": "",  # 使用FilePath控件  
            "process@button": False     # 使用Button控件
        }
        
        self.panel = Panel(params, self.on_change, 
                          name="数据处理器", with_plot=True)
    
    def on_change(self, values):
        if values.get('process@button'):
            threshold = values['threshold']
            file_path = values['input_file@filepath']
            
            # 使用工具函数格式化显示
            print(f"处理文件: {file_path}")
            print(f"阈值: {format_value(threshold)}")
    
    def run(self):
        self.panel.mainloop()

# 使用
processor = DataProcessor()
processor.run()
```

**优势**:
- 🎯 **精确导入**: 只加载需要的模块
- ⚡ **更快启动**: 减少不必要的模块加载
- 🔧 **易于扩展**: 可以轻松替换或扩展特定模块

## 5分钟快速开始

### 第一步：最简单的例子

```python
from adjuster import Panel

# 定义你要调节的参数
params = {
    "频率": 1000.0,
    "振幅": 1.0,
    "启用": True
}

# 参数变化时会调用这个函数
def on_change(values):
    print(f"当前参数：{values}")

# 创建界面
panel = Panel(params, on_change)
panel.mainloop()  # 启动界面
```

就这么简单！运行后你会看到：
- 数值调节器（带 +/- 按钮）
- 复选框  
- 每次修改参数都会打印当前值

### 第二步：添加更多控件类型

```python
params = {
    # 基本类型（自动识别控件）
    "频率": 1000.0,           # → 数值调节器
    "名称": "测试",           # → 文本输入框
    "启用": True,            # → 复选框
    
    # 特殊类型（用后缀指定）
    "数据文件@filepath": "",     # → 文件选择器
    "输出目录@folderpath": "",   # → 文件夹选择器
    "处理@button": False,       # → 按钮
    "模式@dropdown": ["模式1", "模式2", "模式3"]  # → 下拉菜单
}
```

### 第三步：响应用户操作

```python
def on_change(values):
    # 检查哪些参数发生了变化
    changed = values.get('@on_change', [])
    print(f"变化的参数: {changed}")
    
    # 响应按钮点击
    if values.get('处理@button'):
        print("开始处理...")
        # 这里写你的处理逻辑
    
    # 响应参数变化
    if '频率' in changed:
        print(f"频率变为: {values['频率']}")
```

## 核心概念

### 1. 参数字典是一切的开始

参数字典的键值对决定了界面上显示什么控件：

| 值的类型 | 生成的控件 | 示例 |
|---------|-----------|------|
| `float/int` | 数值调节器 | `"频率": 1000.0` |
| `bool` | 复选框 | `"启用": True` |
| `str` | 文本输入框 | `"名称": "默认"` |
| `str + "@filepath"` | 文件选择器 | `"文件@filepath": ""` |
| `str + "@button"` | 按钮 | `"执行@button": False` |
| `list + "@dropdown"` | 下拉菜单 | `"模式@dropdown": ["A", "B"]` |

### 2. 数值调节器的智能功能

数值调节器不只是简单的输入框：

```python
# 这些操作都支持：
# 点击 < > 按钮微调 (×0.9, ×1.1)
# 点击 << >> 按钮大幅调节 (×0.5, ×2.0)  
# 直接输入数值
# 支持单位：1k = 1000, 2.5M = 2500000
# RST 按钮重置到默认值
```

### 3. 回调函数机制

```python
def on_change(values):
    # values 包含所有当前参数值
    # values['@on_change'] 包含本次变化的参数名列表
    pass
```

## 进阶功能

### 1. 条件显示（动态隐藏控件）

```python
params = {
    "模式": "手动",
    "手动频率": 1000.0,
    "文件路径@filepath": "",
    
    # 条件控制配置
    "@param": {
        "手动频率": {"if": "模式 == '手动'"},           # 只在手动模式显示
        "文件路径@filepath": {"if": "模式 == '文件'"}    # 只在文件模式显示
    }
}
```

### 2. 多标签页界面

```python
# 主面板
main_params = {"输入@filepath": "", "输出@folderpath": ""}
main_panel = Panel(main_params, callback, name="主面板")

# 子面板（会变成标签页）
settings_params = {"阈值": 0.5, "迭代次数@int": 100}
settings_panel = Panel(settings_params, callback, name="设置")

main_panel.mainloop()  # 启动多标签界面
```

### 3. 显示程序输出

```python
# 添加 redirect_stdout=True 参数
panel = Panel(params, callback, redirect_stdout=True)

# 现在所有的 print() 输出都会显示在界面下方的文本区域
print("这条消息会显示在界面中")
```

## 实际应用示例

### 数据处理工具

```python
from adjuster import Panel

def process_data(values):
    # 检查是否点击了处理按钮
    if values.get('process@button'):
        input_file = values.get('input_file@filepath')
        threshold = values.get('threshold')
        print(f"处理文件: {input_file}, 阈值: {threshold}")

params = {
    "input_file@filepath": "",     # 输入文件
    "threshold": 0.5,              # 阈值
    "smooth_window@int": 10,       # 平滑窗口
    "enable_filter": True,         # 启用滤波
    "process@button": False        # 处理按钮
}

panel = Panel(params, process_data, name="数据处理工具")
panel.mainloop()
```

### 信号发生器

```python
from adjuster import Panel
import numpy as np

def update_signal(values):
    freq = values.get('frequency', 1000)
    amp = values.get('amplitude', 1.0)
    print(f"信号频率: {freq}Hz, 幅度: {amp}V")
    
    # 如果点击了开始按钮
    if values.get('start@button'):
        print("开始生成信号...")

params = {
    "frequency": 1000.0,          # 频率 (Hz)
    "amplitude": 1.0,             # 幅度 (V)  
    "waveform@dropdown": ["sine", "square", "triangle"],  # 波形
    "enable": True,               # 使能
    "start@button": False,        # 开始按钮
    "stop@button": False          # 停止按钮
}

panel = Panel(params, update_signal, name="信号发生器")
panel.mainloop()
```

## 组件类型详解

### 数值调节器 (`float` / `int`)
```python
"frequency": 1000.0,              # 浮点数调节器
"count@int": 100                  # 整数调节器
```
- 点击 `<` `>` 微调 (×0.9, ×1.1)
- 点击 `<<` `>>` 大幅调节 (×0.5, ×2.0)
- 支持单位：1k=1000, 2.5M=2500000
- `RST` 按钮重置到默认值

### 复选框 (`bool`)
```python
"enable": True,                   # 复选框
"debug_mode": False
```

### 文本框 (`str`)
```python
"device_name": "Device1",         # 文本输入框
"description": "测试设备"
```

### 文件选择器 (`@filepath`)
```python
"config_file@filepath": "",       # 文件选择
"data_file@filepath": "/path/to/file.txt"
```

### 文件夹选择器 (`@folderpath`)
```python
"output_dir@folderpath": "",      # 文件夹选择
"work_dir@folderpath": "/path/to/folder"
```

### 按钮 (`@button`)
```python
"start@button": False,            # 按钮
"stop@button": False,
"reset@button": False
```

### 下拉菜单 (`@dropdown`)
```python
"mode@dropdown": ["Auto", "Manual", "Custom"],
"device@dropdown": ["COM1", "COM2", "COM3"]
```

## 高级功能

### 条件显示
根据其他参数的值来控制组件的显示/隐藏：

```python
params = {
    "mode@dropdown": ["Manual", "Auto"],
    "manual_freq": 1000.0,
    "auto_range": 10.0,
    
    # 条件控制配置
    "@param": {
        "manual_freq": {"if": "mode@dropdown == 'Manual'"},
        "auto_range": {"if": "mode@dropdown == 'Auto'"}
    }
}
```

### 回调函数详解
```python
def on_change(values):
    # values: 当前所有参数的值
    # values['@on_change']: 本次改变的参数名列表
    
    changed = values.get('@on_change', [])
    
    if 'frequency' in changed:
        print(f"频率改变为: {values['frequency']}")
    
    if values.get('start@button'):
        print("开始按钮被点击")
```

### 多标签页
```python
# 主面板
main_params = {"input@filepath": "", "output@folderpath": ""}
main_panel = Panel(main_params, callback, name="主面板")

# 设置面板（会自动变成标签页）
settings_params = {"threshold": 0.5, "iterations@int": 100}
settings_panel = Panel(settings_params, callback, name="设置")

main_panel.mainloop()  # 启动界面
```

### 输出重定向
```python
# 显示程序输出到界面中
panel = Panel(params, callback, redirect_stdout=True)

# 现在所有print()都会显示在界面下方
print("这条消息会在界面中显示")
```

## 技巧和最佳实践

### 1. 合理组织参数
```python
# 推荐：按功能分组
params = {
    # 输入设置
    "input_file@filepath": "",
    "sample_rate": 44100,
    
    # 处理参数  
    "filter_enable": True,
    "cutoff_freq": 1000.0,
    
    # 输出设置
    "output_dir@folderpath": "",
    "save_format@dropdown": ["WAV", "MP3", "FLAC"]
}
```

### 2. 使用有意义的名称
```python
# 好的命名
params = {
    "input_voltage": 3.3,         # 清楚表明是输入电压
    "measurement_enable": True,   # 清楚表明是测量使能
    "start_measurement@button": False  # 清楚表明是开始测量按钮
}
```

### 3. 合理设置默认值
```python
params = {
    "frequency": 1000.0,          # 合理的默认频率
    "amplitude": 1.0,             # 安全的默认幅度
    "output_enable": False,       # 默认关闭输出（安全）
}
```

### 4. 使用回调函数进行参数验证
```python
def validate_and_update(values):
    # 参数范围检查
    freq = values.get('frequency', 1000)
    if freq > 1000000:  # 1MHz
        print("警告：频率过高，可能导致问题")
    
    # 参数联动
    if values.get('auto_mode'):
        # 自动模式下禁用手动设置
        panel.set_values({"manual_freq": 0})
```

## 常见问题

### Q: 如何在程序中修改参数值？
```python
panel = Panel(params, callback)
# 修改参数值
panel.set_values({"frequency": 2000.0, "enable": True})
```

### Q: 如何获取当前所有参数值？
```python
current_values = panel.get_values()
print(current_values)
```

### Q: 按钮点击后如何重置？
按钮会自动重置，你不需要手动处理。

### Q: 数值输入支持哪些单位？
- p (pico, 10^-12)
- n (nano, 10^-9)  
- u (micro, 10^-6)
- m (milli, 10^-3)
- k (kilo, 10^3)
- M (Mega, 10^6)
- G (Giga, 10^9)
- T (Tera, 10^12)

### Q: 如何处理错误输入？
```python
def safe_callback(values):
    try:
        freq = float(values.get('frequency', 1000))
        if freq <= 0:
            print("错误：频率必须大于0")
            return
        # 处理有效输入...
    except ValueError:
        print("错误：无效的频率值")
```

## 完整示例：测量仪器控制界面

```python
from adjuster import Panel
import time

class InstrumentController:
    def __init__(self):
        self.measuring = False
        
    def control_callback(self, values):
        changed = values.get('@on_change', [])
        
        # 连接设备
        if values.get('connect@button'):
            device = values.get('device@dropdown')
            print(f"连接到设备: {device}")
        
        # 开始测量
        if values.get('start_measure@button'):
            if not self.measuring:
                self.start_measurement(values)
        
        # 停止测量
        if values.get('stop_measure@button'):
            if self.measuring:
                self.stop_measurement()
        
        # 参数实时更新
        if 'range' in changed:
            print(f"测量范围设置为: {values['range']}")
    
    def start_measurement(self, values):
        self.measuring = True
        range_val = values.get('range')
        resolution = values.get('resolution@int')
        print(f"开始测量 - 范围:{range_val}, 分辨率:{resolution}")
    
    def stop_measurement(self):
        self.measuring = False
        print("停止测量")
    
    def run(self):
        params = {
            # 设备设置
            "device@dropdown": ["DMM1", "DMM2", "Scope1"],
            "connect@button": False,
            
            # 测量参数
            "range": 10.0,
            "resolution@int": 1000,
            "auto_range": True,
            
            # 控制按钮
            "start_measure@button": False,
            "stop_measure@button": False,
            
            # 输出设置
            "save_data": True,
            "output_file@filepath": "",
            
            # 条件控制
            "@param": {
                "range": {"if": "auto_range == False"}
            }
        }
        
        panel = Panel(params, self.control_callback, 
                     name="测量仪器控制", redirect_stdout=True)
        panel.mainloop()

# 运行
if __name__ == "__main__":
    controller = InstrumentController()
    controller.run()
```

## 🔧 模块化开发指南 (重构新特性)

### 模块详解

重构后的adjuster由5个专门的模块组成，每个模块负责特定功能：

#### 1. `adjuster_utils.py` - 工具函数模块
包含通用工具函数和辅助类：

```python
from adjuster_utils import format_value, parse_value_with_unit, apply_unit_conversion

# 数值格式化
formatted = format_value(123.456789)  # "123.46"

# 单位解析
value, unit = parse_value_with_unit("100k")  # (100.0, 'k')

# 单位转换
converted = apply_unit_conversion(1000, "m")  # 1.0
```

**主要功能**:
- `format_value()` - 智能数值格式化
- `parse_value_with_unit()` - 解析带单位的字符串
- `apply_unit_conversion()` - 单位换算
- `calculate_text_width()` - 文本宽度计算
- `RepeatButton` - 可重复触发的按钮类
- `StdoutRedirector` - 输出重定向类

#### 2. `adjuster_widgets.py` - UI控件模块
包含所有用户界面控件：

```python
from adjuster_widgets import Adjuster, TextField, Checkbox, FilePath
import tkinter as tk

# 创建根窗口
root = tk.Tk()

# 使用单独的控件
adjuster = Adjuster(root, "频率", 1000.0, 100.0, 10000.0, 100.0)
textfield = TextField(root, "设备名", "Device1")
checkbox = Checkbox(root, "启用", True)
```

**可用控件**:
- `TextField` - 文本输入框
- `Adjuster` - 数值调节器 (滑块+按钮+输入框)
- `Checkbox` - 复选框
- `FilePath` - 文件选择器
- `FolderPath` - 文件夹选择器
- `Button` - 自定义按钮
- `Dropdown` - 下拉菜单

#### 3. `adjuster_plots.py` - 绘图模块
专门处理matplotlib绘图集成：

```python
from adjuster_plots import Plotter
import matplotlib.pyplot as plt

# 创建绘图器
plotter = Plotter(parent_frame)

# 获取绘图轴
ax = plotter.get_axes()
ax.plot([1, 2, 3], [1, 4, 2])
plotter.update_plot()  # 刷新显示
```

**主要功能**:
- matplotlib与tkinter集成
- 实时绘图更新
- 图形保存功能
- 绘图工具栏

#### 4. `adjuster_core.py` - 核心模块
包含Panel类和主要业务逻辑：

```python
from adjuster_core import Panel

# Panel类包含所有UI管理功能
# 数据绑定、事件处理、窗口管理等
```

**核心功能**:
- 完整的Panel类实现
- UI布局管理
- 数据绑定和事件系统
- 多标签页管理
- 条件显示控制

#### 5. `adjuster.py` - 主API接口
提供向后兼容的统一接口：

```python
# 这个文件重新导出所有功能，保持API兼容性
from adjuster import *  # 和以前完全一样
```

### 模块化开发优势

#### 1. **按需导入，优化性能**
```python
# 只需要工具函数时
from adjuster_utils import format_value, parse_value_with_unit

# 只需要特定控件时  
from adjuster_widgets import Adjuster, TextField

# 只需要绘图功能时
from adjuster_plots import Plotter
```

#### 2. **清晰的功能边界**
- **工具类** → `adjuster_utils`
- **UI控件** → `adjuster_widgets`
- **绘图功能** → `adjuster_plots`
- **核心逻辑** → `adjuster_core`
- **兼容接口** → `adjuster`

#### 3. **便于扩展和维护**
```python
# 添加新的工具函数到 adjuster_utils.py
def my_custom_formatter(value):
    return f"Custom: {value}"

# 添加新的控件到 adjuster_widgets.py
class CustomWidget:
    def __init__(self, master, label):
        # 自定义控件实现
        pass

# 在 adjuster.py 中导出新功能
from adjuster_utils import my_custom_formatter
from adjuster_widgets import CustomWidget
__all__.extend(['my_custom_formatter', 'CustomWidget'])
```

#### 4. **团队协作**
- **前端开发者**: 专注 `adjuster_widgets.py`
- **算法工程师**: 专注 `adjuster_utils.py`
- **可视化专家**: 专注 `adjuster_plots.py`
- **架构师**: 专注 `adjuster_core.py`

### 迁移指南

#### 现有项目 (零修改)
```python
# 代码完全不变，继续使用
from adjuster import Panel, Adjuster, format_value
# 一切正常工作！
```

#### 新项目 (推荐做法)
```python
# 按功能导入，代码更清晰
from adjuster_core import Panel
from adjuster_widgets import Adjuster, TextField, Checkbox
from adjuster_utils import format_value, parse_value_with_unit

# 或者混合使用
from adjuster import Panel  # 主要类仍从主模块导入
from adjuster_utils import format_value  # 工具函数从工具模块导入
```

#### 自定义扩展项目
```python
# 基于特定模块进行扩展
from adjuster_widgets import TextField

class MyCustomTextField(TextField):
    def __init__(self, master, label, default="", validation_func=None):
        super().__init__(master, label, default)
        self.validation_func = validation_func
    
    def validate_input(self, value):
        if self.validation_func:
            return self.validation_func(value)
        return True
```

### 兼容性保证

1. **API兼容性**: 所有原有接口保持不变
2. **功能兼容性**: 所有原有功能完整保留
3. **行为兼容性**: 程序行为与重构前完全一致
4. **数据兼容性**: 配置文件和数据文件格式不变

## 总结

`adjuster.py` 让创建参数调节界面变得非常简单：

1. **定义参数字典** - 描述你需要的界面
2. **编写回调函数** - 响应用户操作  
3. **创建Panel并运行** - 启动界面

### 重构升级带来的好处
- ✅ **更好的代码组织**: 功能模块化，便于理解和维护
- ✅ **更高的开发效率**: 团队可并行开发不同模块
- ✅ **更强的扩展性**: 新功能可在对应模块中轻松添加
- ✅ **更好的性能**: 按需导入，减少内存占用
- ✅ **100%向后兼容**: 现有代码无需任何修改

从简单的例子开始，逐步添加更多功能。记住，复杂的界面也是从简单的参数字典开始的！

现在就试试吧 - 复制第一个例子，运行看看效果！

---

### 📚 相关文档
- `REFACTORING_REPORT.md` - 详细的重构报告
- `adjuster_original.py` - 原始代码备份
- 各模块源码中的详细注释
