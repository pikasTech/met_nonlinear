import time
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import keyboard  # Make sure to install this module: `pip install keyboard`
from multiprocessing import Process
from tensorflow.keras.callbacks import Callback
import time
from queue import Queue
from datetime import datetime, timedelta
from archive_legacy.richdemo import ScrollingLogHandler
from core.training_state import TrainingStateManager
from core.training_log import TrainingLogger
from models.base_models import BaseModel, ModelEvent, ModelEventType


class RealTimeTrainingCallback(Callback):
    def __init__(self, model_engine):
        super().__init__()
        self.project = model_engine
        self.scrolling_log_handler = ScrollingLogHandler(log_queue=Queue())
        self.scrolling_log_handler.start()
        self.state_manager = model_engine.state_manager
        self.min_loss = self.state_manager['min_loss']
        origin_min_val_loss = self.state_manager['val_loss']
        self.min_val_loss = origin_min_val_loss
        self.origin_min_loss = self.state_manager['min_loss']
        print(f"Origin min loss: {self.origin_min_loss}")
        print(f"Origin min val loss: {origin_min_val_loss}")
        self.user_model: BaseModel = model_engine.model_comp
        self.project_name = model_engine.project_name
        self.start_time = time.time()
        self.epoch_times = []  # 记录每个 epoch 的结束时间
        self.alpha = 0.05  # 指数衰减因子
        self.smoothed_speed = -1

        # 记录训练过程中的验证损失最低值
        self.training_logger: TrainingLogger = model_engine.training_logger
        if not hasattr(self, 'save_each_epoch'):
            self.save_each_epoch = False

    def on_epoch_begin(self, epoch, logs=None):
        self.epoch_start_time = time.time()

    def on_epoch_end(self, epoch, logs=None):
        """
        每个 epoch 结束时调用，计算并更新速度及剩余时间。
        """
        current_time = time.time()
        elapsed_time = current_time - self.start_time  # 总训练时间
        epoch_duration = current_time - self.epoch_start_time  # 当前 epoch 的持续时间
        self.epoch_times.append(epoch_duration)
        self.epoch_start_time = current_time  # 更新下一 epoch 的开始时间

        total_epochs = self.project.config.epoch_train
        completed_epoch = self.state_manager['completed_epoch']
        remaining_epochs = total_epochs - completed_epoch

        # 1. 计算当前 epoch 的速度（每小时完成的 epoch 数）
        if epoch_duration > 0:
            current_speed = 3600.0 / epoch_duration  # 将秒转换为小时
        else:
            current_speed = 0.0

        # 2. 更新平滑后的速度（指数移动平均）
        if self.smoothed_speed == -1:
            # 如果是第一次更新，直接使用当前速度
            self.smoothed_speed = current_speed
        else:
            # 应用指数滤波公式
            self.smoothed_speed = (1 - self.alpha) * \
                self.smoothed_speed + self.alpha * current_speed

        # 3. 使用平滑后的速度估算剩余时间
        if self.smoothed_speed > 0:
            remaining_time_hours = remaining_epochs / self.smoothed_speed
            remaining_time = remaining_time_hours * 3600
            expected_finish_time = datetime.now() + timedelta(seconds=remaining_time)
        else:
            remaining_time = 0
            expected_finish_time = datetime.now()

        loss = logs.get('loss') or 0.0
        val_loss = logs.get('val_loss') or 0.0
        mae = logs.get('mae') or 0.0
        val_mae = logs.get('val_mae') or 0.0
        power_log_loss = logs.get('power_log_loss') or 0.0
        val_power_log_loss = logs.get('val_power_log_loss') or 0.0

        opt = self.model.optimizer
        lr = opt.learning_rate
        if isinstance(lr, tf.keras.optimizers.schedules.LearningRateSchedule):
            lr = lr(opt.iterations)
        lr = tf.keras.backend.get_value(lr)

        # 构建滚动日志信息，包含训练速度
        log_message = (
            f"[{self.project_name} | "
            f"{completed_epoch + 1}/{total_epochs} | "
            f"{self.format_time(elapsed_time)}/{self.format_time(remaining_time)}/{expected_finish_time.strftime('%Y-%m-%d %H:%M:%S')} | "
            f"Loss: {loss:.4f}/{val_loss:.4f} | "
            f"MAE: {mae:.4f}/{val_mae:.4f} | "
            f"AFMAE: {power_log_loss:.4f}/{val_power_log_loss:.4f} | "
            f"{self.smoothed_speed:.1f}/{current_speed:.1f} epochs/h]")

        self.scrolling_log_handler.update_log(log_message)

        data = {
            "epoch": int(completed_epoch) + 1,
            "loss": float(loss),
            "val_loss": float(val_loss),
            "mae": float(mae),
            "val_mae": float(val_mae),
            "power_log_loss": float(power_log_loss),
            "val_power_log_loss": float(val_power_log_loss),
            "lr": float(lr),
        }

        self.state_manager['min_loss'] = self.min_loss
        self.state_manager['min_val_loss'] = self.min_val_loss
        self.state_manager['val_loss'] = val_loss
        self.state_manager['val_mae'] = val_mae
        self.state_manager['val_power_log_loss'] = val_power_log_loss
        self.state_manager['loss'] = loss
        self.state_manager['mae'] = mae
        self.state_manager['power_log_loss'] = power_log_loss
        self.state_manager['lr'] = float(lr)
        self.state_manager['elapsed_time'] = elapsed_time
        self.state_manager['remaining_time'] = remaining_time
        self.state_manager['expected_finish_time'] = expected_finish_time.strftime(
            '%Y-%m-%d %H:%M:%S')
        self.state_manager['smoothed_speed'] = self.smoothed_speed
        self.state_manager['completed_epoch'] += 1
        self.training_logger.append_data(data)
        self.user_model.exec_callback(
            ModelEvent(
                ModelEventType.EPOCH_END,
                data=data
            )
        )
        if getattr(self, 'save_each_epoch', False):
            self.user_model.save_weights(
                os.path.join(self.project.checkpoint_dir, f'epoch_{data["epoch"]}.weights.h5'))
            predict_linspace_path = os.path.join(
                self.project.checkpoint_dir, f'epoch_{data["epoch"]}_IO.json')
            self.user_model.predict_linspace(
                debug=True, save_path=predict_linspace_path)

        # 检查是否是新的最小 loss
        if loss < self.min_loss:
            self.min_loss = loss
            best_loss_message = (
                f"Min Loss: {self.min_loss:.4f}/{val_loss:.4f} | "
                f'Ori Loss: {self.origin_min_loss:.4f} | '
                f"PLog: {power_log_loss:.4f}/{val_power_log_loss:.4f} | "
                f"Epoch: {epoch + 1} | "
                f"{self.format_time(elapsed_time)}")
            self.scrolling_log_handler.print_message(best_loss_message)
            # 保存最佳权重或其他操作
            self.user_model.exec_callback(
                ModelEvent(
                    ModelEventType.BEST_LOSS,
                    data={
                        'epoch': int(epoch) + 1,
                        'min_loss': float(self.min_loss),
                    }
                )
            )
            self.user_model.save_weights(
                self.user_model.best_weights_file)

        if val_loss < self.min_val_loss:
            self.min_val_loss = val_loss
            best_val_loss_message = (
                f"Min  Val: {loss:.4f}/{self.min_val_loss:.4f} | "
                f'Ori Loss: {self.origin_min_loss:.4f} | '
                f"PLog: {power_log_loss:.4f}/{val_power_log_loss:.4f} | "
                f"Epoch: {epoch + 1} | "
                f"{self.format_time(elapsed_time)}")
            self.scrolling_log_handler.print_message(best_val_loss_message)
            # 保存最佳权重或其他操作
            self.user_model.exec_callback(
                ModelEvent(
                    ModelEventType.BEST_VAL_LOSS,
                    data={
                        'epoch': int(epoch) + 1,
                        'min_val_loss': float(self.min_val_loss),
                    }
                )
            )
            self.user_model.save_weights(
                self.user_model.best_val_weights_file)

        # 检查是否有停止按键
        if sys.platform.startswith('win'):
            if keyboard.is_pressed('s') and keyboard.is_pressed('t'):
                self.scrolling_log_handler.print_message(
                    "Training stopped by user.")
                # self.IPC_queue.put('STOP')
                self.user_model.exec_callback(
                    ModelEvent(ModelEventType.STOP))
                self.user_model.stop_training = True

    def on_train_end(self, logs=None):
        # 训练结束时停止滚动日志处理器
        self.scrolling_log_handler.stop()
        self.scrolling_log_handler.join()
        self.user_model.exec_callback(
            ModelEvent(ModelEventType.STOP))

    def format_time(self, seconds):
        return str(timedelta(seconds=int(seconds)))


