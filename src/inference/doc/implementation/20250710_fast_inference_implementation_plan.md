# 快速推理功能实施计划

**日期**: 2025-07-10  
**方案**: 命令行参数控制方案  
**命令**: `python cli.py -i --quick PROJECT_NAME` 或 `python cli.py -i -q PROJECT_NAME`

## 1. 命令行设计

### 1.1 新增参数
- **长参数**: `--quick`
- **短参数**: `-q` (小写q，表示Quick inference，与 -f 有明显区分)
- **用法示例**:
  ```bash
  # 标准推理
  python cli.py -i PROJECT_NAME
  
  # 快速推理（只加载最小最大震级）
  python cli.py -i --quick PROJECT_NAME
  python cli.py -i -q PROJECT_NAME
  
  # 快速推理 + 强制重新生成
  python cli.py -i --quick -f PROJECT_NAME
  python cli.py -i -q -f PROJECT_NAME
  ```

## 2. 具体修改计划

### 2.1 修改 `cli.py`

**位置**: 主程序入口，约396-406行附近

**修改内容**:
```python
# 在现有参数解析部分添加
if '-i' in sys.argv:
    task_type = 'inference'

# 新增：检测快速推理模式
quick_inference = '--quick' in sys.argv or '-q' in sys.argv

# 修改推理执行部分（约473-482行）
elif task_type == 'inference':
    try:
        project = ProjectManager(project_path)
        project.run_inference(force=force_mode, quick=quick_inference)  # 传递quick参数
        if len(project_names) == 1:
            plt.show()
    except Exception as e:
        print(f"Error occurred while running inference for project '{project_name}': {e}")
        traceback.print_exc()
        continue
```

### 2.2 修改 `ProjectManager.run_inference()`

**位置**: `cli.py` 约316-318行

**修改内容**:
```python
def run_inference(self, force=False, quick=False):
    """委托给推理管理器"""
    self.inference_manager.run_inference(force=force, quick=quick)
```

### 2.3 修改 `InferenceManager.run_inference()`

**位置**: `inference/manager.py` 约45-93行

**修改内容**:
```python
def run_inference(self, force=False, quick=False):
    """
    运行推理数据生成
    
    参数:
        force: 是否强制重新生成（删除已有数据）
        quick: 是否使用快速模式（只加载最小最大震级）
    """
    print(f'🔍 推理数据生成项目: {self.project_name}')
    if quick:
        print(f'⚡ 快速推理模式：只加载最小和最大震级数据')
    
    # 保存quick模式标志，供后续使用
    self.quick_mode = quick
    
    # ... 其余代码不变
```

### 2.4 修改 `InferenceManager._generate_inference_data()`

**位置**: `inference/manager.py` 约239行附近

**修改内容**:
```python
def _generate_inference_data(self, output_dir):
    """生成推理数据"""
    # ... 前面代码不变
    
    # 创建 ModelEngine 实例时传递quick模式
    model_engine = ModelEngine(
        self.project,
        checkpoint_dir=self.checkpoint_dir,
        quick_inference=self.quick_mode  # 新增参数
    )
    
    # ... 后续代码
```

### 2.5 修改 `ModelEngine.__init__()`

**位置**: `core/model_engine.py` 约17-25行

**修改内容**:
```python
def __init__(self,
             project,
             checkpoint_dir='data',
             quick_inference=False):  # 新增参数
    self.project_name = project.project_name
    self.config: Config = project.config
    self.quick_inference = quick_inference  # 保存快速推理标志
    # ... 其余初始化代码
```

### 2.6 修改 `ModelEngine.load_dataset()`

**位置**: `core/model_engine.py` 约52-81行

