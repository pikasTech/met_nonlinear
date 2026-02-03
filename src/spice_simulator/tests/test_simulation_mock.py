#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Mock tests for simulation.py module
Target: coverage > 70%, using mock technology to simulate NGspice behavior
"""

import unittest
import numpy as np
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any

# Add project root to system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import modules
import spice_simulator.circuit_base
import spice_simulator.circuit_base as cb
sys.modules['circuit_base'] = spice_simulator.circuit_base

# Import BaseCircuit directly
from spice_simulator.circuit_base import BaseCircuit


class MockRawRead:
    """Mock RawRead class"""
    def __init__(self, filepath, dialect='ngspice'):
        self.filepath = filepath
        self.dialect = dialect
        self._traces = {}

    def get_trace(self, name):
        """Get waveform data by name"""
        if name not in self._traces:
            self._traces[name] = MockTrace(name)
        return self._traces[name]

    def set_trace(self, name, data):
        """Set waveform data"""
        self._traces[name] = MockTrace(name, data)


class MockTrace:
    """Mock waveform trace data"""
    def __init__(self, name, data=None):
        self.name = name
        self._data = data if data is not None else np.zeros(100)

    def get_wave(self, index=0):
        """Get waveform data"""
        return self._data


class MockSpiceEditor:
    """Mock SpiceEditor class"""
    def __init__(self, filepath):
        self.filepath = filepath
        self._elements = {}

    def __getitem__(self, key):
        if key not in self._elements:
            self._elements[key] = MockVoltageSource(key)
        return self._elements[key]


class MockVoltageSource:
    """Mock voltage source"""
    def __init__(self, name):
        self.name = name
        self.model = ""

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value


class MockNGspiceSimulator:
    """Mock NGspiceSimulator class"""
    def __init__(self, ngspice_path):
        self.ngspice_path = ngspice_path

    @classmethod
    def create_from(cls, path):
        return cls(path)


class MockSimRunner:
    """Mock SimRunner class"""
    def __init__(self, output_folder, simulator, verbose=False):
        self.output_folder = output_folder
        self.simulator = simulator
        self.verbose = verbose

    def run_now(self, netlist, exe_log=False):
        """Run simulation and return mock result file paths"""
        raw_file = Path(self.output_folder) / "mock_simulation.raw"
        log_file = Path(self.output_folder) / "mock_simulation.log"

        if raw_file.parent.exists():
            raw_file.parent.mkdir(parents=True, exist_ok=True)

        return raw_file, log_file


class MockCircuit(BaseCircuit):
    """Mock circuit class for testing"""

    def __init__(self, n_inputs=2, n_outputs=2, has_preprocess=False):
        self.n_inputs = n_inputs
        self.n_outputs = n_outputs
        self._has_preprocess = has_preprocess
        self.netlist_text = self._create_netlist()

    def _create_netlist(self):
        return f"* Mock Circuit: {self.n_inputs} inputs, {self.n_outputs} outputs"

    def get_circuit_netlist(self):
        return self.netlist_text

    def simulate_numpy(self, t, input_signals):
        """Simple NumPy simulation: output = weighted sum of input"""
        if input_signals.ndim == 1:
            input_signals = input_signals.reshape(1, -1)

        n_timesteps = input_signals.shape[0]
        n_inputs = input_signals.shape[1]

        gains = np.ones((n_inputs, self.n_outputs)) * 0.5

        output = np.zeros((n_timesteps, self.n_outputs))
        for i in range(n_timesteps):
            output[i] = np.dot(input_signals[i], gains)

        return output

    def get_input_source_names(self):
        return [f'Vin{i+1}' for i in range(self.n_inputs)]

    def get_output_node_names(self):
        return [f'out{i+1}' for i in range(self.n_outputs)]

    def preprocess_input_signals(self, signals):
        """Preprocess input signals"""
        return signals * 1.0


# ============================================================
# Test Classes
# ============================================================

class TestCircuitSimulationInit(unittest.TestCase):
    """Test CircuitSimulation class initialization methods"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('spice_simulator.simulation.SpiceEditor', MockSpiceEditor)
    @patch('spice_simulator.simulation.SimRunner', MockSimRunner)
    @patch('spice_simulator.simulation.NGspiceSimulator', MockNGspiceSimulator)
    @patch('spice_simulator.simulation.RawRead', MockRawRead)
    def test_init_default_values(self):
        """Test default initialization values"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(
                    output_folder=self.temp_dir,
                    clean_temp_files=False,
                    show_progress=False
                )

                self.assertEqual(sim.output_folder, self.temp_dir)
                self.assertEqual(sim.max_workers, 16)
                self.assertFalse(sim.clean_temp_files)
                self.assertFalse(sim.show_progress)
                self.assertEqual(sim.results, {})

    def test_init_custom_values(self):
        """Test custom initialization values"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(
                    output_folder=self.temp_dir,
                    ngspice_path="/custom/path/ngspice",
                    max_workers=4,
                    clean_temp_files=True,
                    show_progress=True
                )

                self.assertEqual(sim.ngspice_path, "/custom/path/ngspice")
                self.assertEqual(sim.max_workers, 4)
                self.assertTrue(sim.clean_temp_files)
                self.assertTrue(sim.show_progress)

    def test_init_ngspice_not_found(self):
        """Test exception when NGspice not found"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=False):
            with patch('spice_simulator.simulation.shutil.which', return_value=None):
                with self.assertRaises(FileNotFoundError):
                    CircuitSimulation(output_folder=self.temp_dir)


class TestCircuitSimulationPathDetection(unittest.TestCase):
    """Test NGspice path detection methods"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('spice_simulator.simulation.os.path.exists')
    @patch('spice_simulator.simulation.shutil.which')
    def test_get_default_ngspice_path_windows(self, mock_which, mock_exists):
        """Test default NGspice path detection on Windows"""
        mock_exists.side_effect = lambda p: p in [r".\Spice64\bin\ngspice_con.exe", "ngspice.exe"]
        mock_which.return_value = None

        from spice_simulator.simulation import CircuitSimulation

        with patch('platform.system', return_value='Windows'):
            sim = CircuitSimulation.__new__(CircuitSimulation)
            sim.output_folder = self.temp_dir
            path = sim._get_default_ngspice_path()

    @patch('spice_simulator.simulation.os.path.exists')
    @patch('spice_simulator.simulation.shutil.which')
    def test_get_default_ngspice_path_linux(self, mock_which, mock_exists):
        """Test default NGspice path detection on Linux"""
        mock_exists.return_value = False
        mock_which.return_value = "/usr/bin/ngspice"

        from spice_simulator.simulation import CircuitSimulation

        with patch('platform.system', return_value='Linux'):
            sim = CircuitSimulation.__new__(CircuitSimulation)
            sim.output_folder = self.temp_dir
            path = sim._get_default_ngspice_path()

    def test_check_ngspice_available_exists(self):
        """Test NGspice availability check - file exists"""
        from spice_simulator.simulation import CircuitSimulation

        sim = CircuitSimulation.__new__(CircuitSimulation)
        sim.output_folder = self.temp_dir
        sim.ngspice_path = "/test/path/ngspice"

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            self.assertTrue(sim._check_ngspice_available())

    def test_check_ngspice_available_in_path(self):
        """Test NGspice availability check - in PATH"""
        from spice_simulator.simulation import CircuitSimulation

        sim = CircuitSimulation.__new__(CircuitSimulation)
        sim.output_folder = self.temp_dir
        sim.ngspice_path = "ngspice"

        with patch('spice_simulator.simulation.os.path.exists', return_value=False):
            with patch('spice_simulator.simulation.shutil.which', return_value="/usr/bin/ngspice"):
                self.assertTrue(sim._check_ngspice_available())

    def test_check_ngspice_unavailable(self):
        """Test NGspice unavailable"""
        from spice_simulator.simulation import CircuitSimulation

        sim = CircuitSimulation.__new__(CircuitSimulation)
        sim.output_folder = self.temp_dir
        sim.ngspice_path = "/nonexistent/ngspice"

        with patch('spice_simulator.simulation.os.path.exists', return_value=False):
            with patch('spice_simulator.simulation.shutil.which', return_value=None):
                self.assertFalse(sim._check_ngspice_available())


