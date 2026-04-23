from core.board_inference.models.frikan import _render_frikan_main_c
from core.board_inference.models.sequence import (
    _render_grn_main_c,
    _render_lstm_transformer_main_c,
    _render_main_c,
    _render_rnn_main_c,
)
from core.board_inference.template_loader import load_template


def test_external_main_templates_load_expected_banners():
    assert 'LSTM_QEMU_VALIDATION' in _render_main_c()
    assert 'RNN_QEMU_VALIDATION' in _render_rnn_main_c()
    assert 'GRN_QEMU_VALIDATION' in _render_grn_main_c()
    assert 'LSTM_TRANSFORMER_QEMU_VALIDATION' in _render_lstm_transformer_main_c()


def test_external_frikan_template_keeps_placeholder_regions():
    template = load_template('models/frikan_main_template.c')
    assert '__FRIKAN_LUT_LAYER_FUNCTIONS__' in template
    assert '__FRIKAN_LUT_LAYER_MACROS__' in template
    assert '__FRIKAN_FORWARD_BODY__' in template
    assert '__FRIKAN_FORWARD_BODY_BENCHMARK__' in template
    assert '__FRIKAN_BENCHMARK_IIR_BODY__' in template


def test_external_lstm_template_keeps_validation_guard_shape():
    rendered = _render_main_c()
    assert '#if !defined(BENCHMARK_PLATFORM_KEIL)' in rendered
    assert 'validation_output_scaled_' in rendered


def test_external_rnn_template_keeps_validation_guard_shape():
    rendered = _render_rnn_main_c()
    assert '#if !defined(BENCHMARK_PLATFORM_KEIL)' in rendered
    assert 'validation_output_scaled_' in rendered
