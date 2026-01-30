"""
Tests for model_layers module

This module contains unit tests for:
- BaseLayerModel: Base class for wrapped layer models
- SVFLayer: State Variable Filter layer wrapper
- DenseLayer: Dense layer wrapper with SPICE export support
"""

import pytest
import sys
import tempfile
import numpy as np
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add src to path
_SRC_DIR = Path(__file__).parent.parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


class TestBaseLayerModel:
    """Test cases for BaseLayerModel class."""

    @pytest.fixture
    def keras_model(self):
        """Create a simple Keras model for testing."""
        from tensorflow.keras import layers, models
        input_layer = layers.Input(shape=(10,), name='test_input')
        dense = layers.Dense(5, name='test_dense')(input_layer)
        return models.Model(inputs=input_layer, outputs=dense, name='test_keras_model')

    @pytest.fixture
    def base_layer_model(self, keras_model):
        """Create a BaseLayerModel instance for testing."""
        from models.model_layers import BaseLayerModel
        return BaseLayerModel(keras_model, 'test_layer', 'test_type')

    def test_initialization(self, base_layer_model, keras_model):
        """Test BaseLayerModel initialization."""
        assert base_layer_model.model is keras_model
        assert base_layer_model.name == 'test_layer'
        assert base_layer_model.type == 'test_type'

    def test_callable(self, base_layer_model):
        """Test BaseLayerModel __call__ method."""
        input_data = np.random.random((1, 10))
        result = base_layer_model(input_data)
        assert result.shape == (1, 5)

    def test_get_weights(self, base_layer_model):
        """Test get_weights method."""
        weights = base_layer_model.get_weights()
        assert weights is not None
        assert isinstance(weights, list)

    def test_set_weights(self, base_layer_model):
        """Test set_weights method."""
        weights = base_layer_model.get_weights()
        base_layer_model.set_weights(weights)
        # Should not raise any exception

    def test_get_config(self, base_layer_model):
        """Test get_config method."""
        config = base_layer_model.get_config()
        assert config['name'] == 'test_layer'
        assert config['type'] == 'test_type'

    def test_get_layer_info(self, base_layer_model):
        """Test get_layer_info method."""
        info = base_layer_model.get_layer_info()
        assert info['name'] == 'test_layer'
        assert info['type'] == 'test_type'
        assert 'input_shape' in info
        assert 'output_shape' in info

    def test_get_layer_by_name(self, base_layer_model):
        """Test get_layer method with name."""
        layer = base_layer_model.get_layer(name='test_dense')
        assert layer is not None
        assert layer.name == 'test_dense'

    def test_get_layer_by_index(self, base_layer_model):
        """Test get_layer method with index."""
        layer = base_layer_model.get_layer(index=1)
        assert layer is not None

    def test_summary(self, base_layer_model):
        """Test summary method."""
        # Should not raise exception
        base_layer_model.summary()

    def test_predict(self, base_layer_model):
        """Test predict method."""
        input_data = np.random.random((1, 10))
        result = base_layer_model.predict(input_data)
        assert result.shape == (1, 5)

    def test_get_inner_layers(self, base_layer_model):
        """Test get_inner_layers method."""
        layers = base_layer_model.get_inner_layers()
        assert isinstance(layers, list)
        assert len(layers) > 0

    def test_input_shape_property(self, base_layer_model):
        """Test input_shape property."""
        assert base_layer_model.input_shape == (None, 10)

    def test_output_shape_property(self, base_layer_model):
        """Test output_shape property."""
        assert base_layer_model.output_shape == (None, 5)

    def test_trainable_weights_property(self, base_layer_model):
        """Test trainable_weights property."""
        weights = base_layer_model.trainable_weights
        assert weights is not None

    def test_non_trainable_weights_property(self, base_layer_model):
        """Test non_trainable_weights property."""
        weights = base_layer_model.non_trainable_weights
        assert weights is not None

    def test_layers_property(self, base_layer_model):
        """Test layers property."""
        layers = base_layer_model.layers
        assert isinstance(layers, list)

    def test_inputs_property(self, base_layer_model):
        """Test inputs property."""
        inputs = base_layer_model.inputs
        assert inputs is not None

    def test_outputs_property(self, base_layer_model):
        """Test outputs property."""
        outputs = base_layer_model.outputs
        assert outputs is not None

    def test_input_property(self, base_layer_model):
        """Test input property."""
        inp = base_layer_model.input
        assert inp is not None

    def test_output_property(self, base_layer_model):
        """Test output property."""
        out = base_layer_model.output
        assert out is not None

    def test_getattr_from_model(self, base_layer_model):
        """Test __getattr__ delegates to model."""
        # name should be accessible from model
        assert base_layer_model.name == 'test_layer'

    def test_getattr_nonexistent_raises(self, base_layer_model):
        """Test __getattr__ raises AttributeError for non-existent attributes."""
        with pytest.raises(AttributeError):
            _ = base_layer_model.nonexistent_attribute