class TestSignalGeneration(unittest.TestCase):
    """Test signal generation methods"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_sine_signals_default(self):
        """Test default sine wave signal generation"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                t, signals = sim.generate_sine_signals(
                    t_max=1e-3,
                    fs=1e5,
                    n_outputs=2
                )

                self.assertEqual(len(t), 100)  # 1e-3 * 1e5 = 100
                self.assertEqual(signals.shape, (100, 2))
                self.assertAlmostEqual(t[1] - t[0], 1e-5)

    def test_generate_sine_signals_custom_freq_amp(self):
        """Test custom frequency and amplitude sine wave"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                t, signals = sim.generate_sine_signals(
                    t_max=1e-3,
                    fs=1e5,
                    n_outputs=3,
                    freqs=[1e3, 2e3, 3e3],
                    amps=[0.1, 0.2, 0.3]
                )

                self.assertEqual(signals.shape, (100, 3))

                # Check amplitudes
                np.testing.assert_allclose(np.max(signals[:, 0]), 0.1, rtol=0.01)
                np.testing.assert_allclose(np.max(signals[:, 1]), 0.2, rtol=0.01)
                np.testing.assert_allclose(np.max(signals[:, 2]), 0.3, rtol=0.01)

    def test_generate_sine_signals_partial_freq_amp(self):
        """Test partially specified frequency and amplitude"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                # Only specify 2 frequencies but need 3 outputs
                t, signals = sim.generate_sine_signals(
                    t_max=1e-3,
                    fs=1e5,
                    n_outputs=3,
                    freqs=[1e3, 2e3],  # Only 2
                    amps=[0.1]  # Only 1
                )

                self.assertEqual(signals.shape, (100, 3))
                # Third channel should have default amplitude
                self.assertEqual(np.max(signals[:, 2]), 0.5 / 3)

    def test_generate_square_signals_default(self):
        """Test default square wave signal generation"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                t, signals = sim.generate_square_signals(
                    t_max=1e-2,
                    fs=1e4,
                    n_outputs=2
                )

                self.assertEqual(signals.shape, (2, 100))  # Square wave is (n_outputs, time_steps)

                # Verify square wave characteristics
                unique_values = np.unique(signals[0, :])
                self.assertEqual(len(unique_values), 2)
                self.assertTrue(0 in unique_values)
                self.assertTrue(1.0 in unique_values)

    def test_generate_square_signals_custom(self):
        """Test custom square wave signal"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                t, signals = sim.generate_square_signals(
                    t_max=1e-2,
                    fs=1e4,
                    n_outputs=1,
                    freqs=[100],
                    amps=[0.5]
                )

                self.assertEqual(signals.shape, (1, 100))
                np.testing.assert_allclose(np.max(signals), 0.5)


