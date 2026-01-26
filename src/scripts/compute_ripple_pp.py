import json
import argparse
from pathlib import Path
from typing import Tuple, List


def load_linear_response(path: Path):
    with path.open('r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def select_band_indices(frequencies: List[float], band: Tuple[float, float]):
    f_min, f_max = band
    return [i for i, f in enumerate(frequencies) if f_min <= f <= f_max]


def peak_to_peak(values, indices):
    if not indices:
        return float('nan')
    subset = [values[i] for i in indices]
    return float(max(subset) - min(subset))


def main():
    parser = argparse.ArgumentParser(description='计算 linear_response.json 中各幅度在指定频段的峰峰值波动 (max-min)。')
    parser.add_argument('-f', '--file', default='projects/LSTMu32al_rs300_ex3/data/linear_response.json', help='linear_response.json 路径')
    parser.add_argument('--fmin', type=float, default=90.0, help='频段下限 (含)')
    parser.add_argument('--fmax', type=float, default=100.0, help='频段上限 (含)')
    parser.add_argument('--show-band', action='store_true', help='输出频段内的频率点数量')
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        raise SystemExit(f'文件不存在: {path}')

    data = load_linear_response(path)
    frequencies = data['frequencies']
    gains_origin = data['gains_origin']  # List[List[float]]
    gains_comped = data['gains_comped']  # List[List[float]]
    magnitudes = data.get('magnitudes', [f'M{i}' for i in range(len(gains_origin))])

    if len(gains_origin) != len(gains_comped):
        raise SystemExit('gains_origin 与 gains_comped 列表长度不一致')

    indices = select_band_indices(frequencies, (args.fmin, args.fmax))
    if not indices:
        raise SystemExit(f'指定频段无频率点: {args.fmin}-{args.fmax}')

    # 输出表头
    print('\n峰峰值波动 (max - min) @ 频段 [{:.2f}, {:.2f}] Hz'.format(args.fmin, args.fmax))
    print('-' * 70)
    print(f"{'Idx':>3}  {'Magnitude':>10}  {'Orig_pp':>10}  {'Comp_pp':>10}  {'Supp.%':>8}")
    print('-' * 70)

    for idx, (orig_series, comp_series, mag) in enumerate(zip(gains_origin, gains_comped, magnitudes)):
        r_orig = peak_to_peak(orig_series, indices)
        r_comp = peak_to_peak(comp_series, indices)
        if r_orig > 0:
            suppression = (r_orig - r_comp) / r_orig * 100.0
        else:
            suppression = float('nan')
        print(f"{idx:>3}  {str(mag):>10}  {r_orig:10.4f}  {r_comp:10.4f}  {suppression:8.2f}")

    print('-' * 70)
    if args.show_band:
        print(f"频段内频率点数量: {len(indices)}")
        first = frequencies[indices[0]]
        last = frequencies[indices[-1]]
        print(f"首尾频率: {first} Hz -> {last} Hz")


if __name__ == '__main__':
    main()
