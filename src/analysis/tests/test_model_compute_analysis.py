"""模型计算量分析测试。"""

from types import SimpleNamespace

import tensorflow as tf

from analysis.model_compute_analysis import (
    analyze_model_compute,
    analyze_model_component,
)
from experimental.mimoiir import DIAGIIR, SIMOIIR
from tfkan.layers.dense import DenseKAN


def test_analyze_model_compute_for_lstm16_dense_stack():
    """LSTMu16 结构的单步计算量统计应正确。"""
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(
            units=16,
            activation='tanh',
            return_sequences=True,
            input_shape=(None, 1)
        ),
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(1),
    ])
    model.build(input_shape=(None, None, 1))

    analysis = analyze_model_compute(model, model_type='LSTM')

    assert analysis['total_params'] == 1441
    assert analysis['totals']['multiplications'] == 1408
    assert analysis['totals']['additions'] == 1376
    assert analysis['totals']['maps'] == 96
    assert analysis['estimated_cost']['weighted_units']['total'] == 9216.0
    assert analysis['estimated_cost']['weighted_units']['maps'] == 2208.0
    assert analysis['unsupported_layers'] == []

    lstm_layer = analysis['layers'][0]
    assert lstm_layer['type'] == 'LSTM'
    assert lstm_layer['num_params'] == 1152
    assert lstm_layer['compute']['multiplications'] == 1136
    assert lstm_layer['compute']['additions'] == 1104
    assert lstm_layer['compute']['maps'] == 80

    hidden_dense = analysis['layers'][1]
    assert hidden_dense['type'] == 'Dense'
    assert hidden_dense['num_params'] == 272
    assert hidden_dense['compute']['multiplications'] == 256
    assert hidden_dense['compute']['additions'] == 256
    assert hidden_dense['compute']['maps'] == 16

    output_dense = analysis['layers'][2]
    assert output_dense['type'] == 'Dense'
    assert output_dense['num_params'] == 17
    assert output_dense['compute']['multiplications'] == 16
    assert output_dense['compute']['additions'] == 16
    assert output_dense['compute']['maps'] == 0


def test_analyze_model_compute_marks_unsupported_layers():
    """Dropout 在推理期应计为 0 成本且视为已支持。"""
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(4,)),
        tf.keras.layers.Dropout(0.1),
        tf.keras.layers.Dense(2, activation='relu'),
    ])

    analysis = analyze_model_compute(model)

    assert analysis['unsupported_layers'] == []
    assert analysis['layers'][0]['type'] == 'Dropout'
    assert analysis['layers'][0]['supported'] is True
    assert analysis['layers'][0]['compute']['total'] == 0
    assert analysis['layers'][0]['estimated_cost']['weighted_units']['total'] == 0.0
    assert analysis['layers'][1]['compute']['maps'] == 2




def test_analyze_model_compute_for_explicit_activation_layer():
    """显式 Activation 层应按输出元素计入 MAP，不再标记为 unsupported。"""
    inputs = tf.keras.Input(shape=(None, 8), name='input')
    outputs = tf.keras.layers.Activation('relu', name='explicit_relu')(inputs)
    model = tf.keras.Model(inputs=inputs, outputs=outputs, name='ActivationOnly')

    analysis = analyze_model_compute(model, model_type='ActivationOnly')

    assert analysis['unsupported_layers'] == []
    activation_layer = next(layer for layer in analysis['layers'] if layer['name'] == 'explicit_relu')
    assert activation_layer['type'] == 'Activation'
    assert activation_layer['supported'] is True
    assert activation_layer['compute']['additions'] == 0
    assert activation_layer['compute']['multiplications'] == 0
    assert activation_layer['compute']['maps'] == 8
    assert activation_layer['estimated_cost']['weighted_units']['total'] == 184.0



def test_analyze_model_compute_for_conv1d_layer():
    """Conv1D 应按真实卷积核形状计入单步计算量。"""
    model = tf.keras.Sequential([
        tf.keras.layers.Conv1D(
            filters=8,
            kernel_size=5,
            padding='same',
            activation='linear',
            input_shape=(None, 1),
        ),
    ])
    model.build((None, None, 1))

    analysis = analyze_model_compute(model, model_type='CNN')

    assert analysis['unsupported_layers'] == []
    conv_layer = analysis['layers'][0]
    assert conv_layer['type'] == 'Conv1D'
    assert conv_layer['compute']['multiplications'] == 40
    assert conv_layer['compute']['additions'] == 40
    assert conv_layer['compute']['maps'] == 0
    assert conv_layer['estimated_cost']['weighted_units']['total'] == 200.0