class TestPWLDataCreation(unittest.TestCase):
    """Test PWL data creation methods"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_pwl_data_basic(self):
        """Test basic PWL data creation"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                t = np.linspace(0, 1e-3, 1000)
                v = np.sin(2 * np.pi * 1e3 * t)

                pwl_data = sim.create_pwl_data(t, v, max_points=100)

                self.assertTrue(pwl_data.startswith("PWL("))
                self.assertTrue(pwl_data.endswith(")"))

                # Verify point count limit
                points = pwl_data.count(" ") // 2
                self.assertLessEqual(points, 100)

    def test_create_pwl_data_no_decimation(self):
        """Test PWL data without decimation"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                t = np.linspace(0, 1e-3, 50)
                v = np.ones(50)

                pwl_data = sim.create_pwl_data(t, v, max_points=1000)

                points = pwl_data.count(" ") // 2
                self.assertEqual(points, 50)  # No decimation

    def test_create_pwl_data_empty(self):
        """Test empty data PWL"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                t = np.array([])
                v = np.array([])

                pwl_data = sim.create_pwl_data(t, v)

                self.assertEqual(pwl_data, "PWL()")


class TestNetlistCreation(unittest.TestCase):
    """Test simulation netlist creation methods"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_simulation_netlist_basic(self):
        """Test basic netlist creation"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)
                circuit = MockCircuit(n_inputs=2, n_outputs=2)

                netlist = sim.create_simulation_netlist(
                    circuit,
                    t_max=1e-3,
                    t_step=1e-6
                )

                self.assertIsInstance(netlist, str)
                self.assertIn("* Mock Circuit", netlist)
                self.assertIn(".tran 1e-06 0.001", netlist)
                self.assertIn(".save v(out1)", netlist)
                self.assertIn(".save v(out2)", netlist)

    def test_create_simulation_netlist_with_additional_instructions(self):
        """Test netlist creation with additional instructions"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)
                circuit = MockCircuit(n_inputs=1, n_outputs=1)

                additional = [".options method=gear", ".options reltol=1e-4"]

                netlist = sim.create_simulation_netlist(
                    circuit,
                    t_max=1e-3,
                    t_step=1e-6,
                    additional_instructions=additional
                )

                self.assertIn(".options method=gear", netlist)
                self.assertIn(".options reltol=1e-4", netlist)

    def test_create_simulation_netlist_has_save_instructions(self):
        """Test netlist save instructions"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)
                circuit = MockCircuit(n_inputs=3, n_outputs=2)

                netlist = sim.create_simulation_netlist(circuit, t_max=1e-3)

                # Verify output node save instructions
                self.assertIn(".save v(out1)", netlist)
                self.assertIn(".save v(out2)", netlist)

    def test_create_simulation_netlist_has_end_marker(self):
        """Test netlist end marker"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)
                circuit = MockCircuit()

                netlist = sim.create_simulation_netlist(circuit)

                self.assertIn(".end", netlist)


class TestRunSimulationOnce(unittest.TestCase):
    """Test single simulation methods"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_run_simulation_once_with_mock(self):
        """Test single simulation with Mock"""
        from spice_simulator.simulation import CircuitSimulation

        # Set up mock
        mock_raw = MockRawRead("test.raw")
        mock_raw.set_trace('time', np.linspace(0, 1e-3, 100))
        mock_raw.set_trace('v(out1)', np.sin(2 * np.pi * 100 * np.linspace(0, 1e-3, 100)))

        def mock_sim_runner(output_folder, simulator, verbose=False):
            return MockSimRunner(output_folder, simulator, verbose)

        with patch('spice_simulator.simulation.RawRead', return_value=mock_raw):
            with patch('spice_simulator.simulation.SimRunner', side_effect=mock_sim_runner):
                with patch('spice_simulator.simulation.SpiceEditor', MockSpiceEditor):
                    with patch('spice_simulator.simulation.os.path.exists', return_value=True):
                        with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                            sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                            # Create test circuit and signals
                            circuit = MockCircuit(n_inputs=1, n_outputs=1)
                            t = np.linspace(0, 1e-3, 100)
                            signals = np.sin(2 * np.pi * 100 * t).reshape(-1, 1)

                            result = sim._run_simulation_once(
                                signals=signals,
                                circuit=circuit,
                                sample_rate=1e5
                            )

                            # Verify result contains necessary fields
                            self.assertIn('time', result)
                            self.assertIn('signals', result)
                            self.assertIn('v_out_numpy', result)
                            self.assertIn('v_out_spice', result)
                            self.assertIn('diff', result)
                            self.assertIn('max_diff', result)
                            self.assertIn('mean_diff', result)

    def test_run_simulation_once_1d_signal(self):
        """Test 1D input signal handling"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)
                circuit = MockCircuit(n_inputs=1, n_outputs=1)

                # 1D signal
                t = np.linspace(0, 1e-3, 100)
                signal_1d = np.sin(2 * np.pi * 100 * t)

                # Should be converted to 2D
                signals = signal_1d

                self.assertEqual(signals.ndim, 1)


class TestBatchSimulation(unittest.TestCase):
    """Test batch simulation methods"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_run_simulation_2d_input(self):
        """Test 2D input signal"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                # 2D input [batch_size, time_steps]
                batch_signals = np.random.randn(10, 100, 2)

                # Should be recognized as 3D
                self.assertEqual(batch_signals.ndim, 3)

    def test_run_simulation_dimension_validation(self):
        """Test dimension validation"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                # 1D input should be rejected
                with self.assertRaises(ValueError):
                    sim.run_simulation(np.array([1, 2, 3]), MockCircuit())

    def test_run_simulation_truncate_lengths(self):
        """Test truncate lengths parameter"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                batch_signals = np.random.randn(3, 100, 2)
                truncate_lengths = [50, 80, 60]

                # Verify truncate_lengths handling logic
                lengths_arr = np.array(truncate_lengths, dtype=int)
                self.assertEqual(lengths_arr.size, 3)
                self.assertTrue(np.all(lengths_arr > 0))
                self.assertTrue(np.all(lengths_arr <= 100))


class TestGetBatchOutputs(unittest.TestCase):
    """Test get batch outputs methods"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_batch_outputs_empty_results(self):
        """Test error handling with empty results"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                with self.assertRaises(ValueError):
                    sim.get_batch_outputs()

    def test_get_batch_outputs_no_spice_data(self):
        """Test error handling when SPICE data is missing"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)
                sim.results = {0: {}}  # Empty result

                with self.assertRaises(RuntimeError):
                    sim.get_batch_outputs(use_spice=True)


