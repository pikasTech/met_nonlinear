import os
import json
import sys
import logging
from matplotlib import pyplot as plt

FREQ_LIST = [1, 10, 100, 1000]
FREQ_START_SKIP = 6
FREQ_END_SKIP = 6
CONF_DROPOUT = 0.0


USE_REAL_TIME_PLOT = False
IN_DEBUG = sys.gettrace() is not None
if IN_DEBUG:
    USE_REAL_TIME_PLOT = False
    # print("Debug 模式下禁用实时绘图。")


class Config:
    def __init__(self):
        self.using_gpu = True
        self.epoch_train = 200000
        self.step_per_epoch = 2
        self.learning_rate = 0.01
        self.use_train_model = True
        self.use_model = 'GRN'  # 可以是 'GRN', 'FRIKAN', 'LSTM', 'Transformer', 'WaveNet', 'RNN'
        self.use_power_loss = True
        self.loss_type = None
        self.use_points = 8000
        self.resume_training = True  # 断点续训
        self.use_best_val_weights = True  # 加载旧的权重文件
        self.SPLINE_ORDER = 2
        self.use_auto_lr = True  # 余弦退火学习率调整
        self.auto_lr_decay_steps = 100
        self.IIR_TRAINABLE = False
        self.USE_FAST_MODEL = True
        self.IIR_INIT_BY_SYSTEM = True
        self.USE_ASSIGN_WEIGHTS = False  # 手动指定权重
        self.use_scale = True  # 数据归一化
        self.use_predict_features = False  # 进行预测
        self.use_predict_tr = False  # 时域响应预测
        self.use_predict_tr_from_file = False
        self.RESTART_AFTER_N_CYCLES = 50
        # self.PREDICT_TR_FILE_PATH = 'data\output_20250116_162604_MTSS-1-Ws_震级0.0_data.json'
        # self.PREDICT_TR_FILE_PATH = "data/M50/output_20241022_164246_MTSS1_ws_A16_震级5.0_data.json"
        # self.PREDICT_TR_FILE_PATH ="data\output_20250117_144925_MTSS-1-Ws-冲击_A16_震级0.0_data.json"
        # self.PREDICT_TR_FILE_PATH ="data\output_20250117_161920_MTSS-1-Ws-冲击_A16_震级0.0_data.json"
        # self.PREDICT_TR_FILE_PATH ="data\output_20250117_182948_MTSS-1-Ws-周期多频_A16_震级2.5_data.json"
        # self.PREDICT_TR_FILE_PATH ="data\output_20250117_191736_MTSS-1-Ws-周期多频_A16_震级1.0_data.json"
        # self.PREDICT_TR_FILE_PATH_BASE ="data\output_20250117_183139_MTSS-1-Ws-周期多频_A16_震级0.1_data.json"
        self.PREDICT_TR_FILE_PATH = "data/output_20250117_205108_MTSS-1-Ws-40-80Hz_A16_震级1.2_data.json"
        self.PREDICT_TR_FILE_PATH_BASE = "data/output_20250117_205021_MTSS-1-Ws-40-80Hz_A16_震级0.36_data.json"
        self.use_predict_fr = True  # 频率响应预测
        self.USE_PREDICT_LINEAR = True
        self.USE_PREDICT_LINSPACE = False
        self.use_cache_features = True
        self.use_spline = False
        self.use_sin_fr = False
        self.use_debug_plot = False
        self.sample_rate = 2000
        self.time_clipped_s = 4.0
        self.GRID_SIZE = 8
        self.FIX_SCALE_FACTOR = True
        self.H_UNITS = 16
        self.INNER_KAN_UNITS = 12
        self.INNER_KAN_LAYERS = 1
        self.kernal_units = 64
        self.basis_activation = 'tanh'
        self.feature_range = [-1, 1]
        self.data_path = 'data/M50'
        # 获取环境变量中的基路径，如果没有设置则使用空字符串
        self.data_base_path = os.environ.get(
            'MET_DATA_BASE', 'F:\\BaiduSyncdisk')
        self.target_sweep = 2
        self.dataset_type = 'MET'
        self.grid_range = (0.0, 1.0)
        self.kan_log_grid = False
        self.kan_grid_expand = True
        self.adjust_weight = False
        self.save_each_epoch = False
        self.activation = 'tanh'
        self.base_project = ""  # 默认为空字符串表示不使用base模型
        self.AUG_TIMES = 1  # 数据增广倍数
        self.AUG_N = 4
        self.RVTDCNN_memory_depth = 32
        self.RVTDCNN_nonlinearity_order = 4
        self.RVTDCNN_kernel_size = (5, 3)
        self.RVTDCNN_dense_units = 4
        self.model_subcfg = {}
        
        # 数据集配置
        self.dataset = {
            # 可选的频率范围配置，Hz单位
            # 缺省时使用传统range(6, n-4)逻辑
            'freq_range_hz': None,  # 例如: [10, 128]
            # 波形反相配置，用于解决Alias数据集的相位问题
            'inverse_origin': False,  # 反相origin波形（output_ori）
            'inverse_target': False,  # 反相target波形（output_tar）
            'inverse_input': False    # 反相input波形（inputs）
        }
        
        # 推理相关配置
        self.inference_temp_dir = "inference/temp"  # 默认推理临时目录
        
        # 偏置分析配置
        self.enable_bias_analysis = True  # 是否启用偏置分析
        self.bias_method = 'auto'  # 偏置分析方法
        self.bias_params = {}  # 偏置分析参数
        
        # 推理配置，包含偏置补偿和高通滤波器
        self.inference_config = {
            'bias_compensation': {
                'enabled': False,
                'layer_bias_adjustments': {}     # 分层调整 {0: [0.001, -0.001], 1: [0.002]}
            },
            'high_pass_config': {
                'enable': False,
                'cutoff_freq': 1.0,
                'capacitance': None,
                'resistance': None,
                'bias_voltage': 0.0,
                'auto_bias': True,
                'bias_divider_high': 10000,
                'bias_divider_low': 10000
            }
        }

        logger = logging.getLogger(__name__)
        logger.info(f"base_data_path: {self.data_base_path}")

    @property
    def full_data_path(self):
        """返回完整的数据路径，如果设置了基路径则进行拼接"""
        if self.data_base_path:
            return os.path.join(self.data_base_path, self.data_path)
        return self.data_path

    def get_full_path(self, relative_path):
        base_path = self.data_base_path
        if base_path:
            return os.path.join(base_path, relative_path)
        return relative_path
    
    def get_layer_bias_adjustment(self, layer_idx):
        """获取指定层的偏置调整值（新方法）
        
        Args:
            layer_idx: 层索引
            
        Returns:
            偏置调整值或None
        """
        bc = self.inference_config.get('bias_compensation', {})
        if not bc.get('enabled', True):
            return None
        
        layer_adjustments = bc.get('layer_bias_adjustments', {})
        return layer_adjustments.get(str(layer_idx))

    def validate_bias_compensation_config(self, model=None):
        """验证偏置补偿配置（新方法）
        
        Args:
            model: 模型对象，用于形状验证
            
        Raises:
            ValueError: 当配置验证失败时
        """
        bc = self.inference_config.get('bias_compensation', {})
        if not bc.get('enabled', True):
            return  # 配置禁用时不验证
        
        # 检查废弃的配置字段
        if 'bias_adjustment_matrix' in bc:
            raise ValueError(
                "❌ 配置中发现已废弃的 'bias_adjustment_matrix' 字段！\n"
                "此字段已被彻底移除，请使用 'layer_bias_adjustments' 代替。\n"
                "请更新您的配置文件以使用新的配置格式。"
            )
        
        layer_adjustments = bc.get('layer_bias_adjustments', {})
        if model and layer_adjustments:
            from inference.common.bias_validation import validate_bias_compensation_config
            validate_bias_compensation_config(bc, model)

    def save_to_json(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.__dict__, f, indent=4)
        logger = logging.getLogger(__name__)
        logger.info(f"配置已保存到 {file_path}")

    @classmethod
    def load_from_json(cls, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)

        # 创建默认配置实例用于比较
        config = cls()
        default_attrs = set(config.__dict__.keys())
        json_attrs = set(data.keys())

        # 检查是否存在未知字段
        unknown_attrs = json_attrs - default_attrs
        if unknown_attrs:
            raise ValueError(f"配置文件包含未知字段: {', '.join(unknown_attrs)}")

        # 检查默认值是否被更新
        for key in default_attrs & json_attrs:
            if config.__dict__[key] != data[key]:
                logger = logging.getLogger(__name__)
                logger.info(f"字段 '{key}' 的值从 {config.__dict__[key]} 更新为 {data[key]}")

        # 更新配置
        config.__dict__.update(data)
        
        # 验证偏置补偿配置（可选，因为模型可能还未加载）
        try:
            config.validate_bias_compensation_config(model=None)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"偏置补偿配置验证警告: {e}")
        
        logger = logging.getLogger(__name__)
        logger.info(f"配置已从 {file_path} 加载")
        return config
