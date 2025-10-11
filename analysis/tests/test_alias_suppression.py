"""
假频抑制评估模块的测试
"""

import pytest
import json
import os
import numpy as np
from pathlib import Path

# 导入要测试的模块
from analysis.alias_suppression import (
    evaluate_alias_suppression,
    calculate_smoothness,
    calculate_peak_improvement,
    calculate_weighted_score,
    determine_grade,
    batch_evaluate_experiments
)


@pytest.fixture
def sample_data():
    """提供测试用的样本数据"""
    test_data_path = Path(__file__).parent / 'test_data' / 'sample_linear_response.json'
    with open(test_data_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def sample_gains():
    """提供测试用的增益数据"""
    # 模拟90-100Hz区间的数据
    gains_origin = np.array([180.0, 160.0, 170.0, 190.0, 210.0, 230.0, 250.0, 260.0, 255.0, 245.0])
    gains_comped = np.array([205.0, 202.0, 203.0, 204.0, 206.0, 208.0, 210.0, 211.0, 210.5, 210.0])
    return gains_origin, gains_comped


class TestAliasSuppression:
    """测试假频抑制评估功能"""
    
    def test_evaluate_alias_suppression_with_dict(self, sample_data):
        """测试使用字典输入的评估功能"""
        results = evaluate_alias_suppression(sample_data)
        
        # 检查返回结果包含所有必要的键
        assert 'ASR_core' in results
        assert 'ASR_extended' in results
        assert 'ASR_full' in results
        assert 'smoothness_enhancement' in results
        assert 'peak_improvement_ratio' in results
        assert 'overall_score' in results
        assert 'grade' in results
        
        # 检查ASR_core的结构
        asr_core = results['ASR_core']
        assert 'suppression_ratio' in asr_core
        assert 'original_ripple' in asr_core
        assert 'compensated_ripple' in asr_core
        assert 'frequency_range' in asr_core
        assert asr_core['frequency_range'] == (90, 100)
        
        # 检查数值合理性
        assert 0 <= asr_core['suppression_ratio'] <= 100
        assert asr_core['original_ripple'] >= 0
        assert asr_core['compensated_ripple'] >= 0
        assert 0 <= results['overall_score'] <= 100
        assert results['grade'] in ['A', 'B', 'C', 'D']
    
    def test_evaluate_alias_suppression_with_file(self, tmp_path, sample_data):
        """测试使用文件路径输入的评估功能"""
        # 创建临时文件
        test_file = tmp_path / "test_response.json"
        with open(test_file, 'w') as f:
            json.dump(sample_data, f)
        
        # 使用文件路径进行评估
        results = evaluate_alias_suppression(str(test_file))
        
        # 检查结果存在
        assert results is not None
        assert 'overall_score' in results
    
    def test_calculate_smoothness(self, sample_gains):
        """测试平滑度计算"""
        gains_origin, gains_comped = sample_gains
        indices = np.arange(len(gains_origin))
        
        smoothness_orig = calculate_smoothness(gains_origin, indices)
        smoothness_comp = calculate_smoothness(gains_comped, indices)
        
        # 检查返回值类型
        assert isinstance(smoothness_orig, float)
        assert isinstance(smoothness_comp, float)
        
        # 检查数值合理性
        assert smoothness_orig >= 0
        assert smoothness_comp >= 0
        
        # 补偿后应该更平滑（平滑度值更小）
        assert smoothness_comp < smoothness_orig
    
    def test_calculate_smoothness_edge_cases(self):
        """测试平滑度计算的边界情况"""
        # 空索引
        gains = np.array([1, 2, 3, 4, 5])
        assert calculate_smoothness(gains, []) == 0.0
        
        # 单个索引
        assert calculate_smoothness(gains, [0]) == 0.0
        
        # 常数序列（完全平滑）
        constant_gains = np.array([5.0, 5.0, 5.0, 5.0])
        indices = np.arange(len(constant_gains))
        assert calculate_smoothness(constant_gains, indices) == 0.0
    
    def test_calculate_peak_improvement(self, sample_gains):
        """测试峰值改善率计算"""
        gains_origin, gains_comped = sample_gains
        
        improvement = calculate_peak_improvement(gains_origin, gains_comped)
        
        # 检查返回值
        assert isinstance(improvement, float)
        assert 0 <= improvement <= 100
    
    def test_calculate_weighted_score(self):
        """测试加权评分计算"""
        results = {
            'ASR_core': {'suppression_ratio': 60.0},
            'ASR_extended': {'suppression_ratio': 55.0},
            'peak_improvement_ratio': 40.0,
            'smoothness_enhancement': 30.0
        }
        
        weights = {
            'ASR_core': 0.4,
            'ASR_extended': 0.3,
            'peak_improvement_ratio': 0.2,
            'smoothness_enhancement': 0.1
        }
        
        score = calculate_weighted_score(results, weights)
        
        # 手动计算期望值
        expected = 60*0.4 + 55*0.3 + 40*0.2 + 30*0.1
        
        assert abs(score - expected) < 0.01
        assert 0 <= score <= 100
    
    def test_determine_grade(self):
        """测试等级判定"""
        assert determine_grade(85) == 'A'
        assert determine_grade(80) == 'A'
        assert determine_grade(70) == 'B'
        assert determine_grade(60) == 'B'
        assert determine_grade(50) == 'C'
        assert determine_grade(40) == 'C'
        assert determine_grade(30) == 'D'
        assert determine_grade(0) == 'D'
    
    def test_batch_evaluate_experiments(self, tmp_path, sample_data):
        """测试批量评估功能"""
        # 创建模拟的项目结构
        project_dir = tmp_path / "projects" / "test_project" / "data"
        project_dir.mkdir(parents=True)
        
        # 保存测试数据
        with open(project_dir / "linear_response.json", 'w') as f:
            json.dump(sample_data, f)
        
        # 更改工作目录到tmp_path
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            # 执行批量评估
            output_file = "test_results.json"
            results = batch_evaluate_experiments(['test_project'], output_file)
            
            # 检查结果
            assert len(results) == 1
            assert results[0]['experiment'] == 'test_project'
            assert 'ASR_core' in results[0]
            assert 'overall_score' in results[0]
            assert 'grade' in results[0]
            
            # 检查输出文件
            assert os.path.exists(output_file)
            with open(output_file, 'r') as f:
                saved_results = json.load(f)
                assert len(saved_results) == 1
                assert saved_results[0]['experiment'] == 'test_project'
                
        finally:
            # 恢复原始工作目录
            os.chdir(original_cwd)
    
    def test_suppression_ratio_calculation(self):
        """测试抑制率计算的正确性"""
        # 构造简单的测试数据
        test_data = {
            'gains_origin': [[100.0] * 10 + [200.0] * 10 + [100.0] * 10],  # 波动100
            'gains_comped': [[140.0] * 10 + [160.0] * 10 + [140.0] * 10],  # 波动20
            'frequencies': list(range(85, 115)),  # 85-114 Hz
            'magnitudes': [1.0],
            'fit_params_origin': [[1, 1, 1]],
            'fit_params_comped': [[1, 1, 1]]
        }
        
        results = evaluate_alias_suppression(test_data)
        
        # 在90-100Hz范围内，原始波动=100，补偿后波动=20
        # 抑制率应该是 (100-20)/100 * 100 = 80%
        assert abs(results['ASR_core']['suppression_ratio'] - 80.0) < 0.1
        assert abs(results['ASR_core']['original_ripple'] - 100.0) < 0.1
        assert abs(results['ASR_core']['compensated_ripple'] - 20.0) < 0.1


class TestEdgeCases:
    """测试边界情况和异常处理"""
    
    def test_zero_ripple(self):
        """测试原始波动为零的情况"""
        test_data = {
            'gains_origin': [[200.0] * 30],  # 完全平坦
            'gains_comped': [[205.0] * 30],  # 完全平坦
            'frequencies': list(range(85, 115)),
            'magnitudes': [1.0],
            'fit_params_origin': [[1, 1, 1]],
            'fit_params_comped': [[1, 1, 1]]
        }
        
        results = evaluate_alias_suppression(test_data)
        
        # 当原始波动为0时，抑制率应该是0
        assert results['ASR_core']['suppression_ratio'] == 0.0
    
    def test_negative_improvement(self):
        """测试补偿后反而变差的情况"""
        test_data = {
            'gains_origin': [[190.0, 200.0, 210.0] * 10],  # 波动20
            'gains_comped': [[170.0, 200.0, 230.0] * 10],  # 波动60
            'frequencies': list(range(85, 115)),
            'magnitudes': [1.0],
            'fit_params_origin': [[1, 1, 1]],
            'fit_params_comped': [[1, 1, 1]]
        }
        
        results = evaluate_alias_suppression(test_data)
        
        # 抑制率应该是负数
        assert results['ASR_core']['suppression_ratio'] < 0
        
        # 但综合评分应该被限制在0以上
        assert results['overall_score'] >= 0