**修改内容**:
```python
def load_dataset(self, dataset_type='MET'):
    if dataset_type == 'MET':
        # ... 数据路径检查代码不变
        
        data_info_list = find_data_info(data_path)
        if not data_info_list:
            raise ValueError(
                f"在路径 {data_path} 中未找到任何数据文件！\n"
                f"请确保该目录下存在以 '震级*.analyze.json' 格式命名的数据文件。"
            )
        
        # 根据模式选择sweep_list
        if self.quick_inference:
            # 快速模式：只选择最小和最大震级
            all_magnitudes = [info.magnitude for info in data_info_list]
            min_idx = np.argmin(all_magnitudes)
            max_idx = np.argmax(all_magnitudes)
            sweep_list = [min_idx, max_idx]
            
            print(f"⚡ 快速推理模式已启用")
            print(f"   最小震级: {all_magnitudes[min_idx]:.2f} (索引: {min_idx})")
            print(f"   最大震级: {all_magnitudes[max_idx]:.2f} (索引: {max_idx})")
            print(f"   数据减少: {len(data_info_list)} → 2 个震级")
        else:
            # 标准模式
            sweep_list = range(1, 50, 2)
            print(f"📊 标准模式：加载 {len(list(sweep_list))} 个震级数据")
        
        self.dataset_origin = Dataset_COMP_MET(
            data_info_list,
            self.config.target_sweep,
            sweep_list,
            use_cache=self.config.use_cache_features,
            time_cliped_s=self.config.time_clipped_s,
            fs=self.config.sample_rate
        )
        # ... 其余代码不变
```

### 2.7 修改 `ProjectManager.generate_wave_data()`（可选）

**位置**: `cli.py` 约324-343行

**修改内容**:
```python
def generate_wave_data(self, output_folder=None, compress=True, force=False, quick=False):
    """
    生成波形数据
    
    Args:
        output_folder: 输出目录
        compress: 是否压缩
        force: 是否强制覆盖
        quick: 是否使用快速模式
    """
    from core.wave_generator import DatasetWaveGenerator
    
    # 如果需要支持wave生成的快速模式
    if hasattr(self, '_quick_mode'):
        self._quick_mode = quick
    
    generator = DatasetWaveGenerator(self)
    return generator.generate_wave_data(
        output_folder=output_folder,
        compress=compress,
        force=force
    )
```

## 3. 测试计划

### 3.1 功能测试
```bash
# 1. 测试标准推理
python cli.py -i WNET5q0.5h2u6l4

# 2. 测试快速推理
python cli.py -i --quick WNET5q0.5h2u6l4

# 3. 测试短参数
python cli.py -i -q WNET5q0.5h2u6l4

# 4. 测试组合参数
python cli.py -i --quick -f WNET5q0.5h2u6l4
python cli.py -i -q -f WNET5q0.5h2u6l4
```

### 3.2 验证要点
1. 确认快速模式只加载2个震级
2. 验证推理结果文件正确生成
3. 对比快速模式和标准模式的执行时间
4. 检查生成的wave文件内容

## 4. 错误处理

### 4.1 边界情况
- 数据文件少于2个震级时的处理
- 所有震级值相同时的处理
- 最小最大震级数据损坏时的处理

### 4.2 错误提示
```python
# 在 load_dataset 中添加错误处理
if len(data_info_list) < 2:
    raise ValueError(
        f"快速推理模式需要至少2个震级的数据，"
        f"但只找到 {len(data_info_list)} 个数据文件"
    )
```

## 5. 文档更新

### 5.1 更新 CLAUDE.md
在推理系统部分添加快速模式说明

### 5.2 更新命令行帮助
```python
# 可选：在 cli.py 添加使用说明
if '-h' in sys.argv or '--help' in sys.argv:
    print("推理模式:")
    print("  -i              运行推理")
    print("  -i --quick/-q   快速推理（只使用最小最大震级）")
    print("  -f/--force      强制重新生成")
```

## 6. 实施顺序

1. **第一步**: 修改 `cli.py` 添加参数解析
2. **第二步**: 修改 `ModelEngine` 支持快速加载
3. **第三步**: 修改 `InferenceManager` 传递参数
4. **第四步**: 测试基本功能
5. **第五步**: 添加错误处理和优化
6. **第六步**: 更新文档

## 7. 预期效果

- **性能提升**: 数据加载时间从 ~30秒 减少到 ~3秒
- **内存优化**: 内存使用减少 90%
- **使用简便**: 只需添加 `--quick` 或 `-q` 参数即可启用
- **向后兼容**: 不影响现有标准模式功能