class CosineAnnealingWithDecayFixedPeriod(tf.keras.optimizers.schedules.LearningRateSchedule):
    def __init__(
            self,
            initial_lr,
            decay_steps,
            cycle_decay_rate=0.90,
            extra_step_multiplier=0.0,
            min_lr_ratio=0.01,
            warmup_ratio=0.1,
            decay_ratio=0.8,
            restart_after_n_cycles=50,  # 50 周期后重启指数衰减，即5000epoch重启一次
            step_begin=0):
        super(CosineAnnealingWithDecayFixedPeriod, self).__init__()
        self.initial_lr = tf.convert_to_tensor(initial_lr, dtype=tf.float32)
        self.decay_steps = tf.cast(decay_steps, tf.float32)
        self.cycle_decay_rate = tf.convert_to_tensor(
            cycle_decay_rate, dtype=tf.float32)
        self.extra_step_length = tf.cast(
            decay_steps * extra_step_multiplier, tf.float32)
        self.min_lr_ratio = tf.convert_to_tensor(
            min_lr_ratio, dtype=tf.float32)
        self.warmup_ratio = tf.convert_to_tensor(
            warmup_ratio, dtype=tf.float32)
        self.decay_ratio = tf.convert_to_tensor(decay_ratio, dtype=tf.float32)
        self.step_begin = tf.cast(step_begin, tf.float32)
        self.pi = tf.constant(np.pi, dtype=tf.float32)
        self.restart_after_n_cycles = restart_after_n_cycles  # 保存重启周期数

    def __call__(self, step):
        step = tf.cast(step, tf.float32)
        step_use = step + self.step_begin
        cycle_length = self.decay_steps + self.extra_step_length

        # 计算当前周期
        cycle = tf.floor(step_use / cycle_length)

        # 添加学习率重启功能
        if self.restart_after_n_cycles is not None:
            # 计算重启后的周期数
            cycle_in_restart = tf.math.floormod(
                cycle, self.restart_after_n_cycles)
        else:
            cycle_in_restart = cycle

        cycle_max_lr, min_lr = self.compute_scaling_factors(cycle_in_restart)

        # 计算进度比例
        progress, within_decay_phase = self.compute_progress_ratio(
            step_use, cycle_length)

        # 计算归一化的输出（包含线性增长和余弦下降阶段）
        normalized_output = self.compute_normalized_output(progress)

        # 计算最终的学习率
        lr = self.compute_learning_rate(
            cycle_max_lr, min_lr, normalized_output, within_decay_phase)
        return lr

    def compute_scaling_factors(self, cycle):
        """计算缩放因子（指数衰减），考虑学习率重启"""
        scaling_factor = tf.pow(self.cycle_decay_rate, cycle)
        cycle_max_lr = self.initial_lr * scaling_factor
        min_lr = cycle_max_lr * self.min_lr_ratio
        return cycle_max_lr, min_lr

    def compute_progress_ratio(self, step_use, cycle_length):
        """计算进度比例（0~1）"""
        modulo = tf.math.floormod(step_use, cycle_length)
        within_decay_phase = modulo < self.decay_steps
        progress = modulo / self.decay_steps
        return progress, within_decay_phase

    def compute_normalized_output(self, progress):
        """计算归一化的输出，最大值为1，包含线性增长和余弦下降阶段"""
        progress = tf.clip_by_value(progress, 0.0, 1.0)

        # 计算各阶段的边界
        warmup_end = self.warmup_ratio
        decay_start = 1.0 - self.decay_ratio

        # 计算线性增长和余弦下降的 process
        linear_process = progress / warmup_end  # 在 [0, warmup_end] 内从 0 增加到 1
        # 在 [decay_start, 1.0] 内从 0 增加到 1
        cosine_decay_process = (progress - decay_start) / (1.0 - decay_start)

        # 确保 process 在 [0, 1] 范围内
        linear_process = tf.clip_by_value(linear_process, 0.0, 1.0)
        cosine_decay_process = tf.clip_by_value(cosine_decay_process, 0.0, 1.0)

        # 调用归一化的子函数
        linear_output = self.linear_increase(linear_process)
        cosine_output = self.cosine_decay(cosine_decay_process)

        # 根据 progress 阶段选择输出
        normalized_output = tf.where(
            progress < warmup_end,
            linear_output,
            tf.where(
                progress > decay_start,
                cosine_output,
                tf.constant(1.0, dtype=tf.float32)
            )
        )
        return normalized_output

    def linear_increase(self, process):
        """归一化的线性增长函数，输入和输出都是 [0,1]"""
        return process  # 线性从 0 增加到 1

    def cosine_decay(self, process):
        """归一化的余弦下降函数，输入和输出都是 [0,1]"""
        return 0.5 * (1 + tf.cos(self.pi * process))

    def compute_learning_rate(self, cycle_max_lr, min_lr, normalized_output, within_decay_phase):
        """计算最终的学习率"""
        lr = (cycle_max_lr - min_lr) * normalized_output + min_lr
        # 如果不在衰减阶段，学习率为最小学习率
        lr = tf.where(within_decay_phase, lr, min_lr)
        return lr


