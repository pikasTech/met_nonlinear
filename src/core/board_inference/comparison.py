"""Artifact comparison helpers for the board inference debug CLI."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict

from .paths import build_path_aliases
from .types import ArtifactDiff, DirectoryComparison


_TEXT_SUFFIXES = {
    '.c',
    '.csv',
    '.h',
    '.json',
    '.jsonl',
    '.ld',
    '.log',
    '.md',
    '.ps1',
    '.py',
    '.txt',
    '.uvoptx',
    '.uvprojx',
    '.xml',
}

_IGNORED_PATH_PATTERNS = (
    'data/.keil_capture/capture_all.jsonl',
    'data/.keil_capture/capture_result.json',
    'keil_project/MDK-ARM/*.lst',
    'keil_project/MDK-ARM/output/**',
    'legacy_cli_process.json',
    'legacy_cli_stderr.log',
    'legacy_cli_stdout.log',
)

_VOLATILE_JSON_KEYS = {
    'capture_start_time': '__TIMESTAMP__',
    'creation_date': '__TIMESTAMP__',
    'id': '__ENTRY_ID__',
    'job_id': '__JOB_ID__',
    'modified_date': '__TIMESTAMP__',
    'pid': '__PID__',
    'timestamp': '__TIMESTAMP__',
}

_BENCHMARK_START_PATTERN = re.compile(r'[A-Z0-9_]*BENCHMARK_VALIDATION(?=\s*iterations=)')
_BENCHMARK_END_MARKER = 'validation_complete=1'
_FLASH_LOAD_FINISHED_PATTERN = re.compile(r'Flash Load finished at \d{2}:\d{2}:\d{2}')
_KEIL_JOB_ARTIFACT_KEYS = frozenset({
    '_log_file',
    'log_file',
    'state_file',
})
_SERIAL_CAPTURE_COUNT_KEYS = frozenset({
    'count',
    'record_count',
    'stream_length',
    'totalCount',
})


def _sorted_aliases(aliases) -> list[str]:
    return sorted(aliases, key=len, reverse=True)


def _normalize_scalar(value: Any, aliases) -> Any:
    if isinstance(value, str):
        normalized = value
        for alias in _sorted_aliases(aliases):
            normalized = normalized.replace(alias, '__EP_ROOT__')
        return normalized
    if hasattr(value, 'item') and not isinstance(value, (dict, list, str, bytes)):
        try:
            return _normalize_scalar(value.item(), aliases)
        except Exception:
            pass
    if isinstance(value, list):
        return [_normalize_scalar(item, aliases) for item in value]
    if isinstance(value, dict):
        return {key: _normalize_scalar(item, aliases) for key, item in value.items()}
    return value


def _normalize_text(text: str, aliases) -> str:
    normalized = text
    for alias in _sorted_aliases(aliases):
        normalized = normalized.replace(alias, '__EP_ROOT__')
    return normalized


def _should_ignore_path(relative_path: str) -> bool:
    return any(fnmatch.fnmatch(relative_path, pattern) for pattern in _IGNORED_PATH_PATTERNS)


def _extract_benchmark_stream(text: str) -> str:
    matches = list(_BENCHMARK_START_PATTERN.finditer(text))
    if not matches:
        return text
    start = matches[-1].start()
    end = text.find(_BENCHMARK_END_MARKER, start)
    if end < 0:
        return text[start:]
    return text[start:end + len(_BENCHMARK_END_MARKER)]


def _normalize_json_metadata(payload: Any) -> Any:
    if isinstance(payload, dict):
        normalized: Dict[str, Any] = {}
        for key, value in payload.items():
            if key in _VOLATILE_JSON_KEYS:
                normalized[key] = _VOLATILE_JSON_KEYS[key]
            else:
                normalized[key] = _normalize_json_metadata(value)
        return normalized
    if isinstance(payload, list):
        return [_normalize_json_metadata(item) for item in payload]
    return payload


def _normalize_elapsed_seconds(payload: Any) -> Any:
    if isinstance(payload, dict):
        normalized: Dict[str, Any] = {}
        for key, value in payload.items():
            if key == 'elapsed_seconds':
                normalized[key] = '__ELAPSED_SECONDS__'
            else:
                normalized[key] = _normalize_elapsed_seconds(value)
        return normalized
    if isinstance(payload, list):
        return [_normalize_elapsed_seconds(item) for item in payload]
    return payload


def _normalize_host_elapsed_measurements(payload: Any) -> Any:
    if isinstance(payload, dict):
        normalized = {
            key: _normalize_host_elapsed_measurements(value)
            for key, value in payload.items()
        }
        if str(normalized.get('timer_source', '')) == 'host_elapsed':
            if 'measurement_total' in normalized:
                normalized['measurement_total'] = '__HOST_ELAPSED_TOTAL__'
            if 'measurement_per_iter' in normalized:
                normalized['measurement_per_iter'] = '__HOST_ELAPSED_PER_ITER__'
        sources = normalized.get('measurement_sources')
        if isinstance(sources, list) and sources and {str(item) for item in sources} == {'host_elapsed'}:
            if 'avg_host_elapsed_seconds' in normalized:
                normalized['avg_host_elapsed_seconds'] = '__HOST_ELAPSED_AVG__'
            if 'avg_measurement_per_iter' in normalized:
                normalized['avg_measurement_per_iter'] = '__HOST_ELAPSED_PER_ITER_AVG__'
        return normalized
    if isinstance(payload, list):
        return [_normalize_host_elapsed_measurements(item) for item in payload]
    return payload


def _normalize_benchmark_summary_payload(payload: Any) -> Any:
    normalized = _normalize_elapsed_seconds(payload)
    return _normalize_host_elapsed_measurements(normalized)


def _normalize_keil_log_excerpt(text: str, aliases) -> str:
    normalized = _normalize_text(text, aliases)
    return _FLASH_LOAD_FINISHED_PATTERN.sub('Flash Load finished at __TIME__', normalized)


def _normalize_keil_benchmark_summary_payload(payload: Any, aliases, path: str = '') -> Any:
    if isinstance(payload, dict):
        normalized: Dict[str, Any] = {}
        for key, value in payload.items():
            key_path = f'{path}.{key}' if path else key
            if key in {'created_at', 'started_at', 'finished_at'}:
                normalized[key] = '__TIMESTAMP__'
                continue
            if key in _KEIL_JOB_ARTIFACT_KEYS:
                normalized[key] = '__KEIL_JOB_ARTIFACT__'
                continue
            if key == 'log_excerpt' and isinstance(value, str):
                normalized[key] = _normalize_keil_log_excerpt(value, aliases)
                continue
            if key in _SERIAL_CAPTURE_COUNT_KEYS and key_path.startswith('serial_capture'):
                normalized[key] = '__SERIAL_CAPTURE_COUNT__'
                continue
            if key_path.endswith('timeRange.start') or key_path.endswith('timeRange.end'):
                normalized[key] = '__TIMESTAMP__'
                continue
            normalized[key] = _normalize_keil_benchmark_summary_payload(value, aliases, key_path)
        return normalized
    if isinstance(payload, list):
        return [
            _normalize_keil_benchmark_summary_payload(item, aliases, f'{path}[]')
            for item in payload
        ]
    return _normalize_scalar(payload, aliases)


def _normalize_json_payload(payload: Any, relative_path: str, aliases) -> Any:
    normalized = _normalize_scalar(payload, aliases)
    normalized = _normalize_json_metadata(normalized)
    if relative_path.endswith('benchmark_summary.json') or relative_path.endswith('keil_benchmark_summary.json'):
        normalized = _normalize_benchmark_summary_payload(normalized)
    if relative_path.endswith('keil_benchmark_summary.json'):
        normalized = _normalize_keil_benchmark_summary_payload(normalized, aliases)
    return normalized


def _read_normalized(path: Path, relative_path: str, aliases) -> Any:
    suffix = path.suffix.lower()
    if suffix == '.wave':
        import numpy as np

        archive = np.load(path, allow_pickle=True)
        normalized_archive: Dict[str, Any] = {}
        for key in archive.files:
            value = archive[key]
            if key == 'metadata':
                metadata = value.item() if hasattr(value, 'item') else value
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
                normalized_archive[key] = _normalize_wave_metadata(metadata, aliases)
            else:
                array = np.asarray(value)
                normalized_archive[key] = {
                    'shape': list(array.shape),
                    'dtype': str(array.dtype),
                    'sha256': hashlib.sha256(array.tobytes()).hexdigest(),
                }
        return json.dumps(normalized_archive, ensure_ascii=False, indent=2, sort_keys=True)

    if suffix == '.jsonl':
        if relative_path.endswith('keil_serial_raw.jsonl'):
            stream_parts = []
            with open(path, 'r', encoding='utf-8') as file_obj:
                for raw_line in file_obj:
                    stripped = raw_line.strip()
                    if not stripped:
                        continue
                    try:
                        payload = json.loads(stripped)
                    except json.JSONDecodeError:
                        return _normalize_text(path.read_text(encoding='utf-8'), aliases)
                    stream_parts.append(str(payload.get('data', '')))
            return _extract_benchmark_stream(''.join(stream_parts))

        normalized_lines = []
        with open(path, 'r', encoding='utf-8') as file_obj:
            for raw_line in file_obj:
                stripped = raw_line.strip()
                if not stripped:
                    continue
                try:
                    payload = json.loads(stripped)
                except json.JSONDecodeError:
                    return _normalize_text(path.read_text(encoding='utf-8'), aliases)
                normalized_lines.append(_normalize_json_payload(payload, relative_path, aliases))
        return json.dumps(normalized_lines, ensure_ascii=False, indent=2, sort_keys=True)

    if suffix == '.json':
        with open(path, 'r', encoding='utf-8') as file_obj:
            payload = json.load(file_obj)
        payload = _normalize_json_payload(payload, relative_path, aliases)
        return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)

    if suffix in _TEXT_SUFFIXES:
        text = _normalize_text(path.read_text(encoding='utf-8'), aliases)
        if relative_path.endswith('keil_serial_stream.txt'):
            return _extract_benchmark_stream(text)
        return text

    return path.read_bytes()


def _normalize_wave_metadata(metadata: Any, aliases) -> Any:
    if isinstance(metadata, dict):
        normalized: Dict[str, Any] = {}
        for key, value in metadata.items():
            if key in {'creation_date', 'modified_date'}:
                normalized[key] = '__TIMESTAMP__'
            else:
                normalized[key] = _normalize_wave_metadata(value, aliases)
        return normalized
    if isinstance(metadata, list):
        return [_normalize_wave_metadata(item, aliases) for item in metadata]
    return _normalize_scalar(metadata, aliases)


def _relative_file_map(root: Path) -> Dict[str, Path]:
    return {
        file_path.relative_to(root).as_posix(): file_path
        for file_path in root.rglob('*')
        if file_path.is_file()
    }


def _excerpt(value: Any, limit: int = 240) -> str:
    if isinstance(value, bytes):
        return value[:limit].hex()
    text = str(value)
    if len(text) <= limit:
        return text
    return text[:limit] + '...'


def compare_directory_trees(left_root: Path, right_root: Path) -> DirectoryComparison:
    """Compare two directory trees after normalizing per-run root paths."""

    comparison = DirectoryComparison(left_root=left_root, right_root=right_root)
    left_files = _relative_file_map(left_root)
    right_files = _relative_file_map(right_root)

    all_paths = sorted(set(left_files) | set(right_files))
    left_aliases = build_path_aliases(left_root)
    right_aliases = build_path_aliases(right_root)

    for relative_path in all_paths:
        if _should_ignore_path(relative_path):
            continue
        left_file = left_files.get(relative_path)
        right_file = right_files.get(relative_path)

        if left_file is None:
            comparison.missing_in_left.append(relative_path)
            continue
        if right_file is None:
            comparison.missing_in_right.append(relative_path)
            continue

        left_value = _read_normalized(left_file, relative_path, left_aliases)
        right_value = _read_normalized(right_file, relative_path, right_aliases)
        if left_value != right_value:
            comparison.differing_files.append(
                ArtifactDiff(
                    path=relative_path,
                    reason='content_mismatch',
                    left_excerpt=_excerpt(left_value),
                    right_excerpt=_excerpt(right_value),
                )
            )

    return comparison
