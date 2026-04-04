# 边缘设备推理仿真

## 功能概述

通过 QEMU 模拟 Cortex-M4 环境，在 PC 上完成最小固件冒烟验证，并为后续的边缘设备推理时延评估提供可重复的基础环境。

当前仓库的最小可运行路径不再依赖 semihosting，而是使用 QEMU 官方支持的 `olimex-stm32-h405` 板卡，并通过 STM32F405 的 `USART1` 输出 `Hello World!`。

已在 2026-04-03 本机实测通过，QEMU 控制台成功打印 `Hello World!`。

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
python cli.py ep ex_projects/inference/qemu-c-inference/frikan_h8u6l6_nosym_interp
python cli.py ep ex_projects/inference/qemu-c-inference/frikan_h8u6l6_nosym
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

`qemu-c-inference` 当前会自动识别模型类型，已支持：

- `lstm`：生成经典 LSTM + Dense 的裸机 C 推理工程。
- `frikan`：将前端 FRIRNN 导出为经典二阶 IIR 级联，将 KAN 部分导出为静态 LUT 数组并生成专用裸机 C 工程。

FRIKAN 任务可在 `generation_config` 中继续调节 LUT 相关参数，例如 `lut_points` 和 `lut_interpolation`。

当前模板默认 `lut_interpolation=false`，以减少查表热路径开销；但像 `frikan_h8u6l6_nosym` 这类已经验证过精度的样例，如果需要把 C/TF 误差继续压低，仍可在该 EP 的 `config.json` 中显式设置为 `true`。

当前仓库内已经提供一组可直接复现实验口径的三模型样例：

- `lstm_u16_base`：LSTM 基线。
- `frikan_h8u6l6_nosym_interp`：FRIKAN 插值版，侧重精度。
- `frikan_h8u6l6_nosym`：FRIKAN 非插值版，侧重性能。

该命令会读取 `validation_config` 中指定的 MET 数据集和筛选条件，先在 Python/TensorFlow 侧生成参考输出，再在对应 EP 目录下生成 `qemu_project/` 并调用现有 `cli.py qemu` 工作流进行构建与运行。

默认流程包括：

1. 从 `best_val.weights.json` 和对应 `.h5` 权重加载模型，并自动识别 `model_type`。
2. 按 `magnitudes`、`frequencies`、`start_time_s`、`end_time_s` 选择 MET 数据集子集。
3. 导出 C 端所需的模型参数、缩放参数和验证输入序列到 `qemu_project/model_data.h`。
4. 先执行 benchmark-only 运行，在捕获到 `benchmark_complete=1` 后立即结束 QEMU，得到纯推理计时。
5. 再执行完整 validation 运行，在捕获到 `validation_complete=1` 后导出逐样本输出与中间层调试信息。
6. 生成 `data/benchmark_summary.json`、`data/validation_comparison.json`、`data/waves/*.wave` 和 `data/plots/*.png`。

该入口在 EP 索引中归类为 `qemu-c-inference` 任务，路径格式与模板生成规则见 [ep 子命令说明](ep.md)。

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
| `data/waves/tf_*.wave` / `data/waves/c_*.wave` | 模型相关的 TF/C 中间层调试波形；LSTM 通常包含 `input_scaled`、`lstm_hidden`、`dense_output`、`output_scaled`，FRIKAN 通常包含 `input_scaled`、`iir_output`、`kan_layer_*`、`output_scaled` |
| `data/plots/*.png` | 每条 validation record 的四曲线对比图，叠加 `origin`、`target`、`c_inference`、`tf_inference` |

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

在当前仓库 2026-04-04 已验证的三样例上，同一条 validation record（`mag0.24_freq10`，`sample_count=400`）的结果如下：

| 模型 | benchmark-only 耗时 | validation run 耗时 | MAE | MSE |
|------|---------------------|---------------------|-----|-----|
| `lstm_u16_base` | `0.07148281 s/iter` | `0.09995057 s/iter` | `0.0006196653` | `4.7243715e-07` |
| `frikan_h8u6l6_nosym_interp` | `0.06392591 s/iter` | `0.09929439 s/iter` | `3.8875193e-05` | `4.2627435e-09` |
| `frikan_h8u6l6_nosym` | `0.04341357 s/iter` | `0.08093242 s/iter` | `0.0805903773` | `0.0098489184` |

可以据此快速判断当前实现的权衡：

- 纯性能最高的是 `frikan_h8u6l6_nosym`，但误差也最大。
- 综合速度与精度表现最好的是 `frikan_h8u6l6_nosym_interp`，它比 LSTM 更快，同时 MSE 也显著更低。
- `lstm_u16_base` 仍适合作为结构简单、行为稳定的对照基线。