def test_analyze_model_compute_for_gru16_dense_stack():
    """GRN 主干使用的 GRU 不应再被漏算。"""
    model = tf.keras.Sequential([
        tf.keras.layers.GRU(
            units=16,
            activation='tanh',
            return_sequences=True,
            input_shape=(None, 1)
        ),
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(1),
    ])
    model.build(input_shape=(None, None, 1))

    analysis = analyze_model_compute(model, model_type='GRN')

    assert analysis['total_params'] == 1201
    assert analysis['totals']['multiplications'] == 1136
    assert analysis['totals']['additions'] == 1168
    assert analysis['totals']['maps'] == 64
    assert analysis['estimated_cost']['weighted_units']['total'] == 7184.0
    assert analysis['unsupported_layers'] == []

    gru_layer = analysis['layers'][0]
    assert gru_layer['type'] == 'GRU'
    assert gru_layer['num_params'] == 912
    assert gru_layer['compute']['multiplications'] == 864
    assert gru_layer['compute']['additions'] == 896
    assert gru_layer['compute']['maps'] == 48

def test_analyze_model_component_for_frikan_fast_path():
    """FRIKAN 开启 fast 时，统计结果也应与主模型语义一致。"""
    fast_iir = DIAGIIR(
        units=8,
        a1_list=[0.0] * 8,
        a2_list=[0.0] * 8,
        b0_list=[1.0] * 8,
        b1_list=[0.0] * 8,
        b2_list=[0.0] * 8,
        trainable=False,
        init_by_system=True,
    )
    fast_iir.build((None, None, 1))

    fast_model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(None, 8)),
        DenseKAN(units=6, grid_size=8, spline_order=2),
        DenseKAN(units=6, grid_size=8, spline_order=2),
        DenseKAN(units=6, grid_size=8, spline_order=2),
        DenseKAN(units=6, grid_size=8, spline_order=2),
        DenseKAN(units=6, grid_size=8, spline_order=2),
        DenseKAN(units=6, grid_size=8, spline_order=2),
        DenseKAN(units=1, grid_size=8, spline_order=2),
    ])
    fast_model.build((None, None, 8))

    semantic_model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(None, 1)),
        tf.keras.layers.Dropout(0.0),
        SIMOIIR(
            units=8,
            a1_list=[0.0] * 8,
            a2_list=[0.0] * 8,
            b0_list=[1.0] * 8,
            b1_list=[0.0] * 8,
            b2_list=[0.0] * 8,
            trainable=False,
            init_by_system=True,
        ),
        DenseKAN(units=6, grid_size=8, spline_order=2),
        DenseKAN(units=6, grid_size=8, spline_order=2),
        DenseKAN(units=6, grid_size=8, spline_order=2),
        DenseKAN(units=6, grid_size=8, spline_order=2),
        DenseKAN(units=6, grid_size=8, spline_order=2),
        DenseKAN(units=6, grid_size=8, spline_order=2),
        DenseKAN(units=1, grid_size=8, spline_order=2),
    ])
    semantic_model.build((None, None, 1))

    component = SimpleNamespace(
        fast_iir=fast_iir,
        fast_model=fast_model,
        model=semantic_model,
    )

    analysis = analyze_model_component(component, model_type='FRIKAN')

    assert analysis['analysis_target'] == 'model_semantics'
    assert analysis['assumptions']['fast_mode_equivalence']
    assert analysis['totals']['multiplications'] == 40
    assert analysis['totals']['additions'] == 266
    assert analysis['totals']['maps'] == 234
    assert analysis['totals']['total'] == 540
    assert analysis['estimated_cost']['weighted_units']['total'] == 5808.0
    assert analysis['unsupported_layers'] == []

    dropout_layer = next(
        layer for layer in analysis['layers']
        if layer['type'] == 'Dropout'
    )
    assert dropout_layer['compute']['total'] == 0

    iir_layer = next(
        layer for layer in analysis['layers']
        if layer['type'] == 'SIMOIIR'
    )
    assert iir_layer['type'] == 'SIMOIIR'
    assert iir_layer['compute']['multiplications'] == 40
    assert iir_layer['compute']['additions'] == 32
    assert iir_layer['compute']['maps'] == 0

    first_kan = next(
        layer for layer in analysis['layers']
        if layer['type'] == 'DenseKAN'
    )
    assert first_kan['type'] == 'DenseKAN'
    assert first_kan['compute']['multiplications'] == 0
    assert first_kan['compute']['additions'] == 48
    assert first_kan['compute']['maps'] == 48

    last_kan = analysis['layers'][-1]
    assert last_kan['type'] == 'DenseKAN'
    assert last_kan['compute']['additions'] == 6
    assert last_kan['compute']['maps'] == 6


