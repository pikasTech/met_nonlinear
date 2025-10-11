# 频率范围配置改进实施计划 (简化版)

## 📋 项目概述

**目标**: 将系统中硬编码的频率范围配置（如`range(6, n-4)`和各种频率范围）改进为基于Hz的简化配置系统

**原则**:
1. **向后兼容**: 缺省dataset.freq_range_hz时，保持原有`range(6, n-4)`行为
2. **简化配置**: 通过dataset.freq_range_hz配置Hz范围，自动计算频率索引
3. **统一管理**: 统一所有硬编码频率范围，消除不一致性
4. **单一模式**: 避免复杂的双模式切换，简化实现和使用

## 🎯 问题分析

### 当前问题
- **硬编码过度**: `range(6, n-4)`、`freq_range=(5,200)`等硬编码分散在多个文件
- **配置不一致**: 跳过点数存在6与4的不一致问题
- **缺乏统一**: 不同模块使用不同的频率范围配置
- **不可配置**: 无法通过配置文件灵活调整频率范围

### 目标状态
- **简化配置**: 通过dataset.freq_range_hz自动计算频率索引
- **统一管理**: FreqConfigManager统一处理所有频率配置
- **完全兼容**: 缺省配置时保持原有`range(6, n-4)`行为
- **清晰日志**: 详细的配置应用日志信息

## 🗂️ 修改文件清单

### 📌 核心配置文件 (2个文件)

#### 1. **config.py** - Config类扩展
**修改类型**: 扩展  
**修改内容**:
```python
class Config:
    def __init__(self):
        # ... 现有配置保持不变 ...
        
        # 新增dataset配置对象
        self.dataset = {
            # 可选的频率范围配置，Hz单位
            # 缺省时使用传统range(6, n-4)逻辑
            'freq_range_hz': None  # 例如: [10, 128]
        }

# 现有全局配置保持不变
FREQ_START_SKIP = 6
FREQ_END_SKIP = 6  # 注意：统一为6，解决当前4与6的不一致
```

#### 2. **core/freq_config_manager.py** - 新建简化频率配置管理器
**修改类型**: 新建  
**核心功能**:
```python
class FreqConfigManager:
    """频率配置统一管理器 - 简化单模式设计"""
    
    def get_freq_indices(self, config, freq_list, n_total):
        """获取频率索引范围（主要方法）"""
        
    def _calculate_from_hz_range(self, freq_range_hz, freq_list):
        """根据Hz范围自动计算频率索引"""
        
    def _get_legacy_range(self, n_total):
        """传统range(6, n-4)逻辑"""
```

### 🛠️ 训练流程修改 (2个文件)

#### 3. **core/model_engine.py** - 训练频率选择逻辑
**修改点**: 4个位置

**修改点1**: `prepare_training_data()` 方法 (line 122-127)
```python
# 原: self.freq_idx_select = range(6, self.dataset_origin.output_ori.shape[1] - 4)
# 新: 
from core.freq_config_manager import FreqConfigManager
freq_manager = FreqConfigManager()
self.freq_idx_select = freq_manager.get_freq_indices(
    self.config, 
    self.dataset_origin.freq_list, 
    self.dataset_origin.output_ori.shape[1]
)
```

**修改点2**: Alias数据集处理 (line 143)
```python
# 原: freq_indices=range(6, self.dataset_origin.output_ori.shape[1] - 4)  
# 新: freq_indices=self.freq_idx_select
```

**修改点3**: 系统拟合频率范围 (line 493)
```python
# 原: ws_fit = exam_process.ws_system_fit(ws, k=1.0, freq_range=(5, 200))
# 新: 
# 使用配置的Hz范围或默认值
default_range = (5, 200)
freq_range_hz = getattr(self.config, 'dataset', {}).get('freq_range_hz', default_range)
ws_fit = exam_process.ws_system_fit(ws, k=1.0, freq_range=freq_range_hz)
```

**修改点4**: 频率响应测试范围 (line 638)
```python
# 原: freq_range=(10, 128)
# 新: 
default_range = (10, 128)
freq_range = getattr(self.config, 'dataset', {}).get('freq_range_hz', default_range)
```

#### 4. **core/data_processing.py** - 数据处理频率过滤
**修改点**: 9个位置

**主要修改**:
- **数据导出频率过滤** (line 420): `10-128Hz` → 动态范围配置
- **系统拟合频率范围** (line 758, 776, 792等): `(5, 200)` → 统一配置
- **可视化频率范围** (line 818, 1085, 1086等): `(5, 200)` → 配置化

### 📊 可视化模块修改 (2个文件)

#### 5. **visualization/figure_paper.py** - 可视化频率配置
**修改点**: 2个位置

