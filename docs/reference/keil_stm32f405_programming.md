# STM32F405 Keil DAPLink Programming

本文档只描述 `src/tests/keil_projects/met_keil_405` 的长期稳定烧录/串口验收约束，不重复抄写通用 CLI 参数。通用安装与命令说明统一见 `C:\Users\lyon\.agents\skills\keil\SKILL.md` 与 `C:\Users\lyon\.agents\skills\serial-monitor\SKILL.md`。

## 适用范围

- 工程：`src/tests/keil_projects/met_keil_405/MDK-ARM/Electrochemical geophone.uvprojx`
- Target：`MET405`
- Device：`STM32F405RGTx`
- 调试链路：CMSIS-DAP / DAP-Link
- 运行态签收：串口启动日志，而不是单看“烧录成功”返回码

## DAP-Link 下载后端选择

对这个工程，`daplink` 下载链需要区分 `programmer.type` 与 `program_backend`：

- `programmer.type = daplink` 表示传输器类型是 CMSIS-DAP / DAP-Link。
- `program_backend = keil` 表示走 `UV4.exe -f <project.uvprojx>` 的工程下载链。
- `program_backend = pyocd` 表示直接走 pyOCD 下载链。
- `program_backend = auto` 表示优先按当前工程的 UV4 下载链执行；如果工程具备 UV4 下载元数据，则失败就直接报失败，不自动回退到 pyOCD，只在结果里提示可以改用其他 backend 重试。

对 `met_keil_405`，稳定做法是：

- 保留 `.uvprojx/.uvoptx` 里的 UV4 元数据用于 target、flash driver 和 probe 诊断。
- 当 `.uvoptx` 绑定的 probe UID 不等于当前在线 CMSIS-DAP，或当前板卡上的 UV4 下载链不可稳定复用时，优先使用 `program_backend = pyocd`。
- 不要在多探头同时在线时依赖 UV4 的隐式探头选择；要么先修正 `.uvoptx` probe 绑定并临时禁用/断开非目标 CMSIS-DAP，要么直接显式走 `pyocd` backend。
- 对当前 probe UID 这类带 `.` 的 selector，`.uvoptx` 中应写成 `-U"SN.33FF4D5074"` 这类带引号形式，不要写成无引号的 `-USN.33FF4D5074`。
- 对当前 `LUele.CMSIS-DAP` + `STM32F405RGTx` 组合，`UV4/CMSIS_AGDI` 对“系统里是否还有其他 CMSIS-DAP 在线”敏感；即使 `.uvoptx` 已绑定正确 UID，只要另一只 CMSIS-DAP 同时可见，仍可能报 `Internal DLL Error / Flash Download failed - Target DLL has been cancelled`。
- 当 `list-devices` 只剩目标 probe `SN.33FF4D5074` 在线时，`program_backend = keil` 与 `reset-run` 都可作为当前工程的可复用路径；如果不能隔离到单 probe，再改用 `program_backend = pyocd`。
- 如果 `program_backend = keil` 或 `reset-run` 在多 probe 环境下失败，但返回里的 `uvoptx_probe_check.status = bound_probe_online`，则应优先把问题归到 host `UV4/CMSIS_AGDI` 多 probe attach 限制，而不是继续怀疑 `.uvoptx` 没绑到明确 UID。
- `keil` skill 现在会在这类失败结果里附带 `diagnosis` 与 `keil_toolchain`；排查时优先对比不同主机上的 `UV4.exe` / `CMSIS_AGDI.dll` 版本差异，再决定是否继续改工程 XML。

## pyOCD 后端约束

这个工程上的 pyOCD 下载链必须满足以下条件：

- pyOCD `target_override` 优先从 `programmer.pyocd_target` 读取；未配置时，直接从 `.uvprojx/<Device>` 推导。
- 对 `STM32F405RGTx`，推导后的 pyOCD target 应为 `stm32f405rgtx`。
- 连接模式使用 `under-reset`，避免目标处于不稳定运行态时 attach 失败。
- 下载频率使用 `1000k`，作为当前工程的稳定口径。
- 当 pyOCD 的默认探测只识别出 generic `cortex_m/CoreSightTarget` 时，不能直接把该结果当作可烧录依据；必须依赖显式 `target_override` 或工程 `Device` 推导值再进行下载。
- pyOCD 下载完成后，还应显式执行一次 `reset + go + status`，确认目标最终处于 `Running`，不要把单独的 flash progress bar 直接当成“固件已经开始运行”。

也就是说，`detect` 允许返回 generic 目标，但 `program` / `flash` 不能在 generic 目标探测结论上盲烧。

## Probe 枚举与探测

`keil` skill 中与 DAP-Link 可见性相关的流程应遵循以下约束：