def plot_loss(project):
    state_manager: TrainingStateManager = project.state_manager
    training_loger: TrainingLogger = project.training_logger
    losses, val_losses, lrs, power_log_losses = [], [], [], []
    last_log_timestamp = 0

    while True:  # 外层循环，用于在捕获异常后重启绘图窗口
        reception_times = []  # 用于存储接收数据的时间戳
        monitoring_started = False
        last_reception_time = time.time()
        try:
            plt.ion()
            fig, ax1 = plt.subplots(figsize=(10, 6))

            # Set up the loss line on a logarithmic scale
            line_loss, = ax1.plot([], [], label='Loss', color='blue',
                                  linestyle="-", marker='', markersize=3, linewidth=0.5)
            line_val_loss, = ax1.plot(
                [], [], label='Validation Loss', color='orange', linestyle="--", marker='', markersize=3, linewidth=0.5)
            ax1.set_xlabel("Epochs")
            ax1.set_ylabel("Loss (Log Scale)")
            ax1.set_yscale('log')  # Set the y-axis for loss to log scale

            ax2 = ax1.twinx()
            line_lr, = ax2.plot([], [], label='Learning Rate',
                                color='red', linestyle="-", marker='', markersize=3, linewidth=0.5)
            ax2.set_ylabel("Learning Rate")
            fig.legend(loc='upper right')

            # Initialize the dashed line for minimum loss
            min_loss_line = ax1.axhline(
                y=1, color='green', linestyle='--', label="Min Loss")
            model_name_text = ax1.text(0.2, 0.96, state_manager['model_name'], transform=ax1.transAxes,
                                       color="red", fontsize=16, verticalalignment='top',
                                       horizontalalignment='left',
                                       )
            min_loss_text = ax1.text(0.2, 0.9, "", transform=ax1.transAxes,
                                     color="blue", fontsize=14, verticalalignment='top',
                                     horizontalalignment='left',
                                     )

            while True:  # 内层循环处理绘图更新
                # Update data for both lines
                # plot on the first time
                if len(losses) > 0:
                    line_loss.set_data(range(len(losses)), losses)
                    line_lr.set_data(range(len(lrs)), lrs)
                    line_val_loss.set_data(range(len(val_losses)), val_losses)

                    # Update x-axis limits for both loss and learning rate
                    ax1.set_xlim(0, len(losses))
                    ax2.set_xlim(0, len(losses))

                    # Update y-axis limits for learning rate
                    min_lr = min(lrs)
                    max_lr = max(lrs)
                    ax2.set_ylim(0, max(max_lr * 1.2, 1e-12))

                    # Update y-axis limits for loss on a logarithmic scale
                    min_loss = min(losses)
                    max_loss = max(losses)
                    val_min_loss, val_max_loss = min(
                        val_losses), max(val_losses)

                    ax1.set_ylim(min(min_loss, val_min_loss) * 0.9,
                                 max(max_loss, val_max_loss) * 1.1)

                    # Update the position of the dashed line for minimum loss
                    min_loss_line.set_ydata([min_loss, min_loss])

                    # Update the label text with the minimum loss
                    min_loss_text.set_text(
                        f"Min Loss: {min_loss:.4f} Min Power Log: {min(power_log_losses):.4f} Min Val Loss: {min(val_losses):.4f}\n"
                        f"    Loss: {loss:.4f}     Power Log: {power_log_loss:.4f}    Val Loss: {val_loss:.4f}")
                    model_name_text.set_text(
                        f"Model: {state_manager['model_name']}")

                plt.pause(0.01)
                current_time = time.time()
                data, last_log_timestamp = training_loger.fetch_log(
                    last_timestamp=last_log_timestamp)
                # print(f"fetched data with timestamp: {last_log_timestamp}")
                # print(f"data fetched: {data}")
                # print(f"last log timestamp: {last_log_timestamp}")
                if data:
                    # print(f"get data: {data}")
                    if data == 'STOP':  # Signal to stop the plotting process
                        plt.ioff()
                        print("Plotting stopped.")
                        plt.close('all')
                        return

                    # Process list of data points
                    for data_point in data:
                        loss = data_point.get('loss', 1e1)
                        val_loss = data_point.get('val_loss', 0)
                        lr = data_point.get('lr', 1e-6)
                        power_log_loss = data_point.get('power_log_loss', 1e1)

                        # Handle inf and nan values
                        if np.isnan(loss) or np.isinf(loss):
                            loss = 1e1
                        if np.isnan(val_loss) or np.isinf(val_loss):
                            val_loss = 1e1
                        if np.isnan(lr) or np.isinf(lr):
                            lr = 1e-6
                        if np.isnan(power_log_loss) or np.isinf(power_log_loss):
                            power_log_loss = 1e1

                        reception_times.append(current_time)
                        last_reception_time = current_time
                        losses.append(loss)
                        val_losses.append(val_loss)
                        lrs.append(lr)
                        power_log_losses.append(power_log_loss)

                # 计算平均接收周期
                if state_manager['training_alive'] and not monitoring_started:
                    monitoring_started = True
                    print("\nMonitoring data reception...")

                # 开始监控数据接收情况
                if monitoring_started:
                    if last_reception_time is not None and (current_time - last_reception_time) > 600:
                        print(
                            "\nNo data received for over 600s. Terminating training process.")
                        state_manager['terminate'] = True
                        reception_times = []  # 重置接收时间列表
                        monitoring_started = False  # 停止监控
                        last_reception_time = time.time()

                    # 计算平均接收时间
                    avg_reception_time = np.mean(
                        np.diff(reception_times)) if len(reception_times) > 1 else 60

                    if len(reception_times) >= 5:
                        # 如果 20 倍的平均接收时间内没有接收到数据，则终止训练，至少等待 10 秒
                        if (current_time - last_reception_time) > max(20 * avg_reception_time, 10):
                            print(
                                "\nNo data received for over 5 times the average reception time. Terminating training process.")
                            print(
                                f'Current time elapsed: {current_time - last_reception_time:.2f} s')
                            print(
                                f'Average reception time: {avg_reception_time:.2f} s')
                            state_manager['terminate'] = True
                            reception_times = []
                            monitoring_started = False
                            last_reception_time = time.time()

                    if state_manager['training_alive'] == False:
                        """
                        重置接收时间列表
                        """
                        reception_times = []  # 重置接收时间列表
                        monitoring_started = False
                        last_reception_time = time.time()

                plt.pause(0.5)  # 每 0.5 秒更新一次图形
        except Exception as e:
            # trace back the exception
            import traceback
            print(f"\nAn error occurred: {e}. Restarting the plot window...")
            print("Traceback:")
            traceback.print_exc()
            plt.close('all')  # 关闭所有图形窗口，防止累积导致内存泄漏
            time.sleep(5)
            continue  # 重启外层循环