**修改点1**: 线性度计算方法 (line 290)
```python
# 保持现有向后兼容接口，无需修改
# 因为使用的是全局config.FREQ_START_SKIP和config.FREQ_END_SKIP
def compute_linearity_metrics(self, freq_start_skip=config.FREQ_START_SKIP, freq_end_skip=config.FREQ_END_SKIP):
    # 保持原有逻辑不变
```

**修改点2**: 震级频率响应绘图 (line 447) 
```python
# 原: freq_range=(10, 128)
# 新: 
default_range = (10, 128)
# 从传入的config参数获取配置，如无则使用默认值
freq_range = getattr(config, 'dataset', {}).get('freq_range_hz', default_range)
```

#### 6. **visualization/model_analysis.py** - 模型分析频率配置
**修改点**: 1个位置

**修改点1**: 系统拟合频率范围 (line 84)
```python
# 原: system_fit_origin = exam_process.ws_system_fit(system_origin, k=1.0, freq_range=(5, 200))
# 新: 
default_range = (5, 200)
# 如果有config参数传入，尝试获取配置的频率范围
freq_range = getattr(config, 'dataset', {}).get('freq_range_hz', default_range) if 'config' in locals() else default_range
system_fit_origin = exam_process.ws_system_fit(system_origin, k=1.0, freq_range=freq_range)
```

### 🔬 分析模块修改 (2个文件)

#### 7. **calibration_analyzer/exam_process.py** - 校准分析频率配置  
**修改点**: 6个位置  
**修改策略**: 为需要频率范围的函数添加可选的config参数
```python
# 修改函数签名，添加可选config参数
def ws_system_fit(ws, k=1.0, freq_range=(5, 200), config=None):
    if config is not None:
        freq_range = getattr(config, 'dataset', {}).get('freq_range_hz', freq_range)
    # ... 原有逻辑 ...
```

#### 8. **models/iirlnrnn.py** - 模型频率配置
**修改点**: 15个位置  
**修改策略**: 类似exam_process.py，为函数添加可选config参数
```python
# 为涉及freq_range的函数添加config参数支持
def function_with_freq_range(param1, freq_range=(5, 200), config=None):
    if config is not None:
        freq_range = getattr(config, 'dataset', {}).get('freq_range_hz', freq_range)
    # ... 原有逻辑 ...
```

## 🔧 实施步骤

### Phase 1: 基础架构 (优先级: 🔴 高)
**预计时间**: 1-2小时
**风险等级**: 🟢 低风险

**任务列表**:
1. ✅ **新建** `core/freq_config_manager.py` 
   - 实现简化的FreqConfigManager类
   - 实现get_freq_indices()主方法
   - 添加Hz范围计算和传统range逻辑
   
2. ✅ **修改** `config.py`
   - 在Config.__init__()中添加dataset对象
   - dataset.freq_range_hz默认为None
   - 保持所有现有配置不变

**验收标准**:
- FreqConfigManager基本功能测试通过
- 缺省配置时行为与原来完全一致
- 配置了freq_range_hz时能正确计算索引

### Phase 2: 训练流程 (优先级: 🔴 高)
**预计时间**: 2-3小时  
**风险等级**: 🟡 中等风险

**任务列表**:
3. ✅ **修改** `core/model_engine.py`
   - 修改点1-2：使用FreqConfigManager替换range(6, n-4)
   - 修改点3-4：系统拟合和频率响应使用配置的Hz范围
   - 保持向后兼容接口
   
4. ✅ **修改** `core/data_processing.py` 
   - 9个修改点：将硬编码频率范围改为从config读取
   - 保持默认值不变，仅增加配置支持
   - 添加配置应用日志

**验收标准**:
- 训练流程完全正常
- 缺省时行为与原来一致
- 配置生效时能正确应用新的频率范围

### Phase 3: 可视化分析 (优先级: 🟡 中)
**预计时间**: 1-2小时
**风险等级**: 🟢 低风险

**任务列表**:
5. ✅ **修改** `visualization/figure_paper.py`
   - 修改点1：保持现有compute_linearity_metrics()接口不变
   - 修改点2：频率响应绘图支持config.dataset.freq_range_hz
   
6. ✅ **修改** `visualization/model_analysis.py`
   - 1个修改点：系统拟合支持配置的频率范围

**验收标准**:
- 可视化图表正常生成
- 支持配置的频率范围
- 向后兼容确认

### Phase 4: 分析模块 (优先级: 🟡 低)
**预计时间**: 2-3小时
**风险等级**: 🟢 低风险

**任务列表**:
7. ✅ **修改** `calibration_analyzer/exam_process.py`
   - 6个修改点：为相关函数添加可选config参数
   - 保持现有接口完全兼容
   
8. ✅ **修改** `models/iirlnrnn.py`
   - 15个修改点：为涉及频率范围的函数添加config支持
   - 保持默认参数不变，仅增加配置能力

**验收标准**:
- 分析功能正常
- 配置支持生效
- 现有调用方式完全不受影响

