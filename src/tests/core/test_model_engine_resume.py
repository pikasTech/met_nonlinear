"""Tests for ModelEngine resume-training checkpoint selection."""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


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
            use_pure_power_loss=False,
            loss_type=None,
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
    engine.x_train = np.zeros((1, 1, 2), dtype=np.float32)
    engine.y_train = np.zeros((1, 1, 2), dtype=np.float32)
    engine.x_test = np.zeros((1, 1, 2), dtype=np.float32)
    engine.y_test = np.zeros((1, 1, 2), dtype=np.float32)
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


def test_evaluate_loss_computes_metrics_from_predictions_for_pure_mae_runs():
    from core.model_engine import ModelEngine
    from core.loss_functions import power_log_loss, pure_mae_metric

    engine = _build_engine(use_best_val_weights=False)
    engine.config.use_power_loss = False
    engine.x_train = np.array([[[1.0, 2.0]]], dtype=np.float32)
    engine.y_train = np.array([[[1.0, 2.0]]], dtype=np.float32)
    engine.x_test = np.array([[[2.0, 1.0]]], dtype=np.float32)
    engine.y_test = np.array([[[2.0, 1.0]]], dtype=np.float32)
    engine.evaluate_loss = ModelEngine.evaluate_loss.__get__(engine, ModelEngine)
    engine.model_comp = MagicMock()
    engine.model_comp.evaluate.side_effect = AssertionError('evaluate() should not be called')

    predictions = [
        np.array([[[1.5], [1.5]]], dtype=np.float32),
        np.array([[[2.5], [0.5]]], dtype=np.float32),
    ]

    def predict_side_effect(*args, **kwargs):
        assert kwargs.get('use_scaler') is False
        return predictions.pop(0)

    engine.model_comp.predict.side_effect = predict_side_effect

    expected_train_true = np.array([[[1.0], [2.0]]], dtype=np.float32)
    expected_train_pred = np.array([[[1.5], [1.5]]], dtype=np.float32)
    expected_val_true = np.array([[[2.0], [1.0]]], dtype=np.float32)
    expected_val_pred = np.array([[[2.5], [0.5]]], dtype=np.float32)

    loss, mae, afmae, val_loss, val_mae, val_afmae = engine.evaluate_loss()

    assert loss == pytest.approx(float(pure_mae_metric(expected_train_true, expected_train_pred).numpy()))
    assert mae == pytest.approx(float(pure_mae_metric(expected_train_true, expected_train_pred).numpy()))
    assert afmae == pytest.approx(float(power_log_loss(expected_train_true, expected_train_pred).numpy()))
    assert val_loss == pytest.approx(float(pure_mae_metric(expected_val_true, expected_val_pred).numpy()))
    assert val_mae == pytest.approx(float(pure_mae_metric(expected_val_true, expected_val_pred).numpy()))
    assert val_afmae == pytest.approx(float(power_log_loss(expected_val_true, expected_val_pred).numpy()))
    assert engine.model_comp.predict.call_count == 2


