# 边缘设备推理仿真

## 功能概述

通过 QEMU 模拟 Cortex-M4 环境，在 PC 上完成最小固件冒烟验证，并为后续的边缘设备推理时延评估提供可重复的基础环境。

当前仓库的最小可运行路径不再依赖 semihosting，而是使用 QEMU 官方支持的 `olimex-stm32-h405` 板卡，并通过 STM32F405 的 `USART1` 输出 `Hello World!`。

## CLI 用法

仓库现已将 QEMU 工程编译与运行封装到 `cli.py qemu` 子命令中，默认不加载 TensorFlow 等重型依赖。

### 可用命令

```powershell
python cli.py qemu list
python cli.py qemu build src/tests/qemu/stm32f405_hello
python cli.py qemu run src/tests/qemu/stm32f405_hello --timeout 5
python cli.py qemu build-run src/tests/qemu/stm32f405_hello --timeout 5
```

### 命令说明

| 命令 | 作用 |
|------|------|
| `python cli.py qemu list` | 扫描仓库内包含 `.c` 和 `.ld` 的 QEMU 工程目录 |
| `python cli.py qemu build DIR` | 编译指定工程目录，自动解析 `.c` 与 `.ld` |
| `python cli.py qemu run DIR` | 运行指定工程的 ELF，默认 5 秒超时后自动结束并保留输出 |
| `python cli.py qemu build-run DIR` | 先编译再运行，适合最小冒烟验证 |

### 常用参数

| 参数 | 说明 |
|------|------|
| `--machine olimex-stm32-h405` | 指定 QEMU 机器型号，默认 `olimex-stm32-h405` |
| `--timeout 5` | 运行超时秒数，默认 5；设为 `0` 表示不设超时 |
| `--output hello.elf` | 指定 ELF 输出文件名或路径 |
| `--linker-script xxx.ld` | 指定链接脚本；工程目录中有多个 `.ld` 时必须显式指定 |
| `--qemu-path PATH` | 手动指定 `qemu-system-arm.exe` 路径 |
| `--gcc-path PATH` | 手动指定 `arm-none-eabi-gcc.exe` 路径 |

### 工程目录约定

`cli.py qemu` 默认将一个目录识别为 QEMU 工程，需要满足：

1. 目录下至少有一个 `.c` 文件。
2. 目录下存在且默认仅存在一个 `.ld` 文件；若有多个，需要用 `--linker-script` 指定。
3. 若目录中已存在且仅存在一个 `.elf` 文件，则默认复用该输出文件名；否则会优先使用非 `startup.c` 的源文件名生成同名 `.elf`。

### 推荐最小验证

```powershell
python cli.py qemu build-run src/tests/qemu/stm32f405_hello --timeout 5
```

### qemu-c-inference 模型感知验证

如果要从已训练项目直接生成裸机 C 工程并运行，可使用：

```powershell
python cli.py ep ex_projects/inference/qemu-c-inference/lstm_u16_base
python cli.py ep ex_projects/inference/qemu-c-inference/lstm_transformeru6_e1k_1
python cli.py ep ex_projects/inference/qemu-c-inference/frikan_h8u6l6_nosym_interp
python cli.py ep ex_projects/inference/qemu-c-inference/frikan_h8u6l6_nosym
```

如果要在同一个 `qemu-c-inference` EP 上直接走真机 Keil benchmark，可使用：

```powershell
python cli.py ep keil-bench ex_projects/inference/qemu-c-inference/lstm_u16_base
python cli.py ep keil-bench ex_projects/inference/qemu-c-inference/frikan_h8u6l6_nosym
```

该命令会复用 EP 的 `config.json -> keil_config`，按同一份模型/validation 配置自动完成：

1. 生成 `qemu_project/` 与 `keil_project/`
2. 调用 `keil-cli.py build` 编译
3. 调用 `keil-cli.py program` 烧录
4. 打开业务串口抓取 benchmark/validation 输出
5. 解析串口输出并生成独立的 `data/keil_benchmark_summary.json`

若当前板卡/串口与默认配置不一致，可临时覆盖：

```powershell
python cli.py ep keil-bench ex_projects/inference/qemu-c-inference/lstm_u16_base --probe-uid 205536951525 --serial-port COM8 --program-backend keil
```

