import json
from pathlib import Path

from core.training_state import TrainingStateManager


def _read_state(state_path: Path) -> dict:
    return json.loads(state_path.read_text(encoding='utf-8'))


def test_same_value_assignment_keeps_timestamp_and_file(tmp_path):
    manager = TrainingStateManager('DemoModel', checkpoint_dir=str(tmp_path))
    state_path = tmp_path / 'training_state.json'

    before_text = state_path.read_text(encoding='utf-8')
    before_state = json.loads(before_text)

    manager['model_name'] = before_state['model_name']

    after_text = state_path.read_text(encoding='utf-8')
    after_state = json.loads(after_text)

    assert after_text == before_text
    assert after_state['timestamp'] == before_state['timestamp']


def test_real_state_update_refreshes_timestamp(tmp_path, monkeypatch):
    import core.training_state as training_state_module

    formatted = iter(['20231114221320.1', '20231114221325.2'])
    monkeypatch.setattr(
        training_state_module.myjson,
        'format_timestamp_number',
        lambda _: next(formatted),
    )

    manager = TrainingStateManager('DemoModel', checkpoint_dir=str(tmp_path))
    state_path = tmp_path / 'training_state.json'
    before_state = _read_state(state_path)

    manager.update_state(model_name='UpdatedModel')

    after_state = _read_state(state_path)
    assert after_state['model_name'] == 'UpdatedModel'
    assert after_state['timestamp'] != before_state['timestamp']
