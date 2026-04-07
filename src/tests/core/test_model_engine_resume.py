"""Tests for ModelEngine resume-training checkpoint selection."""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np


_SRC_DIR = Path(__file__).parent.parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


def _build_engine(use_best_val_weights):
    from core.model_engine import ModelEngine

    project = SimpleNamespace(
        project_name='test_project',
        config=SimpleNamespace(
            using_gpu=False,
            learning_rate=0.001,
            use_power_loss=True,
            step_per_epoch=5,
            resume_training=True,
            use_best_val_weights=use_best_val_weights,
            epoch_train=10,
        ),
        training_logger=MagicMock(),
        state_manager={'completed_epoch': 3},
    )

    with patch('core.model_engine.metnl.set_using_gpu'):
        engine = ModelEngine(project, checkpoint_dir='data')

    engine.x_train_shuffle = np.zeros((1, 1, 2), dtype=np.float32)
    engine.y_train_shuffle = np.zeros((1, 1, 2), dtype=np.float32)
    engine.x_test_shuffle = np.zeros((1, 1, 2), dtype=np.float32)
    engine.y_test_shuffle = np.zeros((1, 1, 2), dtype=np.float32)
    engine.batch_size = 1
    engine.evaluate_loss = MagicMock(return_value=(1.0, 0.0, 0.0, 1.1, 0.0, 0.0))
    engine.model_comp = SimpleNamespace(
        best_weights_file='best.weights.h5',
        best_val_weights_file='best_val.weights.h5',
        fit=MagicMock(),
    )
    engine.load_best_weights = MagicMock()
    engine.load_val_best_weights = MagicMock()
    return engine


def test_resume_training_uses_best_val_weights_when_enabled():
    engine = _build_engine(use_best_val_weights=True)

    with patch('core.model_engine.RealTimeTrainingCallback', return_value=object()):
        engine.train_model()

    engine.load_val_best_weights.assert_called_once_with()
    engine.load_best_weights.assert_not_called()
    assert engine.model_comp.fit.call_args.kwargs['epochs'] == 7


def test_resume_training_uses_best_weights_when_best_val_disabled():
    engine = _build_engine(use_best_val_weights=False)

    with patch('core.model_engine.RealTimeTrainingCallback', return_value=object()):
        with patch('core.model_engine.os.path.exists', return_value=True):
            engine.train_model()

    engine.load_best_weights.assert_called_once_with()
    engine.load_val_best_weights.assert_not_called()
    assert engine.model_comp.fit.call_args.kwargs['epochs'] == 7