from pathlib import Path

from core.board_inference.models.frikan import (
    FrikanIirSpec,
    FrikanKanLayerSpec,
    FrikanModelSpec,
    _render_frikan_main_c,
)


def _make_model_spec() -> FrikanModelSpec:
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
        lut_points=2,
        lut_interpolation=False,
        use_symmetry=True,
        use_even=False,
    )


def test_render_frikan_main_skips_intermediate_serial_dump_on_keil():
    rendered = _render_frikan_main_c(_make_model_spec())

    assert '#if !defined(BENCHMARK_PLATFORM_KEIL)\n        uart_puts("validation_input_scaled_");' in rendered
    assert 'uart_puts("validation_output_scaled_");\n        uart_put_u32(record_index);\n        uart_puts("=");\n        uart_put_matrix_rows(&debug_output_scaled[0u], VALIDATION_SEQ_LEN, 1u);\n        uart_puts("\\n");\n#endif' in rendered
