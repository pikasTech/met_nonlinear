# calibration_analyzer模块测试框架与实践

## 一、测试经验与原则总结

通过对前四轮测试实践（build_test.md到build_test4.md）的分析与学习，我们归纳出以下关键的测试经验和原则：

### 1. 测试设计原则

#### 1.1 测试命名与组织
- **测试文件命名规范**：测试文件必须以`test_`开头，例如`test_wavedata.py`
- **测试方法命名规范**：测试方法必须以`test_`开头，例如`test_load_waveform`
- **测试目录结构**：测试应组织在模块对应的tests目录下，保持清晰的目录结构

#### 1.2 测试功能原则
- **功能单一原则**：每个测试应该只测试一个功能，不要将多个功能混合测试
- **独立性原则**：测试不应依赖于外部环境，如外部网络或API调用
- **时间控制原则**：测试不应耗时过长，对于耗时测试应使用超时机制或放入跳过列表
- **非交互原则**：测试应该能够自动完成，不需要人工干预

#### 1.3 代码不可修改原则
- **源码保护原则**：测试过程中不得修改原始代码
- **测试适应原则**：当测试不通过时，应修改测试代码以适应现有代码，而非修改源码
- **跳过策略原则**：对于无法通过的测试，应使用跳过机制而非强制通过

### 2. 测试技术策略

#### 2.1 测试覆盖率策略
- **覆盖率目标**：应努力达到至少80%的测试覆盖率
- **优先级原则**：优先测试核心功能和关键组件
- **边缘情况覆盖**：确保对边缘情况和异常处理路径进行测试

#### 2.2 测试技术方法
- **单元测试与集成测试结合**：优先编写单元测试，必要时补充集成测试
- **黑盒和白盒测试结合**：根据功能测试与基于代码结构测试相结合
- **参数化测试应用**：使用参数化测试覆盖多种输入组合，减少代码重复
- **模拟对象应用**：使用模拟对象替代外部依赖，使测试更加可控

#### 2.3 测试框架优化
- **超时机制**：为测试添加超时机制，避免死循环或卡死
- **跳过机制**：对于不稳定或依赖外部环境的测试，使用跳过机制
- **测试分组**：根据运行速度或依赖项对测试进行分组

### 3. 解决方案策略

#### 3.1 模块导入问题解决策略
- **动态导入修复**：使用`sys.modules`动态修复导入路径
- **模拟模块策略**：为有问题的模块创建模拟类，保持接口一致
- **条件导入策略**：使用条件导入处理可能失败的导入

#### 3.2 测试稳定性提升策略
- **异常处理增强**：为测试代码添加更多异常处理，提高稳定性
- **灵活断言机制**：使用相对值比较代替绝对值比较，适应不同实现
- **减少实现依赖**：避免对具体实现细节的依赖，使测试更具通用性

## 二、calibration_analyzer测试实施计划

### 1. 项目分析

#### 1.1 核心模块识别
- **数据处理模块**：wavedata.py, waveprocessor.py, dataparser.py
- **分析引擎模块**：analyzer.py, exam_class.py, exam_process.py
- **UI展示模块**：waveviewer.py, adjuster*.py
- **辅助工具模块**：utilities.py, utils.py, config.py

#### 1.2 模块依赖分析
- 识别模块间依赖关系
- 确定测试顺序：基础模块 → 中间模块 → 应用模块
- 确定可独立测试的模块和需要模拟的依赖

### 2. 测试框架设置

#### 2.1 测试目录结构
```
calibration_analyzer/
  └── tests/
      ├── __init__.py           # 测试包初始化
      ├── test_wavedata.py      # 波形数据测试
      ├── test_waveprocessor.py # 波形处理测试
      ├── test_analyzer.py      # 分析器测试
      ├── test_utilities.py     # 工具函数测试
      ├── test_exam_class.py    # 考试类测试
      └── conftest.py           # 测试公共配置和夹具
```

#### 2.2 测试配置
- 配置pytest.ini设置测试参数
- 设置.coveragerc配置覆盖率分析参数
- 创建conftest.py提供通用测试夹具

#### 2.3 测试辅助工具
- 创建模拟数据生成工具
- 设计通用测试基类
- 开发资源清理机制

### 3. 测试用例设计

#### 3.1 wavedata.py测试用例
- 测试WaveData类初始化和基本属性
- 测试WaveRecord类及其功能
- 测试文件加载和保存功能
- 测试数据转换功能（如to_time_series）
- 测试边缘情况（空数据、格式错误等）

#### 3.2 waveprocessor.py测试用例
- 测试WaveProcessor类初始化
- 测试信号生成功能
- 测试频率响应分析功能
- 测试多震级分析功能
- 测试文件操作功能