# Define a custom callback for real-time plotting with auto-adjusted display range


def plot_process_start(project):
    # Initialize the IPC_queue and start the plotting process
    plot_process = Process(target=plot_loss, args=(project,))
    plot_process.start()

# 主进程控制函数


def start_process(project):
    target_function = project.process
    state_manager = project.state_manager
    print("Starting the training process...")
    while True:
        # 在启动子进程前重置 terminate 标志
        state_manager['terminate'] = False

        process = Process(target=target_function, args=())
        process.start()

        while True:
            # 等待一段时间，避免占用过多 CPU 资源
            time.sleep(1)

            # 检查子进程是否已经结束
            if not process.is_alive():
                state_manager['training_alive'] = False
                break  # 退出内层循环，检查退出代码

            # 检查 terminate 标志
            if False and state_manager.get('terminate', False):
                print("\n检测到终止信号，正在杀死子进程。")
                process.terminate()  # 发送 SIGTERM 信号

                timeout = 20  # 等待子进程结束的超时时间
                while process.is_alive() and timeout > 0:
                    time.sleep(1)
                    timeout -= 1
                if process.is_alive():
                    print("子进程未响应，强制终止。")
                    process.kill()

                print("等待子进程结束...")
                process.join()  # 等待子进程真正结束
                print("子进程已结束。")
                break  # 退出内层循环，重新启动子进程

        print(f"子进程退出代码: {process.exitcode}")
        # 检查子进程的退出代码
        if process.exitcode == 0:
            print("子进程正常结束，退出重启机制。")
            break
        else:
            print(f"子进程异常退出，重启中...")
            time.sleep(1)
