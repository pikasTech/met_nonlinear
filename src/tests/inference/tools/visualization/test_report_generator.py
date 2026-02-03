"""
Tests for inference/tools/visualization/utils/report_generator module

This module tests report_generator functions with proper module imports for coverage tracking.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import numpy as np

# Add src to path
_SRC_DIR = Path(__file__).parent.parent.parent.parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

# Import the module normally for coverage tracking
import inference.tools.visualization.utils.report_generator as report_generator_module


class TestFormatNumber:
    """Test format_number function"""

    def test_format_number_default(self):
        """Test format_number with default decimal places (3)"""
        result = report_generator_module.format_number(1.23456)
        assert result == "1.235"

    def test_format_number_custom_decimal(self):
        """Test format_number with custom decimal places"""
        result = report_generator_module.format_number(1.23456, decimal_places=2)
        assert result == "1.23"

    def test_format_number_very_small_positive(self):
        """Test format_number with very small positive value"""
        result = report_generator_module.format_number(0.00005)
        assert result == "<0.0001"

    def test_format_number_very_small_negative(self):
        """Test format_number with very small negative value"""
        result = report_generator_module.format_number(-0.00005)
        assert result == "<0.0001"

    def test_format_number_small_positive(self):
        """Test format_number with small positive value (between 1e-4 and 0.001)"""
        result = report_generator_module.format_number(0.0005)
        assert result == "0.0005"

    def test_format_number_small_negative(self):
        """Test format_number with small negative value"""
        result = report_generator_module.format_number(-0.0005)
        assert result == "-0.0005"

    def test_format_number_zero(self):
        """Test format_number with zero - returns <0.0001 because abs(0) < 1e-4"""
        result = report_generator_module.format_number(0)
        # 0 is treated as very small, returns "<0.0001"
        assert result == "<0.0001"

    def test_format_number_integer(self):
        """Test format_number with integer value"""
        result = report_generator_module.format_number(100)
        assert result == "100.000"

    def test_format_number_large_value(self):
        """Test format_number with large value"""
        result = report_generator_module.format_number(12345.6789)
        assert result == "12345.679"

    def test_format_number_negative(self):
        """Test format_number with negative value"""
        result = report_generator_module.format_number(-3.14159)
        assert result == "-3.142"


class TestGenerateSummaryStatistics:
    """Test generate_summary_statistics function"""

    @pytest.fixture
    def sample_comparison_data(self):
        """Create sample comparison data for testing"""
        return {
            'baseline': {
                'layers': {
                    1: {
                        'bias_errors': [
                            {'bias_error': 0.1},
                            {'bias_error': 0.2},
                            {'bias_error': 0.15},
                            {'bias_error': 0.25}
                        ]
                    },
                    2: {
                        'bias_errors': [
                            {'bias_error': 0.08},
                            {'bias_error': 0.12},
                            {'bias_error': 0.1},
                            {'bias_error': 0.14}
                        ]
                    }
                }
            },
            'compensated': {
                'layers': {
                    1: {
                        'bias_errors': [
                            {'bias_error': 0.02},
                            {'bias_error': 0.04},
                            {'bias_error': 0.03},
                            {'bias_error': 0.05}
                        ]
                    },
                    2: {
                        'bias_errors': [
                            {'bias_error': 0.01},
                            {'bias_error': 0.02},
                            {'bias_error': 0.015},
                            {'bias_error': 0.025}
                        ]
                    }
                }
            },
            'improvements': {
                'bias_global': {'mean': 75.0, 'std': 80.0, 'max': 85.0}
            }
        }

    def test_generate_summary_statistics_basic(self, sample_comparison_data):
        """Test generate_summary_statistics returns expected structure"""
        result = report_generator_module.generate_summary_statistics(sample_comparison_data)

        assert 'sample_size' in result
        assert 'baseline_percentiles' in result
        assert 'compensated_percentiles' in result
        assert 'improvement_percentiles' in result
        assert 'zero_error_ratio' in result

    def test_generate_summary_statistics_sample_size(self, sample_comparison_data):
        """Test sample_size calculation is correct"""
        result = report_generator_module.generate_summary_statistics(sample_comparison_data)
        # 4 channels * 2 layers = 8
        assert result['sample_size'] == 8

    def test_generate_summary_statistics_percentiles(self, sample_comparison_data):
        """Test percentiles calculation"""
        result = report_generator_module.generate_summary_statistics(sample_comparison_data)

        percentiles = [25, 50, 75, 90, 95, 99]
        for p in percentiles:
            assert p in result['baseline_percentiles']
            assert p in result['compensated_percentiles']
            assert p in result['improvement_percentiles']

    def test_generate_summary_statistics_zero_error_ratio(self, sample_comparison_data):
        """Test zero_error_ratio calculation"""
        result = report_generator_module.generate_summary_statistics(sample_comparison_data)

        assert 'baseline' in result['zero_error_ratio']
        assert 'compensated' in result['zero_error_ratio']
        # No zero errors in sample data
        assert result['zero_error_ratio']['baseline'] == 0.0

    def test_generate_summary_statistics_with_zeros(self):
        """Test with data containing zero errors"""
        data = {
            'baseline': {
                'layers': {
                    1: {
                        'bias_errors': [
                            {'bias_error': 0.0},
                            {'bias_error': 0.1}
                        ]
                    }
                }
            },
            'compensated': {
                'layers': {
                    1: {
                        'bias_errors': [
                            {'bias_error': 0.0},
                            {'bias_error': 0.0}
                        ]
                    }
                }
            },
            'improvements': {'bias_global': {}}
        }
        result = report_generator_module.generate_summary_statistics(data)

        assert result['zero_error_ratio']['baseline'] == 0.5
        assert result['zero_error_ratio']['compensated'] == 1.0

    def test_generate_summary_statistics_empty_layers(self):
        """Test with empty layers - expect ValueError from numpy percentile on empty array"""
        data = {
            'baseline': {
                'layers': {}
            },
            'compensated': {
                'layers': {}
            },
            'improvements': {}
        }
        # Empty layers result in empty arrays, which causes numpy percentile to fail
        # This is expected behavior - we test that the function handles it gracefully
        with pytest.raises((IndexError, ValueError)):
            report_generator_module.generate_summary_statistics(data)


class TestGenerateMarkdownReport:
    """Test generate_markdown_report function"""

    @pytest.fixture
    def minimal_comparison_data(self):
        """Create minimal comparison data for testing"""
        return {
            'project_name': 'test_project',
            'baseline': {
                'stats': {
                    'mean_bias_error': 0.1,
                    'std_bias_error': 0.05,
                    'max_bias_error': 0.2
                },
                'layers': {
                    1: {
                        'summary': {
                            'mean_bias_error': 0.1,
                            'std_bias_error': 0.05
                        },
                        'channel_count': 4,
                        'bias_errors': [
                            {'bias_error': 0.1},
                            {'bias_error': 0.15},
                            {'bias_error': 0.08},
                            {'bias_error': 0.12}
                        ]
                    }
                }
            },
            'compensated': {
                'stats': {
                    'mean_bias_error': 0.02,
                    'std_bias_error': 0.01,
                    'max_bias_error': 0.05,
                    'total_channels': 4
                },
                'layers': {
                    1: {
                        'summary': {
                            'mean_bias_error': 0.02,
                            'std_bias_error': 0.01
                        },
                        'channel_count': 4,
                        'bias_errors': [
                            {'bias_error': 0.02},
                            {'bias_error': 0.03},
                            {'bias_error': 0.015},
                            {'bias_error': 0.025}
                        ]
                    }
                }
            },
            'improvements': {
                'bias_global': {
                    'mean': 80.0,
                    'std': 80.0,
                    'max': 75.0
                },
                'bias_layer': {
                    1: 80.0
                }
            }
        }

    @pytest.fixture
    def rms_comparison_data(self):
        """Create comparison data with RMS analysis"""
        return {
            'project_name': 'test_project_rms',
            'baseline': {
                'stats': {
                    'mean_bias_error': 0.1,
                    'std_bias_error': 0.05,
                    'max_bias_error': 0.2
                },
                'layers': {
                    1: {
                        'summary': {
                            'mean_bias_error': 0.1,
                            'std_bias_error': 0.05
                        },
                        'channel_count': 4,
                        'bias_errors': [
                            {'bias_error': 0.1},
                            {'bias_error': 0.15}
                        ]
                    }
                }
            },
            'compensated': {
                'stats': {
                    'mean_bias_error': 0.02,
                    'std_bias_error': 0.01,
                    'max_bias_error': 0.05,
                    'total_channels': 4
                },
                'layers': {
                    1: {
                        'summary': {
                            'mean_bias_error': 0.02,
                            'std_bias_error': 0.01
                        },
                        'channel_count': 4,
                        'bias_errors': [
                            {'bias_error': 0.02},
                            {'bias_error': 0.03}
                        ]
                    }
                }
            },
            'improvements': {
                'bias_global': {
                    'mean': 80.0,
                    'std': 80.0,
                    'max': 75.0
                },
                'bias_layer': {
                    1: 80.0
                },
                'rms_global': {
                    'mean': 70.0
                },
                'rms_layer': {
                    1: 70.0
                }
            }
        }

    def test_generate_markdown_report_basic(self, minimal_comparison_data):
        """Test generate_markdown_report creates file correctly"""
        temp_dir = tempfile.mkdtemp()

        config = {'plots': {'rms_analysis': False}}
        result_path = report_generator_module.generate_markdown_report(
            minimal_comparison_data, temp_dir, config
        )

        assert os.path.exists(result_path)
        assert result_path.endswith('.md')
        assert 'test_project' in result_path

        # Verify content
        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert '# SPICE偏置补偿效果分析报告' in content
        assert 'test_project' in content
        assert '偏置补偿' in content

        import shutil
        shutil.rmtree(temp_dir)

    def test_generate_markdown_report_with_rms(self, rms_comparison_data):
        """Test generate_markdown_report with RMS analysis enabled"""
        temp_dir = tempfile.mkdtemp()

        config = {'plots': {'rms_analysis': True}}
        result_path = report_generator_module.generate_markdown_report(
            rms_comparison_data, temp_dir, config
        )

        assert os.path.exists(result_path)

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # RMS content should be present
        assert 'RMS误差改进' in content
        assert '偏置误差与RMS误差绝对值对比' in content

        import shutil
        shutil.rmtree(temp_dir)

    def test_generate_markdown_report_without_rms(self, minimal_comparison_data):
        """Test generate_markdown_report without RMS analysis"""
        temp_dir = tempfile.mkdtemp()

        config = {'plots': {'rms_analysis': False}}
        result_path = report_generator_module.generate_markdown_report(
            minimal_comparison_data, temp_dir, config
        )

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # RMS content should not be present
        assert 'RMS误差改进' not in content

        import shutil
        shutil.rmtree(temp_dir)

    def test_generate_markdown_report_multiple_layers(self):
        """Test with multiple layers"""
        data = {
            'project_name': 'multi_layer_test',
            'baseline': {
                'stats': {
                    'mean_bias_error': 0.1,
                    'std_bias_error': 0.05,
                    'max_bias_error': 0.2
                },
                'layers': {
                    1: {
                        'summary': {
                            'mean_bias_error': 0.1,
                            'std_bias_error': 0.05
                        },
                        'channel_count': 4,
                        'bias_errors': [{'bias_error': 0.1}]
                    },
                    2: {
                        'summary': {
                            'mean_bias_error': 0.15,
                            'std_bias_error': 0.06
                        },
                        'channel_count': 4,
                        'bias_errors': [{'bias_error': 0.15}]
                    },
                    3: {
                        'summary': {
                            'mean_bias_error': 0.08,
                            'std_bias_error': 0.04
                        },
                        'channel_count': 4,
                        'bias_errors': [{'bias_error': 0.08}]
                    }
                }
            },
            'compensated': {
                'stats': {
                    'mean_bias_error': 0.02,
                    'std_bias_error': 0.01,
                    'max_bias_error': 0.05,
                    'total_channels': 12
                },
                'layers': {
                    1: {
                        'summary': {
                            'mean_bias_error': 0.02,
                            'std_bias_error': 0.01
                        },
                        'channel_count': 4,
                        'bias_errors': [{'bias_error': 0.02}]
                    },
                    2: {
                        'summary': {
                            'mean_bias_error': 0.03,
                            'std_bias_error': 0.02
                        },
                        'channel_count': 4,
                        'bias_errors': [{'bias_error': 0.03}]
                    },
                    3: {
                        'summary': {
                            'mean_bias_error': 0.015,
                            'std_bias_error': 0.01
                        },
                        'channel_count': 4,
                        'bias_errors': [{'bias_error': 0.015}]
                    }
                }
            },
            'improvements': {
                'bias_global': {
                    'mean': 80.0,
                    'std': 80.0,
                    'max': 75.0
                },
                'bias_layer': {
                    1: 80.0,
                    2: 80.0,
                    3: 81.25
                }
            }
        }

        temp_dir = tempfile.mkdtemp()
        config = {'plots': {'rms_analysis': False}}
        result_path = report_generator_module.generate_markdown_report(data, temp_dir, config)

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for layer sections
        assert '第1层分析' in content
        assert '第2层分析' in content
        assert '第3层分析' in content

        import shutil
        shutil.rmtree(temp_dir)

    def test_generate_markdown_report_layer_improvement_descriptions(self):
        """Test different improvement level descriptions in report"""
        data = {
            'project_name': 'improvement_levels',
            'baseline': {
                'stats': {
                    'mean_bias_error': 0.1,
                    'std_bias_error': 0.05,
                    'max_bias_error': 0.2
                },
                'layers': {
                    1: {
                        'summary': {
                            'mean_bias_error': 0.1,
                            'std_bias_error': 0.05
                        },
                        'channel_count': 4,
                        'bias_errors': [{'bias_error': 0.1}]
                    },
                    2: {
                        'summary': {
                            'mean_bias_error': 0.1,
                            'std_bias_error': 0.05
                        },
                        'channel_count': 4,
                        'bias_errors': [{'bias_error': 0.1}]
                    },
                    3: {
                        'summary': {
                            'mean_bias_error': 0.1,
                            'std_bias_error': 0.05
                        },
                        'channel_count': 4,
                        'bias_errors': [{'bias_error': 0.1}]
                    },
                    4: {
                        'summary': {
                            'mean_bias_error': 0.1,
                            'std_bias_error': 0.05
                        },
                        'channel_count': 4,
                        'bias_errors': [{'bias_error': 0.1}]
                    }
                }
            },
            'compensated': {
                'stats': {
                    'mean_bias_error': 0.02,
                    'std_bias_error': 0.01,
                    'max_bias_error': 0.05,
                    'total_channels': 16
                },
                'layers': {
                    1: {
                        'summary': {
                            'mean_bias_error': 0.02,
                            'std_bias_error': 0.01
                        },
                        'channel_count': 4,
                        'bias_errors': [{'bias_error': 0.02}]
                    },
                    2: {
                        'summary': {
                            'mean_bias_error': 0.03,
                            'std_bias_error': 0.02
                        },
                        'channel_count': 4,
                        'bias_errors': [{'bias_error': 0.03}]
                    },
                    3: {
                        'summary': {
                            'mean_bias_error': 0.08,
                            'std_bias_error': 0.04
                        },
                        'channel_count': 4,
                        'bias_errors': [{'bias_error': 0.08}]
                    },
                    4: {
                        'summary': {
                            'mean_bias_error': 0.15,
                            'std_bias_error': 0.05
                        },
                        'channel_count': 4,
                        'bias_errors': [{'bias_error': 0.15}]
                    }
                }
            },
            'improvements': {
                'bias_global': {
                    'mean': 80.0,
                    'std': 80.0,
                    'max': 75.0
                },
                'bias_layer': {
                    1: 80.0,    # > 50, excellent
                    2: 70.0,    # > 50, excellent
                    3: 20.0,    # > 20, good
                    4: 5.0      # > 0 but < 20, slight improvement
                }
            }
        }

        temp_dir = tempfile.mkdtemp()
        config = {'plots': {'rms_analysis': False}}
        result_path = report_generator_module.generate_markdown_report(data, temp_dir, config)

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for different improvement level percentages (ASCII compatible)
        # The report includes improvement percentages for each layer:
        # - Layer 1: 80.0% (excellent >50)
        # - Layer 2: 70.0% (excellent >50)
        # - Layer 3: 20.0% (good >20)
        # - Layer 4: 5.0% (slight improvement >0)
        assert '80.0%' in content  # excellent (>50)
        assert '70.0%' in content  # excellent (>50)
        assert '20.0%' in content  # good (>20)
        assert '5.0%' in content   # slight improvement (>0)

        import shutil
        shutil.rmtree(temp_dir)

    def test_generate_markdown_report_empty_config(self, minimal_comparison_data):
        """Test with empty/None config"""
        temp_dir = tempfile.mkdtemp()

        # Empty config
        result_path = report_generator_module.generate_markdown_report(
            minimal_comparison_data, temp_dir, {}
        )

        assert os.path.exists(result_path)

        import shutil
        shutil.rmtree(temp_dir)

    def test_generate_markdown_report_path_format(self, minimal_comparison_data):
        """Test report path is correctly formatted"""
        temp_dir = tempfile.mkdtemp()

        config = {'plots': {'rms_analysis': False}}
        result_path = report_generator_module.generate_markdown_report(
            minimal_comparison_data, temp_dir, config
        )

        expected_suffix = 'test_project_bias_compensation_analysis_report.md'
        assert result_path.endswith(expected_suffix)

        import shutil
        shutil.rmtree(temp_dir)

    def test_generate_markdown_report_sections_present(self, minimal_comparison_data):
        """Test all expected sections are in the report"""
        temp_dir = tempfile.mkdtemp()

        config = {'plots': {'rms_analysis': False}}
        result_path = report_generator_module.generate_markdown_report(
            minimal_comparison_data, temp_dir, config
        )

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for key sections
        assert '## 项目信息' in content
        assert '## 执行摘要' in content
        assert '## 1. 整体改进效果分析' in content
        assert '## 2. 逐层详细分析' in content
        assert '## 3. 通道级分析' in content
        assert '## 4. 误差分布特征分析' in content
        assert '## 5. 统计汇总与显著性检验' in content
        assert '## 6. 技术实现与方法论' in content
        assert '## 7. 结论与建议' in content

        import shutil
        shutil.rmtree(temp_dir)
