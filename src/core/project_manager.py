"""
项目管理模块

包含 ProjectManager 类，负责管理项目的训练、评估、推理等各种任务。
从 cli.py 中移动而来，保持所有原有功能不变。
"""

import logging
import os
import traceback
import sys
import shutil
from analysis.model_compute_analysis import save_model_compute_analysis
from models.base_models import ModelEvent, ModelEventType
from calibration_analyzer import exam_class
from config import Config
import config
from core.model_engine import ModelEngine
from core.training_log import TrainingLogger
import matplotlib.pyplot as plt
from core.training_state import TrainingStateManager
from inference.manager import InferenceManager

logger = logging.getLogger(__name__)


class ProjectManager:

    def __init__(self, project_path):
        self.project_path = project_path
        self.project_name = project_path.split('/')[-1]
        self.config_path = f'{self.project_path}/config.json'
        self.checkpoint_dir = f'{self.project_path}/data'
        self.config = Config.load_from_json(self.config_path)
        self.state_manager = TrainingStateManager(project_name=self.project_name, checkpoint_dir=self.checkpoint_dir)
        self.training_logger = TrainingLogger(self.checkpoint_dir)
        self._inference_manager = None

    def process(self):
        model_engine = ModelEngine(self, checkpoint_dir=self.checkpoint_dir)
        logger.info(f'Project: {self.project_name}')
        model_engine = self.prepare_dataset_and_model(model_engine)
        if self.config.use_train_model:
            model_engine.train_model()
        if self.config.USE_ASSIGN_WEIGHTS:
            assert self.config.use_model == 'FRIKAN'
            dweights = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
            weights = [0] * len(dweights)
            for i in range(len(dweights)):
                weights[i] = sum(dweights[:i + 1])
            model_engine.model_comp.assign_weights(0, weights)
        self.run_prediction(model_engine)
        if self.config.use_train_model:
            model_engine.evaluate_training_info()
        if sys.platform.startswith('win'):
            plt.ioff()
            plt.show()
        if self.config.adjust_weight:
            while True:
                plt.pause(0.1)
                try:
                    if exam_class.System.ax_gain is not None:
                        exam_class.System.ax_gain.cla()
                    cmd = input('请输入权重调整指令，示例：0 0.1\n')
                    if cmd == 'exit' or cmd == 'q':
                        exit(0)
                    widx, wval = cmd.split()
                    widx = int(widx)
                    wval = float(wval)
                    dweights[widx] = wval
                    for i in range(len(dweights)):
                        weights[i] = sum(dweights[:i + 1])
                    logger.info(f'w:{weights}')
                    model_engine.model_comp.assign_weights(0, weights)
                    model_engine.predict_FR(self.config.USE_PREDICT_LINEAR)
                except Exception as e:
                    error_msg = f'调整权重失败：{e}'
                    logger.error(error_msg)
                    traceback.print_exc()

    def prepare_dataset_and_model(self, model_engine: ModelEngine):
        """初始化模型，包括加载数据集、准备数据、构建模型和加载基础模型权重"""
        model_engine.load_dataset(self.config.dataset_type)
        model_engine.prepare_training_data()
        if 'FRIKAN' in self.config.use_model and 'MET' in self.config.dataset_type and (self.config.H_UNITS > 0):
            model_engine.prepare_systems()
        model_engine.build_model()
        model_engine.dump_model_info(output_folder=self.checkpoint_dir)
        if hasattr(self.config, 'base_project') and self.config.base_project:
            logger.info(f"使用基础模型 '{self.config.base_project}' 加载权重")
            self.load_base_model_weights(model_engine)
        return model_engine

    def run_prediction(self, model_engine: ModelEngine):
        """执行所有预测和评估任务的公共方法"""
        model_engine.model_comp.exec_callback(ModelEvent(ModelEventType.PREDICT_START))
        if self.config.use_spline and self.config.use_model == 'FRIKAN':
            model_engine.plot_spline()
        if self.config.use_predict_fr:
            logger.info(f'预测频率响应...')
            model_engine.predict_FR(self.config.USE_PREDICT_LINEAR)
        if self.config.USE_PREDICT_LINSPACE:
            model_engine.predict_linspace()
        if self.config.use_predict_tr:
            logger.info(f'预测时域响应...')
            model_engine.predict_TR()
        if self.config.use_predict_features:
            model_engine.predict_features()
        if self.config.use_sin_fr:
            model_engine.predict_SIN()
        if self.config.use_predict_tr_from_file:
            logger.info(f'预测文件中的时域响应...')
            model_engine.predict_TR_from_file(self.config.get_full_path(self.config.PREDICT_TR_FILE_PATH))
        model_engine.model_comp.exec_callback(ModelEvent(ModelEventType.PREDICT_END))

    def load_base_model_weights(self, model_engine):
        """从基础模型加载权重"""
        if not self.config.base_project:
            return False
        base_project_name = self.config.base_project
        base_project_path = f'projects/{base_project_name}'
        base_checkpoint_dir = f'{base_project_path}/data'
        if not os.path.exists(base_checkpoint_dir):
            logger.info(f'警告: 基础模型目录不存在: {base_checkpoint_dir}')
            return False
        best_val_weights_file = os.path.join(base_checkpoint_dir, 'best_val.weights.h5')
        if not os.path.exists(best_val_weights_file):
            logger.info(f'警告: 基础模型权重文件不存在: {best_val_weights_file}')
            return False
        try:
            logger.info(f"正在从基础模型 '{base_project_name}' 加载权重: {best_val_weights_file}")
            model_engine.model_comp.load_weights(best_val_weights_file)
            logger.info(f'成功加载基础模型权重')
            new_best_val_weights_file = os.path.join(self.checkpoint_dir, 'best_val.weights.h5')
            if not os.path.exists(new_best_val_weights_file):
                os.makedirs(self.checkpoint_dir, exist_ok=True)
                shutil.copy(best_val_weights_file, new_best_val_weights_file)
                best_weights_file = best_val_weights_file.replace('best_val', 'best')
                new_best_weights_file = new_best_val_weights_file.replace('best_val', 'best')
                shutil.copy(best_weights_file, new_best_weights_file)
                logger.info(f'复制基础模型权重文件到当前项目目录: {new_best_val_weights_file}')
            return True
        except Exception as e:
            error_msg = f'加载基础模型权重失败: {e}'
            logger.error(error_msg)
            traceback.print_exc()
            return False

    def evaluate(self):
        model_engine = ModelEngine(self, checkpoint_dir=self.checkpoint_dir)
        model_engine = self.prepare_dataset_and_model(model_engine)
        if self.config.use_train_model:
            try:
                model_engine.evaluate_training_info()
            except Exception as e:
                error_msg = f'Evaluate training info failed: {e}'
                logger.error(error_msg)
                traceback.print_exc()
        if self.config.use_best_val_weights:
            model_engine.load_val_best_weights()
        compute_analysis_path = os.path.join(
            self.checkpoint_dir,
            'compute_analysis.json'
        )
        save_model_compute_analysis(
            model_engine.model_comp,
            compute_analysis_path,
            model_type=self.config.use_model,
            cost_model=getattr(self.config, 'compute_cost_model', None),
        )
        loss, mae, afmae, val_loss, val_mae, val_afmae = model_engine.evaluate_loss()
        self.run_prediction(model_engine)
        logger.info(f'训练集 loss: {loss:.4f}')
        logger.info(f'验证集 loss: {val_loss:.4f}')
        logger.info(f'训练集 MAE: {mae:.4f}')
        logger.info(f'训练集 AFMAE: {afmae:.4f}')
        logger.info(f'验证集 MAE: {val_mae:.4f}')
        logger.info(f'验证集 AFMAE: {val_afmae:.4f}')
        logger.info(f'评估完成，结果保存在 {self.checkpoint_dir} 中。')

    def lut(self):
        from experimental import kan_lut
        model_engine = ModelEngine(self, checkpoint_dir=self.checkpoint_dir)
        model_engine = self.prepare_dataset_and_model(model_engine)
        if self.config.use_best_val_weights:
            model_engine.load_val_best_weights()
        lut_model = kan_lut.ModelKAN_LUT(lut_points=800)
        weights_json_path = model_engine.model_comp.best_val_weights_file.replace('.h5', '.json')
        lut_model.load_weights_json(weights_json_path)
        x_test = model_engine.x_test_shuffle[201, 1000:1100, :].reshape(1, -1, 1)
        x_test_lut = x_test.reshape(-1, 1)
        logger.info(f'x[]: {x_test_lut}')
        iir_out = model_engine.model_comp.fast_iir(x_test)
        model_out = model_engine.model_comp.fast_model(iir_out)[0, :, 0].numpy()
        lut_out = lut_model.forward(x_test_lut, use_lut=False)
        logger.info(f'y[]: {model_out}')
        plt.figure(figsize=(12, 8))
        plt.plot(lut_out, label='LUT', linestyle='', marker='o')
        plt.plot(model_out, label='Model')
        plt.legend()
        plt.tight_layout()
        plt.show()

    def model_info(self):
        model_engine = ModelEngine(self, checkpoint_dir=self.checkpoint_dir)
        model_engine.load_dataset(self.config.dataset_type)
        model_engine.prepare_training_data()
        model_engine.prepare_systems()
        model_engine.build_model()
        model_engine.dump_model_info(output_folder=self.checkpoint_dir)
        compute_analysis_path = os.path.join(
            self.checkpoint_dir,
            'compute_analysis.json'
        )
        save_model_compute_analysis(
            model_engine.model_comp,
            compute_analysis_path,
            model_type=self.config.use_model,
            cost_model=getattr(self.config, 'compute_cost_model', None),
        )
        model_engine.evaluate_training_info()
        logger.info(f'模型信息保存在 {self.checkpoint_dir} 中。')

    @property
    def inference_manager(self):
        """延迟创建推理管理器"""
        if self._inference_manager is None:
            self._inference_manager = InferenceManager(self)
        return self._inference_manager

    def run_inference(self, force=False, quick=False, layers=None):
        """委托给推理管理器"""
        self.inference_manager.run_inference(force=force, quick=quick, layers=layers)

    def analyze_errors(self, force=False):
        """委托给推理管理器"""
        self.inference_manager.analyze_errors(force=force)

    def generate_wave_data(self, output_folder=None, compress=True, force=False):
        """
        生成波形数据
        
        Args:
            output_folder: 输出目录，默认为项目目录下的 wave_output
            compress: 是否压缩波形文件
            force: 是否强制覆盖已存在的文件
            
        Returns:
            Dict: 包含生成的文件路径和元数据
        """
        from core.wave_generator import DatasetWaveGenerator
        generator = DatasetWaveGenerator(self)
        return generator.generate_wave_data(output_folder=output_folder, compress=compress, force=force)

    def load_dataset(self):
        """加载项目数据集用于可视化
        
        Returns:
            Dataset_COMP: 数据集实例，包含output_ori和output_tar数据
        """
        # 创建ModelEngine实例并加载数据集
        from core.model_engine import ModelEngine
        model_engine = ModelEngine(self, checkpoint_dir=self.checkpoint_dir)
        model_engine.load_dataset(self.config.dataset_type)
        return model_engine.dataset_origin

    def visualize_bias_comparison(self, baseline_dir=None, compensated_dir=None, 
                                output_dir=None, config_path=None):
        """委托给可视化管理器"""
        from inference.visualization_manager import BiasVisualizationManager
        viz_manager = BiasVisualizationManager(self)
        return viz_manager.run_visualization(
            baseline_dir=baseline_dir,
            compensated_dir=compensated_dir,
            output_dir=output_dir,
            config_path=config_path
        )