class TestBaseLayerModelProxy:
    """Test cases for BaseLayerModel proxy behavior."""

    @pytest.fixture
    def keras_model(self):
        """Create a simple Keras model for testing."""
        from tensorflow.keras import layers, models
        input_layer = layers.Input(shape=(10,), name='proxy_input')
        dense = layers.Dense(5, name='proxy_dense')(input_layer)
        return models.Model(inputs=input_layer, outputs=dense, name='proxy_keras_model')

    @pytest.fixture
    def base_layer_model(self, keras_model):
        """Create a BaseLayerModel instance for testing."""
        from models.model_layers import BaseLayerModel
        return BaseLayerModel(keras_model, 'proxy_layer', 'proxy_type')

    def test_name_property_proxy(self, base_layer_model):
        """Test name property is correctly set."""
        assert base_layer_model.name == 'proxy_layer'

    def test_type_property_proxy(self, base_layer_model):
        """Test type property is correctly set."""
        assert base_layer_model.type == 'proxy_type'


class TestSVFLayer:
    """Test cases for SVFLayer class."""

    @pytest.fixture
    def keras_model(self):
        """Create a simple Keras model for testing."""
        from tensorflow.keras import layers, models
        input_layer = layers.Input(shape=(6,), name='svf_input')
        # Simulate SVF output (3 filters * 2 channels: HP, BP, LP)
        output = layers.Dense(6, name='svf_output')(input_layer)
        return models.Model(inputs=input_layer, outputs=output, name='svf_keras_model')

    @pytest.fixture
    def svf_layer(self, keras_model):
        """Create an SVFLayer instance for testing."""
        from models.model_layers import SVFLayer
        return SVFLayer(
            keras_model,
            layer_name='SVF_Layer_Test',
            center_freqs=[10.0, 20.0],
            quality_factors=[1.0, 2.0]
        )

    def test_initialization(self, svf_layer):
        """Test SVFLayer initialization."""
        assert svf_layer.name == 'SVF_Layer_Test'
        assert svf_layer.type == 'SVF'
        assert svf_layer.center_freqs == [10.0, 20.0]
        assert svf_layer.quality_factors == [1.0, 2.0]

    def test_initialization_with_none_params(self, keras_model):
        """Test SVFLayer initialization with None parameters."""
        from models.model_layers import SVFLayer
        layer = SVFLayer(keras_model)
        assert layer.center_freqs is None
        assert layer.quality_factors is None

    def test_get_layer_info_includes_svf_params(self, svf_layer):
        """Test get_layer_info includes SVF specific parameters."""
        info = svf_layer.get_layer_info()
        assert 'center_freqs' in info
        assert 'quality_factors' in info
        assert info['center_freqs'] == [10.0, 20.0]
        assert info['quality_factors'] == [1.0, 2.0]

    def test_get_layer_info_without_svf_params(self, keras_model):
        """Test get_layer_info without SVF parameters."""
        from models.model_layers import SVFLayer
        layer = SVFLayer(keras_model, center_freqs=None, quality_factors=None)
        info = layer.get_layer_info()
        # SVF specific keys should not be present when None
        assert 'center_freqs' not in info
        assert 'quality_factors' not in info

    def test_inherits_from_baselayer_model(self, svf_layer):
        """Test SVFLayer inherits from BaseLayerModel."""
        from models.model_layers import BaseLayerModel
        assert isinstance(svf_layer, BaseLayerModel)

    def test_inherits_from_spice_model_support(self, svf_layer):
        """Test SVFLayer implements SpiceModelSupport."""
        from models.layer_support import SpiceModelSupport
        assert isinstance(svf_layer, SpiceModelSupport)

    def test_to_spice_missing_svfilter(self, keras_model):
        """Test to_spice returns error when SVFFilter is not available."""
        from models.model_layers import SVFLayer
        import sys
        from types import ModuleType

        # Create layer without SVF params to trigger early check
        layer = SVFLayer(
            keras_model,
            layer_name='test',
            center_freqs=None,
            quality_factors=None
        )

        result = layer.to_spice()
        assert isinstance(result, str)
        assert '未提供' in result or 'SVFilter' in result or '无法导出' in result

    def test_post_process_spice_simulation_type(self, svf_layer):
        """Test post_process with SPICE simulation type returns unchanged."""
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        # Create a mock WaveData
        record = WaveRecord(data=np.random.random((10, 6)), sample_rate=2000.0)
        wave_data = WaveData(records=[record])

        result = svf_layer.post_process(wave_data, context={'simulation_type': 'spice'})

        # Should return unchanged for spice simulation type
        assert result is wave_data

    def test_post_process_numpy_simulation_type(self, svf_layer):
        """Test post_process with NumPy simulation type inverts HP and LP channels."""
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        # Create a mock WaveData with specific shape
        original_data = np.ones((10, 6))
        record = WaveRecord(data=original_data.copy(), sample_rate=2000.0)
        wave_data = WaveData(records=[record])

        result = svf_layer.post_process(wave_data, context={'simulation_type': 'numpy'})

        # HP (0, 3) and LP (2, 5) channels should be inverted
        # HP channels at indices 0 and 3 should be -1
        assert result.records[0].data[0, 0] == -1.0  # HP0
        assert result.records[0].data[0, 2] == -1.0  # LP0
        assert result.records[0].data[0, 3] == -1.0  # HP1
        assert result.records[0].data[0, 5] == -1.0  # LP1
        # BP channels (1, 4) should remain 1
        assert result.records[0].data[0, 1] == 1.0  # BP0
        assert result.records[0].data[0, 4] == 1.0  # BP1

    def test_post_process_unknown_simulation_type(self, svf_layer):
        """Test post_process with unknown simulation type applies default inversion."""
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        original_data = np.ones((10, 6))
        record = WaveRecord(data=original_data.copy(), sample_rate=2000.0)
        wave_data = WaveData(records=[record])

        # No context or unknown simulation type
        result = svf_layer.post_process(wave_data, context={})

        # Should still invert HP and LP channels
        assert result.records[0].data[0, 0] == -1.0

    def test_post_process_no_context(self, svf_layer):
        """Test post_process without context applies default inversion."""
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        original_data = np.ones((10, 6))
        record = WaveRecord(data=original_data.copy(), sample_rate=2000.0)
        wave_data = WaveData(records=[record])

        result = svf_layer.post_process(wave_data)

        # Should invert HP and LP channels
        assert result.records[0].data[0, 0] == -1.0


