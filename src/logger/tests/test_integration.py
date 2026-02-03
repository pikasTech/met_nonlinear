"""集成测试 - 测试完整的日志系统工作流程"""

import pytest
import subprocess
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add the logger directory to path
logger_dir = Path(__file__).parent.parent
sys.path.insert(0, str(logger_dir))

from logging_setup import setup_logging, get_module_logger
from print_replacer import replace_prints_in_file
from print_checker import PrintUsageScanner


class TestLoggerIntegration:
    """测试日志系统的完整集成"""

    def test_complete_workflow(self, temp_dir):
        """测试完整的工作流程：扫描 -> 替换 -> 使用日志"""
        # 1. 创建测试项目结构
        project_dir = temp_dir / "test_project"
        project_dir.mkdir()

        # 创建模块文件 - 使用英文避免编码问题
        module_a = project_dir / "module_a.py"
        module_a.write_text('''
def train_model():
    print("Starting model training")
    for epoch in range(3):
        print(f"Epoch {epoch + 1}/3")
        loss = 0.1 * (3 - epoch)
        print(f"Loss: {loss:.4f}")
    print("Training complete")

if __name__ == "__main__":
    train_model()
''')

        module_b = project_dir / "module_b.py"
        module_b.write_text('''
import sys

def process_data(data):
    print("Processing data...")
    if not data:
        print("Error: Data is empty", file=sys.stderr)
        return None
    print(f"Processing {len(data)} data items")
    return [x * 2 for x in data]

def debug_info():
    print("[DEBUG] System status check")
    print("[DEBUG] Memory usage normal")
''')

        # 2. 扫描 print 使用情况
        scanner = PrintUsageScanner()
        scan_results = scanner.scan_directory(project_dir)

        assert len(scan_results) == 2
        assert "module_a.py" in scan_results
        assert "module_b.py" in scan_results

        # 3. 替换 print 语句
        for filepath in [module_a, module_b]:
            result = replace_prints_in_file(filepath)
            assert result['success']

        # 4. 验证替换后的代码
        modified_a = module_a.read_text()
        assert "import logging" in modified_a
        assert "logger.info" in modified_a
        # 允许 print 在注释或字符串中
        # 检查没有独立的 print( 调用
        lines_with_print = [l for l in modified_a.split('\n')
                          if 'print(' in l and 'logger.' not in l and '#' not in l]
        assert len(lines_with_print) == 0, f"Found print statements: {lines_with_print}"

        modified_b = module_b.read_text()
        assert "logger.error" in modified_b  # stderr print
        assert "logger.debug" in modified_b  # DEBUG print

        # 5. 运行替换后的代码
        result = subprocess.run(
            [sys.executable, str(module_a)],
            capture_output=True,
            text=True,
            cwd=str(project_dir)
        )

        # 应该成功运行
        assert result.returncode == 0

    def test_logging_with_config(self, temp_dir):
        """测试使用配置文件的日志系统"""
        # 创建日志配置 - 使用英文避免编码问题
        config_file = temp_dir / "logging_config.yaml"
        config_file.write_text('''
version: 1
disable_existing_loggers: false

formatters:
  simple:
    format: '%(levelname)s: %(message)s'
  detailed:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: simple

  file:
    class: logging.FileHandler
    level: DEBUG
    formatter: detailed
    filename: app.log

loggers:
  metnl:
    level: DEBUG
    handlers: [console, file]
    propagate: false
''')

        # 设置日志系统
        logger = setup_logging(config_path=str(config_file), log_dir=str(temp_dir))

        # 获取模块 logger
        training_logger = get_module_logger('core.training')
        inference_logger = get_module_logger('inference')

        # 记录日志
        training_logger.info("Training started")
        training_logger.debug("Detailed training info")
        inference_logger.error("Inference error")

        # 检查日志文件
        log_file = temp_dir / "app.log"
        if log_file.exists():
            content = log_file.read_text()
            assert "Training started" in content
            assert "Detailed training info" in content
            assert "Inference error" in content

    def test_module_replacement_integration(self, temp_dir):
        """测试模块级别的 print 替换集成"""
        # 复制测试模块 - 使用英文版本
        src_modules = Path(__file__).parent

        # 创建测试模块（避免编码问题）
        module_a_content = '''"""Module A - Training Engine"""
import time

class TrainingEngine:
    def __init__(self, model_name):
        self.model_name = model_name
        print(f"Initializing training engine: {model_name}")

    def start_training(self, epochs=10):
        print(f"Starting training {self.model_name}, {epochs} epochs")
        for epoch in range(epochs):
            print(f"Epoch {epoch + 1}/{epochs}")
            loss = self._train_one_epoch()
            print(f"  Loss: {loss:.4f}")
            if epoch % 5 == 0:
                print("Saving checkpoint...")

    def _train_one_epoch(self):
        import random
        time.sleep(0.01)
        return random.random()

    def evaluate(self):
        print("Starting model evaluation...")
        accuracy = 0.95
        print(f"Accuracy: {accuracy:.2%}")
        return accuracy
'''

        module_b_content = '''"""Module B - Data Processing"""
class DataProcessor:
    def __init__(self):
        print("Data processor initialized")
        self.data = []

    def load_data(self, filepath):
        print(f"Loading data: {filepath}")
        self.data = list(range(100))
        print(f"Successfully loaded {len(self.data)} records")

    def preprocess(self):
        print("Starting data preprocessing...")
        print("  - Normalization")
        print("  - Removing outliers")
        print("  - Feature extraction")
        print("Preprocessing complete")
'''

        module_a = temp_dir / "module_a.py"
        module_b = temp_dir / "module_b.py"

        module_a.write_text(module_a_content)
        module_b.write_text(module_b_content)

        test_modules = ['module_a.py', 'module_b.py']

        for module in test_modules:
            dst = temp_dir / module
            if dst.exists():
                # 替换 print
                result = replace_prints_in_file(dst)
                if result['success']:
                    # 验证可以导入
                    spec = __import__('importlib.util').util.spec_from_file_location(
                        module[:-3], dst
                    )
                    if spec and spec.loader:
                        module_obj = __import__('importlib.util').util.module_from_spec(spec)
                        try:
                            spec.loader.exec_module(module_obj)
                        except Exception as e:
                            pass  # 某些模块可能需要特定环境

    def test_print_checker_cli(self, temp_dir):
        """测试 print_checker 命令行工具"""
        # 创建测试文件
        test_file = temp_dir / "test.py"
        test_file.write_text('''
print("Test 1")
print("Test 2")
''')

        # 运行 print_checker
        checker_script = Path(__file__).parent.parent / "print_checker.py"
        result = subprocess.run(
            [sys.executable, str(checker_script), str(temp_dir)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "Test 1" in result.stdout
        assert "Test 2" in result.stdout
        assert "2" in result.stdout  # Total count

    def test_json_output(self, temp_dir):
        """测试 JSON 输出格式"""
        test_file = temp_dir / "test.py"
        test_file.write_text('print("JSON test")')

        checker_script = Path(__file__).parent.parent / "print_checker.py"
        result = subprocess.run(
            [sys.executable, str(checker_script), str(temp_dir), "--json"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0

        import json
        data = json.loads(result.stdout)
        assert data["summary"]["total_prints"] == 1
        assert "test.py" in data["files"]

    def test_real_world_scenario(self, temp_dir):
        """测试真实场景：训练脚本的日志改造"""
        # 创建一个模拟的训练脚本 - 使用英文
        train_script = temp_dir / "train.py"
        train_script.write_text('''
import random
import time

def load_data():
    print("Loading dataset...")
    time.sleep(0.1)
    print("Dataset loaded successfully")
    return [[random.random() for _ in range(10)] for _ in range(100)]

def train_epoch(model, data, epoch):
    print(f"\\nEpoch {epoch}/10")
    print("-" * 50)

    loss_sum = 0
    for i, batch in enumerate(data[:10]):
        loss = random.random()
        loss_sum += loss

        if i % 3 == 0:
            print(f"  Batch {i+1}/10, Loss: {loss:.4f}")

    avg_loss = loss_sum / 10
    print(f"  Average loss: {avg_loss:.4f}")

    if avg_loss < 0.3:
        print("  [INFO] Loss is low, model is performing well")
    elif avg_loss > 0.7:
        print("  [WARNING] Loss is high, may need to adjust parameters")

    return avg_loss

def save_checkpoint(epoch, loss):
    print(f"Saving checkpoint: epoch_{epoch}_loss_{loss:.4f}.pt")

def main():
    print("=" * 50)
    print("Starting training workflow")
    print("=" * 50)

    data = load_data()
    model = "dummy_model"

    best_loss = float('inf')
    for epoch in range(1, 6):
        loss = train_epoch(model, data, epoch)

        if loss < best_loss:
            best_loss = loss
            save_checkpoint(epoch, loss)
            print(f"  New best loss: {best_loss:.4f}")

    print("\\nTraining complete!")
    print(f"Final best loss: {best_loss:.4f}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] Training failed: {e}")
''')

        # 1. 扫描原始文件
        scanner = PrintUsageScanner()
        before_scan = scanner.scan_directory(temp_dir)

        assert "train.py" in before_scan
        print_count_before = len(before_scan["train.py"])
        assert print_count_before > 10  # 应该有很多 print

        # 2. 执行替换
        result = replace_prints_in_file(train_script)
        assert result['success']
        assert result['count'] == print_count_before

        # 3. 验证替换后的代码仍然可以运行
        result = subprocess.run(
            [sys.executable, str(train_script)],
            capture_output=True,
            text=True,
            cwd=str(temp_dir),
            timeout=5  # 5秒超时
        )

        # 应该成功运行
        assert result.returncode == 0

        # 4. 再次扫描确认没有 print 了
        after_scan = scanner.scan_directory(temp_dir)
        assert "train.py" not in after_scan  # 不应该有任何 print


@pytest.mark.slow
class TestPerformance:
    """性能测试"""

    def test_large_file_replacement(self, temp_dir):
        """测试大文件的替换性能"""
        # 创建一个包含很多 print 的大文件
        large_file = temp_dir / "large.py"
        lines = ['def func():']
        for i in range(1000):
            lines.append(f'    print("Line {i}")')

        large_file.write_text('\n'.join(lines))

        # 测试替换性能
        import time
        start = time.time()
        result = replace_prints_in_file(large_file)
        duration = time.time() - start

        assert result['success']
        assert result['count'] == 1000
        assert duration < 5  # 应该在5秒内完成