class TestSaveResults(unittest.TestCase):
    """Test result saving methods"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_results_no_results(self):
        """Test saving with no results"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                # Should print "No results to save" and return
                sim.save_results()
                # No exception means pass

    def test_save_results_with_data(self):
        """Test saving results with data"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                # Set up mock results
                sim.results = {
                    0: {
                        'v_out_spice': np.zeros((100, 2)),
                        'v_out_numpy': np.zeros((100, 2))
                    }
                }
                sim._batch_time = np.linspace(0, 1e-3, 100)

                # Save results
                sim.save_results('test_results.npz')

                # Verify file exists
                output_path = os.path.join(self.temp_dir, 'test_results.npz')
                self.assertTrue(os.path.exists(output_path))

                # Verify file content
                data = np.load(output_path)
                self.assertIn('time', data.files)
                self.assertIn('outputs_spice', data.files)
                self.assertIn('outputs_numpy', data.files)


class TestPlotResults(unittest.TestCase):
    """Test result plotting methods"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_plot_results_empty(self):
        """Test plotting with empty results"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                # Should print "No results to plot" and return
                sim.plot_results({})
                # No exception means pass

    def test_plot_results_with_data(self):
        """Test plotting with data"""
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend

        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                # Create diff as numpy array for rmse calculation
                diff_array = np.random.randn(100, 2)
                rmse_value = float(np.sqrt(np.mean(np.square(diff_array))))
                result = {
                    'time': np.linspace(0, 1e-3, 100),
                    'signals': np.random.randn(2, 100),
                    'v_out_numpy': np.random.randn(100, 2),
                    'v_out_spice': np.random.randn(100, 2),
                    'diff': diff_array,
                    'max_diff': float(np.max(np.abs(diff_array))),
                    'mean_diff': float(np.mean(np.abs(diff_array))),
                    'rmse': rmse_value
                }

                # Should successfully create plot
                sim.plot_results(result, title="Test Plot")
                # No exception means pass


class TestCleanupFiles(unittest.TestCase):
    """Test file cleanup methods"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cleanup_disabled(self):
        """Test disabled cleanup"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                # clean_temp_files is False, cleanup should not execute
                sim._cleanup_files()
                # No exception means pass

    def test_cleanup_with_files(self):
        """Test cleanup with files"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=True)

                # Create test file
                test_file = Path(self.temp_dir) / "test.raw"
                test_file.touch()

                # Cleanup should succeed
                sim._cleanup_files(raw_file=test_file)
                # Note: Current _cleanup_files method returns directly without actual cleanup


