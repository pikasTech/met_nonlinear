"""
Origin/Target波形可视化模块

专门处理Origin和Target波形的对比可视化，支持按频率和震级生成分类图表
使用ProcessPoolExecutor进行并行化加速，避免matplotlib多线程问题
"""

import os
import asyncio
import concurrent.futures
import matplotlib
matplotlib.use('Agg')  # 无GUI后端，必须在pyplot导入前设置
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Dict, List, Tuple, Any
import logging
from calibration_analyzer.exam_class import TimeSeries

logger = logging.getLogger(__name__)


def _plot_waveform_process(task_data: Dict) -> Optional[str]:
    """独立进程中执行的波形绘制函数"""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from calibration_analyzer.exam_class import TimeSeries
    
    try:
        dataset = task_data['dataset']
        mag_idx = task_data['mag_idx']
        freq_idx = task_data['freq_idx']
        magnitude = task_data['magnitude']
        frequency = task_data['frequency']
        output_path = task_data['output_path']
        
        # 提取数据
        origin_data = dataset.output_ori[mag_idx, freq_idx, :]
        target_data = dataset.output_tar[mag_idx, freq_idx, :]
        
        # 创建TimeSeries对象
        origin_ts = TimeSeries(samples=origin_data, fs=dataset.fs)
        target_ts = TimeSeries(samples=target_data, fs=dataset.fs)
        
        # 创建新的figure
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        
        # 绘制波形
        ax.plot(origin_ts.time, origin_ts.samples, 
               label=f'Origin (Mag={magnitude:.2f})', 
               color='blue', alpha=0.7, linewidth=1.5)
        ax.plot(target_ts.time, target_ts.samples, 
               label=f'Target (Mag={magnitude:.2f})', 
               color='red', alpha=0.7, linewidth=1.5)
        
        # 设置图形属性
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        ax.set_title(f'Origin vs Target Waveforms\n'
                    f'Frequency: {frequency:.1f} Hz, Magnitude: {magnitude:.2f}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 调整布局并保存
        fig.tight_layout()
        fig.canvas.draw()
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        
        # 清理资源
        plt.close(fig)
        plt.clf()
        
        return output_path
        
    except Exception as e:
        # 确保清理资源
        try:
            plt.close('all')
            plt.clf()
        except:
            pass
        raise Exception(f"绘制波形失败 {task_data.get('output_path', 'unknown')}: {e}")

class WaveformVisualizer:
    """Origin/Target波形可视化器 - 支持asyncio并行化加速"""
    
    def __init__(self, project_manager, max_workers=None):
        self.project_manager = project_manager
        self.output_dir = os.path.join(
            project_manager.checkpoint_dir, 
            'visualizations',
            'waveforms'  # 专门的波形子目录
        )
        os.makedirs(self.output_dir, exist_ok=True)
        # 设置最大并行工作进程数，基于系统CPU线程数
        cpu_count = os.cpu_count() or 1
        if max_workers is None:
            # 使用CPU线程数进行并行处理
            self.max_workers = cpu_count
        else:
            self.max_workers = max_workers
        
        logger.info(f"初始化波形可视化器: CPU线程数={cpu_count}, 使用进程数={self.max_workers}")
    
    def visualize_dataset(self, force: bool = False) -> Dict[str, Any]:
        """
        生成数据集的所有波形可视化图 - 使用asyncio并行化
        
        Args:
            force: 是否强制重新生成已存在的文件
            
        Returns:
            Dict: 包含生成的文件路径信息
        """
        # 使用asyncio运行异步方法
        return asyncio.run(self._visualize_dataset_async(force))
    
    async def _visualize_dataset_async(self, force: bool = False) -> Dict[str, Any]:
        """异步版本的数据集可视化方法"""
        logger.info(f"开始并行化波形生成，最大并行数: {self.max_workers}")
        
        # 1. 加载数据集
        dataset = self._load_dataset()
        
        # 2. 准备所有任务
        tasks = []
        for mag_idx, magnitude in enumerate(dataset.magn_list):
            for freq_idx, frequency in enumerate(dataset.freq_list):
                output_path = self._get_output_path(magnitude, frequency)
                
                # 检查现有文件
                if os.path.exists(output_path) and not force:
                    logger.debug(f"跳过已存在的文件: {os.path.basename(output_path)}")
                    continue
                
                # 创建任务
                task_data = {
                    'dataset': dataset,
                    'mag_idx': mag_idx,
                    'freq_idx': freq_idx,
                    'magnitude': magnitude,
                    'frequency': frequency,
                    'output_path': output_path
                }
                tasks.append(task_data)
        
        logger.info(f"需要生成 {len(tasks)} 个波形图")
        
        # 3. 并行执行任务
        generated_files = []
        skipped_files = []
        
        if tasks:
            logger.info(f"开始并行处理 {len(tasks)} 个波形图...")
            
            # 使用ProcessPoolExecutor进行并行处理，避免matplotlib多线程问题
            with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                # 创建future任务列表
                future_to_task = {
                    executor.submit(_plot_waveform_process, task): task 
                    for task in tasks
                }
                
                # 进度跟踪
                completed_count = 0
                total_count = len(future_to_task)
                
                # 收集结果
                for future in concurrent.futures.as_completed(future_to_task):
                    task = future_to_task[future]
                    try:
                        result = future.result()
                        if result:
                            generated_files.append(result)
                            completed_count += 1
                            
                            # 每处理10个文件或处理完毕时显示进度
                            if completed_count % 10 == 0 or completed_count == total_count:
                                progress = (completed_count / total_count) * 100
                                logger.info(f"进度: {completed_count}/{total_count} ({progress:.1f}%) - 最新: {os.path.basename(result)}")
                    except Exception as e:
                        logger.error(f"生成波形图失败 {task['output_path']}: {e}")
                        completed_count += 1
        
        # 统计跳过的文件
        for mag_idx, magnitude in enumerate(dataset.magn_list):
            for freq_idx, frequency in enumerate(dataset.freq_list):
                output_path = self._get_output_path(magnitude, frequency)
                if os.path.exists(output_path) and output_path not in generated_files:
                    skipped_files.append(output_path)
        
        logger.info(f"并行化生成完成: 生成 {len(generated_files)} 个文件，跳过 {len(skipped_files)} 个文件")
        
        return {
            'generated_files': generated_files,
            'skipped_files': skipped_files,
            'output_directory': self.output_dir,
            'total_combinations': len(dataset.magn_list) * len(dataset.freq_list)
        }
    
    def _load_dataset(self):
        """加载项目数据集"""
        # 复用ProjectManager的数据集加载逻辑
        return self.project_manager.load_dataset()
    
    def _get_output_path(self, magnitude: float, frequency: float) -> str:
        """生成输出文件路径"""
        filename = f"waveform_mag{magnitude:.2f}_freq{frequency:.1f}Hz.png"
        return os.path.join(self.output_dir, filename)
