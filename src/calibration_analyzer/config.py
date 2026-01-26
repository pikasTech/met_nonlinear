CONF_SAMPLING_RATE = 20000
CONF_START_TIME = 5
CONF_DURATION = 15
CONF_DURATION_PERIOD_MAX = 999
CONF_DURATION_PERIOD_MIN = 2
CONF_COLOR_HUE_SHIFT = 0.7
CONF_FREQ_RATIO = 1
CONF_USING_IFFT = False
CONF_OUTPUT_FOLDER = 'D:\\output'
CONF_AUTO_SKIP_PARSE = True
CONF_USING_HANNING = True
CONF_USING_ANTI_ALIASING = True
CONF_ANTI_ALIASING_FREQ = 4000
CONF_RAW_VOLTAGE_RATEIO = (3.3 / 32768)

# CONF_GAIN_RATIO = 0.25
# 101.5 mV/g, ref_amp = 20, mV/g -> V/(m/s)
GAIN_REF = 101.5 * 0.001 * (1 / 9.81)  # V/m * s^-2
# AMP_REF = 21.6
AMP_REF = 20
# FIX_RATIO = 1.0416
CONF_FIX_RATIO = 1
CONF_GAIN_RATIO = GAIN_REF * AMP_REF * CONF_FIX_RATIO
CONF_VIBRATION_CALI_RATIO = 1 / (20.25)

CONF_GAIN_RATIO_KEYWORD = [
    ('自激发', 65),
]

CONF_USING_REF_PHASE = False
CONF_USING_REF_GAIN = False

CONF_USING_INTERGRATE = True  # 绘制积分后的结果（基准为加速度时启用）

CONF_PHASE_REF_PS_10R = [
    (5, 52.8),
    (10, -4.65),
    (14, -27.1),
    (20, -43.2),
    (40, -63.2),
    (80, -84.4),
    (160, -90.6),
    (320, -96.4),
    (630, -102.5),
    # (1260, -162.6),
    # (2000, 79)
]


CONF_GAIN_REF_PS_10R = [
    # (1, 0.9),
    (5, 23.1),
    (8, 58.2),
    (10, 82.3),
    (20, 95.1),
    (40, 89.8),
    (80, 87.8),
    (160, 87.0),
    (200, 86.9),
    (320, 87.7),
    (400, 91.6),
    # (500, 85.1),
    # (600, 87.5),
    # (800, 94.2),
    # (1000, 104.9),
    # (1200, 141.0),
    # (1500, 134.6),
    # (2000, 158.1),
]

CONF_GAIN_REF_2HZ = [
    (1, 28.6392),
    (1.26, 46.06154),
    (1.59, 73.22528),
    (2, 111.28727),
    (2.52, 152.63377),
    (3.17, 180.86871),
    (4, 191.22357),
    (5.04, 191.98007),
    (6.35, 189.95525),
    (8, 187.79907),
    (10.08, 186.1031),
    (12.7, 184.92847),
    (16, 183.8782),
    (20.16, 183.28066),
    (25.4, 182.49564),
    (32, 182.49564),
    (40.32, 180.19814),
    (50.8, 191.21578),
    (64, 185.72),
    (80.63, 185.04108),
    (101.59, 184.6922),
    (120, 185.21517),
    (160, 181.58039),
]

CONF_PHASE_REF_2HZ = [
    (1, -29.8),
    (1.26, -38.47),
    (1.59, -50.8),
    (2, -67.91),
    (2.52, -89.37),
    (3.17, -111.3),
    (4, -129.41),
    (5.04, -141.7),
    (6.35, -151.08),
    (8, -157.94),
    (10.08, -163.11),
    (12.7, -167.06),
    (16, -169.81),
    (20.16, -172.16),
    (25.4, -173.99),
    (32, -175.5),
    (40.32, -176.64),
    (50.8, -177.84),
    (64, -178.78),
    (80.63, -179.72),
    (101.59, 179.51 - 360),
    (120, 178.1 - 360),
]

CONF_GAIN_REF_PSO_14E_6D2K = [
    (5,	5.9),
    (8, 15.7),
    (10, 25.3),
    (20, 54.6),
    (40, 52.2),
    (80, 49.9),
    (160, 48.7),
    (200, 47.9),
    (320, 49.9),
    (400, 48.1),
    (500, 46.5),
    # (600, 45.7),
    # (800, 42.2),
    # (1000, 41.1),
    # (1200, 36.1),
    # (1500, 45.4),
    # (2000, 56.2),
]

CONF_PHASE_REF_PSO_14E_6D2K = [
    (5,	67),
    (10, 35.7),
    (14, 4.18),
    (20, -31.1),
    (40, -66.9),
    (80, -82.4),
    (160, -91.9),
    (320, -100.3),
    (630, -113.8),
]

CONF_PHASE_REF = CONF_PHASE_REF_PS_10R
CONF_GAIN_REF = CONF_GAIN_REF_PS_10R
CONF_PHASE_REF_SHIFT = 90

# 关键词预设（检测到关键词则覆盖默认配置）
CONF_KEYWORD_PROFILE = {
    "速度基准": {
        "CONF_USING_INTERGRATE": False,
        "CONF_GAIN_RATIO": 195.2
    }
}


# 初始化默认配置值字典
_DEFAULT_CONFIG_VALUES = {}

# 动态收集所有以"CONF_"开头的全局配置变量的默认值


def collect_default_config():
    for key, value in globals().items():
        if key.startswith('CONF_'):
            _DEFAULT_CONFIG_VALUES[key] = value


# 在程序初始化时调用
collect_default_config()

# 使用收集的默认值复位所有配置


def reset_to_default_configuration():
    for key, value in _DEFAULT_CONFIG_VALUES.items():
        globals()[key] = value
    print("已重置到默认配置。")

# 根据文件名和关键词配置动态调整设置


def load_keyword_profile(file_name: str):
    # 在处理文件之前先重置到默认配置
    reset_to_default_configuration()

    for keyword, overrides in CONF_KEYWORD_PROFILE.items():
        if keyword in file_name:
            print(f"发现关键词 '{keyword}'，将应用特定的配置覆盖默认设置。")
            for key, value in overrides.items():
                # 确保只覆盖以"CONF_"开头的全局配置变量
                if key in globals() and key.startswith('CONF_'):
                    globals()[key] = value
                    print(f"配置 '{key}' 被设置为 {value}。")