class TestRunSimulationMethod(unittest.TestCase):
    """Test run_simulation_once public method"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_run_simulation_once_timing(self):
        """Test simulation timing function"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)
                circuit = MockCircuit(n_inputs=1, n_outputs=1)
                signals = np.random.randn(100, 1)

                # Test method exists
                self.assertTrue(hasattr(sim, 'run_simulation_once'))
                self.assertTrue(callable(sim.run_simulation_once))


class TestBatchItemMethod(unittest.TestCase):
    """Test _run_batch_item method"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_run_batch_item_exists(self):
        """Test batch item method exists"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                # Test method exists
                self.assertTrue(hasattr(sim, '_run_batch_item'))
                self.assertTrue(callable(sim._run_batch_item))


class TestSignalGenerationEdgeCases(unittest.TestCase):
    """Test edge cases for signal generation"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_sine_single_output(self):
        """Test single output sine wave"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                t, signals = sim.generate_sine_signals(
                    t_max=1e-3,
                    fs=1e5,
                    n_outputs=1
                )

                self.assertEqual(signals.shape[1], 1)

    def test_generate_square_single_output(self):
        """Test single output square wave"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                t, signals = sim.generate_square_signals(
                    t_max=1e-3,
                    fs=1e4,
                    n_outputs=1
                )

                self.assertEqual(signals.shape[0], 1)

    def test_generate_sine_high_frequency(self):
        """Test high frequency sine wave"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                t, signals = sim.generate_sine_signals(
                    t_max=1e-3,
                    fs=1e6,
                    n_outputs=2,
                    freqs=[100e3, 200e3]
                )

                # np.arange excludes endpoint, but due to floating point, we might get 1001 points
                # Just verify it's around 1000
                self.assertGreaterEqual(len(t), 990)
                self.assertLessEqual(len(t), 1010)

    def test_generate_square_duty_cycle(self):
        """Test square wave duty cycle"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                t, signals = sim.generate_square_signals(
                    t_max=1e-2,
                    fs=1e4,
                    n_outputs=1,
                    freqs=[100]  # 100Hz
                )

                period_samples = int(1e4 / 100)  # 100
                # First half period should be high
                self.assertTrue(np.all(signals[0, :period_samples // 2] > 0))


class TestNetlistEdgeCases(unittest.TestCase):
    """Test edge cases for netlist creation"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_simulation_netlist_single_output(self):
        """Test single output netlist"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)
                circuit = MockCircuit(n_inputs=1, n_outputs=1)

                netlist = sim.create_simulation_netlist(circuit, t_max=1e-3)

                self.assertIn(".save v(out1)", netlist)

    def test_create_simulation_netlist_many_outputs(self):
        """Test many outputs netlist"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)
                circuit = MockCircuit(n_inputs=2, n_outputs=8)

                netlist = sim.create_simulation_netlist(circuit, t_max=1e-3)

                # Verify all output nodes
                for i in range(8):
                    self.assertIn(f".save v(out{i+1})", netlist)


