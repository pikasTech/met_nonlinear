from pathlib import Path

from core.board_inference.platforms.benchmark_common import (
    ValidationArtifacts,
    ValidationRecord,
    _extract_validation_outputs,
)


def _make_validation_artifacts(seq_len: int) -> ValidationArtifacts:
    return ValidationArtifacts(
        dataset_type='MET',
        full_data_path='data/M50',
        sample_rate=2000.0,
        time_window={'start_time_s': 0.0, 'end_time_s': 0.2},
        input_data_range=1.0,
        output_data_range=1.0,
        loaded_weights_path=Path('weights.json'),
        records=[
            ValidationRecord(
                record_id='record_0',
                magnitude=0.24,
                frequency=10.0,
                input_sequence=[[0.0] for _ in range(seq_len)],
                target_sequence=[0.0 for _ in range(seq_len)],
                tf_output_sequence=[0.0 for _ in range(seq_len)],
            )
        ],
    )


def test_extract_validation_outputs_ignores_trailing_matrix_tail():
    validation_artifacts = _make_validation_artifacts(seq_len=3)
    parsed_output = {
        'validation_record_0': '1.000000,2.000000,3.000000;0.000053;0.000058',
        'validation_complete': 1,
    }

    result = _extract_validation_outputs(parsed_output, validation_artifacts)

    assert result == [[1.0, 2.0, 3.0]]


def test_extract_validation_outputs_recovers_missing_commas_between_fixed6_values():
    validation_artifacts = _make_validation_artifacts(seq_len=3)
    parsed_output = {
        'validation_record_0': '1.0000002.000000,3.000000;0.000053',
        'validation_complete': 1,
    }

    result = _extract_validation_outputs(parsed_output, validation_artifacts)

    assert result == [[1.0, 2.0, 3.0]]
