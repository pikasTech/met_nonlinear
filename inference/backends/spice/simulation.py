import logging
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
'\nSPICE simulation utilities.\n\nThis module handles the actual simulation process using both\nSPICE and NumPy backends.\n'
import os
import sys
from pathlib import Path
import numpy as np
from calibration_analyzer.wavedata import WaveData, WaveRecord
current_dir = Path(__file__).parent.absolute()
parent_dir = current_dir.parent.parent.parent
spice_simulator_dir = parent_dir / 'spice_simulator'
if str(spice_simulator_dir) not in sys.path:
    sys.path.insert(0, str(spice_simulator_dir))
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))
SPICE_AVAILABLE = False
CircuitSimulation = None
BaseCircuit = None
simulate_circuit_with_sweep = None

def _check_spice_dependencies():
    """检查SPICE依赖是否可用，如果不可用则抛出明确的错误"""
    global SPICE_AVAILABLE, CircuitSimulation, BaseCircuit, simulate_circuit_with_sweep
    if SPICE_AVAILABLE:
        return True
    try:
        from spice_simulator.simulation import CircuitSimulation as _CircuitSimulation
        from spice_simulator.circuit_base import BaseCircuit as _BaseCircuit
        CircuitSimulation = _CircuitSimulation
        BaseCircuit = _BaseCircuit
    except ImportError as e:
        raise ImportError(f'\n❌ 无法导入SPICE模拟器核心模块！\n错误详情: {str(e)}\n这通常是因为缺少 spicelib 依赖。\n请在正确的环境中运行：conda run -n tf26 python cli.py -i\n或者安装依赖：pip install spicelib')
    try:
        from spice_simulator.circuit_analysis.simu_sweep import simulate_circuit_with_sweep as _simulate
        simulate_circuit_with_sweep = _simulate
    except ImportError as e:
        raise ImportError(f'\n❌ 无法导入simu_sweep模块！\n错误详情: {str(e)}\n请确保文件存在：spice_simulator/circuit_analysis/simu_sweep.py')
    SPICE_AVAILABLE = True
    return True
AMP = 1
OPAMP_CONFIG = None

class SPICESimulator:
    """Handles SPICE and NumPy circuit simulation"""

    def __init__(self, output_folder, ngspice_path):
        """
        Initialize the simulator
        
        Args:
            output_folder: Folder for temporary files
            ngspice_path: Path to ngspice executable
        """
        _check_spice_dependencies()
        self.output_folder = output_folder
        self.ngspice_path = ngspice_path
        self.CircuitSimulation = CircuitSimulation
        self.BaseCircuit = BaseCircuit

    def simulate_with_spice(self, spice_input, input_wave_data: WaveData, output_name: str='spice_simulation_result') -> WaveData:
        """
        使用 SPICE 对电路进行仿真

        参数:
            spice_input: 模型对象(需要转换)或电路对象(已转换)
            input_wave_data: 输入波形数据
            output_name: 输出名称

        返回:
            WaveData: 仿真结果波形数据
        """
        Path(self.output_folder).mkdir(exist_ok=True)
        if hasattr(spice_input, 'to_spice'):
            output_path = os.path.join(self.output_folder, f'{output_name}_spice_model.cir')
            circuit = spice_input.to_spice(output_path=output_path, opamp_config=OPAMP_CONFIG, amp=AMP)
        else:
            circuit = spice_input
        if AMP != 1:
            input_wave_data = input_wave_data * AMP
        output_wave_data = simulate_circuit_with_sweep(circuit=circuit, input_wave_data=input_wave_data, output_folder=self.output_folder, ngspice_path=self.ngspice_path)
        if hasattr(spice_input, 'post_process'):
            context = {'simulation_type': 'spice'}
            try:
                output_wave_data = spice_input.post_process(output_wave_data, context)
            except TypeError:
                output_wave_data = spice_input.post_process(output_wave_data)
        return output_wave_data

    def simulate_with_numpy(self, circuit_obj, input_wave_data: WaveData, output_name: str='numpy_simulation_result') -> WaveData:
        """
        使用NumPy进行电路仿真
        
        参数:
            circuit_obj: 电路对象
            input_wave_data: 输入波形数据
            output_name: 输出名称
            
        返回:
            WaveData: NumPy仿真结果
        """
        if not hasattr(circuit_obj, 'simulate_numpy'):
            raise ValueError(f'电路对象 {type(circuit_obj).__name__} 不支持NumPy仿真')
        output_wave_data = WaveData(description=f'NumPy仿真结果 - {output_name}', author='NumPy Simulation')
        for record in input_wave_data.records:
            t = record.get_time_axis()
            input_signal = record.data
            output_signal = circuit_obj.simulate_numpy(t, input_signal)
            channel_names = []
            for i in range(output_signal.shape[1]):
                ch_type = ['HP', 'BP', 'LP'][i % 3]
                ch_num = i // 3
                channel_names.append(f'{ch_type}{ch_num}')
            output_record = WaveRecord(data=output_signal, sample_rate=record.sample_rate, channel_names=channel_names, record_id=f'{record.record_id}_numpy', user_metadata={**record.user_metadata, 'simulation_type': 'numpy'})
            output_wave_data.add_record(output_record)
        if hasattr(circuit_obj, 'post_process'):
            context = {'simulation_type': 'numpy'}
            try:
                output_wave_data = circuit_obj.post_process(output_wave_data, context)
            except TypeError:
                output_wave_data = circuit_obj.post_process(output_wave_data)
        return output_wave_data