如果当前默认 `python` 不是 TensorFlow 2.6 环境，应改为显式使用 `tf26` 的解释器运行，例如：

```powershell
& 'C:\Users\liang\.conda\envs\tf26\python.exe' cli.py ep ex_projects/inference/qemu-c-inference/lstm_u16_base
```

这里的绝对路径只是实例，不应硬编码到自动化脚本里。更稳妥的规则是：先定位名为 `tf26` 的 Conda 环境，再使用该环境下的 `python.exe`。

常见路径规律：

- `C:\Users\<用户名>\.conda\envs\tf26\python.exe`
- `C:\Users\<用户名>\MiniConda3\envs\tf26\python.exe`
- `C:\Users\<用户名>\miniconda3\envs\tf26\python.exe`

推荐定位命令：

```powershell
conda env list
where conda
Get-ChildItem "$env:USERPROFILE\.conda\envs\tf26\python.exe","$env:USERPROFILE\MiniConda3\envs\tf26\python.exe","$env:USERPROFILE\miniconda3\envs\tf26\python.exe" -ErrorAction SilentlyContinue
```

`qemu-c-inference` 当前通过 `src/core/board_inference/` 承载生产实现，并自动识别模型类型路由到 native executor。当前稳定支持：

- `lstm`：经典 LSTM + Dense 裸机 C 推理工程。
- `grn`：GRU + Dense 裸机 C 推理工程。
- `lstm_transformer`：LSTM backbone + pooled multi-head attention + FFN。
- `frikan`：FRIKAN 前端 IIR + KAN LUT 裸机 C 推理工程。
- `onedcnn`：1DCNN / ConvStack 类 sequence baseline。
- `tcn`：TCN 时序卷积模型。
- `wavenet2`
- `wavenet3`

### `board_inference` 当前分工

当前 `qemu-c-inference` / `keil-bench` 的生产路径为：

```text
cli.py / external_cli_handler
  -> core.board_inference.entrypoints
  -> core.board_inference.registry
  -> core.board_inference.models.*
  -> core.board_inference.platforms.benchmark_common
```

长期分工是：

- `entrypoints.py` 负责稳定入口与异常边界。
- `registry.py` 负责按 project 配置与权重命名识别模型类型。
- `models/sequence.py` 负责 `lstm`、`grn`、`lstm_transformer`、`onedcnn`、`tcn`、`wavenet2`、`wavenet3`。
- `models/frikan.py` 负责 `frikan`。
- `platforms/benchmark_common.py` 负责 QEMU / Keil 共用的工程生成、构建、串口抓取、summary 写回和比较辅助逻辑。
- `templates/` 负责稳定的 C/H 模板；固定 scaffold 应继续留在模板文件中，而不是重新回流到 Python 长字符串里。

FRIKAN 任务可在 `generation_config` 中继续调节 LUT 相关参数，例如 `lut_points` 和 `lut_interpolation`。

当前模板默认 `lut_interpolation=false`，以减少查表热路径开销；但像 `frikan_h8u6l6_nosym` 这类已经验证过精度的样例，如果需要把 C/TF 误差继续压低，仍可在该 EP 的 `config.json` 中显式设置为 `true`。

当前仓库内常用的 `qemu-c-inference` 样例包括：

- `lstm_u16_base`
- `grnu16_e1k_puremae`
- `lstm_transformeru6_e1k_puremae`
- `frikan_h8u6l6_nosym_interp`
- `frikan_h8u6l6_nosym`
- `onedcnn_c4u8k20l8_e1k_lr18e3_pd8l8_true`
- `tcnc4d1248k3_nopd_true_e1k_lr2e3`

该命令会读取 `validation_config` 中指定的 MET 数据集和筛选条件，先在 Python/TensorFlow 侧生成参考输出，再在对应 EP 目录下生成 `qemu_project/` 并调用现有 `cli.py qemu` 工作流进行构建与运行。

默认流程包括：

