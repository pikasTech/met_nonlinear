from pathlib import Path

from core.board_inference.models.frikan import (
    FrikanIirSpec,
    FrikanKanLayerSpec,
    FrikanModelSpec,
    _pad_frikan_lut_layer,
    _render_frikan_main_c,
)


def _make_model_spec(*, use_lut: bool = True, lut_interpolation: bool = False) -> FrikanModelSpec:
    return FrikanModelSpec(
        model_project_name='projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4',
        weights_json_path=Path('weights.json'),
        input_dim=1,
        feature_count=1,
        kan_layers=[
            FrikanKanLayerSpec(
                name='dense_kan',
                input_dim=1,
                output_dim=1,
                grid_size=2,
                spline_order=1,
                grid_range=[0.0, 1.0],
                spline_kernel=[[[0.0]]],
                bias=[0.0],
                scale_factor=[[1.0]],
                use_symmetry=True,
                only_positive=True,
                use_even=False,
                basis_activation='silu',
                disable_basis_activation=True,
                lut_support_min=0.0,
                lut_support_max=1.0,
                lut_values=[[[0.0, 0.0]]],
            )
        ],
        iir_filters=[
            FrikanIirSpec(
                b0=1.0,
                b1=0.0,
                b2=0.0,
                a1=0.0,
                a2=0.0,
            )
        ],
        output_units=1,
        use_lut=use_lut,
        lut_points=2,
        lut_interpolation=lut_interpolation,
        use_symmetry=True,
        use_even=False,
    )


def test_render_frikan_main_skips_intermediate_serial_dump_on_keil():
    rendered = _render_frikan_main_c(_make_model_spec())

    assert '#if !defined(BENCHMARK_PLATFORM_KEIL)\n        uart_puts("validation_input_scaled_");' in rendered
    assert 'uart_puts("validation_output_scaled_");\n        uart_put_u32(record_index);\n        uart_puts("=");\n        uart_put_matrix_rows(&debug_output_scaled[0u], VALIDATION_SEQ_LEN, 1u);\n        uart_puts("\\n");\n#endif' in rendered


def test_render_frikan_main_supports_exact_no_lut_path():
    rendered = _render_frikan_main_c(_make_model_spec(use_lut=False))

    assert 'frikan_exact_lookup_fast_layer_0' in rendered
    assert 'frikan_layer_spline_kernel[0u][0u][0u]' in rendered
    assert 'frikan_layer_scale_factor[0u][0u][0u]' in rendered
    assert 'FRIKAN_LAYER_LOOKUP_LAYER_0(layer_values, layer_scale, raw_value) frikan_exact_lookup_fast_layer_0((layer_values), (layer_scale), (raw_value))' in rendered


def test_render_frikan_main_supports_lut_interpolation_path():
    rendered = _render_frikan_main_c(_make_model_spec(use_lut=True, lut_interpolation=True))

    assert '#define FRIKAN_LUT_SCALE_LAYER_0' in rendered
    assert 'frikan_lut_accumulate_fast_layer_0' in rendered
    assert 'frikan_layer_lut_0[input_index][lower_index]' in rendered
    assert 'frikan_layer_lut[' not in rendered
    assert 'static inline void frikan_lut_accumulate_fast_layer_0' in rendered
    assert 'outputs[0u] += output_sign * (lower_value_0 + (row_next[0u] - lower_value_0) * frac);' in rendered
    function_body = rendered.split('static inline void frikan_lut_accumulate_fast_layer_0(', 1)[1]
    function_body = function_body.split('\n}\n', 1)[0]
    assert 'for (output_index = 0u;' not in function_body
    core_body = rendered.split('static void frikan_forward_core(', 1)[1]
    core_body = core_body.split('\n}\n\nstatic void frikan_forward_step', 1)[0]
    assert 'frikan_lut_accumulate_fast_layer_0' in core_body
    benchmark_core_body = rendered.split('static inline void frikan_forward_core_benchmark(', 1)[1]
    benchmark_core_body = benchmark_core_body.split('\n}\n\nstatic void frikan_forward_step', 1)[0]
    assert 'frikan_lut_accumulate_fast_layer_0' not in benchmark_core_body
    assert 'const port_float *row = frikan_layer_lut_0[0u][lower_index];' in benchmark_core_body
    assert 'uint32_t layer_0_input_index;' not in benchmark_core_body
    benchmark_body = rendered.split('static void frikan_forward_step_benchmark(', 1)[1]
    benchmark_body = benchmark_body.split('\n}\n\nstatic void run_validation_record', 1)[0]
    assert 'debug_kan_step' not in benchmark_body
    assert 'debug_iir_step' not in benchmark_body
    assert 'for (feature_index = 0u;' not in benchmark_body
    assert 'port_float x1_value = x1[0u];' in benchmark_body
    assert 'frikan_forward_core_benchmark(current_values, output_scaled_value);' in benchmark_body


def test_pad_frikan_lut_layer_transposes_points_ahead_of_outputs():
    transposed = _pad_frikan_lut_layer(
        [
            [
                [1.0, 2.0, 3.0],
                [10.0, 20.0, 30.0],
            ]
        ],
        max_inputs=1,
        max_outputs=2,
        lut_points=3,
    )

    assert transposed == [
        [
            [1.0, 10.0],
            [2.0, 20.0],
            [3.0, 30.0],
        ]
    ]