## 本机工具链

### 已验证路径

| 组件 | 路径 | 版本 | 备注 |
|------|------|------|------|
| QEMU | `C:\Program Files\qemu\qemu-system-arm.exe` | 10.2.0 | 当前机器未加入 PATH |
| ARM GCC | `C:\Program Files (x86)\Arm GNU Toolchain arm-none-eabi\14.2 rel1\bin\arm-none-eabi-gcc.exe` | 14.2.1 | 当前机器未加入 PATH |

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

如果你已经把两者加入 PATH，可以直接去掉绝对路径。

## 方案结论

### 推荐路径

1. 板卡选 `olimex-stm32-h405`，因为它直接对应 STM32F405RGT6，更贴近当前仓库的目标平台。
2. 输出走 `USART1`，基地址为 `0x40011000`。
3. 固件使用自带启动代码和链接脚本，避免 `rdimon.specs` 与自定义 `_start` 冲突。
4. `Hello World` 冒烟验证阶段不再优先使用 semihosting。

### 不再作为首选的路径

| 路径 | 现状 | 结论 |
|------|------|------|
| `b-l475e-iot01a + semihosting` | 当前仓库已复现 HardFault/锁死 | 不适合最小 hello world 验证 |
| `virt + rdimon.specs` | 能运行但输出链路不稳定 | 不作为默认示例 |
| `semihosting + printf` | Windows 下依赖调试代理和初始化顺序 | 仅保留为后续调试选项 |

## 在线调研结论

### QEMU 官方文档

1. QEMU 官方 ARM 文档明确说明 Cortex-M 属于 M-profile 板卡场景，需要选具体板型，不能只靠 `virt` 泛化。
2. `olimex-stm32-h405` 是官方支持的 STM32F405 Cortex-M4 机器。
3. QEMU semihosting 文档说明输出可重定向到 chardev，但 semihosting 本质上依赖特定 ABI 和宿主调试链路，不是最稳的入门输出方式。

### QEMU 源码信息

1. `olimex-stm32-h405` 使用 `STM32F405` SoC，QEMU 把 `serial0` 绑定到 `USART1`，地址为 `0x40011000`。
2. QEMU 的 `STM32F2XX USART` 关键寄存器偏移为：
  - `SR = 0x00`
  - `DR = 0x04`
  - `BRR = 0x08`
  - `CR1 = 0x0c`
3. `TXE` 是 `SR` 的 bit 7，`TE` 是 `CR1` 的 bit 3，`UE` 是 `CR1` 的 bit 13，满足最小轮询发送需求。
4. QEMU 同时把 flash 映射到 `0x08000000`，并在 `0x00000000` 提供 alias；ELF 链接脚本应使用 STM32F405 的 flash 基地址 `0x08000000`。

### Semihosting 资料

1. ARM semihosting 的典型触发方式是 `BKPT 0xAB`。
2. 使用 newlib/rdimon 时，通常需要 `--specs=rdimon.specs` 和 `initialise_monitor_handles()`。
3. Memfault 的实战文档强调 semihosting 很依赖调试代理启用顺序；若在代理未启用前调用，可能直接触发 HardFault。
4. 对当前仓库的目标来说，semihosting 更适合作为调试备选，不适合作为最小可跑通路径。

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

## 已解决的问题

### 1. semihosting 输出链路不稳定

根因不是单一的 PowerShell 重定向问题，而是当前最小样例把输出建立在 `rdimon + semihosting + 板卡/入口地址` 的组合上，链路太脆弱。

修复策略：改为 `olimex-stm32-h405 + USART1`，去掉对 semihosting 的硬依赖。

### 2. 链接脚本错误

旧链接脚本曾被改成适配 `mps2-an386` 的低地址布局，不再适合 STM32F405 板级仿真。

修复策略：

1. ROM 改回 `0x08000000` 起始。
2. RAM 改为 `0x20000000` 起始。
3. 启动栈顶保持为 STM32F405 SRAM 顶部。

### 3. `rdimon.specs` 与自定义启动冲突

旧方案把 semihosting 的运行时和手写启动代码混用，容易出现 `_start` 冲突。

修复策略：

1. Hello World 样例不再使用 `rdimon.specs`。
2. 使用纯 bare-metal 启动代码和轮询 UART。

### 4. `b-l475e-iot01a` HardFault

QEMU 虽然列出了该机器，但当前仓库最小固件没有针对该 STM32L4 板卡完成时钟、向量表和外设初始化，直接跑很容易进 fault。

修复策略：最小验证改用 `olimex-stm32-h405`，直接在 STM32F405 板级模型上完成验证。

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