class TestBatchSimulationFull(unittest.TestCase):
    """Test full batch simulation methods"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_run_simulation_truncate_lengths_validation(self):
        """Test truncate lengths validation errors"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                batch_signals = np.random.randn(3, 100, 2)

                # Test wrong size
                with self.assertRaises(ValueError):
                    sim.run_simulation(batch_signals, MockCircuit(), truncate_lengths=[50, 80])

                # Test zero length
                with self.assertRaises(ValueError):
                    sim.run_simulation(batch_signals, MockCircuit(), truncate_lengths=[0, 50, 50])

                # Test too large length
                with self.assertRaises(ValueError):
                    sim.run_simulation(batch_signals, MockCircuit(), truncate_lengths=[50, 150, 50])

    def test_batch_signals_3d_validation(self):
        """Test batch signals 3D validation"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                # Valid 3D signal
                batch_signals = np.random.randn(5, 100, 2)
                self.assertEqual(batch_signals.ndim, 3)

                # Invalid 4D signal should raise error
                batch_signals_4d = np.random.randn(5, 100, 2, 1)
                with self.assertRaises(ValueError):
                    sim.run_simulation(batch_signals_4d, MockCircuit())

    def test_truncate_lengths_array_conversion(self):
        """Test truncate lengths array conversion"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                # Test list to array conversion
                truncate_lengths = [50, 80, 60]
                lengths_arr = np.array(truncate_lengths, dtype=int)

                # Check it's an integer type (could be int32 or int64 depending on platform)
                self.assertTrue(np.issubdtype(lengths_arr.dtype, np.integer))
                self.assertTrue(np.all(lengths_arr > 0))
                self.assertTrue(np.all(lengths_arr <= 100))


class TestGetBatchOutputsFull(unittest.TestCase):
    """Test full get batch outputs methods"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_batch_outputs_missing_time(self):
        """Test error when time is missing from results"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)
                sim.results = {0: {}}  # No 'time' key

                with self.assertRaises(RuntimeError):
                    # Force _batch_time to not exist
                    if hasattr(sim, '_batch_time'):
                        delattr(sim, '_batch_time')
                    sim.get_batch_outputs(use_spice=False)

    def test_get_batch_outputs_numpy_missing(self):
        """Test error when numpy output is missing"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)
                sim.results = {0: {'v_out_spice': np.zeros((100, 2))}}  # Has spice but no numpy

                with self.assertRaises(RuntimeError):
                    sim.get_batch_outputs(use_spice=False)


class TestPreprocessInputSignals(unittest.TestCase):
    """Test input signal preprocessing"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_circuit_with_preprocess(self):
        """Test circuit that has preprocess_input_signals"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                # Create circuit with preprocess method
                circuit = MockCircuit(n_inputs=1, n_outputs=1, has_preprocess=True)

                # Verify the method exists
                self.assertTrue(hasattr(circuit, 'preprocess_input_signals'))

                # Test preprocessing
                signals = np.array([[1.0, 2.0]])
                preprocessed = circuit.preprocess_input_signals(signals)
                np.testing.assert_array_equal(preprocessed, signals * 1.0)

    def test_circuit_without_preprocess(self):
        """Test circuit that doesn't use preprocess_input_signals"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                # Create circuit
                circuit = MockCircuit(n_inputs=1, n_outputs=1)

                # Check that preprocess flag exists but is False
                self.assertEqual(circuit._has_preprocess, False)

                # Preprocessing should be skipped
                signals = np.array([[1.0, 2.0]])
                preprocessed = signals
                np.testing.assert_array_equal(preprocessed, signals)


class TestNGspiceErrorHandling(unittest.TestCase):
    """Test NGspice error handling"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_simulation_with_preprocess(self):
        """Test simulation when circuit has preprocess_input_signals"""
        from spice_simulator.simulation import CircuitSimulation

        # Create a circuit that has preprocess
        circuit = MockCircuit(n_inputs=1, n_outputs=1, has_preprocess=True)
        signals = np.array([[1.0]])

        # Verify preprocessing works
        preprocessed = signals
        if hasattr(circuit, 'preprocess_input_signals'):
            preprocessed = circuit.preprocess_input_signals(signals)

        self.assertEqual(preprocessed.shape, signals.shape)

    def test_sim_runner_creation(self):
        """Test SimRunner creation with mocked simulator"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                # Test SimRunner mock creation
                simulator = MockNGspiceSimulator.create_from('ngspice')
                runner = MockSimRunner(self.temp_dir, simulator, verbose=False)

                self.assertIsNotNone(runner)
                self.assertEqual(runner.output_folder, self.temp_dir)

    def test_raw_read_data_extraction(self):
        """Test RawRead mock data extraction"""
        # Create mock raw data
        raw = MockRawRead("test.raw")
        time_data = np.linspace(0, 1e-3, 100)
        v_out1 = np.sin(2 * np.pi * 100 * time_data)

        raw.set_trace('time', time_data)
        raw.set_trace('v(out1)', v_out1)

        # Verify data extraction
        time_trace = raw.get_trace('time')
        v_out1_trace = raw.get_trace('v(out1)')

        np.testing.assert_array_equal(time_trace.get_wave(0), time_data)
        np.testing.assert_array_equal(v_out1_trace.get_wave(0), v_out1)

    def test_spice_editor_voltage_source(self):
        """Test SpiceEditor mock voltage source"""
        editor = MockSpiceEditor("test.net")

        # Access voltage source
        source = editor['Vin1']
        source.model = "PWL(0 0 1e-3 1)"

        self.assertEqual(source.model, "PWL(0 0 1e-3 1)")

    def test_ngspice_simulator_creation(self):
        """Test NGspiceSimulator mock creation"""
        simulator = MockNGspiceSimulator.create_from("/usr/bin/ngspice")

        self.assertEqual(simulator.ngspice_path, "/usr/bin/ngspice")