def test_analyze_model_compute_for_cnnkan_stack():
    """CNNKAN 的 Conv1D 前端不应再被漏算。"""
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(None, 1)),
        tf.keras.layers.Conv1D(
            filters=8,
            kernel_size=5,
            padding='same',
            activation='linear',
            name='cnn_filter',
        ),
        DenseKAN(units=6, grid_size=8, spline_order=2),
        DenseKAN(units=6, grid_size=8, spline_order=2),
        DenseKAN(units=6, grid_size=8, spline_order=2),
        DenseKAN(units=6, grid_size=8, spline_order=2),
        DenseKAN(units=6, grid_size=8, spline_order=2),
        DenseKAN(units=6, grid_size=8, spline_order=2),
        DenseKAN(units=1, grid_size=8, spline_order=2),
    ])
    model.build((None, None, 1))

    analysis = analyze_model_compute(model, model_type='CNNKAN')

    assert analysis['unsupported_layers'] == []
    assert analysis['totals']['multiplications'] == 40
    assert analysis['totals']['additions'] == 274
    assert analysis['totals']['maps'] == 234
    assert analysis['estimated_cost']['weighted_units']['total'] == 5816.0


def test_analyze_model_compute_for_lstm_transformer_stack():
    """LSTMTransformer 主干层不应再留下 unsupported。"""
    inputs = tf.keras.Input(shape=(None, 1), name='input')
    x = tf.keras.layers.LSTM(
        units=6,
        activation='tanh',
        return_sequences=True,
        name='lstm_backbone'
    )(inputs)

    attention_context = tf.keras.layers.AveragePooling1D(
        pool_size=2,
        strides=2,
        padding='same',
        name='transformer_context_pool_0'
    )(x)
    attention_output = tf.keras.layers.MultiHeadAttention(
        num_heads=2,
        key_dim=3,
        name='transformer_mha_0'
    )(x, attention_context, attention_context)
    attention_output = tf.keras.layers.Dropout(
        0.1,
        name='transformer_dropout_attn_0'
    )(attention_output)
    x = tf.keras.layers.LayerNormalization(
        epsilon=1e-6,
        name='transformer_ln_attn_0'
    )(x + attention_output)

    ff_output = tf.keras.layers.Dense(
        24,
        activation='relu',
        name='transformer_ffn_expand_0'
    )(x)
    ff_output = tf.keras.layers.Dropout(
        0.1,
        name='transformer_dropout_ffn_0'
    )(ff_output)
    ff_output = tf.keras.layers.Dense(
        6,
        name='transformer_ffn_project_0'
    )(ff_output)
    x = tf.keras.layers.LayerNormalization(
        epsilon=1e-6,
        name='transformer_ln_ffn_0'
    )(x + ff_output)

    outputs = tf.keras.layers.Dense(1, name='output')(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs, name='LSTMTransformer')

    analysis = analyze_model_compute(model, model_type='LSTMTransformer')

    assert analysis['unsupported_layers'] == []
    assert analysis['has_unsupported_layers'] is False
    assert analysis['estimate_status'] == 'complete'
    assert analysis['estimate_warning'] is None
    assert analysis['totals']['multiplications'] == 682
    assert analysis['totals']['additions'] == 680
    assert analysis['totals']['maps'] == 58
    assert analysis['estimated_cost']['weighted_units']['total'] == 4742.0

    layer_types = {layer['name']: layer['type'] for layer in analysis['layers']}
    assert layer_types['transformer_context_pool_0'] == 'AveragePooling1D'
    assert layer_types['transformer_mha_0'] == 'MultiHeadAttention'
    assert layer_types['transformer_ln_attn_0'] == 'LayerNormalization'

    residual_add_layers = [
        layer for layer in analysis['layers']
        if layer['type'] == 'TFOpLambda'
    ]
    assert len(residual_add_layers) == 2
    assert all(layer['supported'] for layer in residual_add_layers)
    assert all(layer['compute']['additions'] == 6 for layer in residual_add_layers)


def test_analyze_model_compute_supports_custom_cost_model():
    """自定义成本模型应覆盖默认 STM32F405 权重。"""
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(3, activation='relu', input_shape=(2,)),
    ])
    model.build((None, 2))

    analysis = analyze_model_compute(
        model,
        cost_model={
            'add_weight': 1.0,
            'mul_weight': 2.0,
            'map_weight': 3.0,
        }
    )

    assert analysis['platform_cost_model']['platform'] == 'stm32f405'
    assert analysis['estimated_cost']['weights']['multiplications'] == 2.0
    assert analysis['estimated_cost']['weights']['maps'] == 3.0
    assert analysis['estimated_cost']['weighted_units']['additions'] == 6.0
    assert analysis['estimated_cost']['weighted_units']['multiplications'] == 12.0
    assert analysis['estimated_cost']['weighted_units']['maps'] == 9.0
    assert analysis['estimated_cost']['weighted_units']['total'] == 27.0