#### 3.3 analyzer.py测试用例
- 测试ChannelAnalyzeResult类的分析功能
- 测试DataAnalyzeResult类的功能
- 测试DataAnalyzeResultList的操作功能
- 测试相位处理和频谱分析函数

#### 3.4 utilities.py和utils.py测试用例
- 测试工具函数的正确性
- 测试异常处理功能

#### 3.5 exam_class.py测试用例
- 测试TimeSeries类的信号生成功能
- 测试System类及其仿真功能
- 测试不同信号类型的处理

### 4. 测试执行与优化

#### 4.1 测试执行步骤
1. 单独运行每个测试文件，确保功能正确
2. 运行全套测试并收集覆盖率
3. 分析未覆盖的代码路径
4. 添加针对性测试提高覆盖率

#### 4.2 测试优化策略
- 识别并优化耗时测试
- 解决模块间依赖问题
- 增加边缘情况测试
- 添加性能测试（可选）

## 三、实施步骤

### 阶段一：基础设置与框架搭建

1. **创建测试目录结构**
   - 创建calibration_analyzer/tests目录
   - 创建__init__.py文件
   - 创建conftest.py文件

2. **配置测试环境**
   - 设置pytest.ini配置文件
   - 配置.coveragerc文件
   - 创建测试工具函数

### 阶段二：核心模块测试实现

1. **实现WaveData测试**
   - 创建test_wavedata.py
   - 实现WaveData和WaveRecord类测试
   - 测试文件操作功能

2. **实现WaveProcessor测试**
   - 创建test_waveprocessor.py
   - 测试波形处理功能
   - 测试频率分析功能

3. **实现Analyzer测试**
   - 创建test_analyzer.py
   - 测试分析算法功能
   - 测试数据处理功能

### 阶段三：辅助模块测试实现

1. **实现工具类测试**
   - 创建test_utilities.py
   - 测试各种工具函数

2. **实现配置模块测试**
   - 创建test_config.py
   - 测试配置加载和应用

### 阶段四：集成测试与覆盖率优化

1. **实现端到端测试**
   - 创建test_integration.py
   - 测试完整处理流程

2. **覆盖率优化**
   - 分析覆盖率报告
   - 添加针对性测试
   - 优化测试策略

## 四、测试示例

下面展示一些典型测试用例的实现方式，作为编写测试的参考：

### 1. WaveData测试示例

```python
import unittest
import numpy as np
import tempfile
import os
from calibration_analyzer.wavedata import WaveData, WaveRecord
from calibration_analyzer.exam_class import TimeSeries

class TestWaveData(unittest.TestCase):
    """测试WaveData类的功能"""
    
    def setUp(self):
        """测试前准备环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, "test_wave.wvd")
        
        # 创建测试用的WaveData对象
        self.wave_data = WaveData(description="测试波形", author="Test")
        
        # 创建一些测试用的WaveRecord
        fs = 1000  # 采样率
        t = np.arange(0, 1, 1/fs)
        
        # 创建正弦波记录
        sin_data = np.sin(2 * np.pi * 10 * t).reshape(-1, 1)  # 10Hz正弦波
        self.sin_record = WaveRecord(
            data=sin_data,
            sample_rate=fs,
            channel_names=["Sin10Hz"],
            units="V",
            user_metadata={"frequency": 10}
        )
        
        # 创建方波记录
        square_data = np.sign(np.sin(2 * np.pi * 5 * t)).reshape(-1, 1)  # 5Hz方波
        self.square_record = WaveRecord(
            data=square_data,
            sample_rate=fs,
            channel_names=["Square5Hz"],
            units="V",
            user_metadata={"frequency": 5}
        )
        
        # 添加记录到WaveData
        self.wave_data.add_record(self.sin_record)
        self.wave_data.add_record(self.square_record)
    
    def tearDown(self):
        """测试后清理环境"""
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        os.rmdir(self.temp_dir)
    
    def test_init(self):
        """测试WaveData初始化"""
        self.assertEqual(self.wave_data.description, "测试波形")
        self.assertEqual(self.wave_data.author, "Test")
        self.assertEqual(len(self.wave_data.records), 2)
    
    def test_add_record(self):
        """测试添加记录功能"""
        # 创建新记录
        fs = 1000
        t = np.arange(0, 1, 1/fs)
        tri_data = np.abs((t * 2) % 2 - 1).reshape(-1, 1)  # 1Hz三角波
        tri_record = WaveRecord(
            data=tri_data,
            sample_rate=fs,
            channel_names=["Triangle1Hz"],
            units="V",
            user_metadata={"frequency": 1}
        )
        
        # 添加到WaveData
        old_count = len(self.wave_data.records)
        self.wave_data.add_record(tri_record)
        
        # 验证添加成功
        self.assertEqual(len(self.wave_data.records), old_count + 1)
        self.assertEqual(self.wave_data.records[-1].channel_names[0], "Triangle1Hz")
    
    def test_save_load(self):
        """测试保存和加载功能"""
        # 保存到文件
        self.wave_data.save(self.temp_file)
        self.assertTrue(os.path.exists(self.temp_file))
        
        # 从文件加载
        loaded_data = WaveData.load(self.temp_file)
        
        # 验证加载的数据
        self.assertEqual(loaded_data.description, self.wave_data.description)
        self.assertEqual(loaded_data.author, self.wave_data.author)
        self.assertEqual(len(loaded_data.records), len(self.wave_data.records))
        
        # 验证记录内容
        for i, (orig_rec, loaded_rec) in enumerate(zip(self.wave_data.records, loaded_data.records)):
            self.assertEqual(orig_rec.channel_names, loaded_rec.channel_names)
            self.assertEqual(orig_rec.sample_rate, loaded_rec.sample_rate)
            self.assertEqual(orig_rec.user_metadata.get("frequency"), 
                         loaded_rec.user_metadata.get("frequency"))
            np.testing.assert_array_almost_equal(orig_rec.data, loaded_rec.data)
    
    def test_to_time_series(self):
        """测试WaveRecord转换为TimeSeries功能"""
        # 获取第一条记录
        record = self.wave_data.records[0]
        
        # 转换为TimeSeries
        ts = record.to_time_series(0)  # 使用第一个通道
        
        # 验证转换结果
        self.assertEqual(ts.fs, record.sample_rate)
        self.assertEqual(len(ts.samples), record.time_steps)
        np.testing.assert_array_almost_equal(ts.samples, record.data[:, 0])
```