1. 从 `best_val.weights.json` 和对应 `.h5` 权重加载模型，并自动识别 `model_type`。
2. 按 `magnitudes`、`frequencies`、`start_time_s`、`end_time_s` 选择 MET 数据集子集。
3. 导出 C 端所需的模型参数、缩放参数和验证输入序列到 `qemu_project/model_data.h`。
4. 先执行 benchmark-only 运行，在捕获到 `benchmark_complete=1` 后立即结束 QEMU，得到纯推理计时。
5. 再执行完整 validation 运行，在捕获到 `validation_complete=1` 后导出逐样本输出与中间层调试信息。
6. 生成 `data/benchmark_summary.json`、`data/validation_comparison.json`、`data/waves/*.wave` 和 `data/plots/*.png`。

该入口在 EP 索引中归类为 `qemu-c-inference` 任务，路径格式与模板生成规则见 [ep 子命令说明](ep.md)。

### 新旧架构一致性验收口径

对 `board_inference` 做重构、迁移或新增模型接入时，长期验收顺序应固定为：

1. 先做静态对比，再跑实际工具链；优先核对模型识别、模板渲染、生成文件名、summary 字段和串口语义是否与旧路径等价。
2. 再做 QEMU 实测，至少确认 `build/run`、`benchmark_complete=1`、`benchmark_summary.json`、`validation_comparison.json` 和关键 MAE 字段一致。
3. 最后做 `ep keil-bench` 实测，至少确认 `build/program/capture`、`keil_benchmark_summary.json`、串口 benchmark 语义流、`comparison.mae` 与耗时字段一致。

长期上，`legacy vs native` 的 compare 结果应按下面两类解释：

- `success_match`：旧/新都成功，且 build/run、MAE、summary 关键字段、串口语义流一致。
- `shared_failure`：旧/新在同一阶段因同一原因失败；这说明它不是 native 独有回归，但也不能当作“已经完成一致性迁移”。

若未来需要再次证明新架构没有误依赖旧单体模块，正确做法是：

1. 临时将 `src/core/lstm_qemu_ep_task.py` 重命名为 `src/core/lstm_qemu_ep_task.py.bck`
2. 仅跑 native 路径完成 QEMU / Keil 验证
3. 验证后恢复原文件名

当前生产路径已经接入 `board_inference`，但这仍然是后续大重构时验证“没有偷偷回退到 legacy 模块”的标准方法。

需要注意：QEMU 当前不能可靠提供 Cortex-M4 的 `DWT_CYCCNT` 计数，直接读 DWT 往往恒为 `0`。当前仓库的生成代码会先探测 DWT；若 DWT 不可用，则不再伪造 guest 内 cycle/tick 计数，而是使用 host 侧 elapsed time 作为回退计时来源。

这里有一个关键口径：

- `benchmark_summary.json` 的 `runs[].parsed_output.measurement_per_iter` 和 `aggregated.avg_measurement_per_iter`，只有在 success pattern 停在 `benchmark_complete=1` 时才表示纯推理 benchmark。
- `benchmark_summary.json` 的 `validation_run.parsed_output.measurement_per_iter` 包含完整 validation/UART 输出时间，不能直接拿来和 benchmark-only 结果做跨模型性能对比。

预期输出中应包含类似：

```text
LSTM_QEMU_VALIDATION
timer_source=host_elapsed
benchmark_complete=1
validation_record_0=...
validation_complete=1
```

或：

```text
FRIKAN_QEMU_VALIDATION
timer_source=host_elapsed
benchmark_complete=1
validation_record_0=...
validation_complete=1
```

或：

```text
LSTM_TRANSFORMER_QEMU_VALIDATION
timer_source=host_elapsed
benchmark_complete=1
validation_record_0=...
validation_complete=1
```

### 验证输出说明

执行完成后，重点看以下产物：