class TestDenseLayer:
    """Test cases for DenseLayer class."""

    @pytest.fixture
    def keras_model(self):
        """Create a simple Keras model for testing."""
        from tensorflow.keras import layers, models
        input_layer = layers.Input(shape=(10,), name='dense_input')
        dense = layers.Dense(5, activation='relu', name='dense_output')(input_layer)
        return models.Model(inputs=input_layer, outputs=dense, name='dense_keras_model')

    @pytest.fixture
    def dense_layer(self, keras_model):
        """Create a DenseLayer instance for testing."""
        from models.model_layers import DenseLayer
        return DenseLayer(
            keras_model,
            layer_name='Dense_Layer_Test',
            activation='relu',
            units=5
        )

    def test_initialization(self, dense_layer):
        """Test DenseLayer initialization."""
        assert dense_layer.name == 'Dense_Layer_Test'
        assert dense_layer.type == 'Dense'
        assert dense_layer.activation == 'relu'
        assert dense_layer.units == 5

    def test_initialization_with_none_params(self, keras_model):
        """Test DenseLayer initialization with None parameters."""
        from models.model_layers import DenseLayer
        layer = DenseLayer(keras_model)
        assert layer.activation is None
        assert layer.units is None

    def test_get_layer_info_includes_dense_params(self, dense_layer):
        """Test get_layer_info includes Dense specific parameters."""
        info = dense_layer.get_layer_info()
        assert 'activation' in info
        assert 'units' in info
        assert info['activation'] == 'relu'
        assert info['units'] == 5

    def test_get_layer_info_without_optional_params(self, keras_model):
        """Test get_layer_info without optional parameters."""
        from models.model_layers import DenseLayer
        layer = DenseLayer(keras_model)
        info = layer.get_layer_info()
        assert 'activation' in info
        # units key should not be present when None
        assert 'units' not in info

    def test_inherits_from_baselayer_model(self, dense_layer):
        """Test DenseLayer inherits from BaseLayerModel."""
        from models.model_layers import BaseLayerModel
        assert isinstance(dense_layer, BaseLayerModel)

    def test_inherits_from_spice_model_support(self, dense_layer):
        """Test DenseLayer implements SpiceModelSupport."""
        from models.layer_support import SpiceModelSupport
        assert isinstance(dense_layer, SpiceModelSupport)

    def test_to_spice_returns_error_on_missing_factory(self, keras_model):
        """Test to_spice returns error string when DenseCircuitFactory is unavailable."""
        from models.model_layers import DenseLayer
        import models.model_layers as ml_module

        # Create layer
        layer = DenseLayer(keras_model, layer_name='test')

        # Save original factory
        original_factory = ml_module.DenseCircuitFactory

        try:
            # Set factory to None to simulate unavailability
            ml_module.DenseCircuitFactory = None

            # Call to_spice - should return error string
            result = layer.to_spice()

            # Result should be an error message string
            assert isinstance(result, str)
            assert '无法导出' in result or 'DenseCircuitFactory' in result
        finally:
            # Restore original factory
            ml_module.DenseCircuitFactory = original_factory

    def test_post_process_inverts_output(self, keras_model):
        """Test post_process inverts output for ReLU activation."""
        from models.model_layers import DenseLayer
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        # Create layer with activation
        dense_layer = DenseLayer(
            keras_model,
            layer_name='test',
            activation='relu'
        )
        # Manually set use_relu to True
        dense_layer.use_relu = True

        original_data = np.array([[1.0, 2.0, 3.0, 4.0, 5.0]])
        record = WaveRecord(data=original_data.copy(), sample_rate=2000.0)
        wave_data = WaveData(records=[record])

        result = dense_layer.post_process(wave_data)

        # Should be inverted
        expected = -original_data
        np.testing.assert_array_almost_equal(result.records[0].data, expected)

    def test_post_process_no_invert_without_relu(self, keras_model):
        """Test post_process does not invert output without ReLU activation."""
        from models.model_layers import DenseLayer
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        # Create layer without activation
        dense_layer = DenseLayer(
            keras_model,
            layer_name='test',
            activation=None
        )
        # Manually set use_relu to False
        dense_layer.use_relu = False

        original_data = np.array([[1.0, 2.0, 3.0, 4.0, 5.0]])
        record = WaveRecord(data=original_data.copy(), sample_rate=2000.0)
        wave_data = WaveData(records=[record])

        result = dense_layer.post_process(wave_data)

        # Should not be inverted
        np.testing.assert_array_almost_equal(result.records[0].data, original_data)

    def test_post_process_invalid_wave_data_raises(self, dense_layer):
        """Test post_process raises ValueError for invalid WaveData."""
        with pytest.raises(ValueError):
            dense_layer.post_process(None)

        with pytest.raises(ValueError):
            dense_layer.post_process("not a WaveData")

    def test_dense_layer_with_bias(self, keras_model):
        """Test DenseLayer handles model with bias."""
        from tensorflow.keras import layers, models

        # Create model with explicit bias
        input_layer = layers.Input(shape=(5,))
        output = layers.Dense(3, use_bias=True, name='biased_dense')(input_layer)
        model = models.Model(inputs=input_layer, outputs=output)

        from models.model_layers import DenseLayer
        layer = DenseLayer(model, layer_name='biased')

        weights = layer.get_weights()
        # Should have weights and bias
        assert len(weights) == 2

    def test_dense_layer_without_bias(self, keras_model):
        """Test DenseLayer handles model without bias."""
        from tensorflow.keras import layers, models

        # Create model without bias
        input_layer = layers.Input(shape=(5,))
        output = layers.Dense(3, use_bias=False, name='no_bias_dense')(input_layer)
        model = models.Model(inputs=input_layer, outputs=output)

        from models.model_layers import DenseLayer
        layer = DenseLayer(model, layer_name='no_bias')

        weights = layer.get_weights()
        # Should only have weights
        assert len(weights) == 1


