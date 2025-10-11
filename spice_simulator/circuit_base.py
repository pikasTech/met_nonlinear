import numpy as np
from abc import ABC, abstractmethod
from typing import List, Union, final


class BaseCircuit(ABC):
    """电路基类，定义了电路接口"""

    # E96标准电阻值系列，公差为1%
    E96_VALUES: List[float] = [
        1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30, 1.33, 1.37, 1.40,
        1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 1.96, 2.00,
        2.05, 2.10, 2.15, 2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87,
        2.94, 3.01, 3.09, 3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
        4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49, 5.62, 5.76, 5.90,
        6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45,
        8.66, 8.87, 9.09, 9.31, 9.53, 9.76
    ]
    
    n_inputs: int
    n_outputs: int

    def _convert_to_standard_value(self, value: float) -> float:
        """
        将任意电阻值转换为最接近的E96标准值

        参数:
            value: 原始电阻值

        返回:
            float: 最接近的E96标准值
        """
        if value <= 0:
            return value  # 不处理非正值

        # 计算十进制指数
        exponent: float = np.floor(np.log10(value))
        mantissa: float = value / (10 ** exponent)

        # 找到最接近的E96标准化系数
        closest_value: float = min(self.E96_VALUES, key=lambda x: abs(x - mantissa))

        # 返回最终的标准值
        return closest_value * (10 ** exponent)

    @abstractmethod
    def get_circuit_netlist(self) -> str:
        """获取电路的网表文本(不包含仿真指令)"""
        pass

    @abstractmethod
    def simulate_numpy(self, t: np.ndarray, input_signals: Union[np.ndarray, List[np.ndarray]]) -> np.ndarray:
        """
        使用NumPy进行理论仿真计算

        参数:
            t: 时间向量
            input_signals: 输入信号

        返回:
            np.ndarray: 输出信号
        """
        pass

    @final
    def get_input_source_names(self) -> List[str]:
        """
        获取输入源的名称列表

        返回:
            list: 输入源名称列表，用于设置PWL数据
        """
        # 统一约定：输入源名称格式为'Vin1', 'Vin2', ...
        # 无论单通道还是多通道，都返回列表格式
        # 这个方法不应该被子类重写
        if hasattr(self, 'n_inputs') and self.n_inputs > 0:
            return [f'Vin{i+1}' for i in range(self.n_inputs)]
        return ['Vin1']  # 默认至少返回一个输入源

    @final
    def get_output_node_names(self) -> List[str]:
        """
        获取输出节点名称列表

        返回:
            list: 输出节点名称列表，用于从仿真结果中提取输出波形
        """
        # 统一约定：输出节点名称格式为'out1', 'out2', ...
        # 无论单通道还是多通道，都返回列表格式
        # 不应该被子类重写
        if hasattr(self, 'n_outputs') and self.n_outputs > 0:
            return [f'out{i+1}' for i in range(self.n_outputs)]
        return ['out1']  # 默认至少返回一个输出节点
