# 推理功能分离修改计划 V2

## 目标
- `-i` 参数**只负责生成推理数据**，不进行误差分析
- 新增独立参数进行误差分析

## 修改方案

### 1. 命令行参数设计

- `-i` : 仅执行推理数据生成（改变现有行为）
- `-a` : 执行误差分析（analyze）- 新增参数

### 2. 代码修改详情

#### A. cli.py 主函数修改（行 689-691 附近）
```python
# 现有代码
if '-i' in sys.argv:
    task_type = 'inference'

# 修改为
if '-i' in sys.argv:
    task_type = 'inference'

if '-a' in sys.argv:
    task_type = 'analyze'
```

#### B. 拆分 run_inference_analysis 为两个独立方法

**方法1: run_inference_generation（新增）**
```python
def run_inference_generation(self):
    """
    仅运行推理数据生成
    """
    print(f'🔍 推理数据生成项目: {self.project_name}')
    
    # 前置条件验证
    self._validate_inference_prerequisites()
    
    # 准备目录
    inference_data_dir = f'{self.checkpoint_dir}/inference'
    os.makedirs(inference_data_dir, exist_ok=True)
    
    # 检查是否已有数据
    has_existing_data = self._check_existing_inference_data(inference_data_dir)
    
    if has_existing_data:
        print("⚠️  已存在推理数据。如需重新生成，请先删除 inference 目录")
        return
    
    print("📊 开始生成推理数据...")
    self._generate_inference_data(inference_data_dir)
    print("✅ 推理数据生成完成")
```

**方法2: run_error_analysis（新增）**
```python
def run_error_analysis(self):
    """
    仅运行误差分析（要求推理数据已存在）
    """
    print(f'🔬 误差分析项目: {self.project_name}')
    
    # 准备目录
    inference_data_dir = f'{self.checkpoint_dir}/inference'
    
    # 检查数据是否存在
    if not os.path.exists(inference_data_dir) or not self._check_existing_inference_data(inference_data_dir):
        raise FileNotFoundError(
            f"未找到推理数据文件。\n"
            f"请先使用 -i 参数生成推理数据：python cli.py -i {self.project_name}"
        )
    
    # 执行误差分析
    print("🔬 开始误差分析...")
    analysis_results = self._analyze_inference_errors(inference_data_dir)
    
    # 生成分析报告
    self._generate_analysis_report(analysis_results, inference_data_dir)
    print("✅ 误差分析完成")
```

**方法3: 保留但废弃 run_inference_analysis（为了兼容性）**
```python
def run_inference_analysis(self):
    """
    运行推理分析（已废弃，请使用 run_inference_generation 和 run_error_analysis）
    
    为了向后兼容性保留此方法，但建议分别使用：
    - run_inference_generation() 生成推理数据
    - run_error_analysis() 进行误差分析
    """
    import warnings
    warnings.warn(
        "run_inference_analysis 已废弃。请使用 -i 生成数据，-a 进行分析。",
        DeprecationWarning,
        stacklevel=2
    )
    
    # 执行原有的完整流程
    self.run_inference_generation()
    self.run_error_analysis()
```

#### C. 主函数任务处理修改（行 756-765）
```python
# 现有代码
elif task_type == 'inference':
    try:
        project = ProjectManager(project_path)
        project.run_inference_analysis()
        if len(project_names) == 1:
            plt.show()
    except Exception as e:
        print(f"Error occurred while running inference analysis for project '{project_name}': {e}")
        traceback.print_exc()
        continue

# 修改为
elif task_type == 'inference':
    try:
        project = ProjectManager(project_path)
        project.run_inference_generation()  # 只生成数据
        if len(project_names) == 1:
            plt.show()
    except Exception as e:
        print(f"Error occurred while running inference for project '{project_name}': {e}")
        traceback.print_exc()
        continue

elif task_type == 'analyze':
    try:
        project = ProjectManager(project_path)
        project.run_error_analysis()  # 只分析误差
        if len(project_names) == 1:
            plt.show()
    except Exception as e:
        print(f"Error occurred while analyzing project '{project_name}': {e}")
        traceback.print_exc()
        continue
```

### 3. 使用示例

```bash
# 步骤1：生成推理数据
python cli.py -i WNET5q0.5h2u6l4

# 步骤2：分析误差
python cli.py -a WNET5q0.5h2u6l4

# 可以重复执行分析而不重新生成数据
python cli.py -a WNET5q0.5h2u6l4
```

### 4. 优势

1. **职责单一**：
   - `-i` 只负责推理生成
   - `-a` 只负责误差分析
   - 每个参数的行为明确且一致

2. **灵活性高**：
   - 可以多次分析而不重新生成数据
   - 便于调试和优化分析算法
   - 可以在不同时间执行不同步骤

3. **代码清晰**：
   - 两个独立的方法，职责分明
   - 更容易维护和扩展

### 5. 影响评估

**需要更新的地方**：
1. 用户文档：说明 `-i` 行为的改变
2. 自动化脚本：如果有脚本依赖 `-i` 的完整行为，需要更新为 `-i` 后跟 `-a`

**向后兼容性考虑**：
- 保留了 `run_inference_analysis()` 方法，带有废弃警告
- 老代码直接调用该方法仍能工作，只是会显示警告

## 实施步骤

1. 添加 `-a` 参数支持（5分钟）
2. 拆分 `run_inference_analysis` 为两个方法（15分钟）
3. 更新主函数的任务处理逻辑（5分钟）
4. 测试新的工作流程（10分钟）
5. 更新相关文档（5分钟）

总计：约40分钟完成全部修改和测试。