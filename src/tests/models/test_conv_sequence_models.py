"""Tests for the real 1DCNN and TCN sequence models."""

import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from tensorflow import keras

_SRC_DIR = Path(__file__).parent.parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


class TestOneDCNN:
    def test_onedcnn_initialization(self):
        from models.conv_models import OneDCNN

        with tempfile.TemporaryDirectory() as tmpdir:
            model = OneDCNN(
                kernel_units=8,
                activation='relu',
                checkpoint_dir=tmpdir,
                model_subcfg={
                    'init_conv_units': 4,
                    'kernel_size': 20,
                    'post_dense': True,
                    'post_dense_units': 8,
                    'post_dense_layers': 2,
                    'dropout_rate': 0.0,
                },
            )

        assert model.model_name == '1DCNN'
        assert isinstance(model.model, keras.Model)
        assert model.model.input_shape == (None, None, 1)
        assert model.model.output_shape == (None, None, 1)


class TestTCN:
    def test_tcn_initialization(self):
        from models.conv_models import TCN

        with tempfile.TemporaryDirectory() as tmpdir:
            model = TCN(
                kernel_units=8,
                activation='relu',
                checkpoint_dir=tmpdir,
                model_subcfg={
                    'dilations': [1, 2, 4, 8],
                    'kernel_size': 3,
                    'init_conv_units': 4,
                    'use_residual': True,
                    'post_dense': True,
                    'post_dense_units': 8,
                    'post_dense_layers': 1,
                    'post_dense_activation': 'relu',
                    'dropout_rate': 0.0,
                },
            )

        assert model.model_name == 'TCN'
        assert isinstance(model.model, keras.Model)
        assert model.model.input_shape == (None, None, 1)
        assert model.model.output_shape == (None, None, 1)

    def test_tcn_rejects_wavenet_gating(self):
        from models.conv_models import TCN

        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match='gating'):
                TCN(
                    kernel_units=8,
                    checkpoint_dir=tmpdir,
                    model_subcfg={'use_gating': True},
                )


class TestModelEngineAliases:
    @staticmethod
    def _make_project(use_model):
        from config import Config

        config = Config()
        config.using_gpu = False
        config.use_model = use_model
        config.kernal_units = 8
        config.activation = 'relu'
        config.model_subcfg = {
            'init_conv_units': 4,
            'kernel_size': 8,
            'post_dense': True,
            'post_dense_units': 8,
            'post_dense_layers': 1,
            'post_dense_activation': 'relu',
            'dropout_rate': 0.0,
        }
        if use_model == 'TCN':
            config.model_subcfg = {
                'dilations': [1, 2, 4],
                'kernel_size': 3,
                'init_conv_units': 4,
                'use_residual': True,
                'post_dense': True,
                'post_dense_units': 8,
                'post_dense_layers': 1,
                'post_dense_activation': 'relu',
                'dropout_rate': 0.0,
            }
        config.use_auto_lr = False
        config.use_scale = False
        config.use_power_loss = True
        config.inference_config = {}
        return SimpleNamespace(
            project_name=f'test_{use_model.lower()}',
            config=config,
            training_logger=None,
            state_manager={},
        )

    def test_model_engine_builds_1dcnn_alias(self):
        from core.model_engine import ModelEngine

        project = self._make_project('1DCNN')
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('core.model_engine.metnl.set_using_gpu'):
                engine = ModelEngine(project, checkpoint_dir=tmpdir)
                engine.build_model()

        assert engine.model_comp.model_name == '1DCNN'

    def test_model_engine_builds_tcn(self):
        from core.model_engine import ModelEngine

        project = self._make_project('TCN')
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('core.model_engine.metnl.set_using_gpu'):
                engine = ModelEngine(project, checkpoint_dir=tmpdir)
                engine.build_model()

        assert engine.model_comp.model_name == 'TCN'
