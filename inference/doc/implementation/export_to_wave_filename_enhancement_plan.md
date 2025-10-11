# export_to_wave() 文件名增强计划

## 问题描述
当前 `core/data_processing.py` 中的 `export_to_wave()` 函数使用固定的文件名：
- `dataset_input.wave`
- `dataset_output_original.wave`

这导致不同类型的数据集（MET、PE、Alias、AliasSimu）导出的文件名相同，无法区分数据类型。

## 解决方案

### 1. 修改文件
- **文件路径**: `/mnt/f/Work/met_nonlinear/core/data_processing.py`
- **修改函数**: `Dataset_COMP.export_to_wave()` (第508-629行)

### 2. 具体修改点

#### 修改点1: 文件名生成逻辑 (第612-614行)
**当前代码:**
```python
input_wave_path = os.path.join(output_folder, "dataset_input")
output_ori_wave_path = os.path.join(
    output_folder, "dataset_output_original")
```

**修改后:**
```python
input_wave_path = os.path.join(output_folder, f"dataset_{self.type}_input")
output_ori_wave_path = os.path.join(
    output_folder, f"dataset_{self.type}_output_original")
```

#### 修改点2: 返回路径更新 (第625-626行)
**当前代码:**
```python
result_paths = {
    "input": f"{input_wave_path}.wave",
    "output_original": f"{output_ori_wave_path}.wave"
}
```

**修改后:**
```python
result_paths = {
    "input": f"{input_wave_path}.wave",
    "output_original": f"{output_ori_wave_path}.wave"
}
```
(此处无需修改，因为路径已经在上一步修改)

### 3. 预期效果

修改后，不同数据集类型将生成不同的文件名：
- **MET数据集**: `dataset_MET_input.wave`, `dataset_MET_output_original.wave`
- **PE数据集**: `dataset_PE_input.wave`, `dataset_PE_output_original.wave`
- **Alias数据集**: `dataset_Alias_input.wave`, `dataset_Alias_output_original.wave`
- **AliasSimu数据集**: `dataset_AliasSimu_input.wave`, `dataset_AliasSimu_output_original.wave`

### 4. 数据集类型定义位置
根据代码分析，各数据集类型在以下位置定义：
- `Dataset_COMP_MET`: 第650行 `self.type = 'MET'`
- `Dataset_COMP_PE`: 第872行 `self.type = 'PE'`
- `Dataset_COMP_Alias`: 第1010行 `self.type = 'Alias'`
- `Dataset_COMP_AliasSimu`: 第1132行 `self.type = 'AliasSimu'`

### 5. 兼容性考虑
- 此修改不会影响现有的API接口
- 文件格式保持不变，只是文件名包含数据类型信息
- 所有数据集子类都继承自 `Dataset_COMP`，均有 `self.type` 属性

### 6. 测试计划
修改完成后，使用以下命令测试：
```bash
conda run -n tf26 cli.py -e WNET5q1h2u6l3
```

验证生成的文件名是否包含正确的数据集类型标识。