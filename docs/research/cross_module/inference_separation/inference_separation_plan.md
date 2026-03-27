# 推理功能分离修改计划

## 目标
将 `-i` 参数的混合行为分离，使推理生成和误差分析成为独立的操作。

## 现状分析

### 当前行为
- `-i` 参数触发 `run_inference_analysis()` 方法
- 该方法会自动判断是否有数据，没有则生成，有则分析
- 用户无法控制只执行其中一个操作

### 问题
1. 行为不一致：同一个参数在不同情况下做不同的事
2. 无法单独执行推理生成或误差分析
3. 调试困难：无法重复执行某一步骤

## 修改方案

### 1. 新增命令行参数（最小改动）

**保持向后兼容性**：
- `-i` : 保持当前行为（生成+分析），确保现有脚本不会破坏
- `-ig` : 仅执行推理生成（inference generate）
- `-ia` : 仅执行误差分析（inference analyze）

### 2. 代码修改详情

#### A. cli.py 主函数修改（行 689-691 附近）
```python
# 现有代码
if '-i' in sys.argv:
    task_type = 'inference'

# 修改为
if '-i' in sys.argv:
    task_type = 'inference'
    inference_mode = 'both'  # 默认行为
elif '-ig' in sys.argv:
    task_type = 'inference' 
    inference_mode = 'generate'
elif '-ia' in sys.argv:
    task_type = 'inference'
    inference_mode = 'analyze'
```

#### B. 修改 run_inference_analysis 方法签名（行 283）
```python
# 现有
def run_inference_analysis(self):

# 修改为
def run_inference_analysis(self, mode='both'):
    """
    运行推理分析
    
    参数:
        mode: 'both' - 生成数据并分析（默认）
              'generate' - 仅生成推理数据
              'analyze' - 仅分析已有数据
    """
```

#### C. 修改 run_inference_analysis 方法逻辑（行 303-318）
```python
def run_inference_analysis(self, mode='both'):
    """运行推理分析"""
    print(f'🔍 推理分析项目: {self.project_name}')
    
    # 前置条件验证
    self._validate_inference_prerequisites()
    
    # 准备目录
    inference_data_dir = f'{self.checkpoint_dir}/inference'
    os.makedirs(inference_data_dir, exist_ok=True)
    
    # 根据模式执行不同操作
    if mode in ['both', 'generate']:
        # 检查是否已有数据
        has_existing_data = self._check_existing_inference_data(inference_data_dir)
        
        if not has_existing_data:
            print("📊 未找到推理数据，开始生成...")
            self._generate_inference_data(inference_data_dir)
            print("✅ 推理数据生成完成")
        else:
            if mode == 'generate':
                print("⚠️  已存在推理数据，跳过生成。如需重新生成，请先删除 inference 目录")
            else:
                print("📂 发现已有推理数据，跳过生成步骤")
    
    if mode in ['both', 'analyze']:
        # 检查数据是否存在
        if not self._check_existing_inference_data(inference_data_dir):
            raise FileNotFoundError(
                "未找到推理数据文件。请先使用 -ig 参数生成推理数据。"
            )
        
        # 执行误差分析
        print("🔬 开始误差分析...")
        analysis_results = self._analyze_inference_errors(inference_data_dir)
        
        # 生成分析报告
        self._generate_analysis_report(analysis_results, inference_data_dir)
        print("✅ 推理分析完成")
```

#### D. 调用处修改（行 758-759）
```python
# 现有
project = ProjectManager(project_path)
project.run_inference_analysis()

# 修改为
project = ProjectManager(project_path)
project.run_inference_analysis(mode=inference_mode)
```

### 3. 使用示例

```bash
# 传统行为（保持兼容）
python cli.py -i WNET5q0.5h2u6l4

# 仅生成推理数据
python cli.py -ig WNET5q0.5h2u6l4

# 仅分析误差（要求数据已存在）
python cli.py -ia WNET5q0.5h2u6l4
```

### 4. 优势

1. **最小化修改**：
   - 只需修改约20行代码
   - 不影响其他功能模块
   - 保持所有现有功能

2. **向后兼容**：
   - `-i` 参数行为完全不变
   - 现有脚本和工作流程不受影响

3. **清晰的职责分离**：
   - 推理生成和误差分析成为独立操作
   - 便于调试和重复执行

4. **扩展性好**：
   - 未来可以轻松添加更多推理相关的子命令
   - 模式参数使得功能扩展更加灵活

## 实施步骤

1. 修改命令行参数解析（5分钟）
2. 修改 `run_inference_analysis` 方法（10分钟）
3. 测试三种模式的行为（10分钟）
4. 更新帮助文档（5分钟）

总计：约30分钟完成全部修改和测试。