# GPU 恢复与优先级说明

## 功能概述

训练命令 `python cli.py -t PROJECT_NAME` 在导入 TensorFlow 之前会执行一次 CUDA 预检查，用于处理多卡排序和 NVIDIA GPU 异常状态。

## 多卡优先级

当系统中有多张 NVIDIA GPU 且未手动设置 `CUDA_VISIBLE_DEVICES` 时，CLI 会按以下优先级重排可见 GPU：

1. `NVIDIA GeForce RTX 2080 Ti`
2. `NVIDIA GeForce RTX 3090`
3. 其他 GPU 保持原始索引顺序

重排发生在 TensorFlow 导入前，通过设置 `CUDA_VISIBLE_DEVICES` 实现。因此当 2080 Ti 和 3090 同时健康在线时，训练会优先落到 2080 Ti。

如果用户或外部脚本已经显式设置 `CUDA_VISIBLE_DEVICES`，CLI 会尊重现有设置，不再重排。

## 3090 lost 判定

出现以下任一现象时，应视为 3090 处于异常状态：

1. `nvidia-smi` 输出 `GPU is lost`
2. `pnputil /enum-devices /class Display` 中 3090 显示为 `已断开连接`
3. TensorFlow 在 `cuInit` 阶段报 `CUDA_ERROR_INVALID_VALUE` 或类似初始化错误

注意：Windows 的 `Win32_VideoController Status=OK` 不能单独作为 GPU 正常的依据，优先以 `nvidia-smi` 和 `pnputil` 为准。

## 训练时的自动处理

CLI 的 CUDA 预检查分两种情况：

1. 检测到 `GPU is lost` 且仍有健康 GPU：自动将 `CUDA_VISIBLE_DEVICES` 限制为健康 GPU，并按优先级排序。
2. 检测到 `GPU is lost` 且没有健康 GPU：自动设置 `CUDA_VISIBLE_DEVICES=-1`，强制回退 CPU。

如果屏蔽 lost GPU 后 TensorFlow 仍然无法完成 `cuInit`，日志会明确提示这是“驱动全局坏状态”，而不是普通的 `no GPU found`。

## 3090 软件恢复方法

管理员 PowerShell 可先尝试设备级重启：

```powershell
pnputil /restart-device "PCI\VEN_10DE&DEV_2204&SUBSYS_87B51043&REV_A1\4&5785E7C&0&0008"
```

如果设备仍在线但状态异常，可继续尝试：

```powershell
pnputil /disable-device "PCI\VEN_10DE&DEV_2204&SUBSYS_87B51043&REV_A1\4&5785E7C&0&0008" /force
pnputil /enable-device "PCI\VEN_10DE&DEV_2204&SUBSYS_87B51043&REV_A1\4&5785E7C&0&0008"
pnputil /scan-devices
```

## 何时停止软件恢复

如果出现以下组合状态，说明软件热恢复基本无效：

1. `pnputil` 提示 `设备没有连接`
2. `pnputil /enum-devices /class Display` 中 3090 持续为 `已断开连接`
3. `nvidia-smi -L` 持续看不到 3090

此时应改为冷启动或硬件排查：

1. 关机并彻底断电 10 到 30 秒
2. 重新上电后检查 `nvidia-smi -L`
3. 如仍异常，检查 PCIe 插槽、供电线和显卡接触状态

## 推荐排查命令

```powershell
pnputil /enum-devices /class Display
nvidia-smi -L
nvidia-smi --query-gpu=index,name,pci.bus_id,driver_version --format=csv,noheader
```

## 相关文件

- `cli.py`：TensorFlow 导入前执行 CUDA 预检查
- `src/utils/cuda_preflight.py`：GPU 排序与 lost GPU 处理逻辑
- `src/core/metnl.py`：TensorFlow GPU 初始化与异常诊断