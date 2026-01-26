import json
import data_utils.myjson as myjson
import os
import portalocker  # 跨平台文件锁
import time


class TrainingStateManager:
    """统一管理训练状态的类，使用JSON文件作为状态存储"""

    def __init__(self, project_name, checkpoint_dir=None):
        self.project_name = project_name
        self.checkpoint_dir = checkpoint_dir or 'checkpoints'
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        self.state_file = os.path.join(
            self.checkpoint_dir, f"training_state.json")
        # 初始化或加载已有状态
        self.initialize_state()

    def initialize_state(self):
        """初始化训练状态文件或加载已有文件"""
        if os.path.exists(self.state_file):
            self.load_state()
        else:
            # 创建新的状态文件
            self.state = {
                "completed_epoch": 0,
                "min_loss": float('inf'),
                "min_val_loss": float('inf'),
                "current_epoch": 0,
                "model_name": self.project_name,
                "training_alive": False,
                "timestamp": myjson.format_timestamp_number(time.time()),
                "best_weights_file": os.path.join(self.checkpoint_dir, f"{self.project_name}_best_weights.h5"),
                "best_val_weights_file": os.path.join(self.checkpoint_dir, f"{self.project_name}_best_val_weights.h5"),
            }
            self.save_state()

    def load_state(self):
        """从文件加载训练状态"""
        try:
            with portalocker.Lock(self.state_file, 'r') as f:
                self.state = json.load(f)
            return True
        except Exception as e:
            print(f"加载训练状态失败: {e}")
            self.state = {}
            return False

    def save_state(self):
        """保存训练状态到文件"""
        # 更新时间戳
        self.state['timestamp'] = myjson.format_timestamp_number(time.time())

        try:
            with portalocker.Lock(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            return True
        except Exception as e:
            print(f"保存训练状态失败: {e}")
            return False

    def update_state(self, **kwargs):
        """更新状态中的特定字段"""
        self.load_state()  # 确保使用最新状态
        for key, value in kwargs.items():
            self.state[key] = value
        if not self.save_state():
            print(f"更新状态失败: {kwargs}")

    def get_state(self, key, default=None):
        """获取特定状态值"""
        self.load_state()  # 确保使用最新状态
        return self.state.get(key, default)

    def __getitem__(self, key):
        """通过方括号获取状态值: state_manager['key']"""
        return self.get_state(key)

    def __setitem__(self, key, value):
        """通过方括号设置状态值: state_manager['key'] = value"""
        self.update_state(**{key: value})

    def __contains__(self, key):
        """支持 'in' 操作符: 'key' in state_manager"""
        return key in self.state

    def keys(self):
        """返回所有状态键"""
        self.load_state()  # 确保使用最新状态
        return self.state.keys()

    def items(self):
        """返回所有状态键值对"""
        self.load_state()  # 确保使用最新状态
        return self.state.items()

    # 支持 get 方法，和 dict 类似
    def get(self, key, default=None):
        return self.get_state(key, default)