- probe 枚举与 `detect` 统一走 pyOCD Python API，不再依赖解析 `pyocd list` 或 `pyocd cmd` 的文本表格输出。
- `list-devices` 的职责是确认“当前有哪些 probe 可见”，以及这些 probe 与工程 `.uvoptx` 绑定之间是否一致。
- `detect` 的职责是确认“某个指定 probe 后面连接的是哪一类目标”；如果没有显式 target override，它可以只得到 generic `CoreSightTarget`。
- 对 `met_keil_405` 这类已有 `.uvprojx Device` 的工程，优先使用带工程上下文的 detect，即让 detect 从 `Device=STM32F405RGTx` 推导 `target_override=stm32f405rgtx`，从而返回具体 `STM32F405RGTx` 结果。
- 当多个 DAP-Link 同时在线时，所有真机下载命令都应显式传 `-u <probe_uid>`；不要依赖隐式第一个探头。
- 如果计划走 `program_backend = keil` 或 `reset-run`，仅有固定的 `.uvoptx` probe 绑定还不够；还应先用 `list-devices -p <project>` 确认当前系统里只剩目标 probe 在线。
- 如果 `list-devices` 明确看到多 probe，但 `uvoptx_probe_check` 仍显示目标 probe 已经 `bound_probe_online`，就不要再在 `-X/-U` 字段上来回盲改；优先看结果里的 `diagnosis.category` 是否已经落到 host-side `uv4_multi_probe_cmsis_agdi_attach_failure`。

## 串口验收约束

对 `met_keil_405`，真正的验收标准是串口启动日志，而不是下载工具本身的 success 字段。

稳定做法：

- 即使当前目标只保留“基础串口 bring-up”，最小 `main()` 也要保留原工程里与板级连线状态相关的前置初始化，至少包括 `MX_DMA_Init()` 与 `SWITCH_GPIO_Init()`；把这两步删掉后，目标可能仍显示 `Running`，但串口链路会在部分复位/重烧录场景下静默。
- `serial-monitor` 的固定服务端口保持不变，不通过修改其默认配置来规避板卡端口漂移。
- 在当前工作站上，`met_keil_405` 已验证的业务 UART 数据口是 `COM8 @ 115200`；不要再把另一个 `COM3` 混入这个工程的启动日志验收。
- 串口监控应绑定“当前实际的 UART 数据口”，而不是历史上曾经出现过的 COM 名称。
- DAP-Link 调试端口和业务 UART 端口可能分别枚举成不同 COM 口；Windows 出现重复或陈旧 COM 别名时，应以当前活跃 UART 口为准。
- 验证连续复位/重烧录稳定性时，优先保持 `serial-monitor` 监控会话持续打开，只做板卡 reset / reflash，然后用时间范围或当前 session 抓取新增日志。
- 不要把频繁 stop/start `serial-monitor` 当成主流程；Windows 释放串口句柄存在短暂竞态，停启过快会放大“端口拒绝访问”的假异常。

## 启动日志签收标准

当前基础串口 bring-up 的签收日志为：

```text
[  OK]: hardware init ok
[Info]: NN bring-up disabled, serial boot only
[Info]: UART1+UART3 mirrored at 115200 baud
```

满足以下条件才算通过：

- 三行日志都出现。
- 波特率口径为 `115200`。
- 日志来自当前活跃 UART 数据口，而不是 DAP-Link 控制接口。
- 同一监控会话内，多次 reflash / reset 后仍可重复抓到该组日志。

## 推荐验收路径

对 `met_keil_405` 的最小稳定验收路径是：

1. 先用 `keil-cli.py list-devices -p <project>` 确认当前系统里只剩目标 probe `SN.33FF4D5074` 在线；如果还有其他 CMSIS-DAP，先禁用或断开非目标 probe。
2. 用 `serial-monitor` 保持 `COM8 @ 115200` 的监控会话持续打开。
3. 单 probe 隔离成立后，优先可复用 `keil-cli.py program --program-backend keil`；如果当前机器条件下不能隔离到单 probe，再改用 `--program-backend pyocd`。
4. 只重启不重烧录时，可用 `keil-cli.py reset-run`；但它的成功仍要回到 `serial-monitor fetch` 的启动日志证据签收。
5. 下载或 reset 完成后，通过 `serial-monitor fetch` 抓取开始时间之后的新日志。
6. 只有当启动日志满足上一节的签收标准时，才判定这次下载链路有效。

## 失效判定

出现以下任一情况，都不应把结果判定为“Keil 项目可稳定烧录”：

- `program_backend = keil` 时，`.uvoptx` probe 绑定 UID 与当前在线 probe 不一致。
- 计划走 `program_backend = keil` 或 `reset-run`，但 `list-devices` 仍看到第二只 CMSIS-DAP 在线。
- 多个 DAP-Link 同时在线，但命令未显式指定 `-u <probe_uid>`。
- pyOCD 只识别出 generic `CoreSightTarget`，却没有显式 target override 仍继续下载。
- 下载工具返回 success，但串口未出现签收日志。
- 通过 stop/start 串口工具才“偶尔抓到”日志，而持续监控 + reset/reflash 不能稳定复现。