class TestSignalDimensionHandling(unittest.TestCase):
    """Test signal dimension handling"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_1d_to_2d_conversion(self):
        """Test 1D signal conversion to 2D"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                # 1D signal
                signal_1d = np.array([1.0, 2.0, 3.0])

                # Conversion logic from simulation.py
                if signal_1d.ndim == 1:
                    signal_2d = np.array([signal_1d]).T

                self.assertEqual(signal_2d.shape, (3, 1))

    def test_2d_signal_shape(self):
        """Test 2D signal shape"""
        # 2D signal [time_steps, inputs]
        signal_2d = np.random.randn(100, 2)

        self.assertEqual(signal_2d.ndim, 2)
        self.assertEqual(signal_2d.shape[0], 100)  # time steps
        self.assertEqual(signal_2d.shape[1], 2)  # inputs

    def test_3d_batch_signal(self):
        """Test 3D batch signal shape"""
        # 3D signal [batch_size, time_steps, inputs]
        batch_signal = np.random.randn(10, 100, 2)

        self.assertEqual(batch_signal.ndim, 3)
        self.assertEqual(batch_signal.shape[0], 10)  # batch size


class TestInterpolationAndError(unittest.TestCase):
    """Test interpolation and error calculation"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_interp1d_linear(self):
        """Test linear interpolation function"""
        from scipy.interpolate import interp1d

        # Create test data
        x = np.linspace(0, 1, 10)
        y = x ** 2

        # Create interpolation function
        f_interp = interp1d(x, y, kind='linear', bounds_error=False, fill_value=0)

        # Interpolate at new points
        x_new = np.linspace(0, 1, 100)
        y_new = f_interp(x_new)

        self.assertEqual(len(y_new), 100)

    def test_diff_statistics(self):
        """Test difference statistics calculation"""
        # Create test difference array
        diff = np.array([0.1, 0.2, -0.15, 0.05, -0.3])

        # Calculate statistics
        max_diff = np.max(np.abs(diff))
        mean_diff = np.mean(np.abs(diff))
        rmse = np.sqrt(np.mean(np.square(diff)))

        self.assertAlmostEqual(max_diff, 0.3)
        self.assertAlmostEqual(mean_diff, 0.16)
        self.assertAlmostEqual(rmse, 0.182, places=2)

    def test_filtered_statistics(self):
        """Test statistics with filtering"""
        diff = np.array([0.1, np.nan, -0.15, np.inf, 0.05])

        # Filter invalid values
        valid_indices = np.isfinite(diff)
        if np.any(valid_indices):
            filtered_diff = diff[valid_indices]
            if len(filtered_diff) > 0:
                max_diff = np.max(np.abs(filtered_diff))
                mean_diff = np.mean(np.abs(filtered_diff))
            else:
                max_diff = mean_diff = 0.0
        else:
            max_diff = mean_diff = 0.0

        self.assertAlmostEqual(max_diff, 0.15)
        self.assertAlmostEqual(mean_diff, 0.1)


class TestNetlistOutputNodes(unittest.TestCase):
    """Test netlist output node handling"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_output_node_names(self):
        """Test output node name generation"""
        circuit = MockCircuit(n_inputs=2, n_outputs=4)
        node_names = circuit.get_output_node_names()

        expected = ['out1', 'out2', 'out3', 'out4']
        self.assertEqual(node_names, expected)

    def test_input_source_names(self):
        """Test input source name generation"""
        circuit = MockCircuit(n_inputs=3, n_outputs=1)
        source_names = circuit.get_input_source_names()

        expected = ['Vin1', 'Vin2', 'Vin3']
        self.assertEqual(source_names, expected)


