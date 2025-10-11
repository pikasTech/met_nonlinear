"""
偏置误差分析修复测试套件

测试analyze_multilayer_bias方法修复后的正确性
"""

import pytest
import numpy as np
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inference.analysis.bias_analyzer import ChannelBiasAnalyzer


class TestBiasAnalyzerFix:
    """偏置误差分析修复测试类"""
    
    def setup_method(self):
        """测试前准备"""
        # 使用稳态方法进行测试
        self.analyzer = ChannelBiasAnalyzer(method='steady_state', steady_ratio=0.8)
        
        # 设置随机种子以确保测试结果可重现
        np.random.seed(42)
    
    def _create_test_data(self, time_steps=1000, channels=6, bias_offset=0.1):
        """创建测试数据"""
        # 创建带有已知偏置的测试数据
        ref_data = np.random.randn(time_steps, channels)
        comp_data = ref_data + bias_offset  # 添加已知偏置
        
        sample_rate = 1000.0
        layer_info = {'layer': 0, 'type': 'test'}
        
        return ref_data, comp_data, sample_rate, layer_info
    
    def test_analyze_multilayer_bias_uniform_channels(self):
        """UT-1: 测试统一通道数"""
        print("\\n=== 执行 UT-1: 统一通道数测试 ===")
        
        # 创建3层，每层6通道的测试数据
        layer_data_pairs = []
        for i in range(3):
            ref_data, comp_data, sample_rate, layer_info = self._create_test_data(channels=6)
            layer_info['layer'] = i
            layer_data_pairs.append((ref_data, comp_data, sample_rate, layer_info))
        
        # 执行分析
        try:
            result = self.analyzer.analyze_multilayer_bias(layer_data_pairs)
            
            # 验证结果结构
            assert 'layer_count' in result
            assert 'layer_statistics' in result
            assert 'global_statistics' in result
            assert 'validation_info' in result
            
            # 验证具体数值
            assert result['layer_count'] == 3
            assert len(result['layer_statistics']) == 3
            assert result['global_statistics']['total_channels'] == 18  # 3层 × 6通道
            assert result['global_statistics']['max_channels_per_layer'] == 6
            assert result['global_statistics']['min_channels_per_layer'] == 6
            
            # 验证每层统计
            for layer_stat in result['layer_statistics']:
                assert 'mean' in layer_stat
                assert 'std' in layer_stat
                assert 'channel_count' in layer_stat
                assert layer_stat['channel_count'] == 6
            
            print("✅ UT-1 PASSED: 统一通道数测试成功")
            return True, result
            
        except Exception as e:
            print(f"❌ UT-1 FAILED: {str(e)}")
            return False, str(e)
    
    def test_analyze_multilayer_bias_different_channels(self):
        """UT-2: 测试不同通道数"""
        print("\\n=== 执行 UT-2: 不同通道数测试 ===")
        
        # 创建3层，通道数分别为6、4、6的测试数据
        layer_data_pairs = []
        channels_list = [6, 4, 6]
        
        for i, channels in enumerate(channels_list):
            ref_data, comp_data, sample_rate, layer_info = self._create_test_data(channels=channels)
            layer_info['layer'] = i
            layer_data_pairs.append((ref_data, comp_data, sample_rate, layer_info))
        
        # 执行分析 - 这里不应该抛出numpy.AxisError
        try:
            result = self.analyzer.analyze_multilayer_bias(layer_data_pairs)
            
            # 验证结果结构
            assert 'layer_count' in result
            assert 'layer_statistics' in result
            assert 'global_statistics' in result
            
            # 验证不同通道数的正确处理
            assert result['layer_count'] == 3
            assert result['global_statistics']['total_channels'] == 16  # 6+4+6
            assert result['global_statistics']['max_channels_per_layer'] == 6
            assert result['global_statistics']['min_channels_per_layer'] == 4
            
            # 验证每层的通道数正确
            expected_channels = [6, 4, 6]
            for i, layer_stat in enumerate(result['layer_statistics']):
                assert layer_stat['channel_count'] == expected_channels[i]
                assert layer_stat['layer'] == i
            
            # 验证验证信息
            validation_info = result['validation_info']
            assert validation_info['channel_counts'] == [6, 4, 6]
            
            print("✅ UT-2 PASSED: 不同通道数测试成功")
            return True, result
            
        except Exception as e:
            print(f"❌ UT-2 FAILED: {str(e)}")
            return False, str(e)
    
    def test_analyze_multilayer_bias_single_channel(self):
        """UT-3: 测试单通道边界情况"""
        print("\\n=== 执行 UT-3: 单通道边界测试 ===")
        
        # 创建2层，每层1通道的测试数据
        layer_data_pairs = []
        for i in range(2):
            ref_data, comp_data, sample_rate, layer_info = self._create_test_data(channels=1)
            layer_info['layer'] = i
            layer_data_pairs.append((ref_data, comp_data, sample_rate, layer_info))
        
        try:
            result = self.analyzer.analyze_multilayer_bias(layer_data_pairs)
            
            # 验证单通道处理
            assert result['layer_count'] == 2
            assert result['global_statistics']['total_channels'] == 2
            assert result['global_statistics']['max_channels_per_layer'] == 1
            assert result['global_statistics']['min_channels_per_layer'] == 1
            
            # 验证每层统计
            for layer_stat in result['layer_statistics']:
                assert layer_stat['channel_count'] == 1
            
            print("✅ UT-3 PASSED: 单通道测试成功")
            return True, result
            
        except Exception as e:
            print(f"❌ UT-3 FAILED: {str(e)}")
            return False, str(e)
    
    def test_analyze_multilayer_bias_empty_data(self):
        """UT-4: 测试空数据异常处理"""
        print("\\n=== 执行 UT-4: 空数据异常测试 ===")
        
        try:
            # 测试空的layer_data_pairs
            result = self.analyzer.analyze_multilayer_bias([])
            print("❌ UT-4 FAILED: 应该抛出异常但没有")
            return False, "应该抛出ValueError"
            
        except ValueError as e:
            if "不能为空" in str(e):
                print("✅ UT-4 PASSED: 正确抛出空数据异常")
                return True, str(e)
            else:
                print(f"❌ UT-4 FAILED: 异常消息不正确: {str(e)}")
                return False, str(e)
        except Exception as e:
            print(f"❌ UT-4 FAILED: 抛出了错误类型的异常: {str(e)}")
            return False, str(e)
    
    def test_validate_layer_data_functionality(self):
        """UT-5: 测试数据验证功能"""
        print("\\n=== 执行 UT-5: 数据验证功能测试 ===")
        
        # 测试正常数据验证
        layer_data_pairs = []
        for i in range(3):
            ref_data, comp_data, sample_rate, layer_info = self._create_test_data(channels=6)
            layer_data_pairs.append((ref_data, comp_data, sample_rate, layer_info))
        
        try:
            validation_info = self.analyzer._validate_layer_data(layer_data_pairs)
            
            assert validation_info['layer_count'] == 3
            assert len(validation_info['channel_counts']) == 3
            
            print("✅ UT-5a PASSED: 正常数据验证成功")
        except Exception as e:
            print(f"❌ UT-5a FAILED: {str(e)}")
            return False, str(e)
        
        # 测试数据形状不匹配
        try:
            ref_data = np.random.randn(1000, 6)
            comp_data = np.random.randn(1000, 4)  # 不同形状
            sample_rate = 1000.0
            layer_info = {'layer': 0}
            
            bad_data = [(ref_data, comp_data, sample_rate, layer_info)]
            validation_info = self.analyzer._validate_layer_data(bad_data)
            
            print("❌ UT-5b FAILED: 应该抛出形状不匹配异常")
            return False, "应该抛出形状不匹配异常"
            
        except ValueError as e:
            if "数据形状不一致" in str(e):
                print("✅ UT-5b PASSED: 正确检测到形状不匹配")
            else:
                print(f"❌ UT-5b FAILED: 异常消息不正确: {str(e)}")
                return False, str(e)
        except Exception as e:
            print(f"❌ UT-5b FAILED: 抛出了错误类型的异常: {str(e)}")
            return False, str(e)
        
        # 测试不同通道数识别
        try:
            irregular_data = []
            channels_list = [6, 4, 8]
            for i, channels in enumerate(channels_list):
                ref_data, comp_data, sample_rate, layer_info = self._create_test_data(channels=channels)
                irregular_data.append((ref_data, comp_data, sample_rate, layer_info))
            
            validation_info = self.analyzer._validate_layer_data(irregular_data)
            
            assert validation_info['channel_counts'] == [6, 4, 8]
            
            print("✅ UT-5c PASSED: 正确识别不同通道数")
            return True, validation_info
            
        except Exception as e:
            print(f"❌ UT-5c FAILED: {str(e)}")
            return False, str(e)
    
    def test_extreme_channel_difference(self):
        """UT-6: 测试极端通道数差异"""
        print("\\n=== 执行 UT-6: 极端通道数差异测试 ===")
        
        # 创建极端差异的通道数：1和20
        layer_data_pairs = []
        channels_list = [1, 20]
        
        for i, channels in enumerate(channels_list):
            ref_data, comp_data, sample_rate, layer_info = self._create_test_data(channels=channels, time_steps=500)
            layer_info['layer'] = i
            layer_data_pairs.append((ref_data, comp_data, sample_rate, layer_info))
        
        try:
            result = self.analyzer.analyze_multilayer_bias(layer_data_pairs)
            
            # 验证极端差异处理
            assert result['global_statistics']['total_channels'] == 21  # 1+20
            assert result['global_statistics']['max_channels_per_layer'] == 20
            assert result['global_statistics']['min_channels_per_layer'] == 1
            
            print("✅ UT-6 PASSED: 极端通道数差异测试成功")
            return True, result
            
        except Exception as e:
            print(f"❌ UT-6 FAILED: {str(e)}")
            return False, str(e)