### 2. Analyzer测试示例

```python
import unittest
import numpy as np
from calibration_analyzer.analyzer import ChannelAnalyzeResult, DataAnalyzeResult
from calibration_analyzer.datastruct import DataRecord

class TestChannelAnalyzeResult(unittest.TestCase):
    """测试ChannelAnalyzeResult类的功能"""
    
    def setUp(self):
        """测试前准备环境"""
        # 创建一个测试信号
        fs = 1000  # 采样率
        t = np.arange(0, 1, 1/fs)
        freq = 10  # 10Hz正弦波
        amplitude = 2.0
        self.test_signal = amplitude * np.sin(2 * np.pi * freq * t)
        
        # 创建ChannelAnalyzeResult对象
        self.analyzer = ChannelAnalyzeResult(self.test_signal, fs)
        
        # 执行FFT分析
        self.analyzer.analyze_fft(freq_select=freq, start_s=0, time_s=1)
    
    def test_analyze_fft(self):
        """测试FFT分析功能"""
        # 验证FFT结果的基本属性
        self.assertTrue(hasattr(self.analyzer, 'fft'))
        self.assertTrue(hasattr(self.analyzer, 'fft_abs'))
        self.assertTrue(hasattr(self.analyzer, 'fft_freq'))
        
        # 验证FFT结果长度
        self.assertEqual(len(self.analyzer.fft), len(self.test_signal))
    
    def test_get_amp(self):
        """测试获取振幅功能"""
        freq = 10
        amp = self.analyzer.get_amp(freq_select=freq)
        
        # 验证计算的振幅与原始信号振幅接近
        # 由于窗口函数和离散性，结果会有一定偏差
        self.assertAlmostEqual(amp, 2.0, delta=0.2)
    
    def test_get_phase(self):
        """测试获取相位功能"""
        freq = 10
        phase = self.analyzer.get_phase(freq_select=freq)
        
        # 验证计算的相位与预期相位接近
        # 由于信号起始点和分析方法，相位可能有偏差
        # 正弦波起始点在0处，理论上相位为-90度
        expected_phase = -90
        self.assertAlmostEqual(phase, expected_phase, delta=10)
```

## 五、测试执行

通过以下步骤执行测试并验证有效性：

1. **单元测试执行**
   ```bash
   # 在项目根目录执行
   python -m pytest calibration_analyzer/tests/
   ```

2. **覆盖率测试执行**
   ```bash
   # 在项目根目录执行
   python -m pytest calibration_analyzer/tests/ --cov=calibration_analyzer --cov-report=html
   ```

3. **覆盖率报告查看**
   - 在浏览器中打开生成的HTML报告(htmlcov/index.html)
   - 分析未覆盖的代码区域
   - 根据报告优化测试策略

## 六、结论与建议

1. **测试框架的持续优化**
   - 根据项目发展不断调整测试策略
   - 将测试融入到开发流程中

2. **测试文档的维护**
   - 建立测试文档，记录测试策略和结果
   - 为新功能添加测试用例的指南

3. **自动化测试集成**
   - 集成到CI/CD流程中
   - 建立定期测试执行机制

通过这些测试实践，我们能确保calibration_analyzer模块的质量和稳定性，同时为后续的开发和维护提供坚实的基础。 