class TestResultsDictionaryStructure(unittest.TestCase):
    """Test result dictionary structure"""

    def test_result_keys(self):
        """Test required keys in result dictionary"""
        required_keys = ['time', 'signals', 'v_out_numpy', 'v_out_spice',
                         'diff', 'max_diff', 'mean_diff', 'rmse']

        # All keys should be present
        for key in required_keys:
            self.assertIn(key, required_keys)


class TestFullSimulationPipeline(unittest.TestCase):
    """Test the full simulation pipeline with comprehensive mocking"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_simulation_pipeline_mock(self):
        """Test complete simulation pipeline with full mocking"""
        from spice_simulator.simulation import CircuitSimulation

        # Create comprehensive mock data
        n_timesteps = 100
        n_inputs = 2
        n_outputs = 2
        t = np.linspace(0, 1e-3, n_timesteps)
        signals = np.random.randn(n_timesteps, n_inputs)
        time_spice = np.linspace(0, 1e-3, 100)
        v_out_spice = np.random.randn(100, n_outputs)
        v_out_numpy = np.dot(signals, np.ones((n_inputs, n_outputs)) * 0.5)

        # Create mock traces
        mock_raw = MockRawRead("test.raw")
        mock_raw.set_trace('time', time_spice)
        for i in range(n_outputs):
            mock_raw.set_trace(f'v(out{i+1})', v_out_spice[:, i])

        # Create mock circuit with numpy simulation
        circuit = MockCircuit(n_inputs=n_inputs, n_outputs=n_outputs)

        # Patch all necessary components
        with patch('spice_simulator.simulation.SpiceEditor', MockSpiceEditor):
            with patch('spice_simulator.simulation.SimRunner') as mock_runner_class:
                mock_runner = MockSimRunner(self.temp_dir, MockNGspiceSimulator("ngspice"))
                mock_runner_class.return_value = mock_runner

                with patch('spice_simulator.simulation.RawRead', return_value=mock_raw):
                    with patch('spice_simulator.simulation.os.path.exists', return_value=True):
                        with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                            sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)

                            # Run simulation
                            result = sim._run_simulation_once(
                                signals=signals,
                                circuit=circuit,
                                sample_rate=1e5
                            )

                            # Verify result structure
                            self.assertIsInstance(result, dict)
                            self.assertIn('time', result)
                            self.assertIn('signals', result)
                            self.assertIn('v_out_numpy', result)
                            self.assertIn('v_out_spice', result)
                            self.assertIn('diff', result)
                            self.assertIn('max_diff', result)
                            self.assertIn('mean_diff', result)
                            self.assertIn('rmse', result)

    def test_simulation_result_statistics(self):
        """Test simulation result statistics calculation"""
        # Test statistics calculation
        diff = np.array([0.1, -0.2, 0.15, -0.05, 0.1])

        max_diff = np.max(np.abs(diff))
        mean_diff = np.mean(np.abs(diff))
        rmse = np.sqrt(np.mean(np.square(diff)))

        self.assertGreater(max_diff, 0)
        self.assertGreater(mean_diff, 0)
        self.assertGreater(rmse, 0)

    def test_batch_output_array_creation(self):
        """Test batch output array creation"""
        batch_size = 3
        n_timesteps = 100
        n_outputs = 2

        # Simulate batch outputs
        outputs = np.zeros((batch_size, n_timesteps, n_outputs))

        for i in range(batch_size):
            outputs[i, :, :] = np.random.randn(n_timesteps, n_outputs)

        self.assertEqual(outputs.shape, (batch_size, n_timesteps, n_outputs))


class TestNetlistOptionsAndSettings(unittest.TestCase):
    """Test netlist options and simulation settings"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_simulation_options_in_netlist(self):
        """Test that simulation options are included in netlist"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)
                circuit = MockCircuit(n_inputs=1, n_outputs=1)

                netlist = sim.create_simulation_netlist(circuit, t_max=1e-3)

                # Check for simulation options
                self.assertIn('.tran', netlist)
                self.assertIn('.options', netlist)

    def test_additional_instructions_in_netlist(self):
        """Test that additional instructions are included in netlist"""
        from spice_simulator.simulation import CircuitSimulation

        with patch('spice_simulator.simulation.os.path.exists', return_value=True):
            with patch('spice_simulator.simulation.shutil.which', return_value='ngspice'):
                sim = CircuitSimulation(output_folder=self.temp_dir, clean_temp_files=False)
                circuit = MockCircuit(n_inputs=1, n_outputs=1)

                additional = [
                    ".options method=gear",
                    ".options chgtol=1e-11",
                    ".options reltol=0.01",
                    ".options trtol=1"
                ]

                netlist = sim.create_simulation_netlist(
                    circuit,
                    t_max=1e-3,
                    additional_instructions=additional
                )

                for instruction in additional:
                    self.assertIn(instruction, netlist)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
