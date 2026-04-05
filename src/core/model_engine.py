from matplotlib import pyplot as plt
import traceback
import os
import logging
from config import Config
import tensorflow as tf
import json
from .training_log import TrainingLogger
from utils import sample_list
import numpy as np
import core.metnl as metnl
from models import *
from calibration_analyzer.exam_class import System, TimeSeries
from calibration_analyzer import exam_process, exam_class
from calibration_analyzer.exam_process import find_data_info
from . import data_processing
from .data_processing import Dataset_COMP_MET, Dataset_COMP_PE,  CustomScaler, Dataset_COMP_AliasSimu, Dataset_COMP_Alias
from visualization.model_analysis import FR_for_comp_real_data
from visualization.frequency_response_json_comparator import quick_compare
from .data_processing import augment_data
from .loss_functions import af_mse_loss, power_log_mae_loss, power_log_loss, pure_power_log_mae_loss, pure_mae_metric
from .training import RealTimeTrainingCallback, CosineAnnealingWithDecayFixedPeriod
from .freq_config_manager import freq_config_manager

# 创建 logger
logger = logging.getLogger(__name__)
from .training_state import TrainingStateManager
from models.base_models import BaseModel


class ModelEngine:
    def __init__(self,
                 project,
                 checkpoint_dir='data'):
        self.project_name = project.project_name
        self.config: Config = project.config
        self.model_comp: BaseModel = None
        self.scaler = None  # 使用集成的scaler替代scaler_x和scaler_y
        self.x_train_shuffle = None
        self.y_train_shuffle = None
        self.x_test_shuffle = None
        self.y_test_shuffle = None
        self.batch_size = None
        self.dataset_origin = None
        self.E = None
        self.target_sys_fit = None
        self.checkpoint_dir = checkpoint_dir
        self.training_logger: TrainingLogger = project.training_logger
        # 设置 GPU 使用
        metnl.set_using_gpu(self.config.using_gpu)
        # 根据是否使用 power loss 调整学习率
        self.learning_rate = self.config.learning_rate
        if not self.config.use_power_loss:
            self.learning_rate *= 10
        self.learning_rate /= self.config.step_per_epoch
        self.state_manager: TrainingStateManager = project.state_manager

    def load_dataset(self, dataset_type='MET'):
        if dataset_type == 'MET':
            # 检查数据路径是否存在
            data_path = self.config.full_data_path
            if not os.path.exists(data_path):
                raise FileNotFoundError(
                    f"数据路径不存在: {data_path}\n"
                    f"请检查:\n"
                    f"1. 环境变量 MET_DATA_BASE 是否设置正确（当前值: {os.environ.get('MET_DATA_BASE', '未设置')}）\n"
                    f"2. 相对路径 {self.config.data_path} 是否正确\n"
                    f"3. 完整路径 {data_path} 是否存在"
                )
            
            data_info_list = find_data_info(data_path)
            if not data_info_list:
                raise ValueError(
                    f"在路径 {data_path} 中未找到任何数据文件！\n"
                    f"请确保该目录下存在以 '震级*.analyze.json' 格式命名的数据文件。"
                )
            
            sweep_list = range(1, 50, 2)
            self.dataset_origin = Dataset_COMP_MET(
                data_info_list,
                self.config.target_sweep,
                sweep_list,
                use_cache=self.config.use_cache_features,
                time_cliped_s=self.config.time_clipped_s,
                fs=self.config.sample_rate
            )
            self.target_sys_fit = self.dataset_origin.sys_target_fit
        elif dataset_type == 'Alias':
            # 检查数据路径是否存在
            data_path = self.config.full_data_path
            if not os.path.exists(data_path):
                raise FileNotFoundError(
                    f"数据路径不存在: {data_path}\n"
                    f"请检查:\n"
                    f"1. 环境变量 MET_DATA_BASE 是否设置正确（当前值: {os.environ.get('MET_DATA_BASE', '未设置')}）\n"
                    f"2. 相对路径 {self.config.data_path} 是否正确\n"
                    f"3. 完整路径 {data_path} 是否存在"
                )
            
            data_info_list = find_data_info(data_path)
            if not data_info_list:
                raise ValueError(
                    f"在路径 {data_path} 中未找到任何数据文件！\n"
                    f"请确保该目录下存在以 '震级*.analyze.json' 格式命名的数据文件。"
                )
            
            sweep_list = range(0, len(data_info_list), 1)
            self.dataset_origin = Dataset_COMP_Alias(
                data_info_list,
                self.config.target_sweep,
                sweep_list,
                use_cache=self.config.use_cache_features,
                time_cliped_s=self.config.time_clipped_s,
                fs=self.config.sample_rate,
                config=self.config  # 传递完整配置对象
            )
        elif dataset_type == 'PE':
            self.dataset_origin = Dataset_COMP_PE()
        elif dataset_type == 'AliasSimu':
            self.dataset_origin = Dataset_COMP_AliasSimu()
        else:
            raise ValueError(f'未知的数据集类型: {dataset_type}')
        
        # 统一应用反相处理（所有Dataset类型通用）
        self.dataset_origin.apply_inverse_transform(self.config)
        
        # self.dataset_origin.plot_target_and_origin()

    def prepare_training_data(self, output_folder='temp/'):
        # 选择特征向量 - 使用FreqConfigManager统一管理
        from core.freq_config_manager import freq_config_manager
        self.freq_idx_select = freq_config_manager.get_freq_indices(
            self.config, 
            self.dataset_origin.freq_list, 
            self.dataset_origin.output_ori.shape[1]
        )
        self.freq_select = [self.dataset_origin.freq_list[i]
                            for i in self.freq_idx_select]
        self.magn_select = self.dataset_origin.magn_list
        if self.config.dataset_type == 'MET':
            dataset_select = self.dataset_origin.select(
                magn_indices=None, freq_indices=self.freq_idx_select
            )
        elif self.config.dataset_type == 'PE':
            dataset_select = self.dataset_origin.select(
                None, None
            )
        elif self.config.dataset_type == 'AliasSimu':
            dataset_select = self.dataset_origin.select(
                None, None
            )
        elif self.config.dataset_type == 'Alias':
            dataset_select = self.dataset_origin.select(
                None, freq_indices=self.freq_idx_select
            )
        else:
            raise ValueError(f'未知的数据集类型: {self.config.dataset_type}')
        self.dataset_select = dataset_select
        X_select, y_select = dataset_select.output_ori, dataset_select.output_tar
        print(f'After select_and_reshape_feature_vector:')
        print(f'X_select: {X_select.shape}')
        print(f'y_select: {y_select.shape}')

        # 创建 test Dataset_COMP 和 train Dataset_COMP
        print(f'use shuffle and split data')
        dataset_train_shuffle, dataset_test_shuffle, dataset_train, dataset_test = self.dataset_select.shuffle_and_split_data(
            use_points=self.config.use_points)

        if output_folder is not None:
            # 导出数据集为 .wave 文件
            dataset_test.export_to_wave(output_folder=output_folder)

        self.dataset_test = dataset_test
        self.dataset_train = dataset_train
        self.dataset_train_shuffle = dataset_train_shuffle
        self.dataset_test_shuffle = dataset_test_shuffle        # 数据归一化
        if self.config.use_scale:
            # 尝试加载现有的scaler
            loaded_scaler = self.load_scalers()
            if loaded_scaler is None:
                # 如果加载失败，则根据选择的数据计算并创建新的scaler
                print("创建新的集成缩放器...")
                from .data_processing import CombinedScaler
                self.scaler = CombinedScaler(feature_range=self.config.feature_range)
                X, y = self.scaler.fit_transform(X_select, y_select)
                print(f'X range: {X.min()} to {X.max()}')
                print(f'y range: {y.min()} to {y.max()}')

                # 保存新创建的scaler
                self.save_scalers()
            else:
                # 如果加载成功，使用加载的scaler转换数据
                X, y = self.scaler.transform(X_select, y_select)
                print(f'使用已加载的集成缩放器对数据进行变换')            # 对训练和测试数据应用相同的scaler
            self.x_train_shuffle, self.y_train_shuffle = self.scaler.transform(
                dataset_train_shuffle.output_ori, dataset_train_shuffle.output_tar)
            self.x_test_shuffle, self.y_test_shuffle = self.scaler.transform(
                dataset_test_shuffle.output_ori, dataset_test_shuffle.output_tar)
            
            self.x_train, self.y_train = self.scaler.transform(
                dataset_train.output_ori, dataset_train.output_tar)
            self.x_test, self.y_test = self.scaler.transform(
                dataset_test.output_ori, dataset_test.output_tar)

        if self.config.AUG_TIMES > 1:  # !TODO：需要修复
            # n 代表一次增广时随机选取几条样本相加
            n = self.config.AUG_N
            # j 代表增广后总数据量是原来的多少倍
            j = self.config.AUG_TIMES

            # 增广训练集
            # 设置随机种子，保证每次增广结果一致
            np.random.seed(42)
            self.x_train_shuffle, self.y_train_shuffle = augment_data(
                self.x_train_shuffle, self.y_train_shuffle, n=n, times=j)

            # 如果也想增广 ns_x_train, ns_y_train，可解除注释
            # self.ns_x_train, self.ns_y_train = augment_data(self.ns_x_train, self.ns_y_train, n=n, times=j)            np.random.seed(63)
            self.x_test_shuffle, self.y_test_shuffle = augment_data(
                self.x_test_shuffle, self.y_test_shuffle, n=n, times=j)
            # self.ns_x_test, self.ns_y_test = augment_data(self.ns_x_test, self.ns_y_test, n=n, times=j)

            print(f'After data augmentation:')
            print(f'x_train shape: {self.x_train_shuffle.shape}')
            print(f'y_train shape: {self.y_train_shuffle.shape}')
            # 如果增广了测试集，也相应打印
            print(f'x_test shape: {self.x_test_shuffle.shape}')
            print(f'y_test shape: {self.y_test_shuffle.shape}')

        seq_num = self.x_train_shuffle.shape[0] * self.x_train_shuffle.shape[1]
        self.batch_size = max(1, int(seq_num / self.config.step_per_epoch))
        print(f'seq_num: {seq_num}')
        print(f'batch_size: {self.batch_size}')

    def save_scalers(self):
        """保存集成的 scaler 到JSON文件"""
        if self.scaler is not None:
            scaler_dir = os.path.join(self.checkpoint_dir, 'scalers')
            os.makedirs(scaler_dir, exist_ok=True)

            self.scaler.dump_json(os.path.join(scaler_dir, 'combined_scaler.json'))
            print(f"已将集成缩放器保存到 {scaler_dir}")
        else:
            print("警告：scaler为None，无法保存")

    def load_scalers(self):
        """尝试从JSON文件加载集成scaler，如果找不到，则尝试从base_project加载"""
        from .data_processing import CombinedScaler
        
        scaler_dir = os.path.join(self.checkpoint_dir, 'scalers')
        combined_scaler_path = os.path.join(scaler_dir, 'combined_scaler.json')
        
        # 优先尝试加载集成scaler
        if os.path.exists(combined_scaler_path):
            try:
                self.scaler = CombinedScaler.from_json(combined_scaler_path)
                logger.info(f"已成功加载集成缩放器")
                return self.scaler
            except Exception as e:
                print(f"加载集成缩放器失败：{e}")
        
        # 尝试加载旧版本的分离scaler并转换为集成scaler
        scaler_x_path = os.path.join(scaler_dir, 'scaler_x.json')
        scaler_y_path = os.path.join(scaler_dir, 'scaler_y.json')
        
        if os.path.exists(scaler_x_path) and os.path.exists(scaler_y_path):
            try:
                from .data_processing import CustomScaler
                scaler_x = CustomScaler.from_json(scaler_x_path)
                scaler_y = CustomScaler.from_json(scaler_y_path)
                
                # 创建集成scaler并设置参数
                self.scaler = CombinedScaler(feature_range=scaler_x.feature_range)
                self.scaler.scaler_x = scaler_x
                self.scaler.scaler_y = scaler_y
                self.scaler._fitted = True
                
                print(f"已成功加载并转换旧版缩放器为集成缩放器")
                
                # 保存转换后的集成scaler
                self.save_scalers()
                return self.scaler
            except Exception as e:
                print(f"加载旧版缩放器失败：{e}")
        
        # 尝试从base_project加载scaler
        if hasattr(self.config, 'base_project') and self.config.base_project:
            base_project_name = self.config.base_project
            base_project_path = f'projects/{base_project_name}'
            base_scaler_dir = f'{base_project_path}/data/scalers'
            base_combined_scaler_path = os.path.join(base_scaler_dir, 'combined_scaler.json')
            
            # 优先尝试加载集成scaler
            if os.path.exists(base_combined_scaler_path):
                try:
                    self.scaler = CombinedScaler.from_json(base_combined_scaler_path)
                    print(f"已从基础项目 '{base_project_name}' 加载集成缩放器")
                    
                    # 将从基础项目加载的scaler保存到当前项目
                    self.save_scalers()
                    return self.scaler
                except Exception as e:
                    print(f"从基础项目加载集成缩放器失败：{e}")
            
            # 尝试加载旧版本分离scaler
            base_scaler_x_path = os.path.join(base_scaler_dir, 'scaler_x.json')
            base_scaler_y_path = os.path.join(base_scaler_dir, 'scaler_y.json')
            
            if os.path.exists(base_scaler_x_path) and os.path.exists(base_scaler_y_path):
                try:
                    from .data_processing import CustomScaler
                    scaler_x = CustomScaler.from_json(base_scaler_x_path)
                    scaler_y = CustomScaler.from_json(base_scaler_y_path)
                    
                    # 创建集成scaler并设置参数
                    self.scaler = CombinedScaler(feature_range=scaler_x.feature_range)
                    self.scaler.scaler_x = scaler_x
                    self.scaler.scaler_y = scaler_y
                    self.scaler._fitted = True
                    
                    print(f"已从基础项目 '{base_project_name}' 加载并转换旧版缩放器")
                    
                    # 保存转换后的集成scaler
                    self.save_scalers()
                    return self.scaler
                except Exception as e:
                    print(f"从基础项目加载旧版缩放器失败：{e}")

        print(f"未找到缩放器文件，将创建新的集成缩放器")
        return None

    def build_model(self):
        # 构建模型
        if 'FRIKAN' in self.config.use_model:
            mod_class = eval(self.config.use_model)
            self.model_comp = mod_class.fromSystem(
                self.E,
                fs=self.config.sample_rate,
                grid_size=self.config.GRID_SIZE,
                grid_range=(
                    self.config.grid_range[0], self.config.grid_range[1]),
                spline_order=self.config.SPLINE_ORDER,
                basis_activation=self.config.basis_activation,
                fix_scale_factor=self.config.FIX_SCALE_FACTOR,
                inner_kan_units=self.config.INNER_KAN_UNITS,
                inner_kan_layers=self.config.INNER_KAN_LAYERS,
                iir_trainable=self.config.IIR_TRAINABLE,
                use_fast_model=self.config.USE_FAST_MODEL,
                iir_init_by_system=self.config.IIR_INIT_BY_SYSTEM,
                checkpoint_dir=self.checkpoint_dir,
                kan_log_grid=self.config.kan_log_grid,
                kan_grid_expand=self.config.kan_grid_expand,
                save_each_epoch=self.config.save_each_epoch,
                model_subcfg=self.config.model_subcfg
            )
        elif self.config.use_model == 'LSTM':
            self.model_comp = LSTM(
                fs=self.config.sample_rate,
                lstm_units=self.config.kernal_units,
                checkpoint_dir=self.checkpoint_dir,
                activation=self.config.activation,
                model_subcfg=self.config.model_subcfg
            )
        elif self.config.use_model == 'LSTMTransformer':
            self.model_comp = LSTMTransformer(
                fs=self.config.sample_rate,
                lstm_units=self.config.kernal_units,
                checkpoint_dir=self.checkpoint_dir,
                activation=self.config.activation,
                model_subcfg=self.config.model_subcfg
            )
        elif self.config.use_model == 'GRN':
            self.model_comp = GRN(
                fs=self.config.sample_rate,
                grn_units=self.config.kernal_units,
                checkpoint_dir=self.checkpoint_dir,
                activation=self.config.activation,
                model_subcfg=self.config.model_subcfg
            )
        elif 'WaveNet' in self.config.use_model:
            mod_class = eval(self.config.use_model)
            self.model_comp = mod_class(
                fs=self.config.sample_rate,
                checkpoint_dir=self.checkpoint_dir,
                kernel_units=self.config.kernal_units,
                activation=self.config.activation,
                model_subcfg=self.config.model_subcfg,
                inference_config=self.config.inference_config,
            )
        elif self.config.use_model == 'RNN':
            self.model_comp = RNN(
                fs=self.config.sample_rate,
                rnn_units=self.config.kernal_units,
                checkpoint_dir=self.checkpoint_dir,
                model_subcfg=self.config.model_subcfg
            )
        elif self.config.use_model == 'RVTDCNN':
            self.model_comp = RVTDCNN(
                fs=self.config.sample_rate,
                filters=self.config.kernal_units,
                checkpoint_dir=self.checkpoint_dir,
                memory_depth=self.config.RVTDCNN_memory_depth,
                nonlinearity_order=self.config.RVTDCNN_nonlinearity_order,
                dense_units=self.config.RVTDCNN_dense_units,
                kernel_size=self.config.RVTDCNN_kernel_size,                model_subcfg=self.config.model_subcfg,
            )
        elif self.config.use_model == 'CNNKAN':
            self.model_comp = CNNKAN(
                fs=self.config.sample_rate,
                grid_size=self.config.GRID_SIZE,
                grid_range=(
                    self.config.grid_range[0], self.config.grid_range[1]),
                spline_order=self.config.SPLINE_ORDER,
                basis_activation=self.config.basis_activation,
                fix_scale_factor=self.config.FIX_SCALE_FACTOR,
                inner_kan_units=self.config.INNER_KAN_UNITS,
                inner_kan_layers=self.config.INNER_KAN_LAYERS,
                checkpoint_dir=self.checkpoint_dir,
                kan_log_grid=self.config.kan_log_grid,
                kan_grid_expand=self.config.kan_grid_expand,
                save_each_epoch=self.config.save_each_epoch,
                model_subcfg=self.config.model_subcfg,
                cnn_filters=self.config.CNN_FILTERS,
                cnn_kernel_size=self.config.CNN_KERNEL_SIZE,
                dropout_rate=self.config.CNN_DROPOUT_RATE,
            )
        else:
            raise ValueError(f'未知的模型类型: {self.config.use_model}')

        self.model_comp.summary()
        self.state_manager['model_name'] = self.model_comp.model_name

        if self.config.use_scale:
            self.model_comp.set_scaler(self.scaler)

        # 配置优化器
        if self.config.use_model == 'RVTDCNN':
            self.learning_rate *= 5
        if self.config.use_auto_lr:
            learning_rate_schedule = CosineAnnealingWithDecayFixedPeriod(
                initial_lr=self.learning_rate,
                decay_steps=self.config.auto_lr_decay_steps * self.config.step_per_epoch,
                step_begin=self.state_manager.get(
                    "completed_epoch", 0) * self.config.step_per_epoch,
                restart_after_n_cycles=self.config.RESTART_AFTER_N_CYCLES,
            )
            optimizer = tf.keras.optimizers.Adam(
                learning_rate=learning_rate_schedule)
        else:
            optimizer = tf.keras.optimizers.Adam(
                learning_rate=self.learning_rate)

        loss_type = getattr(self.config, 'loss_type', None)
        loss_map = {
            'afmse': af_mse_loss,
            'power_log_mae': power_log_mae_loss,
            'pure_power_log_mae': pure_power_log_mae_loss
        }
        if loss_type is not None:
            loss_fn = loss_map[loss_type]
        elif self.config.use_pure_power_loss:
            loss_fn = pure_power_log_mae_loss
        elif self.config.use_power_loss:
            loss_fn = power_log_mae_loss
        else:
            loss_fn = 'mae'

        if loss_fn == 'mae':
            self.model_comp.compile(
                optimizer=optimizer,
                loss=loss_fn,
                metrics=[pure_mae_metric]
            )
        elif loss_fn == pure_power_log_mae_loss:
            self.model_comp.compile(
                optimizer=optimizer,
                loss=loss_fn,
                metrics=[power_log_loss]
            )
        else:
            self.model_comp.compile(
                optimizer=optimizer,
                loss=loss_fn,
                metrics=[pure_mae_metric, power_log_loss]
            )

    def _convert_np_types(self, obj):
        """Recursively convert NumPy types to native Python types."""
        if isinstance(obj, np.ndarray):
            return obj.tolist()  # Convert numpy arrays to lists
        elif isinstance(obj, np.generic):
            # Convert numpy scalar types (e.g., np.int32, np.float32) to native Python types
            return obj.item()
        elif isinstance(obj, dict):
            return {key: self._convert_np_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_np_types(item) for item in obj]
        else:
            return obj  # Return the object as-is if it's not a NumPy type

    def dump_model_info(self, output_folder='results'):
        """
        Dumps model information to a JSON file.
        Args:
            model: A trained model.
            save_path: Path to save the model info as a JSON file.
        """
        save_path = os.path.join(output_folder, 'model_info.json')
        model = self.model_comp.model
        # Get the model summary
        model_summary = []
        for layer in model.layers:
            layer_info = {
                "name": layer.name,
                "type": layer.__class__.__name__,
                "output_shape": layer.output_shape,
                "trainable": layer.trainable,
                "num_params": layer.count_params()
            }
            model_summary.append(layer_info)

        # Get total parameters (trainable and non-trainable)
        total_params = model.count_params()
        trainable_params = np.sum([np.prod(var.shape)
                                   for var in model.trainable_variables])
        non_trainable_params = total_params - trainable_params

        # Prepare model information
        model_info = {
            "model_type": self.config.use_model,
            "input_shape": model.input_shape,
            "output_shape": model.output_shape,
            "total_params": total_params,
            "trainable_params": trainable_params,
            "non_trainable_params": non_trainable_params,
            "model_summary": model_summary
        }

        # Convert NumPy types to native Python types
        model_info = self._convert_np_types(model_info)

        # Save model information to a JSON file
        with open(save_path, 'w') as f:
            json.dump(model_info, f, indent=4)

        print(f"Model information saved to {save_path}")

    def evaluate_training_info(self):
        self.training_logger.evaluate_training_info()

    def prepare_systems(self):
        data_info_list = find_data_info(self.config.full_data_path)
        sweep_list = range(1, 50, 2)
        h_index_list = sample_list.sample_list(
            sweep_list, self.config.H_UNITS)
        H_fit = []
        H = []
        for index in h_index_list:
            ws = System.loadFile(data_info_list[index].file_path)
            # 使用配置的Hz范围或默认值
            default_range = (5, 200)
            freq_range_hz = freq_config_manager.get_freq_range_hz(self.config, default_range)
            ws_fit = exam_process.ws_system_fit(ws, k=1.0, freq_range=freq_range_hz)
            H_fit.append(ws_fit)
            H.append(ws)
            if self.config.use_debug_plot:
                ws_fit.plot(label=f"H_fit_{index}")

        ws_target = self.target_sys_fit
        E1 = [exam_class.ws_compensator(hi, ws_target) for hi in H_fit]

        E2 = []
        # 双向法选择最佳 E
        for i in range(len(H_fit)):
            E_i = exam_class.ws_compensator(H_fit[i], H_fit[len(H_fit) - 1])
            if self.config.use_debug_plot:
                E_i.plot(label=f"E_double{i}")
            E2.append(E_i)

        self.E = E1  # 可以根据需要组合 E1 和 E2

        if self.config.use_debug_plot:
            for i in range(len(H)):
                H_after_comp = exam_process.cascade_system(H[i], self.E[i])
                H_after_comp.plot(label=f"H_comp_{i}")

    def load_best_weights(self):
        logger.info(f"加载最低loss权重文件...")
        if os.path.exists(self.model_comp.best_weights_file):
            try:
                self.model_comp.load_weights(
                    self.model_comp.best_weights_file)
                logger.info(f"已成功加载模型权重文件: {self.model_comp.best_weights_file}")
            except Exception as e:
                logger.error(f"加载权重文件失败: {e}")
                print(f'Error: {e}')
                raise
        else:
            raise FileNotFoundError(
                f"权重文件不存在: {self.model_comp.best_weights_file}\n"
                f"请先训练模型或确保权重文件路径正确。"
            )

    def load_val_best_weights(self):
        logger.info(f"加载最佳验证集权重文件: {self.model_comp.best_val_weights_file}")
        if os.path.exists(self.model_comp.best_val_weights_file):
            try:
                self.model_comp.load_weights(
                    self.model_comp.best_val_weights_file)
                logger.info(f"已成功加载模型权重文件: {self.model_comp.best_val_weights_file}")
            except Exception as e:
                logger.error(f"加载权重文件失败: {e}")
                print(f'Error: {e}')
                raise
        else:
            try:
                print("[Warning!]：未找到验证集最佳权重，使用训练集最佳权重代替。")
                self.load_best_weights()
            except Exception as e:
                print("加载权重文件失败，请检查文件是否正确。")
                print(f'Error: {e}')
                raise

    def evaluate_loss(self, use_shifting=False):
        # (magn_num, freq_num, point_num) -> (magn_num * freq_num, point_num, 1)
        if use_shifting:
            x_train = self.x_train_shuffle.reshape(
                -1, self.x_train_shuffle.shape[2], 1)
            x_test = self.x_test_shuffle.reshape(-1,
                                                 self.x_test_shuffle.shape[2], 1)
            y_train = self.y_train_shuffle.reshape(
                -1, self.y_train_shuffle.shape[2], 1)
            y_test = self.y_test_shuffle.reshape(-1,
                                                 self.y_test_shuffle.shape[2], 1)
        else:
            x_train = self.x_train.reshape(-1, self.x_train.shape[2], 1)
            x_test = self.x_test.reshape(-1, self.x_test.shape[2], 1)
            y_train = self.y_train.reshape(-1, self.y_train.shape[2], 1)
            y_test = self.y_test.reshape(-1, self.y_test.shape[2], 1)
        result = self.model_comp.evaluate(
            x_train, y_train, batch_size=self.batch_size
        )
        val_result = self.model_comp.evaluate(
            x_test, y_test, batch_size=self.batch_size
        )
        if len(result) == 2:
            loss, metrics = result
            if not isinstance(metrics, list):
                metrics = [metrics]
        elif len(result) >= 3:
            loss = result[0]
            metrics = list(result[1:])
        if len(val_result) == 2:
            val_loss, val_metrics = val_result
            if not isinstance(val_metrics, list):
                val_metrics = [val_metrics]
        elif len(val_result) >= 3:
            val_loss = val_result[0]
            val_metrics = list(val_result[1:])
        if isinstance(metrics, list) and len(metrics) >= 2:
            mae, afmae = metrics[0], metrics[1]
        elif isinstance(metrics, list) and len(metrics) == 1:
            mae = metrics[0]
            afmae = metrics[0]
        else:
            mae = metrics
            afmae = metrics
        if isinstance(val_metrics, list) and len(val_metrics) >= 2:
            val_mae, val_afmae = val_metrics[0], val_metrics[1]
        elif isinstance(val_metrics, list) and len(val_metrics) == 1:
            val_mae = val_metrics[0]
            val_afmae = val_metrics[0]
        else:
            val_mae = val_metrics
            val_afmae = val_metrics
        return loss, mae, afmae, val_loss, val_mae, val_afmae

    def train_model(self):
        # (magn_num, freq_num, point_num) -> (magn_num * freq_num, point_num, 1)
        x_train_feature = self.x_train_shuffle.reshape(
            -1, self.x_train_shuffle.shape[2], 1)
        y_train_feature = self.y_train_shuffle.reshape(
            -1, self.y_train_shuffle.shape[2], 1)
        x_test_feature = self.x_test_shuffle.reshape(
            -1, self.x_test_shuffle.shape[2], 1)
        y_test_feature = self.y_test_shuffle.reshape(
            -1, self.y_test_shuffle.shape[2], 1)
        self.state_manager['training_alive'] = True
        # 断点续训
        if self.config.resume_training:
            print(f'加载断点...')
            if os.path.exists(self.model_comp.best_weights_file):
                try:
                    self.load_best_weights()
                except Exception as e:
                    print("加载最佳权重失败，将从头开始训练。")
                    print(e)
            else:
                print(f"未找到最佳权重文件，将从头开始训练。")
        else:
            print(f"将从头开始训练。")
        print(f'评估初始权重...')
        # 计算初始 loss
        loss, mae, afmae, val_loss, val_mae, val_afmae = self.evaluate_loss()
        lr = 0
        power_log_loss = afmae
        print(f'初始 loss: {loss:.4f}')
        self.state_manager['loss'] = loss
        self.state_manager['min_loss'] = loss
        self.state_manager['val_loss'] = val_loss
        self.state_manager['min_val_loss'] = val_loss
        self.state_manager['mae'] = mae
        self.state_manager['afmae'] = afmae
        self.state_manager['val_mae'] = val_mae
        self.state_manager['val_afmae'] = val_afmae
        # 实例化回调函数
        real_time_plotting_callback = RealTimeTrainingCallback(
            self
        )
        # 开始训练
        print(f'x_train_feature shape: {x_train_feature.shape}')
        print(f'y_train_feature shape: {y_train_feature.shape}')
        self.model_comp.fit(
            x_train_feature,
            y_train_feature,
            validation_data=(x_test_feature, y_test_feature),
            epochs=self.config.epoch_train -
            self.state_manager.get('completed_epoch', 0),
            batch_size=self.batch_size,
            verbose=0,
            callbacks=[real_time_plotting_callback],
            shuffle=False  # RVTDCNN 模型的时序会被shuffle打乱
        )
        self.state_manager['training_alive'] = False

    def predict_FR(self, USE_PREDICT_LINEAR=True):
        # 频率响应预测
        if self.config.dataset_type == 'MET':
            FR_for_comp_real_data(
                self.model_comp,
                self.dataset_test,
                freq_range=freq_config_manager.get_freq_range_hz(self.config, (10, 128)),
                gain_range=(30, 200),
                freq_start_skip=0,
                freq_end_skip=2,
                output_folder=self.checkpoint_dir,
                use_linear_response=USE_PREDICT_LINEAR
            )
        elif self.config.dataset_type == 'PE':
            FR_for_comp_real_data(
                self.model_comp,
                self.dataset_test,
                output_folder=self.checkpoint_dir,
                freq_start_skip=0,
                freq_end_skip=0,
                use_linear_response=USE_PREDICT_LINEAR
            )
        elif self.config.dataset_type == 'AliasSimu':
            FR_for_comp_real_data(
                self.model_comp,
                self.dataset_test,
                output_folder=self.checkpoint_dir,
                freq_start_skip=0,
                freq_end_skip=0,
                use_linear_response=USE_PREDICT_LINEAR
            )
        elif self.config.dataset_type == 'Alias':
            FR_for_comp_real_data(
                self.model_comp,
                self.dataset_test,
                output_folder=self.checkpoint_dir,
                freq_start_skip=0,
                freq_end_skip=0,
                use_linear_response=USE_PREDICT_LINEAR
            )
        else:
            raise ValueError(f'未知的数据集类型: {self.config.dataset_type}')
        
        if USE_PREDICT_LINEAR:
            checkpoint_dir_normalized = self.checkpoint_dir.replace('\\', '/')
            if checkpoint_dir_normalized.endswith('/data'):
                project_path = checkpoint_dir_normalized[:-5]
            else:
                project_path = os.path.dirname(os.path.dirname(self.checkpoint_dir.replace('\\', '/')))
            if project_path.startswith('projects/'):
                projects_root = 'projects'
                project_rel_path = project_path[len('projects/'):]
            else:
                parts = project_path.split('/')
                projects_root = '/'.join(parts[:-1])
                project_rel_path = parts[-1]
            try:
                logger.info(f'生成频响补偿对比图...')
                quick_compare(
                    project1=project_rel_path,
                    project2=project_rel_path,
                    state1='origin',
                    state2='compensation',
                    layout='overlay',
                    output_dir=self.checkpoint_dir,
                    projects_root=projects_root,
                    dpi=150
                )
                logger.info(f'频响补偿对比图已保存到 {self.checkpoint_dir}')
            except Exception as e:
                logger.warning(f'生成频响补偿对比图失败: {e}')

    def predict_TR(self):
        # 时域响应预测
        x_tr = TimeSeries(
            samples=self.dataset_origin.output_ori, fs=self.config.sample_rate)
        y_tr = TimeSeries(
            samples=self.dataset_origin.output_tar, fs=self.config.sample_rate)
        y_pred = self.model_comp.time_response(
            x_tr, batch_size=self.batch_size)

        y_tr.plot(label='True')
        y_pred.plot(label='Predict')
        plt.legend()
        plt.tight_layout()

    def predict_TR_from_file(self, file_path):
        tr_input_list, tr_output_list, freq_list = data_processing.load_and_preprocess_data(
            file_path,
            # fade_in=0.0,
            # fade_out=0.0,
            # time_cliped_s=None
        )
        tr_input_list_base, tr_output_list_base, freq_list_base = data_processing.load_and_preprocess_data(
            self.config.get_full_path(self.config.PREDICT_TR_FILE_PATH_BASE),
            # # fade_in=0.0,
            # # fade_out=0.0,
            # time_cliped_s=None
        )
        # tr_comp_list = [self.model_comp.time_response(
        #     tr_output, batch_size=self.batch_size) for tr_output in tr_output_list]

        # for i, tr_comp in enumerate(tr_comp_list):
        #     tr_comp.plot(label=f'Comp_{i}')
        # for i, tr_output in enumerate(tr_output_list):
        #     tr_output.plot(label=f'True_{i}')
        zeta = 0.8510095448317654
        f_n = 34.576789157276444
        amp = 114.29307223621167

        # mid_index = len(tr_input_list) // 2
        index = len(tr_input_list) - 8
        if index < 0:
            index = 0
        if index >= len(tr_input_list):
            index = len(tr_input_list) - 1
        s = exam_class.System.s
        sys_target = exam_class.System.fromSymbol(amp * 4 * np.pi * f_n * zeta * s / (
            s ** 2 + 4 * np.pi * f_n * zeta * s + 4 * (np.pi**2) * (f_n ** 2)))
        # sys_target.plot(label='Target')

        if len(tr_input_list) < 5:
            # contact
            tr_input = TimeSeries.concatenate(tr_input_list)
            tr_output = TimeSeries.concatenate(tr_output_list)
            tr_output_base = TimeSeries.concatenate(tr_output_list_base)
        else:
            tr_input = tr_input_list[index]
            tr_output = tr_output_list[index]
            tr_output_base = tr_output_list_base[index]

        tr_input = tr_input.invert()
        # tr_target = sys_target.time_response(tr_input)
        # tr_output = tr_output.apply_gain(1/16)

        # tr_output = tr_output.offset(-12.5)
        tr_output = tr_output.limit(-44, 42)

        if 1:
            # tr_output_base = tr_output_base.apply_gain(9.2/7.4)
            tr_target = self.model_comp.time_response(
                tr_output_base, batch_size=self.batch_size)
        else:
            tr_target = tr_output_base

        tr_comp = self.model_comp.time_response(
            tr_output, batch_size=self.batch_size)

        tr_target = tr_target.apply_gain(1.2/0.36)

        # tr_target = tr_target.filter(filter_type='bandpass', cutoff_freq=[
        #                            10, 100])
        # tr_comp = tr_comp.filter(filter_type='bandpass', cutoff_freq=[
        #                            10, 100])
        # tr_output = tr_output.filter(filter_type='bandpass', cutoff_freq=[
        #                            10, 100])

        tr_target.plot(label='Target')
        tr_comp.plot(label='Comp')
        tr_output.plot(label='Origin')

        plt.legend()
        plt.tight_layout()

    def predict_linspace(
            self,
            start=0.2,
            stop=2,
            fs: int = 2000,
            time_length: float = 1,
            fade_in: float = 0.0,
            fade_out: float = 0.0,
            debug: bool = True
    ):
        """
        基于线性间隔生成输入数据并进行预测。

        Args:
            start (float): 生成线性时间序列的起始值。
            stop (float): 生成线性时间序列的终止值。
            fs (int): 采样频率。
            time_length (float): 时间长度（秒）。
            fade_in (float): 渐入比例（0.0 到 1.0）。
            fade_out (float): 渐出比例（0.0 到 1.0）。
            debug (bool): 是否启用调试模式，绘制生成的时间序列和预测结果。
        """
        self.model_comp.predict_linspace()

    def predict_features(self, post_filter=False):
        # 特征预测
        # (magn_num, freq_num, point_num) -> (magn_num * freq_num, point_num, 1)
        x = self.x_test.reshape(-1, self.x_test.shape[2], 1)
        y = self.y_test.reshape(-1, self.y_test.shape[2], 1)
        y_pred = self.model_comp.predict(
            x,
            batch_size=self.batch_size,
            use_scaler=False,
        )
        # y_pred: (batch_size, seq_len, 1)
        # 将 y_pred 压平为一维数组
        # -> (batch_size, seq_len)
        x = x.reshape(x.shape[0], x.shape[1])
        y = y.reshape(y.shape[0], y.shape[1])
        y_pred = y_pred.reshape(y_pred.shape[0], y_pred.shape[1])
        # save to json with {"freq": freq, "magn":, "data":{"origin": x, "comped": y_pred, "target": y}}
        json_data = []
        for i, freq in enumerate(self.freq_select):
            for j, magn in enumerate(self.magn_select):
                x_item = x[j*len(self.freq_select) + i].tolist()
                y_pred_item = y_pred[j*len(self.freq_select) + i].tolist()
                y_item = y[j*len(self.freq_select) + i].tolist()
                data_item = {
                    "freq": freq,
                    "magn": magn,
                    "data": {
                        "origin": x_item,
                        "comped": y_pred_item,
                        "target": y_item
                    }
                }
                json_data.append(data_item)
        with open(f'cache/predict_features.json', 'w') as f:
            json.dump(json_data, f, indent=1)

        # 抽取前 10 个 batch 的数据
        x = x[:10]
        y_pred = y_pred[:10]
        y = y[:10]
        if post_filter:
            # 对每个数据进行滤波
            x_tr_list = [TimeSeries(
                samples=xi, fs=self.config.sample_rate) for xi in x]
            y_pred_tr_list = [TimeSeries(
                samples=yi, fs=self.config.sample_rate) for yi in y_pred]
            y_tr_list = [TimeSeries(
                samples=yi, fs=self.config.sample_rate) for yi in y]
            x_tr_list = [xi.filter(filter_type='bandpass', cutoff_freq=[
                                   10, 128]) for xi in x_tr_list]
            y_pred_tr_list = [yi.filter(filter_type='bandpass', cutoff_freq=[
                                        10, 128]) for yi in y_pred_tr_list]
            y_tr_list = [yi.filter(filter_type='bandpass', cutoff_freq=[
                                   10, 128]) for yi in y_tr_list]
            x = np.array([xi.samples for xi in x_tr_list])
            y_pred = np.array([yi.samples for yi in y_pred_tr_list])
            y = np.array([yi.samples for yi in y_tr_list])
        x = x.reshape(-1)
        y_pred = y_pred.reshape(-1)
        y = y.reshape(-1)
        plt.figure(figsize=(12, 8))
        plt.plot(x, label='origin')
        plt.plot(y_pred, label='comped')
        plt.plot(y, label='target')
        plt.title('Predict features')
        plt.legend()
        plt.tight_layout()

    def plot_spline(self):
        self.model_comp.plot_spline(feature_range=self.config.feature_range)

    def predict_SIN(self):
        # 正弦频率响应测试
        amplitudes = [1, 50, 100, 200]
        for amp in amplitudes:
            kan_fr = self.model_comp.frequency_response_system(
                time_length=10,
                f_range=(5, 200),
                points=20,
                amplitude=amp
            )
            kan_fr.plot(label=f'A={amp}')
        plt.legend()
        plt.tight_layout()