| 文件 | 作用 |
|------|------|
| `data/benchmark_summary.json` | 记录 QEMU build/run 结果、模型类型、benchmark-only 计时字段，以及完整 validation 运行摘要 |
| `data/validation_comparison.json` | 记录每条波形的 MAE、最大绝对误差、最大值、最小值、均值、能量，以及中间层对比结果 |
| `data/waves/origin_input.wave` | 输入波形 |
| `data/waves/target_output.wave` | 目标输出波形 |
| `data/waves/tf_output.wave` | TF26 参考输出波形 |
| `data/waves/c_output.wave` | QEMU C 推理输出波形 |
| `data/waves/tf_*.wave` / `data/waves/c_*.wave` | 模型相关的 TF/C 中间层调试波形；LSTM 通常包含 `input_scaled`、`lstm_hidden`、`dense_output`、`output_scaled`，LSTMTransformer 通常包含 `input_scaled`、`lstm_hidden`、`transformer_ln_attn_*`、`transformer_ln_ffn_*`、`post_dense`、`output_scaled`，FRIKAN 通常包含 `input_scaled`、`iir_output`、`kan_layer_*`、`output_scaled` |
| `data/plots/*.png` | 每条 validation record 的四曲线对比图，叠加 `origin`、`target`、`c_inference`、`tf_inference` |
| `data/keil_benchmark_summary.json` | Keil build/program 结果、串口抓取元数据、解析后的 benchmark 标量、`validation_record_*` 与独立 comparison |
| `data/keil_validation_comparison.json` | Keil 真机输出相对 TF 参考波形的独立对比结果 |
| `data/keil_serial_stream.txt` | 本次真机运行的串口原始文本流 |
| `data/keil_serial_raw.jsonl` | 本次真机运行的串口分块抓取记录 |
| `data/waves/keil_output.wave` | Keil 真机输出波形，便于与 TF/QEMU 输出并排比对 |

当前实现里，`benchmark_summary.json` 和 `validation_comparison.json` 都会汇总以下指标：

- `mae`
- `max_abs_error`
- `c_output_stats.min/max/mean/energy`
- `tf_output_stats.min/max/mean/energy`
- `diff_stats.min/max/mean/energy`

若需要跨模型比较 MSE，当前推荐统一使用：

$$
MSE = \frac{\text{overall.diff\_stats.energy}}{\text{overall.sample\_count}}
$$

这样可以直接基于 `validation_comparison.json` 的现有字段计算，而无需额外修改导出格式。

此外：

- `benchmark_summary.json` 会显式记录 `model_type`，并将纯 benchmark 结果放在 `runs` / `aggregated`，将完整 validation 运行结果放在 `validation_run`。
- `plot_paths` 会指向自动生成的 PNG 对比图。
- `validation_comparison.json` 的 `intermediate` 或 `benchmark_summary.json` 的 `intermediate_comparison` 会给出模型相关的逐层误差统计。

如果 `c_output` 与 `tf_output` 偏差明显，说明当前 C 侧实现与 TensorFlow 参考实现仍存在数值不一致，通常应优先查看四曲线对比图，并结合中间层 wave 与 `intermediate_comparison` 排查激活函数近似、缩放参数、输出格式化链路，或 FRIKAN 的 IIR/LUT 配置。

### 跨模型比较口径

如果要对比不同 `qemu-c-inference` 项目的推理性能，建议统一以下条件：

1. `benchmark_config.iterations`、`reset_state_each_run`、`repeat_runs` 保持一致。
2. `qemu_config.machine` 保持一致，例如统一使用 `olimex-stm32-h405`。
3. 性能只比较 `benchmark_summary.json` 里的纯 benchmark 字段，例如 `aggregated.avg_measurement_per_iter`。
4. 一致性则比较 `validation_comparison.json` 里的 `overall.mae` 和 `overall.max_abs_error`。

不要把 `validation_run.parsed_output.measurement_per_iter` 当成纯推理耗时，因为它会把 validation 阶段的 UART 输出时间一并算进去。

不要把某一轮实测数字直接写成长久结论。跨模型结论应始终基于当前项目产物重新判断：

- QEMU 指标看各 EP 的 `benchmark_summary.json` / `validation_comparison.json`
- Keil 指标看各 EP 的 `keil_benchmark_summary.json`
- 横评表格与 compare 报告优先看项目级 `metrics.json` 中的 `board_qemu_mae`、`board_keil_mae`、`board_keil_speed`

## 工具链准备

### 安装命令

```powershell
winget install --id SoftwareFreedomConservancy.QEMU
winget install --id Arm.GnuArmEmbeddedToolchain -e --accept-package-agreements --accept-source-agreements
```

### 验证命令

