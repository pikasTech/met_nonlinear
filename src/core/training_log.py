import os
import numpy as np
import json
import time
import data_utils.myjson as myjson
import portalocker  # 添加 portalocker 导入


class TrainingLogger:
    # NaN 替代值常量
    NAN_PLACEHOLDER = 1e6  # 使用一个足够大但不会导致溢出的值

    def __init__(self, checkpoint_path):
        self.checkpoint_path = checkpoint_path
        log_file = os.path.join(checkpoint_path, "training_log.jsonl")
        self.log_file = log_file
        self.log_step = 0

        if not os.path.exists(log_file):
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

    def _append_to_file(self, log_entry):
        """将单条日志按JSONL格式追加到文件，使用portalocker加锁"""
        # 处理 NaN 值
        processed_entry = {}
        for key, value in log_entry.items():
            if isinstance(value, (int, float)) and np.isnan(value):
                processed_entry[key] = self.NAN_PLACEHOLDER
            else:
                processed_entry[key] = value

        with portalocker.Lock(self.log_file, 'a', timeout=10) as f:
            f.write(myjson.dumps(processed_entry) + '\n')

    def load(self, use_debug=False):
        """从文件读取日志数据，返回日志数据而不是缓存到实例变量"""
        if use_debug:
            print(f"Loading log from: {self.log_file}")
        data = {"timestamps": []}

        if not os.path.exists(self.log_file):
            return data

        with portalocker.Lock(self.log_file, 'r', timeout=10) as f:
            for line in f:
                try:
                    log_entry = myjson.loads(line.strip())
                    timestamp = log_entry.pop("timestamp", None)
                    if timestamp:
                        data["timestamps"].append(timestamp)

                    for key, value in log_entry.items():
                        if key not in data:
                            data[key] = []
                        # 将大数转回 NaN
                        if isinstance(value, (int, float)) and value == self.NAN_PLACEHOLDER:
                            data[key].append(float('nan'))
                        else:
                            data[key].append(value)
                except Exception as e:
                    print(f"Warning: Skipping invalid JSON line: {e}")

        return data

    def append_data(self, data_dict, use_debug=False):
        timestamp = time.time()

        if use_debug:
            print(f"Appending data at timestamp: {timestamp}")
            print(f"Current log step: {self.log_step}")
            print(f"Data to append: {data_dict}")

        # 创建要追加到文件的日志条目，时间戳放在最前面
        log_entry = {"timestamp": timestamp}
        log_entry.update(data_dict)

        if use_debug:
            print(f"Final log entry to write: {log_entry}")
            print(f"Writing to file: {self.log_file}")

        # 直接追加到文件
        self._append_to_file(log_entry)
        self.log_step += 1

        if use_debug:
            print(f"Log step incremented to: {self.log_step}")
            print("Data append completed successfully")
            data = self.load()
            print(f"Data Length after append: {len(data['timestamps'])}")

    def fetch_log(self, last_timestamp=0, use_debug=False):
        """获取指定时间戳之后的日志

        Args:
            last_timestamp: 上次获取的最后时间戳
            use_debug: 是否打印调试信息

        Returns:
            tuple: (新日志列表, 最新时间戳)
        """
        # 从文件读取最新数据
        data = self.load()

        if use_debug:
            print(f"Fetching logs after timestamp: {last_timestamp}")
            print(f"Total timestamps available: {len(data['timestamps'])}")

        if not data["timestamps"]:
            if use_debug:
                print("No timestamps available in log")
            return [], 0

        # 找到时间戳之后的索引
        index_start = None
        for i, ts in enumerate(data["timestamps"]):
            if ts > last_timestamp:
                index_start = i
                break

        if use_debug:
            print(f"Starting index for new logs: {index_start}")

        # 如果没有新日志，返回空列表和最后的时间戳
        if index_start is None:
            if use_debug:
                print("No new logs found")
            return [], data["timestamps"][-1]

        # 构建新日志列表
        new_logs = []
        for i in range(index_start, len(data["timestamps"])):
            log_entry = {"timestamp": data["timestamps"][i]}
            for key, values in data.items():
                if key != "timestamps" and i < len(values):
                    log_entry[key] = values[i]
            new_logs.append(log_entry)

        if use_debug:
            print(f"Found {len(new_logs)} new log entries")
            print(f"Latest timestamp: {data['timestamps'][-1]}")

        # 返回新日志和最新时间戳
        latest_timestamp = data["timestamps"][-1]
        return new_logs, latest_timestamp

    def clean_log(self):
        if os.path.exists(self.log_file):
            with portalocker.Lock(self.log_file, 'w', timeout=10) as f:
                f.write("")  # 清空文件内容

    def evaluate_training_info(
        self,
        epoch_limit=10e6,
        training_log_path=None
    ):
        # 如果未指定路径，使用当前实例的数据
        if training_log_path is None:
            training_log = self.load()  # 从文件读取数据
            # 确定输出路径
            training_info_path = os.path.join(
                self.checkpoint_path, "training_info.json")
        else:
            # 构造 training_info 的路径
            training_info_path = training_log_path.replace(
                'training_log.json', 'training_info.json')

            # 从提供的 JSONL 文件读取数据
            training_log = {"timestamps": []}
            try:
                with portalocker.Lock(training_log_path, 'r', timeout=10) as f:
                    for line in f:
                        try:
                            log_entry = myjson.loads(line.strip())
                            timestamp = log_entry.pop("timestamp", None)
                            if timestamp:
                                training_log["timestamps"].append(timestamp)

                            for key, value in log_entry.items():
                                if key not in training_log:
                                    training_log[key] = []
                                training_log[key].append(value)
                        except Exception as e:
                            print(f"Warning: Skipping invalid JSON line: {e}")
            except FileNotFoundError:
                print(f"Training log file not found: {training_log_path}")
                return

        # 检查训练日志是否为空
        if not training_log.get("epoch") or len(training_log.get("epoch", [])) == 0:
            print("Skipping training info generation: No training log data found.")
            return

        # 根据 epoch_limit 截断训练日志
        if "epoch" in training_log:
            epoch_limit = min(epoch_limit, len(training_log["epoch"]))
            for key in training_log:
                if len(training_log[key]) > epoch_limit:
                    training_log[key] = training_log[key][:epoch_limit]

        # 提取信息
        total_epochs = len(training_log.get("epoch", []))

        # 获取各项指标的最小值及其对应参数
        min_loss, params_at_min_loss = self.get_min_value_and_params(
            "loss", training_log)
        min_val_loss, params_at_min_val_loss = self.get_min_value_and_params(
            "val_loss", training_log)
        min_power_log_loss, params_at_min_power_log_loss = self.get_min_value_and_params(
            "power_log_loss", training_log)
        min_val_power_log_loss, params_at_min_val_power_log_loss = self.get_min_value_and_params(
            "val_power_log_loss", training_log)
        min_mae, params_at_min_mae = self.get_min_value_and_params(
            "mae", training_log)
        min_val_mae, params_at_min_val_mae = self.get_min_value_and_params(
            "val_mae", training_log)

        # 获取学习率的统计信息
        lr = training_log.get("lr", [])
        max_lr = max(lr) if lr else None
        min_lr = min(lr) if lr else None
        mean_lr = np.mean(lr) if lr else None

        # 准备要保存的训练信息
        training_info = {
            "total_epochs": total_epochs,
            "min_loss": min_loss,
            "params@min_loss": params_at_min_loss,
            "min_val_loss": min_val_loss,
            "params@min_val_loss": params_at_min_val_loss,
            "min_mae": min_mae,
            "params@min_mae": params_at_min_mae,
            "min_val_mae": min_val_mae,
            "params@min_val_mae": params_at_min_val_mae,
            "min_power_log_loss": min_power_log_loss,
            "params@min_power_log_loss": params_at_min_power_log_loss,
            "min_val_power_log_loss": min_val_power_log_loss,
            "params@min_val_power_log_loss": params_at_min_val_power_log_loss,
            "learning_rate_max": max_lr,
            "learning_rate_min": min_lr,
            "learning_rate_mean": mean_lr
        }

        # 将训练信息保存到 training_info.json
        with open(training_info_path, 'w') as f:
            json.dump(training_info, f, indent=4)

        print(f"Training information saved to {training_info_path}")

    def get_min_value_and_params(self, metric_name, training_log):
        """
        提取指定指标的最小值及其对应的其他参数（如 epoch、val_loss 等）
        :param metric_name: 指标名（如 'loss', 'val_loss'）
        :param training_log: 训练日志字典
        :return: 最小值及最小值对应的参数（epoch 和其他相关指标）
        """
        metric = training_log.get(metric_name, [])
        min_value = min(metric)
        min_epoch = metric.index(min_value) + 1  # 训练轮次从1开始
        min_val_loss = training_log.get('val_loss', [])[min_epoch - 1]
        min_mae = training_log.get('mae', [])[min_epoch - 1]
        min_val_mae = training_log.get('val_mae', [])[min_epoch - 1]
        min_power_log_loss = training_log.get(
            'power_log_loss', [])[min_epoch - 1]
        min_val_power_log_loss = training_log.get(
            'val_power_log_loss', [])[min_epoch - 1]
        return min_value, {
            "epoch": min_epoch,
            "val_loss": min_val_loss,
            "mae": min_mae,
            "val_mae": min_val_mae,
            "power_log_loss": min_power_log_loss,
            "val_power_log_loss": min_val_power_log_loss
        }
