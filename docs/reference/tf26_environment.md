# tf26 环境配置

## 概述

本项目训练与评估默认使用名为 `tf26` 的 Conda 环境 Python，而不是硬编码某台机器的绝对路径。

`tf26` 对应的是 TensorFlow 2.6 这一代的原生 GPU 栈。它仍属于 TensorFlow 官方曾经支持过的 native Windows GPU 时代，但整体已经是旧环境；因此环境变量、CUDA 组件和驱动的兼容性约束必须显式管理，不能把“能识别到 GPU”误判为“所有 GPU 相关高级特性都稳定可用”。

## 路径规律

tf26 环境的 Python 可执行文件常见位置：

- `C:\Users\<用户名>\.conda\envs\tf26\python.exe`
- `C:\Users\<用户名>\MiniConda3\envs\tf26\python.exe`
- `C:\Users\<用户名>\miniconda3\envs\tf26\python.exe`

## 定位方法

先找 `tf26` 这个环境名，再拼接到对应的 Conda 根目录，不要先假设用户名或 Conda 安装目录固定。

推荐定位命令：

```bash
# 查看所有 conda 环境
conda env list

# 查找 conda 位置
where conda

# 在常见位置搜索
ls /c/Users/*/.conda/envs/tf26/python.exe
ls /c/Users/*/MiniConda3/envs/tf26/python.exe
```

## 直接调用

需要执行 `python cli.py` 时，如果默认 Python 不是 tf26，需使用完整路径调用：

```bash
/c/Users/lyon/MiniConda3/envs/tf26/python.exe cli.py --metrics --all-projects
```

## Windows 原生 GPU 支持边界

- TensorFlow 官方安装文档说明：`2.10` 是最后一个支持 native Windows GPU 的正式版本；从 `2.11` 开始，官方建议改用 WSL2 或 CPU/DirectML 路线。
- 因此，`tf26` 虽然仍在“曾经支持 native Windows GPU”的版本区间内，但它本身就是旧栈，不应把较新的实验性 CUDA allocator、驱动特性或跨版本经验直接视为稳定默认行为。
- 新机器若以长期稳定训练为目标，优先选择 WSL2/Linux 上的受支持 TensorFlow GPU 环境；native Windows 下的 `tf26` 更适合历史项目复现和兼容性维护。

## `TF_GPU_ALLOCATOR` 约束

### 基本规则

- 本项目在 native Windows 的 `tf26` 环境下，默认应保持 `TF_GPU_ALLOCATOR` 未设置。
- 不要把 `TF_GPU_ALLOCATOR=cuda_malloc_async` 写入用户级、系统级环境变量，也不要作为训练脚本、Agent 默认前置环境。
- 只有在明确做 allocator 兼容性实验，且能接受进程级崩溃、无 traceback 退出和整机差异时，才允许临时显式设置该变量。

### 项目默认行为

- `cli.py` 在导入 TensorFlow 之前，会对 native Windows 会话做一次环境归一化：如果检测到 `TF_GPU_ALLOCATOR=cuda_malloc_async`，会在当前进程内主动移除该变量。
- 同一预处理阶段会默认设置 `TF_FORCE_GPU_ALLOW_GROWTH=true`；如果用户已显式设置该变量，则保留用户值不覆盖。
- 这两个动作只影响当前 CLI 进程，不会改写用户级或系统级环境变量。

### 为什么它是高风险项

- TensorFlow 源码中，`TF_GPU_ALLOCATOR=cuda_malloc_async` 会直接切换到 `cudaMallocAsync` 分配器，而不是普通的 BFC allocator。
- TensorFlow 对该路径的源码检查非常底层：要求驱动至少兼容 CUDA 11.2、设备支持 memory pools，并且源码直接把“不支持的 OS / 驱动 / GPU / CUDA 版本”列为可能原因。
- 同一源码位置还明确警告：该 allocator 路径在多 GPU 场景下“probably will not work”。
- NVIDIA 的 TensorFlow 发布说明也把 `TF_GPU_ALLOCATOR=cuda_malloc_async` 列为可选开关，并明确记录过“可能导致 hangs / crashes / severe performance regressions”的已知问题，建议出现问题时直接 unset。

### 对本项目的长期结论

- 在 native Windows + `tf26` 组合下，`TF_GPU_ALLOCATOR=cuda_malloc_async` 应视为危险试验项，而不是常规优化项。
- 即使某台机器短期能启动，也不能把它推广为仓库默认推荐，因为它的兼容性同时受 GPU 架构、驱动版本、CUDA runtime、Windows 原生支持边界和 TensorFlow 构建方式共同影响。
- 如果某个项目只有在加上该变量时才“看起来更能吃满显存”或“更像能避开碎片化”，也不能因此默认保留；必须先证明它不会引入启动崩溃、无 traceback 退出、评估链中断或跨机器不可复现。

## 已知重大缺陷：`cuda_malloc_async` 可导致原生崩溃

以下信号组合应直接归类为 allocator 兼容性缺陷，而不是模型结构、数据集或普通 Python 逻辑错误：

- 日志出现 `Using CUDA malloc Async allocator for GPU` 后，进程在训练真正开始前就直接退出。
- 终端没有 Python traceback，但 Windows 事件查看器记录 `python.exe` / `ntdll.dll` / `0xc0000374`、`access violation` 或类似原生崩溃。
- 同一条训练命令在保持其余条件不变时，去掉 `TF_GPU_ALLOCATOR=cuda_malloc_async` 后可以继续构图、恢复权重或进入 epoch 循环。
- TensorFlow 直接报出 `TF_GPU_ALLOCATOR=cuda_malloc_async isn't currently supported`、driver too old、OS not supported、CUDA version too old 等底层 fatal 信息。

