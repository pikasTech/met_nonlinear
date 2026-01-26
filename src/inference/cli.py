import logging
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
'\n命令行接口模块\n\n此模块提供推理工具的命令行接口\n'
import argparse
import os
from .processor import InferenceProcessor, USE_SCALER

def main():
    """主函数，用于测试推理功能"""
    default_input = 'inference/temp/dataset_input.wave'
    if not os.path.exists(default_input):
        logger.info(f'警告: 默认输入文件不存在: {default_input}')
        logger.info('请检查文件位置或使用 --input 参数指定正确路径')
    parser = argparse.ArgumentParser(description='模型推理工具')
    parser.add_argument('--model', type=str, default='projects/WNET5q1h2u6l3', help='模型路径')
    parser.add_argument('--input', type=str, default='inference/temp/dataset_input.wave', help='输入波形文件路径')
    parser.add_argument('--output', type=str, default='inference/temp/dataset_inference.wave', help='输出波形文件路径')
    parser.add_argument('--layer_dir', type=str, default='inference/temp/layers', help='分层输出目录路径')
    parser.add_argument('--comparison_dir', type=str, default='data/spice_comparison', help='SPICE对比数据目录路径')
    parser.add_argument('--magnitude', type=float, default=6.0, help='指定要过滤的震级值，不指定则使用样本数最多的震级')
    parser.add_argument('--process', action='store_true', default=False, help='是否进行数据处理（仿真）')
    args = parser.parse_args()
    model_path = args.model
    input_wave_path = args.input
    output_wave_path = args.output
    layer_dir = args.layer_dir
    comparison_dir = args.comparison_dir
    inference_processor = InferenceProcessor(model_path)
    if args.process:
        logger.info('\n进行推理并保存结果...')
        output_dir = os.path.dirname(output_wave_path)
        result = inference_processor.infer_and_save(input_wave_path, output_dir=output_dir, use_scaler=USE_SCALER)
        logger.info(f'推理完成，返回结果类型: {result.backend_type}')
        logger.info('\n测试分层推理功能...')
        inference_processor.set_backend('layer_by_layer')
        layer_result = inference_processor.infer_and_save(input_wave_path, output_dir=layer_dir, use_scaler=USE_SCALER, return_layers=True)
        logger.info(f'分层推理完成，共{len(layer_result.layers)}层')
        output_wave_path = layer_result.get_final_output().file_path
        logger.info('\n测试SPICE后端和分层后端对比功能...')
        inference_processor.generate_spice_comparison_data(input_wave_path, comparison_dir, use_scaler=USE_SCALER)
    logger.info('\n可视化推理结果...')
    inference_processor.visualize_results(input_wave_path, output_wave_path)
    logger.info('\n可视化分层结果...')
    inference_processor.visualize_layer_results(input_wave_path, layer_dir)
    logger.info('\n比较最后一层输出和直接输出...')
    inference_processor.compare_layer_with_direct_output(input_wave_path, layer_dir, output_wave_path)
    logger.info('\n分析SPICE对比数据...')
    comparison_results = inference_processor.analyze_spice_comparison(comparison_dir)
    if 'comparison_stats' in comparison_results:
        logger.info('\n总体对比统计信息:')
        for layer_stats in comparison_results['comparison_stats']:
            layer_index = layer_stats.get('layer_index', '?')
            layer_name = layer_stats.get('layer_name', f'Layer {layer_index}')
            logger.info(f'层 {layer_name}:')
            logger.info(f'  平均误差: {layer_stats.get("mean_error", 0):.6f}')
            logger.info(f'  误差标准差: {layer_stats.get("std_error", 0):.6f}')
            logger.info(f'  最大误差: {layer_stats.get("max_error", 0):.6f}')
            logger.info(f'  RMS误差: {layer_stats.get("rms_error", 0):.6f}')
if __name__ == '__main__':
    main()