def run_all_unit_tests():
    """运行所有单元测试"""
    print("\\n" + "="*60)
    print("开始执行偏置误差分析修复单元测试套件")
    print("="*60)
    
    test_instance = TestBiasAnalyzerFix()
    test_instance.setup_method()
    
    test_results = {}
    
    # 测试用例列表
    test_cases = [
        ("UT-1", "统一通道数", test_instance.test_analyze_multilayer_bias_uniform_channels),
        ("UT-2", "不同通道数", test_instance.test_analyze_multilayer_bias_different_channels),
        ("UT-3", "单通道边界", test_instance.test_analyze_multilayer_bias_single_channel),
        ("UT-4", "空数据异常", test_instance.test_analyze_multilayer_bias_empty_data),
        ("UT-5", "数据验证功能", test_instance.test_validate_layer_data_functionality),
        ("UT-6", "极端通道差异", test_instance.test_extreme_channel_difference),
    ]
    
    # 执行测试
    passed = 0
    failed = 0
    
    for test_id, test_name, test_func in test_cases:
        try:
            success, result = test_func()
            test_results[test_id] = {
                'name': test_name,
                'status': 'PASSED' if success else 'FAILED',
                'result': result
            }
            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            test_results[test_id] = {
                'name': test_name,
                'status': 'ERROR',
                'result': str(e)
            }
            failed += 1
            print(f"❌ {test_id} ERROR: {str(e)}")
    
    # 输出测试总结
    print("\\n" + "="*60)
    print("测试结果总结")
    print("="*60)
    
    for test_id, result in test_results.items():
        status_icon = "✅" if result['status'] == 'PASSED' else "❌"
        print(f"{status_icon} {test_id}: {result['name']} - {result['status']}")
    
    print(f"\\n总计: {passed + failed} 个测试")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"成功率: {passed/(passed+failed)*100:.1f}%")
    
    return test_results


if __name__ == "__main__":
    # 直接运行测试
    results = run_all_unit_tests()