class TestSVFLayerEdgeCases:
    """Test edge cases for SVFLayer."""

    def test_svf_layer_with_single_frequency(self):
        """Test SVFLayer with single center frequency and Q factor."""
        from tensorflow.keras import layers, models
        from models.model_layers import SVFLayer

        input_layer = layers.Input(shape=(3,))
        output = layers.Dense(3, name='single_svf')(input_layer)
        model = models.Model(inputs=input_layer, outputs=output)

        layer = SVFLayer(
            model,
            layer_name='single_svf',
            center_freqs=[10.0],
            quality_factors=[1.5]
        )

        info = layer.get_layer_info()
        assert info['center_freqs'] == [10.0]
        assert info['quality_factors'] == [1.5]

    def test_svf_layer_with_many_frequencies(self):
        """Test SVFLayer with multiple center frequencies and Q factors."""
        from tensorflow.keras import layers, models
        from models.model_layers import SVFLayer

        input_layer = layers.Input(shape=(12,))
        output = layers.Dense(12, name='multi_svf')(input_layer)
        model = models.Model(inputs=input_layer, outputs=output)

        center_freqs = [5.0, 10.0, 20.0, 50.0]
        quality_factors = [0.5, 1.0, 2.0, 3.0]

        layer = SVFLayer(
            model,
            layer_name='multi_svf',
            center_freqs=center_freqs,
            quality_factors=quality_factors
        )

        info = layer.get_layer_info()
        assert info['center_freqs'] == center_freqs
        assert info['quality_factors'] == quality_factors


