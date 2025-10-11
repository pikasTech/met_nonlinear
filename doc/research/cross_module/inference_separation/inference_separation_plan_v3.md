# 推理功能分离修改计划 V3（直接废弃原方法）

## 目标
- `-i` 参数**只负责生成推理数据**
- 新增 `-a` 参数进行误差分析
- **直接删除** `run_inference_analysis` 方法

## 修改方案

### 1. 命令行参数设计

- `-i` : 仅执行推理数据生成
- `-a` : 执行误差分析（analyze）

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

#### B. 删除 run_inference_analysis，新增两个方法

**删除方法（行 283-318）**：
```python
# 完全删除 run_inference_analysis 方法
```

**新增方法1: run_inference（原 run_inference_analysis 改名）**
```python
def run_inference(self):
    """
    运行推理数据生成
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

**新增方法2: analyze_errors（新增）**
```python
def analyze_errors(self):
    """
    运行误差分析（要求推理数据已存在）
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
        project.run_inference()  # 新方法名
        if len(project_names) == 1:
            plt.show()
    except Exception as e:
        print(f"Error occurred while running inference for project '{project_name}': {e}")
        traceback.print_exc()
        continue

elif task_type == 'analyze':
    try:
        project = ProjectManager(project_path)
        project.analyze_errors()  # 新方法
        if len(project_names) == 1:
            plt.show()
    except Exception as e:
        print(f"Error occurred while analyzing project '{project_name}': {e}")
        traceback.print_exc()
        continue
```

### 3. 方法名调整说明

- `run_inference_analysis` → **删除**
- 新增 `run_inference`：只负责推理数据生成
- 新增 `analyze_errors`：只负责误差分析
- 保持私有方法不变：
  - `_validate_inference_prerequisites`
  - `_check_existing_inference_data`
  - `_generate_inference_data`
  - `_analyze_inference_errors`
  - `_generate_analysis_report`
  - `_generate_visualization`
  - `_combine_layer_outputs`
  - `_get_timestamp`

### 4. 使用示例

```bash
# 步骤1：生成推理数据
python cli.py -i WNET5q0.5h2u6l4

# 步骤2：分析误差
python cli.py -a WNET5q0.5h2u6l4

# 错误示例：没有数据就分析
python cli.py -a WNET5q0.5h2u6l4
# 输出：FileNotFoundError: 未找到推理数据文件。
#       请先使用 -i 参数生成推理数据：python cli.py -i WNET5q0.5h2u6l4
```

### 5. 影响和注意事项

**破坏性改变**：
- 任何直接调用 `run_inference_analysis()` 的代码都会报错
- 使用 `-i` 参数的脚本行为会改变（不再包含分析）

**需要更新的地方**：
1. 所有调用 `run_inference_analysis()` 的代码
2. 依赖 `-i` 完整功能的自动化脚本
3. 用户文档和使用说明

### 6. 实施步骤

1. 添加 `-a` 参数支持（2分钟）
2. 删除 `run_inference_analysis` 方法（1分钟）
3. 新增 `run_inference` 和 `analyze_errors` 方法（10分钟）
4. 更新主函数的任务处理逻辑（5分钟）
5. 搜索并更新所有调用旧方法的地方（10分钟）
6. 测试新的工作流程（10分钟）

总计：约38分钟完成全部修改和测试。

### 7. 代码简洁性提升

通过这次修改，代码结构更加清晰：
- 每个方法职责单一
- 方法名更直观（`run_inference` vs `analyze_errors`）
- 用户使用更明确（`-i` 推理，`-a` 分析）