## 📋 配置示例

### 传统模式 (向后兼容)
**项目config.json**: 缺省dataset对象或dataset.freq_range_hz字段
```json
{
    "dataset_type": "MET",
    "sample_rate": 2000
    // 缺省dataset配置，使用传统range(6, n-4)
}
```

**行为**: 完全保持当前系统行为，`range(6, n-4)`等硬编码逻辑继续生效

### 简化配置模式 (新功能)  
**项目config.json**: 配置dataset.freq_range_hz
```json
{
    "dataset_type": "MET",
    "sample_rate": 2000,
    "dataset": {
        "freq_range_hz": [10, 128]
    }
}
```

**行为**: 
- 自动根据10-128Hz范围计算频率索引
- 统一所有模块使用配置的频率范围
- 提供详细的配置应用日志信息

## ⚡ 关键特性

### 🔄 简化计算逻辑
```python
def get_freq_indices(self, config, freq_list, n_total):
    """
    根据配置获取频率索引范围
    
    逻辑:
    1. 检查config.dataset.freq_range_hz是否存在
    2. 存在: 根据Hz范围计算索引 (find_indices_by_hz)
    3. 不存在: 使用传统range(6, n-4)逻辑
    
    示例:
    config.dataset.freq_range_hz = [10, 128]
    freq_list = [5,10,15,20,...,200]
    输出: range(1, 25)  # 10Hz对应索引1, 128Hz对应索引24
    """
```

### 📊 配置验证
- ✅ 验证频率范围是否在数据集范围内
- ✅ 检查配置一致性和合理性
- ✅ 提供详细的警告和建议
- ✅ 自动fallback到安全配置

### 📝 日志提示示例
```
INFO: 检测到dataset.freq_range_hz配置: [10, 128]Hz
INFO: 数据集频率范围: 5Hz - 200Hz (共40个频率点)
INFO: 计算得出频率索引范围: range(1, 25)
INFO: 有效频率点数: 24 (从10Hz到128Hz)

# 或缺省配置时:
INFO: 未配置dataset.freq_range_hz，使用传统range(6, 36)
INFO: 传统频率配置: 跳过前6个和后4个频率点
```

## ✅ 验证计划

### 兼容性验证
- [ ] **传统模式测试**: 确保缺省dataset.freq_range_hz时行为与原来完全一致
- [ ] **配置生效测试**: 验证配置了freq_range_hz时能正确计算和应用
- [ ] **项目无影响测试**: 确保现有项目config.json无需任何修改即可正常工作

### 功能验证  
- [ ] **Hz计算测试**: 验证Hz范围到索引转换的准确性
- [ ] **边界处理测试**: 测试超出数据集范围的配置处理
- [ ] **性能测试**: 确保FreqConfigManager调用开销很小
- [ ] **日志完整测试**: 确保配置应用过程有清晰日志

### 集成验证
- [ ] **端到端测试**: 完整训练流程验证
- [ ] **多配置测试**: 不同配置组合的功能测试
- [ ] **回滚测试**: 验证配置回滚的有效性

## 🔍 风险评估与缓解

### 风险等级: 🟢 低风险  

#### 主要风险点
1. **训练流程影响**: 频率索引计算修改可能影响模型训练
   - **缓解**: 缺省时完全保持原有逻辑，分阶段验证
   
2. **配置理解**: 用户可能不理解Hz范围配置  
   - **缓解**: 详细的配置示例和日志说明

3. **计算错误**: Hz到索引转换可能有边界错误
   - **缓解**: 充分的单元测试，边界情况处理

#### 回滚策略
- **配置回滚**: 删除config.json中的dataset.freq_range_hz即可
- **代码回滚**: 每个Phase独立，影响范围清晰
- **简单验证**: 对比缺省配置下的行为是否一致

## 📈 预期效果

### 短期效果 (Phase 1-2完成后)
- ✅ 消除核心训练流程的硬编码range(6, n-4)问题
- ✅ 提供简单直观的Hz范围配置能力 
- ✅ 保持100%向后兼容性

### 长期效果 (全部Phase完成后)
- ✅ 统一所有频率相关配置为单一来源
- ✅ 提供用户友好的Hz范围配置方式
- ✅ 建立清晰的配置架构
- ✅ 显著提升系统可配置性和易用性

## 📚 相关文档

- **技术背景**: [数据集频率范围配置系统调查报告](../research/frequency_range_config_investigation_report.md)
- **详细设计**: [FreqConfigManager设计文档](../design/freq_config_manager_design.md) (待创建)
- **测试计划**: [频率配置测试方案](../testing/frequency_config_test_plan.md) (待创建)

---

**计划状态**: 📋 待实施  
**创建时间**: 2025-01-06  
**预计完成**: 2025-01-08  
**负责人**: 系统开发团队