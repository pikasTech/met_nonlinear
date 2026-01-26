# 推理Wave集成实施指南

## 快速实施清单

基于简化的实现方案：只查找 `dataset_{TYPE}_output_original.wave` 文件。

### 第一步：修改 InferenceManager._find_input_file()

**文件**: `inference/manager.py`

**修改位置**: 第182行 `_find_input_file` 方法

**替换整个方法**:
```python
def _find_input_file(self) -> str:
    """
    查找推理输入文件
    只查找 data/wave_output/dataset_{TYPE}_output_original.wave
        
    Returns:
        str: wave文件路径
        
    Raises:
        FileNotFoundError: 文件不存在时报错并提示使用 -w 生成
    """
    # 构建目标文件路径
    wave_output_dir = os.path.join(self.project_path, "data", "wave_output")
    dataset_type = self.config.dataset_type
    target_file = f"dataset_{dataset_type}_output_original.wave"
    target_path = os.path.join(wave_output_dir, target_file)
    
    # 检查文件是否存在
    if os.path.exists(target_path):
        relative_path = os.path.relpath(target_path, self.project_path)
        self.logger.info(f"找到推理输入文件: {relative_path}")
        print(f"✓ 使用wave文件: {relative_path}")
        return target_path
    
    # 文件不存在，生成有用的错误信息
    project_name = os.path.basename(self.project_path)
    
    error_msg = f"未找到推理输入文件: {target_file}\n"
    
    if not os.path.exists(wave_output_dir):
        error_msg += f"\nwave输出目录不存在: {wave_output_dir}\n"
    else:
        # 列出目录中的wave文件
        wave_files = [f for f in os.listdir(wave_output_dir) if f.endswith('.wave')]
        if wave_files:
            error_msg += f"\nwave输出目录中找到以下文件:\n"
            for f in wave_files:
                error_msg += f"  - {f}\n"
            error_msg += f"\n但需要的是: {target_file}\n"
        else:
            error_msg += f"\nwave输出目录为空\n"
    
    error_msg += f"\n请先运行以下命令生成wave数据:\n"
    error_msg += f"  python cli.py -w {project_name}\n"
    
    raise FileNotFoundError(error_msg)
```

### 第二步：修改调用处

由于删除了 `default_path` 参数，需要修改所有调用 `_find_input_file` 的地方：

**文件**: `inference/manager.py`

**修改位置**: `run_inference` 方法（约第90行）和 `_generate_inference_data` 方法（约第160行）

```python
# run_inference 方法中
try:
    input_wave = self._find_input_file()  # 删除参数
except FileNotFoundError as e:
    print(f"\n❌ 推理失败")
    print(str(e))
    return  # 直接返回，不继续执行

# _generate_inference_data 方法中
input_wave = self._find_input_file()  # 删除参数
```

### 第三步：删除相关配置（可选）

由于不再支持自定义输入路径，可以从配置中删除相关字段：

**文件**: `config.py`

**删除属性**:
```python
# 删除这行（如果存在）
inference_input_path: str = "inference/temp/dataset_input.wave"
```

### 注意事项

这个简化方案：
- **不需要**修改 Config 类
- **不需要**添加新的配置项
- **不支持**回退到旧的默认路径
- **强制要求**先运行 `-w` 生成wave数据

## 测试验证

### 1. 正常流程测试

```bash
# 步骤1：生成wave数据
python cli.py -w WNET5q1h2u6l3

# 步骤2：运行推理（应该成功）
python cli.py -i WNET5q1h2u6l3
# 预期输出：
# ✓ 使用wave文件: data/wave_output/dataset_MET_output_original.wave
# 开始推理...
```

### 2. 错误场景测试

```bash
# 场景1：没有生成wave文件
rm -rf projects/WNET5q1h2u6l3/data/wave_output
python cli.py -i WNET5q1h2u6l3
# 预期输出：
# ❌ 推理失败
# 未找到推理输入文件: dataset_MET_output_original.wave
# wave输出目录不存在: projects/WNET5q1h2u6l3/data/wave_output
# 请先运行以下命令生成wave数据:
#   python cli.py -w WNET5q1h2u6l3

# 场景2：wave文件类型不匹配
# （例如生成了dataset_COMP_output_original.wave，但配置是MET）
python cli.py -i WNET5q1h2u6l3
# 预期输出：
# ❌ 推理失败
# 未找到推理输入文件: dataset_MET_output_original.wave
# wave输出目录中找到以下文件:
#   - dataset_COMP_output_original.wave
#   - dataset_COMP_input.wave
# 但需要的是: dataset_MET_output_original.wave
# 请先运行以下命令生成wave数据:
#   python cli.py -w WNET5q1h2u6l3
```

### 3. 验证点

- [x] 只查找 `dataset_{TYPE}_output_original.wave` 文件
- [x] 文件不存在时报错并提示使用 `-w`
- [x] 错误信息包含具体的文件名和命令
- [x] 成功时显示使用的文件路径
- [x] 不再支持旧的默认路径

## 实施影响

### 破坏性变更

这个简化方案是**破坏性变更**：
- 不再支持 `inference/temp/dataset_input.wave`
- 必须先运行 `-w` 生成wave数据
- 不支持自定义输入路径

### 优点

1. **实现极简**：只需修改一个方法
2. **逻辑清晰**：没有复杂的回退机制
3. **错误明确**：用户立即知道需要做什么
4. **强制规范**：确保使用统一的数据流程

### 缺点

1. **不兼容旧项目**：旧项目需要先运行 `-w`
2. **灵活性降低**：不支持自定义输入
3. **依赖性增加**：推理依赖于wave生成

## 迁移建议

对于现有项目：
```bash
# 一次性迁移命令
for project in projects/*; do
    if [ -d "$project" ]; then
        echo "迁移 $(basename $project)..."
        python cli.py -w $(basename $project)
    fi
done
```

## 预期效果

```bash
# 成功案例
$ python cli.py -i WNET5q1h2u6l3
✓ 使用wave文件: data/wave_output/dataset_MET_output_original.wave
开始神经网络推理...

# 失败案例
$ python cli.py -i WNET5q1h2u6l3
❌ 推理失败
未找到推理输入文件: dataset_MET_output_original.wave

wave输出目录不存在: projects/WNET5q1h2u6l3/data/wave_output

请先运行以下命令生成wave数据:
  python cli.py -w WNET5q1h2u6l3
```