```powershell
& 'C:\Program Files\qemu\qemu-system-arm.exe' -version
& 'C:\Program Files (x86)\Arm GNU Toolchain arm-none-eabi\14.2 rel1\bin\arm-none-eabi-gcc.exe' --version
```

如果你已经把两者加入 PATH，可以直接去掉绝对路径；若尚未加入 PATH，则可继续使用 `--qemu-path`、`--gcc-path` 或绝对路径运行。

## 平台与链接约束

1. 板卡选 `olimex-stm32-h405`，因为它直接对应 STM32F405RGT6，更贴近当前仓库的目标平台。
2. 输出走 `USART1`，基地址为 `0x40011000`。
3. 链接脚本应使用 STM32F405 的地址布局：flash `0x08000000`、RAM `0x20000000`。
4. 最小固件优先使用仓库自带的 bare-metal 启动代码和轮询 UART，不要默认依赖 `rdimon.specs`、`initialise_monitor_handles()` 或 semihosting。
5. `Hello World` 和最小 QEMU 冒烟验证阶段不再优先使用 semihosting。

下列路径可以作为调试备选，但不再作为长期默认入口：

| 路径 | 现状 | 结论 |
|------|------|------|
| `b-l475e-iot01a + semihosting` | 当前仓库已复现 HardFault/锁死 | 不适合最小 hello world 验证 |
| `virt + rdimon.specs` | 能运行但输出链路不稳定 | 不作为默认示例 |
| `semihosting + printf` | Windows 下依赖调试代理和初始化顺序 | 仅保留为后续调试选项 |

## 测试目录

QEMU 最小样例现已收纳到 `src/tests/qemu/stm32f405_hello/`，避免继续占用仓库根目录。

```
src/tests/qemu/stm32f405_hello/
├── hello.c        # 直接写 USART1 输出 Hello World
├── startup.c      # Cortex-M 启动代码，负责向量表、data/bss 初始化
├── stm32f405.ld   # STM32F405 的 flash/ram 链接脚本
└── hello.elf      # 编译产物（按需生成）
```

## 编译命令

底层原生命令如下；如果只是为了仓库内直接使用，优先使用上面的 `cli.py qemu build`。

```powershell
& 'C:\Program Files (x86)\Arm GNU Toolchain arm-none-eabi\14.2 rel1\bin\arm-none-eabi-gcc.exe' \
  -mcpu=cortex-m4 \
  -mthumb \
  -mfloat-abi=soft \
  -ffreestanding \
  -nostdlib \
  -Wl,-T,src/tests/qemu/stm32f405_hello/stm32f405.ld \
  -Wl,--gc-sections \
  -o src/tests/qemu/stm32f405_hello/hello.elf \
  src/tests/qemu/stm32f405_hello/startup.c src/tests/qemu/stm32f405_hello/hello.c
```

## 运行命令

底层原生命令如下；如果只是为了仓库内直接使用，优先使用上面的 `cli.py qemu run` 或 `build-run`。

```powershell
& 'C:\Program Files\qemu\qemu-system-arm.exe' \
  -M olimex-stm32-h405 \
  -kernel src/tests/qemu/stm32f405_hello/hello.elf \
  -display none \
  -serial stdio \
  -monitor none
```

预期输出：

```text
Hello World!
```

## 后续如何迁移到算法验证

1. 先把核心推理代码裁成不依赖文件系统、动态分配和复杂外设的纯 C 路径。
2. 保持 `startup.c` 和 `UART` 输出路径不变，只替换 `main()` 调用的算法主体。
3. 若需要粗测执行时间，可先在 QEMU 端统计宿主时间；若需要可信周期数据，回到真实硬件使用 `DWT->CYCCNT`。

## 限制说明

1. QEMU 不是 cycle-accurate，不能把它当真实芯片周期计数器。
2. `olimex-stm32-h405` 也不是 cycle-accurate 模型，仍不能替代真实 STM32F405 硬件测时。
3. 对 GPIO、ADC、DMA、时钟树等 STM32 专有外设，QEMU 结果只能做功能冒烟，不能做最终性能结论。

## 相关文档

- [推理功能](inference.md) - 模型推理执行
- [计算量分析](compute_analysis.md) - 推理 FLOPs 估算
- [模型信息](model_info.md) - 模型结构导出