当出现上述任一模式时，应先把问题判定为“环境 / allocator 不兼容”，而不是继续调模型超参数或重做数据集。

## 推荐替代手段

如果目的是缓解显存占用、降低碎片风险或避免一次性占满 GPU，优先使用以下更稳妥的手段：

1. 保持 `TF_GPU_ALLOCATOR` 未设置，继续使用 TensorFlow 默认 allocator。
2. 使用 `TF_FORCE_GPU_ALLOW_GROWTH=true` 或 TensorFlow 的 `set_memory_growth`，避免进程启动时一次性抢占全部显存。
3. 使用 `tf.config.set_logical_device_configuration` 给单个 TensorFlow 进程设置显存上限。
4. 用 `CUDA_VISIBLE_DEVICES` 固定目标 GPU，避免多卡互相干扰。
5. 如果确实要评估 `cuda_malloc_async`，优先放到 WSL2/Linux 上受支持的新环境里做显式实验，不要先在 native Windows 的 `tf26` 上默认启用。

## 排查顺序

遇到 GPU 初始化后立即退出、训练无输出或 native crash 时，按以下顺序判断：

1. 先检查当前 shell、用户环境变量、系统环境变量中是否存在 `TF_GPU_ALLOCATOR`。
2. 如果值为 `cuda_malloc_async`，先完全移除，再重试同一训练命令。
3. 如果移除后问题消失，则记录为 allocator 兼容性缺陷，不继续沿模型代码方向深挖。
4. 如果仍失败，再继续排查 GPU lost、驱动坏状态、CUDA 可见卡排序、数据路径和模型实现问题。

## 与慢速训练的边界

- `TF_GPU_ALLOCATOR` 相关问题在本项目里优先表现为启动崩溃、无 traceback 退出或 GPU 初始化失败，而不是“只有某个 FRIKAN 变体掉到几十 `epoch/h`、但标准 FRIKAN 仍保持 `>1000 epoch/h`”。
- 因此，如果标准 FRIKAN 的前台 1 分钟测速已经恢复到正常区间，就不应继续把 trainable-IIR / true-IIR 变体的局部慢速首先归因于 allocator，而应回到模型训练路径、`MAX_BATCH_SIZE` 和语义等价性排查。
- 这类模型侧速度排查详见 [docs/reference/frikan_trainable_iir_speed.md](frikan_trainable_iir_speed.md)。

## 推荐检查命令

PowerShell：

```powershell
# 当前会话
$env:TF_GPU_ALLOCATOR

# 用户级 / 系统级
[Environment]::GetEnvironmentVariable('TF_GPU_ALLOCATOR', 'User')
[Environment]::GetEnvironmentVariable('TF_GPU_ALLOCATOR', 'Machine')

# 清除当前会话
Remove-Item Env:TF_GPU_ALLOCATOR -ErrorAction SilentlyContinue
```

Python：

```python
import os
print(os.environ.get("TF_GPU_ALLOCATOR"))
```

## 调用时机

当出现以下情况时，应优先回到本页检查环境边界，而不是立即改训练代码：

- `ModuleNotFoundError: No module named 'tensorflow'`
- TensorFlow GPU 初始化完成后立即退出
- 日志停在 `Using CUDA malloc Async allocator for GPU`
- 同一项目只在某些机器上因为加了某个环境变量才能启动
- 前台训练命令没有 traceback，但事件查看器出现 `python.exe` 原生崩溃

## 外部参考

- TensorFlow install (native Windows GPU support boundary): [https://www.tensorflow.org/install/pip](https://www.tensorflow.org/install/pip)
- TensorFlow GPU guide (`set_memory_growth` / GPU memory controls): [https://www.tensorflow.org/guide/gpu](https://www.tensorflow.org/guide/gpu)
- TensorFlow source (`TF_GPU_ALLOCATOR` switches allocator implementation): [https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/common_runtime/gpu/gpu_process_state.cc](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/common_runtime/gpu/gpu_process_state.cc)
- TensorFlow source (`cuda_malloc_async` support checks: driver / SM / OS / CUDA version): [https://android.googlesource.com/platform/external/tensorflow/+/refs/heads/main/tensorflow/core/common_runtime/gpu/gpu_cudamallocasync_allocator.cc](https://android.googlesource.com/platform/external/tensorflow/+/refs/heads/main/tensorflow/core/common_runtime/gpu/gpu_cudamallocasync_allocator.cc)
- NVIDIA TensorFlow user guide (`TF_GPU_ALLOCATOR=cuda_malloc_async` is optional and unset by default): [https://docs.nvidia.com/deeplearning/frameworks/tensorflow-user-guide/index.html](https://docs.nvidia.com/deeplearning/frameworks/tensorflow-user-guide/index.html)
- NVIDIA TensorFlow release notes (known hangs / crashes / regressions): [https://docs.nvidia.com/deeplearning/frameworks/tensorflow-release-notes/rel_22-08.html](https://docs.nvidia.com/deeplearning/frameworks/tensorflow-release-notes/rel_22-08.html)
- Public TensorFlow issue (`TF_GPU_ALLOCATOR=cuda_malloc_async` can fail even outside Windows): [https://github.com/tensorflow/tensorflow/issues/50669](https://github.com/tensorflow/tensorflow/issues/50669)
- Public Windows report with immediate termination after enabling the allocator: [https://forums.developer.nvidia.com/t/cudnn64-8-dll-is-causing-oom-error/192241](https://forums.developer.nvidia.com/t/cudnn64-8-dll-is-causing-oom-error/192241)