def test_evaluate_loss_computes_metrics_from_predictions_for_pure_afmae_runs():
    from core.model_engine import ModelEngine
    from core.loss_functions import power_log_loss, pure_mae_metric, pure_power_log_mae_loss

    engine = _build_engine(use_best_val_weights=False)
    engine.config.use_power_loss = False
    engine.config.use_pure_power_loss = True
    engine.x_train = np.array([[[1.0, 2.0]]], dtype=np.float32)
    engine.y_train = np.array([[[1.0, 2.0]]], dtype=np.float32)
    engine.x_test = np.array([[[2.0, 1.0]]], dtype=np.float32)
    engine.y_test = np.array([[[2.0, 1.0]]], dtype=np.float32)
    engine.evaluate_loss = ModelEngine.evaluate_loss.__get__(engine, ModelEngine)
    engine.model_comp = MagicMock()
    engine.model_comp.evaluate.side_effect = AssertionError('evaluate() should not be called')

    predictions = [
        np.array([[[1.5], [1.5]]], dtype=np.float32),
        np.array([[[2.5], [0.5]]], dtype=np.float32),
    ]

    def predict_side_effect(*args, **kwargs):
        assert kwargs.get('use_scaler') is False
        return predictions.pop(0)

    engine.model_comp.predict.side_effect = predict_side_effect

    expected_train_true = np.array([[[1.0], [2.0]]], dtype=np.float32)
    expected_train_pred = np.array([[[1.5], [1.5]]], dtype=np.float32)
    expected_val_true = np.array([[[2.0], [1.0]]], dtype=np.float32)
    expected_val_pred = np.array([[[2.5], [0.5]]], dtype=np.float32)

    loss, mae, afmae, val_loss, val_mae, val_afmae = engine.evaluate_loss()

    assert loss == pytest.approx(float(pure_power_log_mae_loss(expected_train_true, expected_train_pred).numpy()))
    assert mae == pytest.approx(float(pure_mae_metric(expected_train_true, expected_train_pred).numpy()))
    assert afmae == pytest.approx(float(power_log_loss(expected_train_true, expected_train_pred).numpy()))
    assert val_loss == pytest.approx(float(pure_power_log_mae_loss(expected_val_true, expected_val_pred).numpy()))
    assert val_mae == pytest.approx(float(pure_mae_metric(expected_val_true, expected_val_pred).numpy()))
    assert val_afmae == pytest.approx(float(power_log_loss(expected_val_true, expected_val_pred).numpy()))
    assert engine.model_comp.predict.call_count == 2


def test_evaluate_loss_ignores_evaluate_metrics_and_uses_prediction_metrics():
    from core.model_engine import ModelEngine
    from core.loss_functions import power_log_loss, power_log_mae_loss, pure_mae_metric

    engine = _build_engine(use_best_val_weights=False)
    engine.x_train = np.array([[[1.0, 2.0]]], dtype=np.float32)
    engine.y_train = np.array([[[1.0, 2.0]]], dtype=np.float32)
    engine.x_test = np.array([[[2.0, 1.0]]], dtype=np.float32)
    engine.y_test = np.array([[[2.0, 1.0]]], dtype=np.float32)
    engine.evaluate_loss = ModelEngine.evaluate_loss.__get__(engine, ModelEngine)
    engine.model_comp = MagicMock()
    engine.model_comp.evaluate.side_effect = AssertionError('evaluate() should not be called')

    predictions = [
        np.array([[[1.5], [1.5]]], dtype=np.float32),
        np.array([[[2.5], [0.5]]], dtype=np.float32),
    ]

    def predict_side_effect(*args, **kwargs):
        assert kwargs.get('use_scaler') is False
        return predictions.pop(0)

    engine.model_comp.predict.side_effect = predict_side_effect

    expected_train_true = np.array([[[1.0], [2.0]]], dtype=np.float32)
    expected_train_pred = np.array([[[1.5], [1.5]]], dtype=np.float32)
    expected_val_true = np.array([[[2.0], [1.0]]], dtype=np.float32)
    expected_val_pred = np.array([[[2.5], [0.5]]], dtype=np.float32)

    loss, mae, afmae, val_loss, val_mae, val_afmae = engine.evaluate_loss()

    assert loss == pytest.approx(float(power_log_mae_loss(expected_train_true, expected_train_pred).numpy()))
    assert mae == pytest.approx(float(pure_mae_metric(expected_train_true, expected_train_pred).numpy()))
    assert afmae == pytest.approx(float(power_log_loss(expected_train_true, expected_train_pred).numpy()))
    assert val_loss == pytest.approx(float(power_log_mae_loss(expected_val_true, expected_val_pred).numpy()))
    assert val_mae == pytest.approx(float(pure_mae_metric(expected_val_true, expected_val_pred).numpy()))
    assert val_afmae == pytest.approx(float(power_log_loss(expected_val_true, expected_val_pred).numpy()))
    assert engine.model_comp.predict.call_count == 2