class TestDenseLayerEdgeCases:
    """Test edge cases for DenseLayer."""

    def test_dense_layer_linear_activation(self):
        """Test DenseLayer with linear (no) activation."""
        from tensorflow.keras import layers, models
        from models.model_layers import DenseLayer

        input_layer = layers.Input(shape=(10,))
        output = layers.Dense(5, activation=None, name='linear_dense')(input_layer)
        model = models.Model(inputs=input_layer, outputs=output)

        layer = DenseLayer(model, layer_name='linear', activation=None)

        assert layer.activation is None

    def test_dense_layer_different_activations(self):
        """Test DenseLayer with different activation functions."""
        from tensorflow.keras import layers, models
        from models.model_layers import DenseLayer

        for activation in ['relu', 'sigmoid', 'tanh', 'softmax']:
            input_layer = layers.Input(shape=(10,))
            output = layers.Dense(5, activation=activation, name=f'{activation}_dense')(input_layer)
            model = models.Model(inputs=input_layer, outputs=output)

            layer = DenseLayer(model, layer_name=f'{activation}_layer', activation=activation)

            assert layer.activation == activation

    def test_dense_layer_2d_weights(self):
        """Test DenseLayer handles 2D weight matrix."""
        from tensorflow.keras import layers, models
        from models.model_layers import DenseLayer
        import numpy as np

        # Create a simple dense model
        input_layer = layers.Input(shape=(10,))
        output = layers.Dense(5)(input_layer)
        model = models.Model(inputs=input_layer, outputs=output)

        layer = DenseLayer(model, layer_name='dense_2d')

        weights = layer.get_weights()
        # Should have 2D weights (input_dim, output_dim)
        assert len(weights) == 2  # weights + bias
        assert weights[0].ndim == 2


class TestBaseLayerModelEdgeCases:
    """Test edge cases for BaseLayerModel."""

    def test_empty_model(self):
        """Test BaseLayerModel with minimal model."""
        from tensorflow.keras import layers, models
        from models.model_layers import BaseLayerModel

        # Single layer model
        input_layer = layers.Input(shape=(1,))
        output = layers.Dense(1)(input_layer)
        model = models.Model(inputs=input_layer, outputs=output)

        layer = BaseLayerModel(model, 'minimal', 'minimal_type')

        assert layer.input_shape == (None, 1)
        assert layer.output_shape == (None, 1)

    def test_multi_output_model(self):
        """Test BaseLayerModel with multi-output model."""
        from tensorflow.keras import layers, models
        from models.model_layers import BaseLayerModel

        input_layer = layers.Input(shape=(10,))
        output1 = layers.Dense(5, name='output1')(input_layer)
        output2 = layers.Dense(3, name='output2')(input_layer)
        model = models.Model(inputs=input_layer, outputs=[output1, output2])

        layer = BaseLayerModel(model, 'multi_output', 'multi_type')

        # Should handle multi-output
        assert layer.output is not None

    def test_nested_model(self):
        """Test BaseLayerModel with nested (functional) model."""
        from tensorflow.keras import layers, models
        from models.model_layers import BaseLayerModel

        input_layer = layers.Input(shape=(10,))
        x = layers.Dense(8)(input_layer)
        x = layers.Dense(6)(x)
        output = layers.Dense(4)(x)
        model = models.Model(inputs=input_layer, outputs=output)

        layer = BaseLayerModel(model, 'nested', 'nested_type')

        inner_layers = layer.get_inner_layers()
        assert len(inner_layers) == 4  # Input + 3 Dense layers
