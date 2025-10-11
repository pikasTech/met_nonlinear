import json
import argparse
from pathlib import Path
import math
from typing import List, Tuple


def load_data(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def select_indices(freqs: List[float], band: Tuple[float, float]):
    lo, hi = band
    return [i for i, f in enumerate(freqs) if lo <= f <= hi]


def peak_to_peak(values: List[float]):
    return float(max(values) - min(values))


def ratio_db(values: List[float]):
    vmax = max(values)
    vmin = min(values)
    if vmin <= 0:
        return float('nan')
    return 20.0 * math.log10(vmax / vmin)


def main():
    parser = argparse.ArgumentParser(description='合并全部 magnitude 计算指定频段灵敏度波动 (线性与 dB)。')
    parser.add_argument('-f','--file', default='projects/LSTMu32al_rs300_ex3/data/linear_response.json', help='linear_response.json 路径')
    parser.add_argument('--fmin', type=float, default=90.0)
    parser.add_argument('--fmax', type=float, default=100.0)
    parser.add_argument('--show-extrema', action='store_true', help='输出原始与补偿的最大/最小值')
    args = parser.parse_args()

    data = load_data(Path(args.file))
    freqs = data['frequencies']
    gains_origin = data['gains_origin']  # List[List[float]]
    gains_comped = data['gains_comped']

    band_indices = select_indices(freqs, (args.fmin, args.fmax))
    if not band_indices:
        raise SystemExit('频段内无频率点')

    # 合并所有 magnitude 在该频段的值
    orig_vals = []
    comp_vals = []
    for mag_idx in range(len(gains_origin)):
        series_o = gains_origin[mag_idx]
        series_c = gains_comped[mag_idx]
        for i in band_indices:
            orig_vals.append(series_o[i])
            comp_vals.append(series_c[i])

    # 线性峰峰值
    pp_orig = peak_to_peak(orig_vals)
    pp_comp = peak_to_peak(comp_vals)

    # dB 波动 (用 max/min 比值转换为 dB)
    ripple_db_orig = ratio_db(orig_vals)
    ripple_db_comp = ratio_db(comp_vals)

    if pp_orig > 0:
        suppression_linear = (pp_orig - pp_comp) / pp_orig * 100.0
    else:
        suppression_linear = float('nan')

    if ripple_db_orig > 0:
        suppression_db = (ripple_db_orig - ripple_db_comp) / ripple_db_orig * 100.0
    else:
        suppression_db = float('nan')

    print('\n合并全部 magnitude 频段 [{:.2f},{:.2f}] Hz 灵敏度波动:'.format(args.fmin, args.fmax))
    print('-'*78)
    print(f"线性峰峰值  原始: {pp_orig:.6f}  补偿: {pp_comp:.6f}  抑制: {suppression_linear:.2f}%")
    print(f"dB 波动(20log10(max/min))  原始: {ripple_db_orig:.6f} dB  补偿: {ripple_db_comp:.6f} dB  抑制: {suppression_db:.2f}%")

    if args.show_extrema:
        print('\n原始: max={:.6f}  min={:.6f}'.format(max(orig_vals), min(orig_vals)))
        print('补偿: max={:.6f}  min={:.6f}'.format(max(comp_vals), min(comp_vals)))
        # 也给出两者分别的均值供参考
        mean_orig = sum(orig_vals)/len(orig_vals)
        mean_comp = sum(comp_vals)/len(comp_vals)
        print('均值: 原始={:.6f}  补偿={:.6f}'.format(mean_orig, mean_comp))

if __name__ == '__main__':
    main()
